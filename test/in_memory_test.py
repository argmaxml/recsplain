import sys, unittest
from pathlib import Path
sys.path.append(str(Path(__file__).absolute().parent.parent))
from recsplain import AvgUserStrategy


class InMemory(unittest.TestCase):
    def setUp(self):
        self.strategy = AvgUserStrategy()
        self.data = [
            {
                "id": "1",
                "price": "low",
                "category": "meat",
                "weight": 2.2,
                "country": "US"
            },
            {
                "id": "2",
                "price": "mid",
                "category": "meat",
                "weight": 3.0,
                "country": "US"
            },
            {
                "id": "3",
                "price": "low",
                "category": "dairy",
                "weight": 1.5,
                "country": "US"
            },
            {
                "id": "4",
                "price": "high",
                "category": "meat",
                "weight": 2.8,
                "country": "EU"
            }
        ]

        self.strategy.init_schema(
            filters=[
                {"field": "country", "values": ["US", "EU"]}
            ],
            encoders=[
                {"field": "price", "values": ["low", "mid", "high"], "type": "onehot", "weight": 1},
                {"field": "category", "values": ["dairy", "meat"], "type": "onehot", "weight": 2},
                {"field": "weight", "values": [], "type": "numeric", "weight": 2}
            ],
            metric="l2"
        )
        self.strategy.index(self.data)

    def test_encode(self):
        datum = {
            "id": "3",
            "price": "low",
            "category": "dairy",
            "weight": 1.5,
            "country": "US"
        }
        vector = self.strategy.encode(datum).tolist()
        expected = [0.0, 1.0, 0.0, 0.0, 0.0, 2.0, 0.0, 3.0]
        self.assertListEqual(vector, expected)

    def test_restore(self):
        datum = {
                "id": "3",
                "price": "low",
                "category": "dairy",
                "weight": 1.5,
                "country": "US"
            }
        partition_num = self.strategy.schema.partition_num(datum)
        index = 2
        vector = self.strategy.schema.restore_vector_with_index(partition_num, index)
        expected = [0.0, 1.0, 0.0, 0.0, 0.0, 2.0, 0.0, 3.0]
        self.assertListEqual(vector, expected)


if __name__ == '__main__':
    unittest.main()