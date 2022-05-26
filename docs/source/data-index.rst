Index
===================

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
