import unittest, sys
import numpy as np
from pathlib import Path
sys.path.append(str(Path(__file__).absolute().parent.parent))
from recsplain import AvgUserStrategy

class BinOrdinalTest(unittest.TestCase):

    def setUp(self):
        self.schema = {
            "filters": [{"field":'language_code', "values": ["en", "de", "fr"]}],
            "encoders":[
            {
            "field": "average_rating",
            "values": [2, 4],
            "type": "binordinal",
            "window": [0.1,1,0.2],
            "weight": np.sqrt(3)
            },
        ],
            "metric": "l2"
            
        }

    def test_no_window(self):
        self.schema["encoders"][0]["window"] = [1]
        strategy = AvgUserStrategy()
        strategy.init_schema(**self.schema)
        data = {"id":1, "language_code":"en", "average_rating": 3.72}
        vec = strategy.encode(data)
        self.assertTrue(np.allclose(vec,  [0,np.sqrt(3),0]))

    def test_window(self):
        self.schema["encoders"][0]["window"] = [0.1,1,0.2]
        strategy = AvgUserStrategy()
        strategy.init_schema(**self.schema)
        data = {"id":1, "language_code":"en", "average_rating": 3.72}
        vec = strategy.encode(data)
        self.assertTrue(np.allclose(vec, [0.1,1,0.2]))

if __name__ == '__main__':
    unittest.main()
