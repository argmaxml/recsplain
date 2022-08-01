import unittest, sys
from pathlib import Path
sys.path.append(str(Path(__file__).absolute().parent.parent))
import pandas as pd
from recsplain import AvgUserStrategy


df_items = pd.read_csv("~/Downloads/df_item.csv")

class DataFrameTest(unittest.TestCase):
    def setUp(self):
        self.schema = {
    "id_col": "item_id",
    "filters": [
        {"field": "board_id", "values": list(df_items['board_id'].unique())}
    ],
    "encoders": [
        {"field": "item_source", "values": [int(x) for x in list(df_items['item_source'].unique())], "type": "onehot", "weight": 1},
        {"field": "item_type", "values": list(df_items['item_type'].unique()), "type": "onehot", "weight": 1},
        {"field": "category_names", "values": list(df_items['category_names'].unique()), "type": "onehot", "weight": 1},
        {"field": "provider_id", "values": list(df_items['provider_id'].unique()), "type": "onehot", "weight": 1},
        {"field": "views_count", "values": [], "type": "numeric", "weight": 1},
        {"field": "new_tags_clean", "values": list(df_items['new_tags_clean'].astype(str)), "npy": "/Users/gadmarkovits/Downloads/w2v1_400.npy",
         "type": "np", "weight": 1}

    ],
    "metric": "l2"
}

    def test_index(self):
        r1 = AvgUserStrategy()
        r1.init_schema(**self.schema)
        r1.index_dataframe(df_items)

        r1.save_model("folloze_item_item_model_NEW")

        r2 = AvgUserStrategy()
        r2.load_model('/Users/gadmarkovits/recsplain/models/folloze_item_item_model_NEW')

        board_sample = df_items[df_items['board_id'] == '125506.0']
        smple = \
        board_sample[['item_id', 'board_id', 'item_source', 'item_type', 'category_names', 'provider_id', 'views_count',
                      'new_tags_clean']].to_dict(orient='records')[0]

        print(r1.query(k=5, data=smple))
        print(r2.query(k=5, data=smple))
