from email.policy import default
import sys, unittest, json
import pandas as pd
import numpy as np
from pathlib import Path
sys.path.append(str(Path(__file__).absolute().parent.parent))
from recsplain import RedisStrategy
from operator import itemgetter as at

# Requires: a running docker on the local host
#          docker run -p 6379:6379 -d redis

class RedisTest(unittest.TestCase):
    def setUp(self):
        redis_credentials = {
            'host': "localhost",
            'port': 6379,
            'db': 0
        }
        weights = {"view": 5, "click": 100}
        self.strategy = RedisStrategy(redis_credentials = redis_credentials, similarity_engine="sk",
            event_key = 'action',item_key='id',user_keys=['ts','action','id','organization_id'],
            event_weights=weights)
        schema = {
            "filters": [{"field": "organization_id", "values": ['org_A', 'org_B']}],
            "encoders": [{"field": "tag", "type": "soh", "values":["t_A", "t_B", "t_C"], "default":"", "weight":1}],
        }
        self.strategy.init_schema(**schema)
        df = pd.DataFrame([
            ["id0","org_A","t_A"],
            ["id1","org_A","t_B"],
            ["id2","org_B","t_C"],
            ["id3","org_B","t_A"],
            ["id4","org_A","t_B"],
            ["id5","org_A","t_C"],
            ["id6","org_B","t_A"],
            ["id7","org_B","t_B"],
            ["id8","org_A","t_C"],
            ["id9","org_A","t_A"],
            ], columns=["id","organization_id","tag"])
        self.strategy.index_dataframe(df, parallel=False)
        # self.strategy.index_dataframe(df)
    
    def test_read_write_to_redis(self):        
        with self.strategy :
            self.strategy.del_user(345633)
            self.strategy.add_event(345633,{'ts': 123, 'action': 'view', 'id': 'id1', 'organization_id': 'org_A'})
            self.strategy.add_event(345633,{'ts': 125, 'action': 'click', 'id': 'id1', 'organization_id': 'org_A'})

        ret = self.strategy.get_events(345633)
        self.assertEqual(",".join(map(at("action"),ret)), "view,click")
        self.assertEqual(",".join(map(at("id"),ret)), "id1,id1")
        self.assertEqual(",".join(map(at("ts"),ret)), "123,125")

    def test_fetch(self):
        fetched = self.strategy.fetch("id1")
        self.assertIn('org_A', fetched)
        self.assertEqual(len(fetched['org_A']),1)
        self.assertEqual(list(fetched['org_A'][0]),[0,1,0])
    
    def test_user_query(self):
        with self.strategy :
            self.strategy.del_user(77787)
            self.strategy.add_event(77787,{'ts': 123, 'action': 'view', 'id': 'id0', 'organization_id': 'org_A'})
            self.strategy.add_event(77787,{'ts': 123, 'action': 'view', 'id': 'id2', 'organization_id': 'org_A'})
            self.strategy.add_event(77787,{'ts': 123, 'action': 'view', 'id': 'id2', 'organization_id': 'org_A'})
            self.strategy.add_event(77787,{'ts': 123, 'action': 'click', 'id': 'id4', 'organization_id': 'org_A'})
        ids,dists = self.strategy.user_query(user_id=77787, user_data = {"organization_id":"org_A"}, k=3)
        self.assertListEqual(list(ids), ['id4', 'id2', 'id0'])
        # dists = [round(i,2) for i in dists]
        # self.assertListEqual(list(dists), [169.25, 181.89, 899.09])
        



if __name__ == '__main__':
    unittest.main()