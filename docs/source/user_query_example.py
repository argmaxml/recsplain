import recsplain as rx

user_query_data = {
  "k": 2,
  "item_history": ["1", "3", "3"],
  "user_data": {
    "country": "US"
  }
}

rec_strategy.user_query(**user_query_data)
