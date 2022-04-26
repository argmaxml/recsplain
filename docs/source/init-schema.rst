
Configure
=================

After installing the package, configure the system with your filters, encoders, and metric.

The reasons you need to configure the system is so that it knows how to:

- Partition items into separate containers 
- Compare items within the same partition 

To enter your configuration settings, use the ``init_schema`` method. 

It requires you send data when you call it, and in response it returns data about the system configurations.

Read below to see an example and to learn more about the inputs and outputs.

Example
----------------

Here is an example of data to pass to the ``init_schema`` method to configure the system.

.. literalinclude:: init_schema_data.json
  :language: JSON

Here is an example of how to call the ``init_schema`` method with the example data above.

.. literalinclude:: init_schema_example.py
  :language: python

.. note::
   The example sends the data as an argument to the method. If you are using the system as a web server, send the data in the body of a POST request instead.

Here is an example of a response from ``init_schema``.

.. literalinclude:: init_schema_response.json
  :language: JSON


Read below to learn more about the inputs and outputs.

Inputs
----------------

The ``init_schema`` method requires the following inputs: 

- ``filters`` 
- ``encoders``
- ``metric``

Filters
****************

Filters control which items the system checks for similarity each time you run an item or user query.

As the example above demonstrates, each filter is comprised of a field and possible values for the field. The two most common hard filters are location and language.

.. note::
   The schema needs to include all possible values for each encoder field.

.. note::
   Each field should correspond to a field for the items in your item database and the values to possible values for those fields.

When you run the ``init_schema`` method, the system creates a partition for each filter value.

In each partition are the indexed items whose value for the filter field matches the value for that partition.

When you search, the system checks the search item or user against the items in a particular partition only if the search item's or user's value for that feature matches the partition's value.

.. note:: 
    In the example above, the system creates two partitions. One for US items and another for EU. When searching, if the search item or user is based in the US, the system only searches the US partition, not the EU partition.

Therefore, ``filters`` are hard filters and are used to separate or exclude items for comparison.

Encoders
****************

Encoders control how the system compares items within each partition.

As you see in the example above, each encoder is comprised of a field, possible values for the field, an encoder type, and a weight.

Here is what each does:

- ``field``: a feature to use in the similarity check
- ``values``: values to check for the field
- ``type``: the type of encoder to use for checking similarity for this feature
- ``weight``: the relative importance the system should attribute to this feature in the similarity check

Unlke the filters, the encoders are not hard filters and therefore do not play a role in creating the partitions.

Instead, the encoders are used when the user searches by item or user to find similar items. 

They are soft filters that dictate how the system checks for similarity.

The encoder fields should be a field that the items in your database have or could have. 

The values for each field in the encoder should be values that each item could potentially have for that field.

The type of encoder sets how the system calculates similarity.

.. note::
    Check out the :doc:`list of encoders<encoders-list>` to learn what encoders you can use and how they work.

The weight tells the system the relative importance of each feature in the encoder.

.. note::
    In the example, category is twice as important as price.

Metric
*******************

COMING SOON

Outputs
----------------

The ``init_schema`` method returns an object containing:

- ``partitions``
- ``vector_size``
- ``feature_sizes``

Partitions
****************

The ``partitions`` value is the number of partitions the system made based on your configuration. 

When you index items, the items are added to the partitions only if the item meets the filter criteria.

.. note::
    A partition is an instance of the similarity server. 

As explained above, the number of partitions is based on the number of values ``init_schema`` has for ``filters``.


Feature Sizes
****************

Each encoder has a feature size. 

The feature size is the number of distinct feature values for each encoder, plus one. The plus one is to account for unknown feature values.

In the example above, the price encoder has three values: ``["low", "mid", "high"]``.

Its feature size, therefore, is 4 because of its three values and the possibility for unknown values.

Similarly, the category feature size is 3 because of its two values and the possibility for an unknown.

Vector Size
****************

The vector size is the sum of the features sizes. 

In the example above, the vector size is 7. Here is why. The the price encoder has 3 values and therefore a feature size of 4. The category encoder has 2 values and therefore a feature size of 3. Therefore, the overall feature size is 7.

Total Items
****************

The total items is the total number of items indexed.

.. note::
    Learn more about :doc:`indexing items from your database<data-index>`.










