# Recserver
An effiicient recsplain server, written in Go and memory optimized

## Features & Limitations

### Numpy Encoder support
Use pretrained embedding saved in numpy format, with the `NumpyEncoder`.
### Numeric Encoder support
Use numeric values features, same functionality as the python version's `NumericEncoder`.
### All other encoders are not supported
Unfortunately, all other encoders (e.g. `OneHotEncoder`, `OrdinalEncoder`, etc) are not supported.

## Variants (A/B testing) support
To run several schemas with traffic splitting, simply create `variants.json` and place it in the same directory as the executable.

The syntax of the `variants` file is as such:

```
[
    {
        "name": "default",
        "percentage": 50,
        "weights": {
            
        }
    },
    {
        "name": "test",
        "percentage": 50,
        "weights": {
            "category_group":0
            
        }
    }
]
```

The `test` variant would turn off the `category_group` feature for 50% of the traffic.

## Usage
### Docker
1. First, create the numpy arrays needed and save them in the save directory as the `Dockerfile`
1. Create schema (`schema.json`) and variants file (optional) and place them in the same folder.
1. Build and deploy the docker image. 
