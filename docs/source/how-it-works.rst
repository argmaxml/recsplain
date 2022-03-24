How it works
================

The recsplain system can be installed in a Python project and used as a webserver or by calling the methods from the package.

After installing, start by configuring the system with your search filters, encoders, and metric.

Then, index the items from you database that you want to use in the system for checking similarity.

When you index your data, the system filters the items into separate partitions based on the filters you configured. The filters he system compares items within a partition but not across. 

.. note::
   The filters are hard filters.

When you query your data, the system uses the encoders you configured to control how items within each partition are compared for similarity.

.. note::
   The system can search by item to find items that are similar and can search a database by user to find items the user is likely to prefer.

The system uses the metric value that you configure as a cutoff for what it considers as within the bounds of acceptable similarity.

Configuring system
-------------------

Configure the recsplain system with your filters, encoders, and metric.

Filters
*******************

Use filters to separate the items into partitions for comparison. 

Each filter is comprised of a field and possible values for the field. 

Here is an example:

.. literalinclude:: init_schema_example.json
  :language: JSON

.. note::
   The field should correspond to a field in your item database and the values to possible values for those fields in your item database.

The system creates a partition for each value.

In the example above, the system creates two partitions. One for US items and another for EU.

..note::
   When analyzing similarity, the system compares items within a partition but not across.

Encoders
*******************

Use encoders to control how the system compares items within each partition.

As you see in the example above, each encoder is comprised of a field, possible values for the field, an encoder type, and a weight.

Here is what each does:

-``field``: tells the system a feature to use in the similarity check
-``values``: tells the system which values to check for the field
-``type``: the type of encoder to use for checking similarity for this feature
-``weight``: the importance the system should attribute to this feature in the similarity check

.. note::
   The encoders are soft filters. Instead of excluding or separating data for the similarity check, the encoders are for dictating how the system checks for similarity.

Metric
*******************

The metric sets the upper-bound for what to system should consider as within the acceptable limit for similarity. 

.. note::
   It is a hard filter on the results.

The value for the metric is a number that represents the similarity between items or how likely a user is to prefer an item.

..note::
   The system uses the distance between vectors to make recommendations based on similarity. So technically the metric is a number that represents acceptable distance. More on vectors below.

Start with a number like `10` or `12` and then fine-tune it based on your data and users. 

.. note::
   The lower the number for metric, the more similar the items need to be for the system to consider them similar items.


Indexing Items
-------------------

Add items from your database to the recsplain system so that the system can compare items and recommend items to users.

Each item that you index in the recsplain system should have an id and a field for each filter and encoder field in your configuration.

Here is an example.

.. literalinclude:: index.json
  :language: JSON

The id should be a unique value and serves an important role in the similarity check and the results. 

The system uses the id in the check and is how you identify the item in the results for each query.

Thererfore, the id should be a value that makes it easy to identify each item.

.. note::
   For example, it is common to use the SKU number of a prodcut as the value for the id.

Also, notice in the example that the fields other than the id appear as either a filter or encoder field in the configutation example code above.

Based on the encoders and filters in the configuration, the recsplain system indexes items from your database into the system and initiates itself for querying.

Comparing Items
-------------------

The recsplain system can compare items for similarity.

The system compares the items to one another based on the item features.

The system takes the item features and creates a numerical vector representing the item. 

Using filters to decide which items to check against one another and encoders to control how to check them, the recsplain system compares two item vectors to calculate the distance between the two.

The closer the distance, the more similar the items are to one another.

Recommending Items
-------------------

The recsplain system can recommend items to users.

When recommending items to a user, the recsplain system takes the user's previous history with the items, such as their item purchase history, and checks it against the items in the database for similarity.

.. note::
   For example, for an online store, the system recommends the items the user is most likely to buy based on how similar the items are to the items the user previously bought.

More specifically, the recsplain system creates a numerical vector for each user based on the user's history with the items and taking into account the features of those items.

The vector positions and values convey the user as a blend of the features of the items based on the user's item history. 

.. note:: 
   In other words, if a customer bought three bananas, an apple, and a carrot, their vector represents a combination of the features from three bananas, an apple, and a carrot.

The recsplain system compares the characteristics of the user vector to the characteristics of the items to calculate the distance between the user vector and item.

The closer the distance, the more likely the user will prefer the item.
