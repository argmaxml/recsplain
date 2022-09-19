import unittest, sys
import numpy as np
from pathlib import Path

sys.path.append(str(Path(__file__).absolute().parent.parent))
from recsplain import AvgUserStrategy


class SKLearnEngineTest(unittest.TestCase):

    def setUp(self):
        self.sklearn_engine = AvgUserStrategy(similarity_engine='sklearn')
        self.faiss_engine = AvgUserStrategy(similarity_engine='faiss')

        self.schema = {
            "filters": [{
                "field": "country",
                "values": ["US", "EU"]
            }],
            "encoders": [{
                "field": "price",
                "values": ["low", "mid", "high"],
                "type": "onehot",
                "weight": 1
                },
                {"field": "category",
                 "values": ["dairy", "meat"],
                 "type": "onehot",
                 "weight": 2
                 }
            ],
            "metric": "l2"
        }

        data = [{
                "id": "1",
                "price": "low",
                "category": "meat",
                "country": "US"
            },
            {
                "id": "2",
                "price": "mid",
                "category": "meat",
                "country": "US"
            },
            {
                "id": "3",
                "price": "low",
                "category": "dairy",
                "country": "US"
            },
            {
                "id": "4",
                "price": "high",
                "category": "meat",
                "country": "EU"
            }]

        self.sklearn_engine.init_schema(**self.schema)
        self.faiss_engine.init_schema(**self.schema)

        self.sklearn_engine.index(data)
        self.faiss_engine.index(data)

    def test_item_query_equality(self):
        data = {
                "id": "2",
                "price": "mid",
                "category": "meat",
                "country": "US"
            }

        labels_1, distances_1, _ = self.sklearn_engine.query(data, 3)
        labels_2, distances_2, _ = self.faiss_engine.query(data, 3)
        self.assertEqual(labels_1, labels_2)
        self.assertEqual(distances_1, tuple(np.sqrt(distances_2)))


if __name__ == '__main__':
    unittest.main()
