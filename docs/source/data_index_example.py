import recsplain as rx

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


rx.index(index_data)
