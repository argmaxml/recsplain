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

rx.query(item_query_data)
