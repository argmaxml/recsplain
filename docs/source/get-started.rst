.. argmaxml documentation master file, created by
   sphinx-quickstart on Thu Mar 17 16:08:47 2022.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Get Started 🦖 
==========================================

Installation
----------------

Import the package using the following import statement.

.. code-block:: python
    import recssplain as rx


Configuration
---------------------------------------------------------

Configure the system with your filters, encoders, and metric.

You need to configure the system so that it knows how to:

- Partition the items for comparison 
- Compare items within the same partition 

Enter your configuration settings using the ``init_schema`` method. 

It requires you send data when you call it. The method returns data about the system configurations.

Here is an example of how to call the ``init_schema`` method.

.. literalinclude:: init_schema_example.py
  :language: python

This is the response from ``init_schema``.

.. literalinclude:: init_schema_response.py
  :language: python


Index
---------------------------------------------------------

Add items to the Recsplain system so you have items to partition and compare.

Add items to the system using the ``index`` method. 

.. note::
   If you do not index items, when you search there will be nothing to check the search against for similarity.

The system filters the items into separate partitions based on the filters you configured. 

Here is an example of how to call the ``index`` method.

.. literalinclude:: data_index_example.py
  :language: python

This is the response from ``index``.

.. literalinclude:: data_index_response.py
  :language: python

.. note::
   When reusing the index method, using the same id twice creates duplice entries in the index.


Item Similarity
---------------------------------------------------------

Search by item for similar items. 

Search by item using the ``query`` method. 

It requires you send data about the search item when you call it. 

The method returns explainable recommendations for indexed items that are similar to the search item.

Here is an example of how to call the ``query`` method.

.. literalinclude:: item_query_example.py
  :language: python

This is the response from ``query``.

.. literalinclude:: item_query_response.py
  :language: python


User Preference
---------------------------------------------------------

Search by user for items the user prefers. 

Search by user with the ``user_query`` method. 

It requires you send data about the user when you call it

The method returns explainable recommendations items for indexed items that the user likely prefers.

When recommending items based on user search, the Recsplain system takes the user's previous history with the items, such as their item purchase history, and checks it against the items in the database for similarity.

.. note::
   For example, for an online store, the system recommends the items the user is most likely to buy based on how similar the items are to the items the user previously bought.

Here is an example of how to call the ``user_query`` method.

.. literalinclude:: user_query_example.py
  :language: python

This is the response from ``user_query``.

.. literalinclude:: user_query_response.py
  :language: python


.. toctree::
   :maxdepth: 0
   :titlesonly: