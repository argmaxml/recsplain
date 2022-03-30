import recsplain as rx

user_query_data = {
  "k": 2,
  "item_history": ["1", "3", "3"],
  "data": {
    "country": "US"
  },
  "explain": 1
}

rx.query(user_query_data)
