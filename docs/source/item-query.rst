Item query
===================

After you configure the system and index your items, you can use the system to search by item for similar items. 

To search by item, use the ``query`` method. 
.. note::
  To seach by user, see the :doc:`user-query<user query>` option.

It requires you send data about the search item when you call it, and in response it returns similar items.

Inputs
----------------

The ``query`` method requires the following inputs: 
- ``k``
- ``data``

Here is an example of data to pass to the ``query`` method.

.. literalinclude:: item_query.json
  :language: JSON


k
******
The `k` value is the number of similar items you want the system to return. 

data
******

The data are the features of the item you are searching for.

.. note::
   Like the item features in the filters and indexing stages, the search item data fields should correspond to a field in your item database.


Outputs
----------------

Here is an example result.

.. literalinclude:: item_result.json
  :language: JSON

The index positions of the ids correspond to the index positions of the distances and explanations.

The recommendations are ordered by index position from most to least similar with the lowest index position holding the most similar item. 

.. note::
   In the example, A is the top recommendation and has a distance of 1 from the search item. B is the second next best recommendation and has a distance of 3 from the search item.

The distance values are overall values based on the item features. The lower the distance between two vectors, the more similar the items are to one another.

The explanations have distances values for each encoder. 

In the example above, A is overall more similar to the search item than B is to the search item.

The explanations show that is because A has a lower distance for category than B by 8 and is higher distance for price than B but by only 2. Plus, the encoder configurations weighted category twice as important as price. Because A beats B on category by 4x more than B beats A on price and category is greater weight, A has two reasons to be more similar to the search than B has.
