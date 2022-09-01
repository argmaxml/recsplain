import recsplain as rx

item_query_data = {
  "k": 2,
  "data": {
    "price": "low",
    "category": "meat",
    "country": "US"
  },
  "explain": 1
}

rec_strategy.query(**item_query_data)
