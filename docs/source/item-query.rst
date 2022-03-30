Item query
===================

After you configure the system and index your items, you can use the system to search by item for similar items. 

To search by item, use the ``query`` method. 

.. note::
  To seach by user, see the :doc:`user query<user-query>` option.

The ``item_query`` method requires you send data about the search item when you call it, and in response it returns similar items.

Read below to see an example and to learn more about the inputs and outputs.

Example
----------------

Here is an example of data to pass to the ``query`` method.

.. literalinclude:: item_query_data.json
  :language: JSON

Here is an example of how to call the ``query`` method with the example data above.

.. literalinclude:: item_query_example.py
  :language: python

.. note::
   The example sends the data as an argument to the method. If you are using the system as a web server, send the data in the body of a POST request instead.

Here is an example of a response from ``query``.

.. literalinclude:: item_query_response.json
  :language: JSON

Read below to learn more about the inputs and outputs.

Inputs
----------------

The ``query`` method takes the following inputs: 

- ``k``
- ``data``
- ``explain``

k
***************

The ``k`` value is the number of similar items you want the system to return. 

data
***************

The data is an object containing fields and values for the features of the item you are searching for.

.. note::
   Like the item features in the filters and indexing stages, the search item data fields should correspond to a field in your item database.

explain
***************

The explain value tells the system if you want explanations about the recommendations. 

Send a value of ``1`` for explain in order to get explanations. 

.. note::
  To not include explanations in the results, simply do not include the ``explain`` field when you call the function.

Outputs
----------------

The ``query`` method returns an object containing:

- ``ids``
- ``distances``
- ``explanations``

.. note::
  Explanations are optional. To include them in the response, see above.

ids
***************

The ids are the item recommendations and are ordered by index position from most to least similar to the search input.

The item at index position 0 is the most similar item and the item in the last index position is the least similar. 

.. note::
   In the example, A is the top recommendation and has a distance of 1 from the search item. B is the second next best recommendation and has a distance of 3 from the search item.

distances
***************

The distance values tell you how similar each result is to the search item.

.. note::
  The index positions of the distances correspond to the index positions of the ids.

The smaller the distance between two vectors, the more similar the items are to one another.

The distance is an overall similarity value based on comparing the vector for one indexed item to the vector for the search item. 

explanations
***************

The explanations tell you more about how the system calculated the distances by providing distance values for each encoder. 

.. note::
  The index positions of the explanations correspond to the index positions of the ids.

In the example above, A is overall more similar to the search item than B is to the search item.

The explanations show why. It is because A has a smaller distance for category than B by 8 and is greater distance for price than B but by only 2. 

Plus, the encoder configurations weighted category twice as important as price. 

.. note::
  Because A beats B on category by 4x more than B beats A on price and because category is greater weight, A has two reasons to be more similar to the search than B has.

