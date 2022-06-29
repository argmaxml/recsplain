import itertools
import unittest, sys
import numpy as np
from pathlib import Path
sys.path.append(str(Path(__file__).absolute().parent.parent))
from recsplain import BaseStrategy

class WeightFitTest(unittest.TestCase):

    def setUp(self):
        self.strategy = BaseStrategy()

    def test_read(self):
        self.strategy.init_schema(
            encoders= [{"field": "letter",  "values": ["a", "b"], "type":"strictonehot", "weight":1},
            {"field": "roman",  "values": ["I","II", "III"], "type":"strictonehot", "weight":1}],
            filters= [{"field": "country", "values": ["US", "EU"]}],
            metric= "ip"
        )

        data = {"id":1, "country":"US", "letter": "b", "roman": "II"}
        encoded_col=[np.eye(2),np.eye(3)]
        scores=[]
        w1=22
        w2=44
        expected_weights = [w1,w2]
        vecs = [
            np.array([w1,0,w2,0,0]),
            np.array([w1,0,0,w2,0]),
            np.array([w1,0,0,0,w2]),
            np.array([0,w1,w2,0,0]),
            np.array([0,w1,0,w2,0]),
            np.array([0,w1,0,0,w2]),
        ]
        for i,j in itertools.product(range(6),range(6)):
            s = np.dot(vecs[i],vecs[j])
            scores.append(((i,j),s))
        self.strategy.fit_by_explicit_similarity(scores)
        for i,(feature, encoder) in enumerate(self.strategy.schema.encoders.items()):
                self.assertAlmostEqual(expected_weights[i],encoder.column_weight,places=3)

if __name__ == '__main__':
    unittest.main()
