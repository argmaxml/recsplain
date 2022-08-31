import recsplain as rx

config_data = {
  "filters": [{ "field": "country", "values": ["US", "EU"] }],
  "encoders": [
    {
      "field": "price",
      "values": ["low", "mid", "high"],
      "type": "onehot",
      "weight": 1
    },
    {
      "field": "category",
      "values": ["dairy", "meat"],
      "type": "onehot",
      "weight": 2
    }
  ],
  "metric": "l2"
}

index_data = [
  {
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
  }
]

rec_strategy = rx.AvgUserStrategy()
rec_strategy.init_schema(config_data)
rec_strategy.index(index_data)
