.. argmaxml documentation master file, created by
   sphinx-quickstart on Thu Mar 17 16:08:47 2022.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Get Started 🦖 
==========================================



Configure
---------------------------------------------------------

Configure the system with your filters, encoders, and metric.

The reasons you need to configure the system is so that it knows how to:

- Partition items into separate containers 
- Compare items within the same partition 

To enter your configuration settings, use the ``init_schema`` method. 

It requires you send data when you call it, and in response it returns data about the system configurations.

Read below to see an example and to learn more about the inputs and outputs.

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

Index
---------------------------------------------------------

Add items to the Recsplain system so you have items in the system to check for similarity when you search.

To add items to the system, use the ``index`` method. 

.. note::
   If you do not index items, when you search there will be nothing to check the search against for similarity.

When you index your data, the system filters the items into separate partitions based on the filters you configured. 

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

.. note::
   When reusing the index method, you should note that using the same id twice will create duplications in the index.


Item Similarity Search
---------------------------------------------------------

Search by item for similar items. 

To search by item, use the ``query`` method. 

.. note::
  To seach by user, see the :doc:`user query<user-query>` option.

The ``item_query`` method requires you send data about the search item when you call it, and in response it returns similar items.

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


User Preference Search
---------------------------------------------------------

Search by user for items the user prefers. 

To search by user, use the ``user_query`` method. 

.. note::
   To seach by item, see the :doc:`item query<item-query>` option.

The ``user_query`` method requires you send data about the user when you call it, and in response it returns items the user likely prefers.

When recommending items based on user search, the Recsplain system takes the user's previous history with the items, such as their item purchase history, and checks it against the items in the database for similarity.

.. note::
   For example, for an online store, the system recommends the items the user is most likely to buy based on how similar the items are to the items the user previously bought.

Here is an example of data to pass to the ``user_query`` method to recommend items to a user.

.. literalinclude:: user_query_data.json
  :language: JSON

Here is an example of how to call the ``user_query`` method with the example data above.

.. literalinclude:: user_query_example.py
  :language: python

.. note::
   The example sends the data as an argument to the method. If you are using the system as a web server, send the data in the body of a POST request instead.

Here is an example of a response from ``user_query``.

.. literalinclude:: user_query_response.json
  :language: JSON


.. toctree::
   :maxdepth: 0
   :titlesonly: