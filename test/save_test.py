import sys, unittest
from pathlib import Path
sys.path.append(str(Path(__file__).absolute().parent.parent))
from recsplain import AvgUserStrategy

class SaveLoad(unittest.TestCase):
    def setUp(self):
        self.saved_strategy = AvgUserStrategy()
        self.loaded_strategy = AvgUserStrategy()


        self.saved_strategy.init_schema(
        filters= [
            {"field": "country", "values": ["US", "EU"]}
        ],
        encoders= [
            {"field": "price", "values":["low", "mid", "high"], "type": "onehot", "weight":1},
            {"field": "category", "values":["dairy","meat"], "type": "onehot", "weight":2}
        ],
        metric= "l2"
        )
        self.saved_strategy.index([
        {
            "id": "1",
            "price": "low",
            "category": "meat",
            "country":"US"
        },
        {
            "id": "2",
            "price": "mid",
            "category": "meat",
            "country":"US"
        },
        {
            "id": "3",
            "price": "low",
            "category": "dairy",
            "country":"US"
        },
        {
            "id": "4",
            "price": "high",
            "category": "meat",
            "country":"EU"
        }
        ])
        self.saved_strategy.save_model("t1")

    def test_load(self):
        self.loaded_strategy.load_model("t1")
        expected = self.saved_strategy.query(
            k= 2,
            data= {
                "price": "low",
                "category": "meat",
                "country":"US"
            }
        )
        actual = self.loaded_strategy.query(
            k= 2,
            data= {
                "price": "low",
                "category": "meat",
                "country":"US"
            }
        )
        self.assertEqual(expected, actual)




if __name__ == '__main__':
    unittest.main()