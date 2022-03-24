How it works
================

The system filters items into separate partitions for comparison and uses encoders to control how items within each partition are compared for similarity.

The system can search a database by item to find items that are similar and can search a database by user to find items the user is likely to prefer.

Initiating system
-------------------

Initiate the recsplain system with your filters, encoders, and metric.

Indexing Items
-------------------

The recsplain system indexes items from your database.


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
