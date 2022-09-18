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

rec_strategy = rx.AvgUserStrategy()
rec_strategy.init_schema(**config_data)
