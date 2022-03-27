User query
=================

K
----------------

Data
----------------

Item History
----------------

Explain
----------------

Ids
----------------

Distances
----------------

Explanations
----------------


Recommend
-------------------

The recsplain system can recommend items to users. Instead of searching by item like above, you search for similar items for a user.

When recommending items to a user, the recsplain system takes the user's previous history with the items, such as their item purchase history, and checks it against the items in the database for similarity.

.. note::
   For example, for an online store, the system recommends the items the user is most likely to buy based on how similar the items are to the items the user previously bought.

Here is an example of data to pass to the `user_query` method to search by user for items they likely prefer.

.. literalinclude:: user_query.json
  :language: JSON

Notice that the user object has similar information as the item search object but organized differently. The user object has a data field like the item object containing a value from the configuration filters.

The user object, however, has an item history that the item search object does not.

The item history is an array representing the user's history with the items where each element in the array is an item id.

.. note::
   In the example code, this user previously bought item 1 one time and item 3 twice.

To search for items based on the user object, the recsplain system creates a numerical vector for the user that resembles item vectors. To make a user vectors that resemble item vectors, the system takes the user's history with the items to create a vector for the user based on the features in the user's item history.

The vector positions and values convey the user as a blend of the features of the items based on the user's item history so that the system can compare apples to apples, so to speak. 

.. note:: 
   In other words, if a customer bought three bananas, an apple, and a carrot, their user vector represents a combination of the features from three bananas, an apple, and a carrot. 

It is like converting a user to an item!

The recsplain system compares the characteristics of the user vector to the characteristics of the items to calculate the distance between the user vector and item.

The closer the distance, the more likely the user will prefer the item.

The results for the user search are the same as for the item search except the user search distances are floats instead of integers.

.. literalinclude:: user_result.json
  :language: JSON