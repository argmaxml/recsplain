import json, itertools, collections, sys, os
from operator import itemgetter as at
import numpy as np
from pathlib import Path

src = Path(__file__).absolute().parent
sys.path.append(str(src))
from encoders import PartitionSchema
from joblib import delayed, Parallel
from similarity_helpers import parse_server_name, FlatFaiss

class BaseStrategy:
    __slots__ = ["schema", "partitions","index_labels", "model_dir", "IndexEngine", "engine_params"]
    def __init__(self, model_dir=None, similarity_engine=None ,engine_params={}):
        if similarity_engine is None:
            self.IndexEngine = FlatFaiss
            self.engine_params = {}
        else:
            self.IndexEngine = parse_server_name(similarity_engine)
            self.engine_params = engine_params
        if model_dir:
            self.model_dir = Path(model_dir)
        else:
            self.model_dir = Path(__file__).absolute().parent.parent / "models"
        self.partitions = None
        self.schema =  None
        self.index_labels = []


    def init_schema(self, **kwargs):
        self.schema = PartitionSchema(**kwargs)
        self.partitions = [self.IndexEngine(self.schema.metric, self.schema.dim, **self.engine_params) for _ in self.schema.partitions]
        enc_sizes = {k:len(v) for k,v in self.schema.encoders.items()}
        return self.schema.partitions, enc_sizes

    def index(self, data):
        errors = []
        vecs = []
        for datum in data:
            try:
                vecs.append((self.schema.partition_num(datum), self.schema.encode(datum), datum[self.schema.id_col]))
            except Exception as e:
                errors.append((datum, str(e)))
        vecs = sorted(vecs, key=at(0))
        affected_partitions = 0
        labels = set(self.index_labels)
        for partition_num, grp in itertools.groupby(vecs, at(0)):
            _, items, ids = zip(*grp)
            for id in ids:
                if id in labels:
                    errors.append((datum, "{id} already indexed.".format(id=id)))
                    continue # skip labels that already exists
                else:
                    labels.add(id)
                    self.index_labels.append(id)
            affected_partitions += 1
            num_ids = list(map(self.index_labels.index, ids))
            self.partitions[partition_num].add_items(items, num_ids)
        return errors, affected_partitions


    def index_dataframe(self, df, parallel=True):
        partitioned = df.groupby(self.schema.filters).apply(lambda ds: ds.to_dict(orient='records'))
        encoded = dict()
        num_ids = dict()
        partition_nums = dict()
        num_id_start = len(self.index_labels)
        affected_partitions = len(partitioned)
        # Cannot be parallelized because index_labels should be consequently updated
        for partition, data in partitioned.items():
            partition_nums[partition] = self.schema.partition_num(data[0])
            if not parallel:
                encoded[partition] = self.encode(data)
            num_ids[partition] =(num_id_start, num_id_start+len(data))
            self.index_labels.extend([datum[self.schema.id_col] for datum in data])
            num_id_start+=len(data)

        if parallel:
            @delayed
            def tup_encode(partition, data):
                return partition, self.encode(data)
            encoded = dict(Parallel(n_jobs=-1)(tup_encode(partition, data) for partition, data in partitioned.items()))

            @delayed
            def add_items_to_partition(data, partition_num, from_, to_):
                ids = np.arange(from_, to_)
                self.partitions[partition_num].add_items(data, ids)
            
            Parallel(n_jobs=-1, require='sharedmem')([add_items_to_partition(data, partition_nums[partition], num_ids[partition][0], num_ids[partition][1]) for partition, data in encoded.items()])
        else:
            for partition, data in encoded.items():
                partition_num = partition_nums[partition]
                from_, to_ = num_ids[partition]
                ids = list(range(from_, to_))
                self.partitions[partition_num].add_items(data, ids)
        return affected_partitions


    def query_by_partition_and_vector(self, partition_num, vec, k, explain=False):
        try:
            vec = vec.reshape(1,-1).astype('float32') # for faiss
            distances, num_ids = self.partitions[partition_num].search(vec, k=k)
        except Exception as e:
            raise Exception("Error in querying: " + str(e))
        if len(num_ids) == 0:
            labels, distances = [], []
        else:
            labels = [self.index_labels[n] for n in num_ids[0]]
            distances = [float(d) for d in distances[0]]
        if not explain:
            return labels,distances, []

        vec = vec.reshape(-1)
        explanation = []
        X = self.partitions[partition_num].get_items(num_ids[0])
        first_sim = None
        for ret_vec in X:
            start=0
            explanation.append({})
            for col,enc in self.schema.encoders.items():
                if enc.column_weight==0:
                    explanation[-1][col] = 0#float(enc.column_weight)
                    continue
                end = start + len(enc)
                ret_part = ret_vec[start:end]
                query_part =   vec[start:end]
                if self.schema.metric=='l2':
                    # The returned distance from the similarity server is not squared
                    dst=((ret_part-query_part)**2).sum()
                else:
                    sim=np.dot(ret_part,query_part)
                    # Correct dot product to be ascending
                    if first_sim is None:
                        first_sim = sim
                        dst = 0
                    else:
                        dst = 1-sim/first_sim
                explanation[-1][col]=float(dst)
                start = end
        return labels,distances, explanation

    def query(self, data, k, explain=False):
        try:
            partition_nums = self.schema.partition_num(data)
        except Exception as e:
            raise Exception("Error in partitioning: " + str(e))
        try:
            vec = self.schema.encode(data)
        except Exception as e:
            raise Exception("Error in encoding: " + str(e))
        if type(partition_nums)!=list:
            return self.query_by_partition_and_vector(partition_nums, vec, k, explain)
        # Aggregate results if multiple partitions are returned:
        labels,distances,explanation = [], [], []
        for partition_num in partition_nums:
            l,d,e = self.query_by_partition_and_vector(partition_num, vec, k, explain)
            labels.extend(l)
            distances.extend(d)
            #TODO: explanation is not supported when having multiple filters
        labels,distances = zip(*sorted(zip(labels,distances), key=at(1)))
        return labels,distances,explanation



    def save_model(self, model_name):
        model_dir = (self.model_dir/model_name)
        if os.sep in model_name:
            model_dir = Path(model_name)
        model_dir.mkdir(parents=True, exist_ok=True)
        with (model_dir/"index_labels.json").open('w') as f:
            json.dump(self.index_labels, f)
        with (model_dir/"schema.json").open('w') as f:
            json.dump(self.schema.to_dict(), f)
        saved=0
        for i,p in enumerate(self.partitions):
            fname = str(model_dir/str(i))
            try:
                p.save_index(fname)
                saved+=1
            except:
                continue
        return {"status": "OK", "saved_indices": saved, "path": str(self.model_dir/model_name)}

    def load_model(self, model_name):
        model_dir = (self.model_dir/model_name)
        if os.sep in model_name:
            model_dir = Path(model_name)
        with (model_dir/"schema.json").open('r') as f:
            schema_dict=json.load(f)
        self.schema = PartitionSchema(**schema_dict)
        self.partitions = [self.IndexEngine(self.schema.metric, self.schema.dim, **self.engine_params) for _ in self.schema.partitions]
        model_dir.mkdir(parents=True, exist_ok=True)
        with (model_dir/"index_labels.json").open('r') as f:
            self.index_labels=json.load(f)
        loaded = 0
        for i,p in enumerate(self.partitions):
            fname = str(model_dir/str(i))
            try:
                p.load_index(fname)
                loaded+=1
            except:
                continue
        return loaded, schema_dict

    def list_models(self):
        ret = [d.name for d in self.model_dir.iterdir() if d.is_dir()]
        ret.sort()
        return ret

    def fetch(self, lbls, numpy=False):
        sil = set(self.index_labels)
        found = [l for l in lbls if l in sil]
        ids = [self.index_labels.index(l) for l in found]
        ret = collections.defaultdict(list)
        for p,pn in zip(self.partitions, self.schema.partitions):
            for id in ids:
                try:
                    if numpy:
                        ret[pn].extend(p.get_items([id]))
                    else:
                        ret[pn].extend([tuple(float(v) for v in vec) for vec in p.get_items([id])])
                except Exception as e:
                    # not found
                    pass
        ret = map(lambda k,v: (k[0],v) if len(k)==1 else (str(k), v),ret.keys(), ret.values())
        ret = dict(filter(lambda kv: bool(kv[1]),ret))
        return ret

    def encode(self, data):
        return self.schema.encode(data)

    def schema_initialized(self):
        return (self.schema is not None)

    def get_partition_stats(self):
        display = lambda t: str(t[0]) if len(t)==1 else str(t)
        max_elements  = {display(p):self.partitions[i].get_max_elements()  for i,p in enumerate(self.get_partitions())}
        element_count = {display(p):self.partitions[i].get_current_count() for i,p in enumerate(self.get_partitions())}
        return {"max_elements": max_elements, "element_count":element_count, "n": len(self.partitions)}

    def get_partitions(self):
        return self.schema.partitions

    def get_embedding_dimension(self):
        return self.schema.dim

    def get_total_items(self):
        return len(self.index_labels)


class AvgUserStrategy(BaseStrategy):
    def user_partition_num(self, user_data):
        # Assumes same features as the item
        return self.schema.partition_num(user_data)

    def user_query(self, user_data, item_history, k, user_coldstart_item=None):
        if user_coldstart_item is None:
            n = 0
            vec = np.zeros(self.schema.dim)
        else:
            n = 1
            vec = self.schema.encode(user_coldstart_item)
        user_partition_num = self.user_partition_num(user_data)
        col_mapping = self.schema.component_breakdown()
        labels,distances = [], []
        if type(item_history) == str:
            item_history = [item_history]
        for item in item_history:
            # Calculate AVG
            item_vectors = [v for vs in self.fetch(item, numpy=True).values() for v in vs]
            n+=len(item_vectors)
            vec += np.sum(item_vectors, axis=0)
        if n>0:
            vec /= n
        # Override column values post aggregation, if needed
        for col, enc in self.schema.user_encoders.items():
            if col not in user_data:
                continue
            start, end = col_mapping[col]
            vec[start:end] = enc(user_data[col])
        # Query
        item_labels,item_distances,_ = self.query_by_partition_and_vector(user_partition_num, vec, k)
        labels.extend(item_labels)
        distances.extend(item_distances)
        return labels, distances

