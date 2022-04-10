import unittest, sys
import numpy as np
from pathlib import Path
sys.path.append(str(Path(__file__).absolute().parent.parent))
from recsplain import AvgUserStrategy

class NumpyTest(unittest.TestCase):

    def setUp(self):
        self.strategy = AvgUserStrategy()
        self.npy =str(Path(__file__).absolute().parent/"test_np_encoder.npy")
        np.save(self.npy, np.eye(5))
        self.strategy.init_schema(
            encoders= [{"field": "state",  "values": ["a", "b", "c", "d", "e"], "type":"np", "weight":1, "npy":self.npy}],
            filters= [{"field": "country", "values": ["US", "EU"]}],
            metric= "cosine"
        )

    def test_read(self):
        data = {"id":1, "country":"US", "state": "b"}
        vec = self.strategy.encode(data)
        self.assertTrue(np.allclose(vec, [0,1,0,0,0]))

    def test_missing(self):
        data = {"id":1, "country":"US", "state": "i"}
        vec = self.strategy.encode(data)
        self.assertTrue(np.allclose(vec, [0,0,0,0,0]))

if __name__ == '__main__':
    unittest.main()
