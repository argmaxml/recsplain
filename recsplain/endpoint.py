from typing import Optional, List, Dict, Any, Union
from pydantic import BaseModel, Field
import sys, json
from fastapi import FastAPI
from pathlib import Path
import gc
try:
    from smart_open import open
except:
    pass
try:
    import uvicorn
except:
    pass
try:
    import ctypes
    libc = ctypes.CDLL("libc.so.6")
    def free_memory():
        gc.collect()
        libc.malloc_trim(0)
except:
    def free_memory():
        gc.collect()
sys.path.append("../src")
from .strategies import AvgUserStrategy
import pandas as pd

strategy = None
api = FastAPI()



class Column(BaseModel):
    field: str
    values: List[str]
    type: Optional[str]
    default: Optional[str]
    weight: Optional[float]
    window: Optional[List[float]]
    url: Optional[str]
    entity: Optional[str]
    environment: Optional[str]
    feature: Optional[str]
    length: Optional[int]


class Schema(BaseModel):
    encoders: List[Column]
    metric: Optional[str]='ip'
    filters: Optional[List[Column]]=[]
    user_encoders: Optional[List[Column]]=[]
    id_col: Optional[str]='id'
    
    def to_dict(self):
        return {
            "metric": self.metric,
            "filters": [vars(c) for c in self.filters],
            "encoders": [vars(c) for c in self.encoders],
        }


class KnnQuery(BaseModel):
    data: Dict[str, Union[List[str],str]]
    k: int
    explain:Optional[bool]=False

class KnnUserQuery(BaseModel):
    item_history: List[str]
    data: Optional[Dict[str, Union[List[str],str]]]={}
    k: int


@api.get("/")
async def read_root():
    return {"status": "OK", "schema_initialized": strategy.schema_initialized(), "total_items": strategy.get_total_items()}


@api.get("/partitions")
async def api_partitions():
    if not strategy.schema_initialized():
        return {"status": "error", "message": "Schema not initialized"}
    ret = strategy.get_partition_stats()
    ret["status"] = "OK"
    return ret


@api.post("/fetch")
def api_fetch(lbls: List[str]):
    if not strategy.schema_initialized():
        return {"status": "error", "message": "Schema not initialized"}
    if strategy.get_total_items()==0:
        return {"status": "error", "message": "No items are indexed"}
    return strategy.fetch(lbls)

@api.post("/encode")
async def api_encode(data: Dict[str, str]):
    if not strategy.schema_initialized():
        return {"status": "error", "message": "Schema not initialized"}
    vec = strategy.encode(data)
    return {"status": "OK", "vec": [float(x) for x in vec]}


@api.post("/init_schema")
def init_schema(sr: Schema):
    schema_dict = sr.to_dict()
    partitions, enc_sizes = strategy.init_schema(**schema_dict)
    free_memory()
    return {"status": "OK", "partitions": len(partitions), "vector_size":strategy.get_embedding_dimension(), "feature_sizes":enc_sizes, "total_items":strategy.get_total_items()}

@api.post("/get_schema")
def get_schema():
    if not strategy.schema_initialized():
        return {"status": "error", "message": "Schema not initialized"}
    else:
        return strategy.schema.to_dict()

@api.post("/index")
async def api_index(data: Union[List[Dict[str, str]], str]):
    if not strategy.schema_initialized():
        return {"status": "error", "message": "Schema not initialized"}
    if type(data)==str and data.endswith(".json"):
        # read data remotely
        with open(data, 'r') as f:
            data = json.load(f)
    elif type(data)==str and data.endswith(".csv"):
        # read csv remotely
        data = pd.read_csv(data)
        affected_partitions = strategy.index_dataframe(data)
        return {"status": "OK", "affected_partitions": affected_partitions}
    errors, affected_partitions = strategy.index(data)
    if any(errors):
        return {"status": "error", "items": errors}
    return {"status": "OK", "affected_partitions": affected_partitions}


@api.post("/query")
async def api_query(query: KnnQuery):
    if not strategy.schema_initialized():
        return {"status": "error", "message": "Schema not initialized"}
    if strategy.get_total_items()==0:
        return {"status": "error", "message": "No items are indexed"}
    try:
        labels,distances, explanation =strategy.query(query.data, query.k, query.explain)
        if any(explanation):
            return {"status": "OK", "ids": labels, "distances": distances, "explanation":explanation}
        return {"status": "OK", "ids": labels, "distances": distances}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@api.post("/user_query")
async def api_user_query(query: KnnUserQuery):
    if not strategy.schema_initialized():
        return {"status": "error", "message": "Schema not initialized"}
    if strategy.get_total_items()==0:
        return {"status": "error", "message": "No items are indexed"}
    try:
        labels,distances =strategy.user_query(query.data, query.item_history, query.k)
        return {"status": "OK", "ids": labels, "distances": distances}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@api.post("/save_model")
async def api_save(model_name:str):
    if not strategy.schema_initialized():
        return {"status": "error", "message": "Schema not initialized"}
    saved = strategy.save_model(model_name)
    return {"status": "OK", "saved_indices": saved}

@api.post("/load_model")
async def api_load(model_name:str):
    loaded = strategy.load_model(model_name)
    free_memory()
    return {"status": "OK", "loaded_indices": loaded}

@api.post("/list_models")
async def api_list():
    return strategy.list_models()

def run_server(config=None, host="0.0.0.0", port=5000, log_level="info"):
    global strategy
    strategy = AvgUserStrategy(config)
    uvicorn.run(api, host=host, port=port, log_level=log_level)

if __name__ == "__main__":
    from argparse import ArgumentParser
    argparse = ArgumentParser()
    argparse.add_argument('--host', default='0.0.0.0', type=str, help='host')
    argparse.add_argument('--port', default=5000, type=int, help='port')
    args = argparse.parse_args()
    
    data_dir = Path(__file__).absolute().parent.parent / "data"
    with (data_dir / "config.json").open('r') as f:
        config = json.load(f)
    strategy = AvgUserStrategy(config)
    uvicorn.run("__main__:api", host=args.host, port=args.port, log_level="info")
