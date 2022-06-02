# Recsplain = Explainable Recommendation Service
## Installation
The Recsplain package is available via [PyPi](https://pypi.org/project/recsplain/), just 

    pip install recsplain
    
And you're ready to go

## Creating a Schema

First, we'll need to specify the column definition of each item property, this description is called a schema.
A schema specifies the list of features, their encoding (embedding, one-hot, ordinal, numeric, hierarchical, etc) and their weight.

A field can be either a *filter field*, used for exact matches only, or an *encoder field* for fuzzy matching.

For example, assume we run a grocery chain with 2 branches - one in the US and one in Eurpoe. we do not want to recommend European items to American customers and vice versa.

On the other hand, we might want to match "low price" items in the similar products page of a "mid price" item, if all of the other properties are similar.

This schema demonstrates these constraints:

```
  {
      "filters": [
          {"field": "country", "values": ["US", "EU"]}
      ],
      "encoders": [
          {"field": "price", "values":["low", "mid", "high"], "type": "oridnal", "weight":1},
          {"field": "category", "values":["dairy","meat"], "type": "onehot", "weight":2}
      ],
      "metric": "l2"
  }
```
  
 
## Query a recommendation

```
  import recsplain as rx

  item_query_data = {
    "k": 2,
    "data": {
      "price": "low",
      "category": "meat",
      "country": "US"
    },
    "explain": true
  }

  rx.query(item_query_data)
``` 
 
The response is a list of items, with component-wise distance - to explain how what the similarity was calculates

```
  {
    "status": "OK",
    "ids": ["1", "2"],
    "distances": [0, 2],
    "explanation": [
      {
        "price": 0,
        "category": 0
      },
      {
        "price": 2,
        "category": 0
      }
    ]
  }
```

## Interested in learning more ?
See our [Getting Started Guide](https://recsplain.readthedocs.io/en/latest/)
