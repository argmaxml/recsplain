import unittest, sys
import numpy as np
from pathlib import Path
sys.path.append(str(Path(__file__).absolute().parent.parent))
from recsplain import AvgUserStrategy


class OrdinalTest(unittest.TestCase):

    def setUp(self):
        self.schema = {
            "filters": [{
                "field": 'language_code',
                "values": ["en", "de", "fr"]
            }],
            "encoders": [{
                "field": "average_rating",
                "values": [2, 4],
                "type": "ordinal",
                "window": [0.1,1,0.2],
                "weight": np.sqrt(3)
            }],
            "metric": "l2"
        }

    def test_window_unhandeled_value(self):
        self.schema["encoders"][0]["window"] = [0.1, 1, 0.2]
        strategy = AvgUserStrategy()
        strategy.init_schema(**self.schema)
        data = {"id": 1, "language_code": "en", "average_rating": 3.72}
        vec = strategy.encode(data)
        self.assertTrue(np.allclose(vec, [1, 0, 0]))

    def test_no_window_unhandeled_value(self):
        self.schema["encoders"][0]["window"] = [1]
        strategy = AvgUserStrategy()
        strategy.init_schema(**self.schema)
        data = {"id": 1, "language_code": "en", "average_rating": 3.72}
        vec = strategy.encode(data)
        self.assertTrue(np.allclose(vec, [np.sqrt(3), 0, 0]))

    def test_window_first_value(self):
        self.schema["encoders"][0]["window"] = [0.1, 1, 0.2]
        strategy = AvgUserStrategy()
        strategy.init_schema(**self.schema)
        data = {"id":1, "language_code":"en", "average_rating": 2}
        vec = strategy.encode(data)
        self.assertTrue(np.allclose(vec, [0, 1, 0.2]))

    def test_window_last_value(self):
        self.schema["encoders"][0]["window"] = [0.1, 1, 0.2]
        strategy = AvgUserStrategy()
        strategy.init_schema(**self.schema)
        data = {"id": 1, "language_code": "en", "average_rating": 4}
        vec = strategy.encode(data)
        self.assertTrue(np.allclose(vec, [0, 0.1, 1]))

    def test_window_large_first_value(self):
        self.schema["encoders"][0]["window"] = [0.5, 0.1, 1, 0.2, 0.4]
        self.schema["encoders"][0]['weight'] = np.sqrt(5)
        self.schema["encoders"][0]["values"] = [1, 2, 3, 4, 5]
        strategy = AvgUserStrategy()
        strategy.init_schema(**self.schema)
        data = {"id": 1, "language_code": "en", "average_rating": 1}
        vec = strategy.encode(data)
        self.assertTrue(np.allclose(vec, [0, 1, 0.2, 0.4, 0, 0]))

    def test_window_large_middle_value(self):
        self.schema["encoders"][0]["window"] = [0.5, 0.1, 1, 0.2, 0.4]
        self.schema["encoders"][0]['weight'] = np.sqrt(5)
        self.schema["encoders"][0]["values"] = [1, 2, 3, 4, 5]
        strategy = AvgUserStrategy()
        strategy.init_schema(**self.schema)
        data = {"id": 1, "language_code": "en", "average_rating": 3}
        vec = strategy.encode(data)
        self.assertTrue(np.allclose(vec, [0, 0.5, 0.1, 1, 0.2, 0.4]))


if __name__ == '__main__':
    unittest.main()
