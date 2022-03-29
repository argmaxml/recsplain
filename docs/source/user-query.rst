User query
=================

After you configure the system and index your items, you can use the system to search by user for items the user prefers. 

To search by user, use the ``user_query`` method. 

.. note::
  To seach by item, see the :doc:`item query<item-query>` option.

It requires you send data about the user when you call it, and in response it returns items the user likely prefers.

When recommending items to a user, the recsplain system takes the user's previous history with the items, such as their item purchase history, and checks it against the items in the database for similarity.

.. note::
   For example, for an online store, the system recommends the items the user is most likely to buy based on how similar the items are to the items the user previously bought.


Inputs
----------------

The ``user_query`` method requires the following inputs: 

- ``k``
- ``item_history``
- ``data``
- ``explain``

Here is an example of data to pass to the ``user_query`` method.

.. literalinclude:: user_query.json
  :language: JSON

k
***************

The `k` value is the number of items you want the system to return as recommendations. 

item history
***************

The `item history` is an array of item ids that the user has previous history with.

.. note::
   A common example is an array of ids for items the user previously purchased. In the example code, this user previously bought item 1 one time and item 3 twice.

The system uses the features of the items in the array to create an item vector that represents the user based on the features of those items.

.. note::
   The system compare the user's item vector to the item vectors for the indexed items. In other words, if a customer bought three bananas, an apple, and a carrot, their user vector represents a combination of the features from three bananas, an apple, and a carrot. 

It is like converting a user to an item!

The recsplain system compares the characteristics of the user's item vector to the item vector for each indexed item to calculate the distance.


data
***************

The data is an object containing fields and values about the user your are searching for.

.. note::
   User data is most commonly used as hard filters. For instance, in the example in these docs, the system will only recommend US items to the user, not EU items.
   
.. note::   
   The user data fields should correspond to a field in your item database.

explain
***************

The explain value tells the system if you want explanations about the recommendations. 

Send a value of 1 for explain in order to get explanations. 

.. note::
  To not include explanations in the results, simply do not include the explain field when you call the function.

Outputs
----------------

The ``user_query`` method returns an object containing:

- ``ids``
- ``distances``
- ``explanations``

Here is an example result.

.. literalinclude:: user_result.json
  :language: JSON

.. note::
  Explanations are optional. To include them in the response, see above.

ids
***************

The ids are the item recommendations and are ordered by index position from most to least similar.

The item at index position 0 is the item the user most likely prefers and the item in the last index position is the item the user least likely prefers. 

.. note::
   In the example, A is the top recommendation and B is the second next best recommendation.

distances
***************

The distance values tell you how likely the user is to prefer the item.

.. note::
  The index positions of the ids correspond to the index positions of the distances. In the example, A is the top recommendation and has a distance of 0.888898987902 from the search item. B is the second next best recommendation and has a distance of 3.555675839384 from the search item.

The smaller the distance for an item, the more likely the user is to prefer the item.

The distance is an overall similarity value based on comparing the vector for one indexed item to the user's item vector. 

.. note::
   The results for the user search are the same as for the item search except the user search distances are floats instead of integers.


explanations
***************

The explanations tell you more about how the system calculated the distances by providing distance values for each encoder. 

In the example above, the user is more likely to prefer A than B.

The explanations show why. It is because A has a lower distance for category than B and a lower distance for price than B. 

.. note::
   Remember to take the encoder weights into account when reviewing the explanations. The encoder configurations in the example weighted category twice as important as price. 

Because A beats B on category and on price, A has two reasons to be more similar to the search than B has.
