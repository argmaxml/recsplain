.. argmaxml documentation master file, created by
   sphinx-quickstart on Thu Mar 17 16:08:47 2022.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Get Started 🦖 
==========================================

Follow the guide below to start making explainable recommendations with Recsplain.

Installation
----------------

Import the package using the following import statement.

.. code-block:: python

    import recssplain as rx


Configuration
---------------------------------------------------------

Use the ``init_schema`` method to configure the system so that it knows how to partition and compare feature vectors.

Here is an example of how to call the ``init_schema`` method.

.. literalinclude:: init_schema_example.py
  :language: python

This is the response from ``init_schema``.

.. literalinclude:: init_schema_response.py
  :language: python


Index
---------------------------------------------------------

Use the ``index`` method to dd items to the Recsplain system so that it has items to partition and compare.


Here is an example of how to call the ``index`` method.

.. literalinclude:: data_index_example.py
  :language: python

This is the response from ``index``.

.. literalinclude:: data_index_response.py
  :language: python

.. note::
   If you do not index items, when you search there will be nothing to check the search against for similarity.

.. note::
   When reusing the index method, using the same id twice creates duplice entries in the index.


Item Similarity
---------------------------------------------------------

Use the ``query`` method to search by item. 

The method returns explainable recommendations for indexed items that are similar to the search item.

Here is an example of how to call the ``query`` method.

.. literalinclude:: item_query_example.py
  :language: python

This is the response from ``query``.

.. literalinclude:: item_query_response.py
  :language: python


User Preference
---------------------------------------------------------

Use the ``user_query`` method to search by user. 

The method returns explainable recommendations for indexed items that the user likely prefers.

When recommending items based on user search, the Recsplain system takes the user's previous history with the items and checks it against the indexed items for similarity.

.. note::
   For example, for an online store, the system recommends the items the user is most likely to buy based on how similar the items are to the items the user previously purchased.

Here is an example of how to call the ``user_query`` method.

.. literalinclude:: user_query_example.py
  :language: python

This is the response from ``user_query``.

.. literalinclude:: user_query_response.py
  :language: python

.. note:: 
   Learn more about the methods in the :doc:`reference`.

.. toctree::
   :maxdepth: 0
   :titlesonly: