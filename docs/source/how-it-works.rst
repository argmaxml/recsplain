How it works
================

The recsplain system is a tabular similarity search server. Install it into your project to have your very own recommendation engine. 

The recsplain system predicts user preferences based on previous relationship with relevant items where the features of the items are taken into consideration.

Install
--------------

You install the system using the PyPI package manager and use it as a web server or with Python bindings to call the methods directly from the package.

.. note:: 
   Learn :doc:`how to install recsplain<installation>`.


Configure
--------------

After you install the package, you configure the system and index your data.

You configure the system to tell it how to:

- partition the items into separate containers 
- compare items within the same partition 

To configure the system, input your preferences into the ``init_schema`` method.

You can input ``filters``, ``encoders``, and ``metric``.

``filters`` are hard filters and are used to separate or exclude items for comparison

.. note::
    The two most common hard filters are location and language.

``encoders`` are soft filters and are used to control how the system compares items to determine similarity.

``metric`` is . . .

Here is an example configuration.

.. code-block:: python
    {
        "filters": [
            {"field": "country", "values": ["US", "EU"]}
        ],
        "encoders": [
            {"field": "price", "values":["low", "mid", "high"], "type": "onehot", "weight":1},
            {"field": "category", "values":["dairy","meat"], "type": "onehot", "weight":2}
        ],
        "metric": "l2"
    }

.. note::
    The example is what you send in a POST body to the `init_schema` server route or pass as an argument to the `init_schema` method.

The `init_schema` method takes your ``filters``, ``encoders``, and ``metric`` and creates `partitions` based on those inputs.

.. note:: 
    A partition is an instance of the similarity server. The number of partitions is based on the number of values your `init_schema` has for `filters`.


Index
---------------

Add items from your database to the recsplain system.

Search
---------------

Search your items and recommend items to users.