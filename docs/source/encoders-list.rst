Encoders
================

Recsplain comes with a variety of encoders. 

.. note:: 
   The code for the encoders is in `encoders.py <https://github.com/argmaxml/recsplain/blob/master/recsplain/encoders.py>`_

Here is the list.

NumericEncoder
"""""""""
Use for numeric data.
example:
.. code-block:: python

    {
      "field": "fat_precentage",
      "values": np.linspace(0, 100, num=101),
      "type": "numeric"",
      "weight": 1
    }


OneHotEncoder
"""""""""
Use for categorical data. First category is saved for "unknown" entries.
example:
.. code-block:: python

    {
      "field": "category",
      "values": ["dairy", "pasrty", "meat"],
      "type": "onehot",
      "weight": 1
    }

StrictOneHotEncoder
"""""""""
Use for categorical data. No "unknown" category.
example:
.. code-block:: python

    {
      "field": "category",
      "values": ["dairy", "pasrty", "meat"],
      "type": "strictonehot",
      "weight": 1
    }

OrdinalEncoder
"""""""""
Use for ordinal data.
``window`` is the allowed similarity leakage between closed values.
example:
.. code-block:: python

    {
      "field": "price",
      "values": ["low", "mid", "high"],
      "type": "ordinal",
      "weight": 1,
      "window": [0.1,1,0.1]

    }

BinEncoder
"""""""""
Use for binning data.
``values`` is the boundaries of the bins.
example:
.. code-block:: python

    {
      "field": "product_color",
      "values": ['blue', 'red', 'green'],
      "type": "bin",
      "weight": 1,
    }

BinOrdinalEncoder
"""""""""
Use for binning ordinal data.
``values`` is the boundaries of the bins.
``window`` is the allowed similarity leakage between closed values.
example:
.. code-block:: python

    {
      "field": "price",
      "values": [10, 50, 100, 500, 1000],
      "type": "binordinal",
      "weight": 1,
      "window": [0.2,1,0.1]
    }

HierarchyEncoder
"""""""""
Use for hierarchical data.
example:
.. code-block:: python

    {
      "field": "sub_category",
      "values": {"meat":["chicken","beef"],"dairy": ['milk','yogurt'],"pastry":['bread','baguette']},
      "type": "hierarchy",
      "weight": 1,
    }

NumpyEncoder
"""""""""
User defined encoder as numpy array.

JSONEncoder
"""""""""
User defined encoder as json.

QwakEncoder
"""""""""
Use with qwak data format.
