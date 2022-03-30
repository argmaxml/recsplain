Index
===================

After installing and configuring the package, add items to the recsplain system so you have items in the system to check for similarity when you search.

To add items to the system, use the ``index`` method. 

.. note::
   If you do not index items, when you search there will be nothing to check the search against for similarity.

When you index your data, the system filters the items into separate partitions based on the filters you configured. 

Read below to see an example and to learn more about the inputs and outputs.

Example
-------------------

Here is an example of data to pass to the ``index`` method to add your items to the system.

.. literalinclude:: data_index.json
  :language: JSON

Here is an example of how to call the ``index`` method with the example data above.

.. literalinclude:: data_index_example.py
  :language: python

.. note::
   The example sends the data as an argument to the method. If you are using the system as a web server, send the data in the body of a POST request instead.

Here is an example of a response from ``index``.

.. literalinclude:: data_index_response.json
  :language: JSON

Read below to learn more about the inputs and outputs.

Inputs
-------------------

The ``index`` method requires that you input data for each item that you want in the system.

The data is an array of item objects.

Each item object should have an id and a field for each item feature.

The id should be a unique value and serves an important role in the similarity check and the results because the system uses the id in the similarity check and the id is how you identify the item in the results for each query.

Thererfore, the id should be a value that makes it easy to identify each item.

.. note::
   For example, it is common to use the SKU number of a product as the value for the id.

Also, notice in the example that the fields other than the id appear as either a filter or encoder field in the ``init_schema`` example code.

.. note::
   Check out the ``init_schema`` :doc:`example configuration<installation>`.

Call the ``index`` method as many times as you want. Each time you call it, the data you send is added to the existing data without replacing the existing data.

Outputs
-------------------

The ``index`` method returns the number of affected partitions.

A partition is an affected partition if the system added the item to the partition.

An item is added only to the partitions that it matches. An item matches a partition if the item has the feature value corresponding to the partition filter field.

.. note:: 
   Using the example from the :doc:`configuration<init-schema>` page, indexing an item sold only in the US would affect one partition, whereas indexing an item sold in both the US and EU would affect two partitions.
