import json, itertools, collections, sys, os
from operator import itemgetter as at
import numpy as np
from pathlib import Path
from typing import List, Dict, Tuple, Union, Optional, Any, Callable

# Optional dependencies
try:
    from redis import Redis
except ModuleNotFoundError:
    Redis = None

# src = Path(__file__).absolute().parent
# sys.path.append(str(src))
from .encoders import PartitionSchema
from joblib import delayed, Parallel
from .similarity_helpers import parse_server_name, FaissIndexFactory

class BaseStrategy:
    __slots__ = ["schema", "partitions","index_labels", "model_dir", "IndexEngine", "engine_params", "parallel"]
    def __init__(self, model_dir=None, similarity_engine=None ,engine_params={}):
        if similarity_engine is None:
            self.IndexEngine = FaissIndexFactory
            self.engine_params = {}
        else:
            self.IndexEngine = parse_server_name(similarity_engine)
            self.engine_params = engine_params
        if model_dir:
            self.model_dir = Path(model_dir)
        else:
            self.model_dir = Path(__file__).absolute().parent.parent / "models"
        self.partitions = {}
        self.schema = {}
        self.index_labels = []
        self.parallel = True


    def init_schema(self, **kwargs):
        self.schema = PartitionSchema(**kwargs)
        self.partitions[self.schema.base_strategy_id()] = [self.IndexEngine(self.schema.metric, self.schema.dim,
                                                                            index_factory=self.schema.index_factory,
                                                                            **self.engine_params)
                                                           for _ in self.schema.partitions]
        enc_sizes = {k: len(v) for k, v in self.schema.encoders[self.schema.base_strategy_id()].items()}
        return self.schema.partitions, enc_sizes

    def add_variant(self, variant):
        variant = self.schema.add_variant(variant)
        self.partitions[variant['id']] = [self.IndexEngine(self.schema.metric, self.schema.dim,
                                                           index_factory=self.schema.index_factory, **self.engine_params)
                                          for _ in self.schema.partitions]
        # enc_sizes = {k: len(v) for k, v in self.schema.encoders[self.schema.base_strategy_id()].items()}
        return variant#, enc_sizes

    def index(self, data, strategy_id=None):
        if not strategy_id:
            strategy_id = self.schema.base_strategy_id()
        errors = []
        vecs = []
        for datum in data:
            try:
                vecs.append((self.schema.partition_num(datum), self.schema.encode(datum), datum[self.schema.id_col]))
            except Exception as e:
                errors.append((datum, str(e)))
        vecs = sorted(vecs, key=at(0))
        affected_partitions = 0
        labels = set(map(str,self.index_labels))
        for partition_num, grp in itertools.groupby(vecs, at(0)):
            _, items, ids = zip(*grp)
            if strategy_id == self.schema.base_strategy_id():
                for id in ids:
                    if str(id) in labels:
                        errors.append((datum, "{id} already indexed.".format(id=id)))
                        continue  # skip labels that already exists
                    else:
                        labels.add(str(id))
                        self.index_labels.append(str(id))
            affected_partitions += 1
            num_ids = list(map(self.index_labels.index, ids))
            self.partitions[strategy_id][partition_num].add_items(items, num_ids)
            if strategy_id == self.schema.base_strategy_id():
                self.schema.add_mapping(partition_num, num_ids, [d for d in data if d['id'] in ids])
        return errors, affected_partitions

    def index_dataframe(self, df, parallel=None, strategy_id=None):
        if not strategy_id:
            strategy_id = self.schema.base_strategy_id()
        if parallel is None:
            parallel = self.parallel
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
                encoded[partition] = self.encode(data, strategy_id)
            num_ids[partition] =(num_id_start, num_id_start+len(data))
            num_id_range=list(range(num_id_start, num_id_start+len(data)))
            ids=[datum[self.schema.id_col] for datum in data]
            self.index_labels.extend(map(str,ids))
            self.schema.add_mapping(partition_nums[partition], num_id_range, data)
            num_id_start+=len(data)

        if parallel:
            @delayed
            def tup_encode(partition, data, strategy_id):
                return partition, self.encode(data, strategy_id)
            encoded = dict(Parallel(n_jobs=-1)(tup_encode(partition, data, strategy_id) for partition, data in partitioned.items()))

            @delayed
            def add_items_to_partition(vecs, partition_num, strategy_id, from_, to_):
                ids = np.arange(from_, to_)
                self.partitions[strategy_id][partition_num].add_items(vecs, ids)
            
            Parallel(n_jobs=-1, require='sharedmem')([add_items_to_partition(data, partition_nums[partition], strategy_id, num_ids[partition][0], num_ids[partition][1]) for partition, data in encoded.items()])
        else:
            for partition, vecs in encoded.items():
                partition_num = partition_nums[partition]
                from_, to_ = num_ids[partition]
                ids = list(range(from_, to_))
                self.partitions[strategy_id][partition_num].add_items(vecs, ids)
        return affected_partitions

    def query_by_partition_and_vector(self, partition_num, strategy_id, vec, k, explain=False):
        if not strategy_id:
            strategy_id = self.schema.base_strategy_id()
        try:
            vec = vec.reshape(1, -1).astype('float32')  # for faiss
            distances, num_ids = self.partitions[strategy_id][partition_num].search(vec, k=k)
            if hasattr(distances[0],"__iter__"):
                distances=distances[0]
                num_ids=num_ids[0]
            distances = [d for d,i in zip(distances,num_ids) if i>=0]
            num_ids = [i for i in num_ids if i>=0]
        except Exception as e:
            raise Exception("Error in querying: " + str(e))
        if len(num_ids) == 0:
            labels, distances = [], []
        else:
            labels = [self.index_labels[n] for n in num_ids]
            distances = [float(d) for d in distances]
        if not explain:
            return labels, distances, []

        vec = vec.reshape(-1)
        explanation = []
        # X = self.partitions[partition_num].get_items(num_ids[0])
        X = np.array([self.schema.restore_vector_with_index(partition_num, index, strategy_id) for index in num_ids], dtype='float32')
        first_sim = None
        for ret_vec in X:
            start = 0
            explanation.append({})
            for col, enc in self.schema.encoders[strategy_id].items():
                if enc.column_weight == 0:
                    explanation[-1][col] = 0  # float(enc.column_weight)
                    continue
                end = start + len(enc)
                ret_part = ret_vec[0][start:end]
                query_part = vec[start:end]
                if self.schema.metric == 'l2':
                    # The returned distance from the similarity server is not squared
                    dst = ((ret_part-query_part)**2).sum()
                else:
                    sim = np.dot(ret_part,query_part)
                    # Correct dot product to be ascending
                    if first_sim is None:
                        first_sim = sim
                        dst = 0
                    else:
                        dst = 1-sim/first_sim
                explanation[-1][col]=float(dst)
                start = end
        return labels, distances, explanation

    def query(self, data, k, strategy_id=None, explain=False):
        if not strategy_id:
            strategy_id = self.schema.base_strategy_id()
        try:
            partition_nums = self.schema.partition_num(data)
            if type(partition_nums) != list:
                partition_nums = [partition_nums]
        except Exception as e:
            raise Exception("Error in partitioning: " + str(e))
        try:
            vec = self.schema.encode(data, strategy_id)
        except Exception as e:
            raise Exception("Error in encoding: " + str(e))
            return self.query_by_partition_and_vector(partition_nums, strategy_id, vec, k, explain)

        # Aggregate results if multiple partitions are returned:
        labels, distances, explanation = [], [], []
        for partition_num in partition_nums:
            l, d, e = self.query_by_partition_and_vector(partition_num, strategy_id, vec, k, explain)
            labels.extend(l)
            distances.extend(d)
            explanation.extend(e)
            #TODO: explanation is not supported when having multiple filters
        labels, distances = zip(*sorted(zip(labels, distances), key=at(1)))
        return labels, distances, explanation



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
        for strategy_id, partitions in self.partitions.items():
            for i,p in enumerate(partitions):
                fname = str(model_dir/str(strategy_id + "_" + str(i)))
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
        self.partitions = {strategy['id']: [self.IndexEngine(self.schema.metric, self.schema.dim, index_factory=self.schema.index_factory,
                                            **self.engine_params) for _ in self.schema.partitions] for strategy in self.schema.strategies}
        model_dir.mkdir(parents=True, exist_ok=True)
        with (model_dir/"index_labels.json").open('r') as f:
            self.index_labels=json.load(f)
        loaded = 0
        for strategy_id, partitions in self.partitions.items():
            for i,p in enumerate(partitions):
                fname = str(model_dir/str(strategy_id + "_" + str(i)))
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

    def fetch(self, lbls, strategy_id=None, numpy=False):
        if not strategy_id:
            strategy_id = self.schema.base_strategy_id()
        sil = set(map(str,self.index_labels))
        if type(lbls) == list:
            found = [str(l) for l in lbls if str(l) in sil]
        else:
            found = [str(lbls)] if str(lbls) in sil else []
        ids = [self.index_labels.index(l) for l in found]
        ret = collections.defaultdict(list)
        for partition_num, (p,pn) in enumerate(zip(self.partitions[strategy_id], self.schema.partitions)):
            for id in ids:
                try:
                    if numpy:
                        # ret[pn].extend(p.get_items([id]))
                        ret[pn].extend(self.schema.restore_vector_with_index(partition_num, id, strategy_id))
                    else:
                        # ret[pn].extend([tuple(float(v) for v in vec) for vec in p.get_items([id])])
                        ret[pn].extend([tuple(float(v) for v in vec) for vec in self.schema.restore_vector_with_index(partition_num, id, strategy_id)])
                except KeyError as e:
                    # print(str(e))
                    # not found
                    pass
        ret = map(lambda k,v: (k[0],v) if len(k)==1 else (str(k), v),ret.keys(), ret.values())
        ret = dict(filter(lambda kv: bool(kv[1]),ret))
        return ret

    def encode(self, data, strategy_id=None):
        return self.schema.encode(data, strategy_id)

    def schema_initialized(self):
        return (self.schema is not None)

    def get_partition_stats(self):
        display = lambda t: str(t[0]) if len(t)==1 else str(t)
        max_elements  = {display(p):self.partitions[self.schema.base_strategy_id()][i].get_max_elements()  for i,p in enumerate(self.get_partitions())}
        element_count = {display(p):self.partitions[self.schema.base_strategy_id()][i].get_current_count() for i,p in enumerate(self.get_partitions())}
        return {"max_elements": max_elements, "element_count":element_count, "n": len(self.partitions[self.schema.base_strategy_id()])}

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

    def user_query(self, user_data, item_history, k, strategy_id=None, user_coldstart_item=None, user_coldstart_weight=1):
        if not strategy_id:
            strategy_id = self.schema.base_strategy_id()
        if user_coldstart_item is None:
            n = 0
            vec = np.zeros(self.schema.dim)
        else:
            n = user_coldstart_weight
            if hasattr(user_coldstart_item, "__call__"):
                item = user_coldstart_item(user_data)
            elif type(user_coldstart_item) == dict:
                item = user_coldstart_item
            vec = self.schema.encode(item, strategy_id)
        user_partition_num = self.user_partition_num(user_data)
        col_mapping = self.schema.component_breakdown()
        labels, distances = [], []
        if type(item_history) == str:
            item_history = {item_history:1}
        elif type(item_history) == list:
            item_history = {i:1 for i in item_history}
        for item, w in item_history.items():
            # Calculate AVG
            item_vectors = [v for vs in self.fetch(item, numpy=True).values() for v in vs]
            n+=w*len(item_vectors)
            vec += w*np.sum(item_vectors, axis=0)
        if n>0:
            vec /= n
        # Override column values post aggregation, if needed
        for col, enc in self.schema.user_encoders.items():
            if col not in user_data:
                continue
            start, end = col_mapping[col]
            vec[start:end] = enc(user_data[col])
        # Query
        item_labels, item_distances, _ = self.query_by_partition_and_vector(user_partition_num, strategy_id, vec, k)
        labels.extend(item_labels)
        distances.extend(item_distances)
        return labels, distances


class RedisStrategy(BaseStrategy):
    def __init__(self, model_dir=None, similarity_engine=None, engine_params={}, redis_credentials=None, user_prefix="user:",vector_prefix="vec:", value_sep="|", user_keys=[],event_key="event",item_key="item",event_weights={}):
        super().__init__(model_dir, similarity_engine, dict(engine_params,redis_credentials=redis_credentials))
        assert Redis is not None, "RedisStrategy requires redis-py to be installed"
        assert redis_credentials is not None, "RedisStrategy requires redis credentials"
        assert len(user_keys)>0, "user_keys not supplied"
        assert event_key in user_keys, "event_key not in user_keys"
        assert item_key in user_keys, "item_key not in user_keys"
        self.redis = Redis(**redis_credentials)
        self.sep = value_sep
        self.user_prefix = user_prefix
        self.vector_prefix = vector_prefix
        self.event_key=event_key
        self.user_keys=user_keys
        self.item_key=item_key
        self.event_weights=event_weights
        self.pipe = None
        self.parallel = False # HACK
    def __enter__(self):
        self.pipe = self.redis.pipeline()
        return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.pipe.execute()
        self.pipe = None
    def set_vector(self, key, arr):
        """Sets a numpy array as a vector in redis"""
        emb = np.array(arr).astype(np.float32).tobytes()
        self.redis.set(self.vector_prefix+str(key), emb)
        return self
    def get_vector(self, key):
        """Gets a numpy array from redis"""
        return np.frombuffer(self.redis.get(self.vector_prefix+str(key)), dtype=np.float32)
    def del_user(self, user_id):
        if self.pipe:
            self.pipe.delete(self.user_prefix+str(user_id))
        else:
            self.redis.delete(self.user_prefix+str(user_id))
    def get_events(self, user_id: str):
        if self.pipe:
            ret = self.redis.lrange(self.user_prefix+str(user_id), 0, -1)
        else:
            ret = self.redis.lrange(self.user_prefix+str(user_id), 0, -1)
        return [dict(zip(self.user_keys,x.decode().split(self.sep))) for x in ret]
    def add_event(self, user_id: str, data: Dict[str, str]):
        vals = []
        for key in self.user_keys:
            v = data.get(key,"")
            # ad hoc int trimming
            try:
                if v==int(v):
                    v=int(v)
            except:
                pass
            vals.append(v)
        val = self.sep.join(map(str, vals))
        if self.pipe:
            self.pipe.rpush(self.user_prefix+str(user_id), val)
        else:
            self.redis.rpush(self.user_prefix+str(user_id), val)
        return self
    def pop_event(self, user_id: str):
        if self.pipe:
            ret = self.pipe.lpop(self.user_prefix+str(user_id))
        else:
            ret = self.redis.lpop(self.user_prefix+str(user_id))
        ret = dict(zip(self.user_keys,ret.decode().split(self.sep)))
        return ret
    def user_partition_num(self, user_data):
        # Assumes same features as the item
        return self.schema.partition_num(user_data)

    def user_query(self, user_data, k, strategy_id=None, user_coldstart_item=None, user_coldstart_weight=1,user_id=None):
        if not strategy_id:
            strategy_id = self.schema.base_strategy_id()
        vec = np.zeros(self.schema.dim)
        n = 0
        if user_coldstart_item is not None:
            n = user_coldstart_weight
            if type(user_coldstart_item) == str:
                vec = self.get_vector(user_coldstart_item)
            elif type(user_coldstart_item) == dict:
                item = user_coldstart_item
                vec = self.schema.encode(item, strategy_id)
        user_partition_num = self.user_partition_num(user_data)
        col_mapping = self.schema.component_breakdown()
        labels, distances = [], []
        if user_id is None:
            user_id = user_data.get("id")
        if user_id is None:
            raise ValueError("user_id not supplied")
        item_history = self.get_events(user_id)
        for item in item_history:
            item_id = item.get(self.item_key)
            if item_id is None:
                continue
            w = self.event_weights.get(item.get(self.event_key),1)
            # Calculate AVG
            item_vectors = [v for vs in self.fetch(item_id, numpy=True).values() for v in vs]
            n+=w*len(item_vectors)
            vec += w*np.sum(item_vectors, axis=0)
        if n>0:
            vec /= n
        # Override column values post aggregation, if needed
        for col, enc in self.schema.user_encoders.items():
            if col not in user_data:
                continue
            start, end = col_mapping[col]
            vec[start:end] = enc(user_data[col])
        # Query
        item_labels, item_distances, _ = self.query_by_partition_and_vector(user_partition_num, strategy_id, vec, k)
        labels.extend(item_labels)
        distances.extend(item_distances)
        labels, distances = zip(*sorted(zip(labels, distances), key=at(1)))
        return labels, distances



        