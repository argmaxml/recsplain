import numpy as np
import collections
from sklearn.neighbors import NearestNeighbors
try:
    import hnswlib
except ModuleNotFoundError:
    print ("hnswlib not found")
    HNSWMock = collections.namedtuple("HNSWMock", ("Index", "max_elements"))
    hnswlib = HNSWMock(None,0)
try:
    import faiss
except ModuleNotFoundError:
    print ("faiss not found")
    faiss = None

def parse_server_name(sname):
    if sname in ["hnswlib", "hnsw"]:
        return LazyHnsw
    elif sname in ["faiss", "flatfaiss"]:
        return FlatFaiss
    else:
        return SKKNN
    raise TypeError(str(sname) + " is not a valid similarity server name")


class FlatFaiss:
    def __init__(self, space, dim, index_factory, **kwargs):
        if index_factory == '':
            index_factory = 'Flat'
        if space in ['ip', 'cosine']:
            self.index = faiss.index_factory(dim, index_factory, faiss.METRIC_INNER_PRODUCT)
            if space == 'cosine':
                # TODO: Support cosine
                print("cosine is not supported yet, falling back to dot")
        elif space == 'l2':
            self.index = faiss.index_factory(dim, index_factory, faiss.METRIC_L2)
        else:
            raise TypeError(str(space) + " is not supported")
        self.index = faiss.IndexIDMap2(self.index)

    def __len__(self):
        return self.get_current_count()

    def  __itemgetter__(self, item):
        return self.index.reconstruct(int(item))
    
    def add_items(self, data, ids):
        data = np.array(data).astype(np.float32)
        self.index.add_with_ids(data, np.array(ids, dtype='int64'))

    def get_items(self, ids):
        # recmap = {k:i for i,k in enumerate(faiss.vector_to_array(self.index.id_map))}
        # return np.vstack([self.index.reconstruct(recmap[v]) for v in ids])
        return np.vstack([self.index.reconstruct(int(v)) for v in ids])

    def get_max_elements(self):
        return -1

    def get_current_count(self):
        return self.index.ntotal

    def search(self, data, k=1):
        return self.index.search(np.array(data).astype(np.float32),k)

    def save_index(self, fname):
        return faiss.write_index(self.index, fname)

    def load_index(self, fname):
        self.index = faiss.read_index(fname)

class LazyHnsw(hnswlib.Index):
    def __init__(self, space, dim, index_factory=None,max_elements=1024, ef_construction=200, M=16):
        super().__init__(space, dim)
        self.init_max_elements = max_elements
        self.init_ef_construction = ef_construction
        self.init_M = M

    def __len__(self):
        return self.get_current_count()

    def  __itemgetter__(self, item):
        return super().get_items([item])[0]

    def init(self, max_elements=0):
        if max_elements == 0:
            max_elements = self.init_max_elements
        super().init_index(max_elements, self.init_M, self.init_ef_construction)

    def add_items(self, data, ids=None, num_threads=-1):
        if self.max_elements == 0:
            self.init()
        if self.max_elements<len(data)+self.element_count:
            super().resize_index(max([len(data)+self.element_count,self.max_elements]))
        return super().add_items(data, ids, num_threads)

    def add(self, data):
        return self.add_items(data)

    def get_items(self, ids=None):
        if self.max_elements == 0:
            return []
        return super().get_items(ids)

    def knn_query(self, data, k=1, num_threads=-1):
        if self.max_elements == 0:
            return [], []
        return super().knn_query(data, k, num_threads)

    def search(self, data, k=1):
        I,D = self.knn_query(data, k)
        return (D,I)

    def resize_index(self, size):
        if self.max_elements == 0:
            return self.init(size)
        else:
            return super().resize_index(size)

    def set_ef(self, ef):
        if self.max_elements == 0:
            self.init_ef_construction = ef
            return
        super().set_ef(ef)

    def get_max_elements(self):
        return self.max_elements

    def get_current_count(self):
        return self.element_count


class SKKNN:
    def __init__(self, space, dim, index_factory=None, **kwargs):
        self.space = space
        self.dim = dim
        self.items = []
        self.ids = []
        self.fitted = False
        self.index = NearestNeighbors(metric=self.space,n_jobs=-1,n_neighbors=10, **kwargs)

    def __len__(self):
        return len(self.items)

    def  __itemgetter__(self, item):
        return self.items[self.ids.index(item)]

    def init(self, **kwargs):
        self.index.fit(self.items)
        self.fitted = True
        
    def add_items(self, data, ids=None, num_threads=-1):
        self.items.extend(data)
        self.ids.extend(ids)
        self.fitted = False

    def get_items(self, ids=None):
        return [self.items[self.ids.index(i)] for i in ids]

    def search(self, data, k=1):
        if not self.fitted:
            self.index.fit(self.items)
            self.fitted = True
        scores, idx = self.index.kneighbors(data ,k, return_distance=True)
        return (scores, idx)

    def get_max_elements(self):
        return -1

    def get_current_count(self):
        return len(self.items)