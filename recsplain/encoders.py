import json, re, itertools, collections, os
from copy import deepcopy as clone
from operator import itemgetter as at
import numpy as np
from .tree_helpers import lowest_depth, get_values_nested
import requests
from smart_open import open
from collections import defaultdict


class PartitionSchema:
    __slots__ = ["encoders", "filters", "partitions", "dim", "metric", "defaults", "id_col", "user_encoders",
                 "feature_embeddings", "feature_mapping", "item_mappings", "index_factory",
                 "strategies"]

    def __init__(self, encoders, strategies=[{"id": "0", "name": "default", "is_base": True}], filters=[], metric='ip', id_col="id",
                 user_encoders={}, index_factory="Flat"):

        self.strategies = strategies
        self.metric = metric
        self.index_factory = index_factory
        self.id_col = id_col
        self.filters, self.partitions = self._parse_filters(filters)
        self.encoders = self._parse_encoders(encoders)
        self.user_encoders = self._parse_encoders(user_encoders)
        self.defaults = {}
        self.item_mappings = defaultdict(dict)
        for f, e in self.encoders[self.base_strategy_id()].items():
            if e.default is not None:
                self.defaults[f] = e.default
        feature_embeddings, self.feature_mapping = self._create_feature_mapping(self.encoders[self.base_strategy_id()].items())
        self.feature_embeddings = {self.base_strategy_id(): feature_embeddings}
        self.dim = sum(map(len, filter(lambda e: e.column_weight != 0, self.encoders[self.base_strategy_id()].values())))

    def _parse_encoders(self, encoders):
        strategy_encoders_dict = dict()
        if type(encoders) == list:
            encoders = {self.base_strategy_id(): encoders}
        for strategy, strategy_encoders in encoders.items():
            encoder_dict = dict()
            for enc in strategy_encoders:
                if enc["type"] in ["onehot", "one_hot", "one hot", "oh"]:
                    encoder_dict[enc["field"]] = OneHotEncoder(column=enc["field"], column_weight=enc["weight"],
                                                        values=enc["values"], default=enc.get("default"))
                elif enc["type"] in ["strictonehot", "strict_one_hot", "strict one hot", "soh"]:
                    encoder_dict[enc["field"]] = StrictOneHotEncoder(column=enc["field"], column_weight=enc["weight"],
                                                                values=enc["values"], default=enc.get("default"))
                elif enc["type"] in ["num", "numeric"]:
                    encoder_dict[enc["field"]] = NumericEncoder(column=enc["field"], column_weight=enc["weight"],
                                                        values=enc["values"], default=enc.get("default"))
                elif enc["type"] in ["ordinal", "ordered"]:
                    encoder_dict[enc["field"]] = OrdinalEncoder(column=enc["field"], column_weight=enc["weight"],
                                                        values=enc["values"], default=enc.get("default"), window=enc["window"])
                elif enc["type"] in ["bin", "binning"]:
                    encoder_dict[enc["field"]] = BinEncoder(column=enc["field"], column_weight=enc["weight"],
                        values=enc["values"], default=enc.get("default"))
                elif enc["type"] in ["binordinal", "bin_ordinal", "bin ordinal", "ord bin"]:
                    encoder_dict[enc["field"]] = BinOrdinalEncoder(column=enc["field"], column_weight=enc["weight"],
                        values=enc["values"], default=enc.get("default"), window=enc["window"])
                elif enc["type"] in ["hier", "hierarchy", "nested"]:
                    encoder_dict[enc["field"]] = HierarchyEncoder(column=enc["field"], column_weight=enc["weight"],
                                                            values=enc["values"], default=enc.get("default"),
                                                            similarity_by_depth=enc["similarity_by_depth"])
                elif enc["type"] in ["numpy", "np", "embedding"]:
                    encoder_dict[enc["field"]] = NumpyEncoder(column=enc["field"], column_weight=enc["weight"],
                                                                values=enc["values"], default=enc.get("default"), npy=enc["npy"])
                elif enc["type"] in ["JSON", "json", "js"]:
                    encoder_dict[enc["field"]] = JSONEncoder(column=enc["field"], column_weight=enc["weight"],
                                                                values=enc["values"], default=enc.get("default"), length=enc["length"])
                elif enc["type"] in ["qwak"]:
                    encoder_dict[enc["field"]] = QwakEncoder(column=enc["field"], column_weight=enc["weight"],
                                                                length=enc["length"], entity_name=enc["entity"], default=enc.get("default"),
                                                                feature_name=enc["feature"], environment=enc["environment"])
                else:
                    raise TypeError("Unknown type {t} in field {f}".format(f=enc["field"], t=enc["type"]))
            strategy_encoders_dict[strategy] = encoder_dict
        return strategy_encoders_dict

    def _parse_filters(self, filters):
        ret_filters = []
        partitions = [("ALL",)]
        if any(filters):
            partitions = list(itertools.product(*[f["values"] for f in filters]))
            ret_filters = [f["field"] for f in filters]
        return ret_filters, partitions

    def _unparse_encoders(self, encoders):
        return [dict({"field": k, "values": e.values, "type": type(e).__name__.replace("Encoder", "").lower(),
                      "weight": e.column_weight, "default": e.default}, **e.special_properties())
                for k, e in encoders.items()]

    def _unparse_filters(self, filters, partitions):
        ret_filters = collections.defaultdict(list)
        for i, k in enumerate(filters):
            for v in map(at(i), partitions):
                ret_filters[k].append(v)
        ret_filters = [{"field":k, "values": list(v)} for k,v in ret_filters.items()]
        return ret_filters

    def _create_feature_mapping(self, encoders):
        embeddings_dict = {}
        mapping_dict = {}
        for name, encoder in encoders:
            if isinstance(encoder, NumericEncoder):
                continue
            embeddings = np.array([encoder.encode(value) for value in encoder.values])
            embeddings_dict[name] = embeddings
            mapping_dict[name] = {v: i for i, v in enumerate(encoder.values)}
        return embeddings_dict, mapping_dict

    def add_variant(self, variant):
        self.encoders[variant['id']] = self.encoders[self.base_strategy_id()].copy()
        for feature_name, weight in variant['weights'].items():
            self.encoders[variant['id']][feature_name].column_weight = weight
        variant_dict = {'id': variant['id'], 'name': variant['name'],
                        'encoders': self._unparse_encoders(self.encoders[variant['id']])}
        feature_embeddings, _ = self._create_feature_mapping(self.encoders[variant['id']].items())
        self.feature_embeddings[variant['id']] = feature_embeddings


        print("Added variant {v}".format(v=variant['id']))
        return variant_dict



    def encode(self, x, strategy_id=None, weights=None):
        if not strategy_id:
            strategy_id = self.base_strategy_id()
            # TODO: raise error if no base strategy
        if type(x) == list:
            return np.vstack([self.encode(t, weights) for t in x])
        elif type(x) == dict:
            # Add default values to dict
            for f, d in self.defaults.items():
                if f not in x:
                    x[f] = d
            if weights is None:
                weights_mapping = {k: v for k, v in zip(self.encoders[strategy_id].keys(),
                                                        [encoder.normalized_column_weight() for
                                                         encoder in self.encoders[strategy_id].values()])}
            else:
                weights_mapping = {k: v for k, v in zip(self.encoders[strategy_id].keys(), weights)}
            encoding = []
            for feature, encoder in self.encoders[strategy_id].items():
                feature_weight = weights_mapping.get(feature, 0)
                if feature_weight != 0:
                    if (type(encoder) == NumericEncoder) or (type(encoder) == NumpyEncoder):
                        encoding.append(encoder.encode(x[feature]) * feature_weight)
                    elif type(encoder) == BinOrdinalEncoder:
                        ind = 0
                        while ind < len(encoder.values) and x[feature] > encoder.values[ind]:
                            ind += 1
                        encoding.append(encoder.encode(encoder.values[ind]) * feature_weight)
                    elif type(encoder) == OrdinalEncoder:
                        encoding.append(encoder.encode(x[feature]) * feature_weight)
                    else:
                        value_index = self.feature_mapping[feature][x[feature]]
                        embedding = self.feature_embeddings[strategy_id][feature][value_index] * feature_weight
                        encoding.append(embedding)
            return np.concatenate(encoding)
            assert len(weights) == len(self.encoders), "Invalid number of weight vector {w}".format(w=len(weights))
        else:
            raise TypeError("Usupported type for encode {t}".format(t=type(x)))

    def add_mapping(self, partition_num, ids, data, strategy_id=None):
        if not strategy_id:
            strategy_id = self.base_strategy_id()
        for index, datum in zip(ids, data):
            item_array = [-1] * len(self.encoders[strategy_id])
            for i, (feature, encoder) in enumerate(self.encoders[strategy_id].items()):
                item_array[i] = self.feature_mapping[feature][datum[feature]] if feature in self.feature_mapping \
                    else float(datum[feature])
            self.item_mappings[partition_num][index] = item_array

    def component_breakdown(self, strategy_id=None):
        if not strategy_id:
            strategy_id = self.base_strategy_id()
        start = 0
        breakdown = {}
        for col, enc in self.encoders[strategy_id].items():
            if enc.column_weight == 0:
                continue
            end = start + len(enc)
            breakdown[col] = (start, end)
        return breakdown

    def partition_num(self, x):
        if not any(self.filters):
            return 0
        combined_key = at(*(self.filters))(x)
        if type(combined_key) != tuple:
            combined_key = (combined_key,)
        if all(type(k) != list for k in combined_key):
            # one partition to lookup
            return self.partitions.index(combined_key)
        # multiple partitions
        combined_key_list = []
        for k in combined_key:
            if type(k) != list:
                k = [k]
            combined_key_list.append(k)
        ret = []
        for combined_key in itertools.product(*combined_key_list):
            ret.append(self.partitions.index(combined_key))
        return ret

    def to_dict(self):
        filters = self._unparse_filters(self.filters, self.partitions)
        encoders = {strategy_id: self._unparse_encoders(strategy_encoders) for strategy_id, strategy_encoders in
                    self.encoders.items()}
        user_encoders = {strategy_id: self._unparse_encoders(user_encoders) for strategy_id, user_encoders in
                         self.user_encoders.items()}
        return {"encoders": encoders, "filters": filters, "index_factory": self.index_factory, "metric": self.metric, "id_col": self.id_col,
                "user_encoders": user_encoders, "strategies": self.strategies}

    def restore_vector_with_index(self, partition_num, index, strategy_id=None):
        if not strategy_id:
            strategy_id = self.base_strategy_id()
        mapping = self.item_mappings[partition_num][index]
        output = []
        for i, (name, encoder) in enumerate(self.encoders[strategy_id].items()):
            if name in self.feature_embeddings[strategy_id]:
                output.extend(self.feature_embeddings[strategy_id][name][mapping[i]]
                              * encoder.normalized_column_weight())
            else:
                output.extend([mapping[i] * encoder.normalized_column_weight()])
        return np.array(output).reshape(1, self.dim)

    def base_strategy_id(self):
        return [strategy['id'] for strategy in self.strategies if 'is_base' in strategy][0]


class BaseEncoder:

    def __init__(self, **kwargs):
        self.column = ''
        self.column_weight = 1
        self.nonzero_elements = 1
        self.default = kwargs.get("default")
        self.__dict__.update(kwargs)

    def __len__(self):
        raise NotImplementedError("len is not implemented")

    def __call__(self, value):
        return self.column_weight * self.encode(value) * np.ones(len(self)) * (1/np.sqrt(self.nonzero_elements))

    def encode(self, value):
        raise NotImplementedError("encode is not implemented")
    
    def special_properties(self):
        return {}

    def normalized_column_weight(self):
        return self.column_weight / np.sqrt(self.nonzero_elements)


class CachingEncoder(BaseEncoder):
    cache_max_size = 1024

    def __init__(self, **kwargs):
        # defaults:
        self.column = ''
        self.column_weight = 1
        self.values = []
        self.nonzero_elements = 1
        self.default = kwargs.get("default")
        # override from kwargs
        self.__dict__.update(kwargs)
        #caching
        self.cache = {}
        self.cache_hits = collections.defaultdict(int)

    def __call__(self, value):
        """Calls encode, multiplies by weight, cached"""
        if value in self.cache:
            self.cache_hits[value] += 1
            return self.cache[value]
        ret = self.encode(value) * self.column_weight * np.ones(len(self)) * (1/np.sqrt(self.nonzero_elements))
        if (self.cache_max_size is None) or (len(self.cache) < self.cache_max_size):
            self.cache[value] = ret
            return ret
        # cache cleanup
        min_key = sorted([(v, k) for k, v in self.cache_hits.items()])[0][1]
        del self.cache_hits[min_key]
        del self.cache[min_key]
        self.cache[value] = ret
        return ret

    def flush_cache(self, new_size=1024):
        self.cache_max_size = new_size
        self.cache = {}
        self.cache_hits = collections.defaultdict(int)


class NumericEncoder(BaseEncoder):
    def __len__(self):
        return 1

    def encode(self, value):
        return np.array([float(value)])


class OneHotEncoder(CachingEncoder):

    def __len__(self):
        return len(self.values) + 1

    def encode(self, value):
        vec = np.zeros(1 + len(self.values))
        try:
            vec[1 + self.values.index(value)] = 1
        except ValueError:  # Unknown
            vec[0] = 1
        return vec


class StrictOneHotEncoder(CachingEncoder):
    def __len__(self):
        return len(self.values)

    def encode(self, value):
        vec = np.zeros(len(self.values))
        try:
            vec[self.values.index(value)] = 1
        except ValueError:  # Unknown
            pass
        return vec


class OrdinalEncoder(OneHotEncoder):
    def __init__(self, column, column_weight, values, window, **kwargs):
        super().__init__(column=column, column_weight=column_weight, values=values, window=window, **kwargs)
        self.window = window
        self.nonzero_elements = len(window)

    def encode(self, value):
        assert len(self.window) % 2 == 1, "Window size should be odd: window: {w}, value: {v}".format(w=self.window,
                                                                                                      v=value)
        vec = np.zeros(1 + len(self.values))
        try:
            ind = self.values.index(value)
        except ValueError:  # Unknown
            vec[0] = 1
            return vec
        vec[ind + 1] = self.window[len(self.window) // 2]
        for offset in range(1, len(self.window) // 2 + 1):
            if ind - offset >= 0:
                vec[1 + ind - offset] = self.window[len(self.window) // 2 - offset]
            if ind + offset < len(self.values):
                vec[1 + ind + offset] = self.window[len(self.window) // 2 + offset]

        return vec

    def special_properties(self):
        return {"window": self.window}


class BinEncoder(CachingEncoder):

    def __len__(self):
        return len(self.values) + 1

    def encode(self, value):
        value = float(value)
        vec = np.zeros(1 + len(self.values))
        i = 0
        while i < len(self.values) and value > self.values[i]:
            i += 1
        vec[i] = 1
        return vec


class BinOrdinalEncoder(BinEncoder):
    def __init__(self, column, column_weight, values, window, **kwargs):
        super().__init__(column=column, column_weight=column_weight, values=values, window=window, **kwargs)
        self.window = window
        self.nonzero_elements = len(window)

    def encode(self, value):
        value = float(value)
        vec = np.zeros(1 + len(self.values))
        ind = 0
        while ind < len(self.values) and value > self.values[ind]:
            ind += 1
        vec[ind] = self.window[len(self.window) // 2]
        for offset in range(1, len(self.window) // 2 + 1):
            if ind - offset >= 0:
                vec[ind - offset] = self.window[len(self.window) // 2 - offset]
            if ind + offset <= len(self.values):
                vec[ind + offset] = self.window[len(self.window) // 2 + offset]
        return vec
    
    def special_properties(self):
        return {"window": self.window}


class HierarchyEncoder(CachingEncoder):
    #values = {'a': ['a1', 'a2'], 'b': ['b1', 'b2'], 'c': {'c1': ['c11', 'c12']}}
    similarity_by_depth = [1, 0.5, 0]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # TODO: Currently this approximation of the nonzero elements assumes:
        # (1) Two level hirearchy
        # (2) Approximately equal size of each hierarchy/category
        # {"A":[1,2,3], "B":[4,5,6]}
        inner_values = len(get_values_nested(self.values))
        outer_values = len(self.values.keys())
        self.nonzero_elements = inner_values / outer_values

    def __len__(self):
        inner_values = get_values_nested(self.values)
        return (1 + len(inner_values))

    def encode(self, value):
        # TODO: very inefficient: move to constructor
        inner_values = get_values_nested(self.values)
        vec = np.zeros(1 + len(inner_values))
        try:
            for other_value in inner_values:
                depth = lowest_depth(self.values, value, other_value)
                if depth >= len(self.similarity_by_depth):
                    # defaults to zero
                    continue
                vec[1 + inner_values.index(other_value)] = self.similarity_by_depth[depth]
        except ValueError:  # Unknown
            vec[0] = 1
        return vec

    def special_properties(self):
        return {"similarity_by_depth": self.similarity_by_depth}


class NumpyEncoder(BaseEncoder):
    def __init__(self, column, column_weight, values, npy, **kwargs):
        super().__init__(column=column, column_weight=column_weight, values=values, npy=npy, **kwargs)
        with open(npy, 'rb') as f:
            self.embedding = np.load(f)

        if type(values) == list:
            self.ids = values
        else:
            with open(values, 'r') as f:
                self.ids = [l.strip() for l in f.readlines() if l.strip() != ""]
        assert self.embedding.shape[0] == len(self.ids), "Dimension mismatch between ids and embedding"
        self.nonzero_elements = 1

    def __len__(self):
        return self.embedding.shape[1]

    def encode(self, value):
        try:
            idx = self.ids.index(value)
        except ValueError:
            return np.zeros(self.embedding.shape[1])
        return self.embedding[idx,:]

    def special_properties(self):
        return {"npy": self.npy}


class JSONEncoder(CachingEncoder):

    def __len__(self):
        return self.length

    def encode(self, value):
        val = value.translate({ord('('):'[',ord(')'):']'})
        val = json.loads(val)
        if type(val) == dict:  # sparse vector
            vec = np.zeros(len(self))
            for k, v in val.items():
                vec[int(k)] = v
        elif type(val) == list:
            vec = np.array(val)
        else:
            raise TypeError(str(type(val)) + " is not supported")
        return vec


class QwakEncoder(BaseEncoder):
    def __init__(self, column, column_weight, environment, length, entity_name, api_key=None, **kwargs):
        super().__init__(column=column, column_weight=column_weight, length=length, entity_name=entity_name,
                         environment=environment, **kwargs)
        if api_key is None:
            api_key = os.environ.get("QWAK_API")
        self.init_access_token(api_key)

    def init_access_token(self, api_key):
        self.access_token = requests.post("https://grpc.qwak.ai/api/v1/authentication/qwak-api-key",
                                          json={"qwakApiKey": api_key}).json()["accessToken"]

    def get_feature(self, entity_value):
        url = "https://api." + str(self.environment)+".qwak.ai/api/v1/features"
        body = {
            "features": [{"batchFeature": {"name": self.column}}],
            "entity": {"name": self.entity_name, "value": entity_value}
        }
        res = requests.post(url, headers={"Authorization": "Bearer "+self.access_token}, json=body).json()
        # Assuming one returned feature
        res = list(res["featureValues"][0]["featureValue"].values())[0]
        # TODO: Do qwak support vector features ?
        return res

    def __len__(self):
        return self.length

    def json_encode(self, value):
        val = value.translate({ord('('):'[',ord(')'):']'})
        val = json.loads(val)
        if type(val) == dict:  # sparse vector
            vec = np.zeros(len(self))
            for k, v in val.items():
                vec[int(k)] = v
        elif type(val) == list:
            vec = np.array(val)
        else:
            raise TypeError(str(type(val)) + " is not supported")
        return vec

    def encode(self, value):
        val = self.get_feature(value)
        return self.json_encode(val)
