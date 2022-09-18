import sys, unittest, json
import pandas as pd
from pathlib import Path
sys.path.append(str(Path(__file__).absolute().parent.parent))
from recsplain import RedisStrategy

class RedisTest(unittest.TestCase):
    def setUp(self):
        with open(Path(__file__).parent/'config.json') as f:
            redis_config = json.load(f)
        self.strategy = RedisStrategy(redis_credentials = redis_config['redis'], similarity_engine="faiss", event_key = 'action',item_key='content_item_id',user_keys=['action_timestamp','action','content_item_id','organization_id'])
        with open(Path(__file__).parent/'schema.json') as f:
            schema_file = json.load(f)
        self.strategy.init_schema(**schema_file)
        df = pd.DataFrame([
            {'content_id': 345633,
            'organization_id': 4029,
            'item_source': 2,
            'item_type': 'pdf',
            'tags': 'NaN',
            'category_names': 'Protect your Organization;Provide Resources for Business Continuity',
            'article_title': 'NaN',
            'views_count': 133},
            {'content_id': 3265,
            'organization_id': 2,
            'item_source': 1,
            'item_type': 'link',
            'tags': 'NaN',
            'category_names': 'NaN',
            'article_title': 'NaN',
            'views_count': 13},
            {'content_id': 145119,
            'organization_id': 2,
            'item_source': 1,
            'item_type': 'snapshot',
            'tags': 'NaN',
            'category_names': 'NaN',
            'article_title': 'NaN',
            'views_count': 165},
            {'content_id': 417215,
            'organization_id': 4029,
            'item_source': 2,
            'item_type': 'mp4',
            'tags': 'NaN',
            'category_names': 'Access Event Resources;Event Slides and Resources',
            'article_title': 'NaN',
            'views_count': 125},
            {'content_id': 383246,
            'organization_id': 4029,
            'item_source': 2,
            'item_type': 'pdf',
            'tags': 'NaN',
            'category_names': 'NaN',
            'article_title': 'NaN',
            'views_count': 673}])
        self.strategy.index_dataframe(df, parallel=False)
        
        
        lead_event = {'action_timestamp': '2000-01-01 0:00:00.00000',
                    'action': 'Item View',
                    'content_item_id': '345633',
                    'organization_id': '4029'}
        already_exists = self.strategy.get_events(123)
        if already_exists:
            self.strategy.pop_event(123)
        self.strategy.add_event(123,lead_event)

    def test_fetch(self):
        lead_data = {'action_timestamp': '2020-05-08 13:29:01.032636',
                'action': 'Item View',
                'content_item_id': '345633',
                'organization_id': '4029'}
        self.assertTrue(any(self.strategy.fetch("345633")))
        ids,dists = self.strategy.user_query(user_id=123, user_data = lead_data, k=5)
        




if __name__ == '__main__':
    unittest.main()