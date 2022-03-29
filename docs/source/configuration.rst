
Configuration
=================

After installing the package, configure the system with your filters, encoders, and metric.

The reasons you need to configure the system is so that it knows how to:

- partition your items into separate containers 
- compare items within the same partition 

To enter your configuration settings, use the ``init_schema`` method. 

It requires you send data when you call it, and in response it returns data about the system configurations.

Inputs
----------------

The ``init_schema`` method requires the following inputs: 

- ``filters`` 
- ``encoders``
- ``metric``

Here is an example of data to pass to the `init_schema` method to configure the system.

.. literalinclude:: init_schema_example.json
  :language: JSON

.. note::
    The example is what you send in a POST body to the `init_schema` server route or pass as an argument to the `init_schema` method.

Filters
****************

Filters control which items are checked for similarity each time you run an item or user query.

As the example above demonstrates, each filter is comprised of a field and possible values for the field. 

.. note::
   Each field should correspond to a field for the items in your item database and the values to possible values for those fields.

When you run the ``init_schema`` method with your inputs, the system creates a partition for each filter value.

.. note:: 
    When you search, the system does not necessarily check against all indexed items. It will check for similarity only the items that meet the criteria of the filters.

In each partition are the indexed items whose value for the filter field matches the value for that partition.

.. note::
    In the example above, the system creates two partitions. One for US items and another for EU.

Only if the search item's or user's value for that feature matches the partition's value does the system check the search item or user against the items in the partition. 

.. note:: 
    In the example above, if the search item is a US item or if the search user is based in the US, the system only searches the US partition, not the EU partition.

Therefore, ``filters`` are hard filters and are used to separate or exclude items for comparison.

.. note::
    The two most common hard filters are location and language.

Encoders
****************

Encoders control how the system compares items within each partition.

As you see in the example above, each encoder is comprised of a field, possible values for the field, an encoder type, and a weight.

Here is what each does:

- ``field``: tells the system a feature to use in the similarity check
- ``values``: tells the system which values to check for the field
- ``type``: the type of encoder to use for checking similarity for this feature
- ``weight``: the importance the system should attribute to this feature in the similarity check

Unlke the filters, the encoders are not hard filters and therefore do not play a role in creating the partitions.

Instead, the encoders are used when the user searches by item or user to find similar items. They are soft filters that dictate how the system checks for similarity.

The encoder fields should be a field that the items in your database have or could have. 

The values for each field in the encoder should be values that each item could potentially have for that field.

The type of encoder sets how the system calculates similarity.

.. note::
    Check out the :doc:`encoders-list<list of encoders>` to learn what encoders you can use and how they work.

The weight tells the system the relative importance of each feature in the encoder.

.. note::
    In the example, category is twice as important as price.

Metric
*******************

The metric sets the upper-bound for what to system should consider as within the acceptable limit for similarity. 

.. note::
   It is a hard filter on the results.

The value for the metric is a number that represents the similarity between items or how likely a user is to prefer an item.

.. note::
   The system uses the distance between vectors to make recommendations based on similarity. So technically the metric is a number that represents acceptable distance. More on vectors below.

Start with a number like 10 or 12 and then fine-tune it based on your data and users. 

.. note::
   The lower the number for metric, the more similar the items need to be for the system to consider them similar items.

Outputs
----------------

The ``init_schema`` method returns an object containing:

- ``partitions``
- ``vector_size``
- ``feature_sizes``

Here is an example of a response from `init_schema`.

.. literalinclude:: init_schema_response.json
  :language: JSON

Partitions
****************

The ``partitions`` value is the number of partitions the system made based on your configuration.

A partition is an instance of the similarity server. 

As explained above, the number of partitions is based on the number of values your `init_schema` has for `filters`.

When you index items, the items are added to the partitions only if the item meets the filter criteria.

Feature Sizes
****************

The features sizes contains the number of features for each encoder, plus one for each encoder to account for unknown feature values.

In the example above, the price encoder has three values: ``["low", "mid", "high"]``.

Its feature size, therefore, is 4 because of its three values and the possibility for unknown values.

Similar for the category encoder, its feature size is 3 because of its two values and the possibility for more.

Vector Size
****************

The vector size is the sum of the features sizes. 

.. note::
    In the example above, the vector size is 7 because the price encoder has 3 values, the category encoder has 2 values, and each of the encoders has the possibility for an unknown value.

Total Items
****************

The total items is the total number of items indexed.

.. note::
    Learn more about :doc:`data-index<indexing items from your database>`.










