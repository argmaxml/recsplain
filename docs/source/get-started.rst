.. argmaxml documentation master file, created by
   sphinx-quickstart on Thu Mar 17 16:08:47 2022.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Get Started !
==========================================

Follow the guide below to start making explainable recommendations with Recsplain.

Start with:

- :ref:`Installation<installation-section>`
- :ref:`Configuration<configuration-section>`
- :ref:`Index<index-section>`

Then start searching by:

- :ref:`Item Similarity<item-section>`
- :ref:`User Preference<user-section>`

.. note:: 
   Learn more about the methods in the :doc:`reference`.


.. _installation-section:

Installation
----------------

Import the package using the following import statement.

.. code-block:: python

    import recssplain as rx

.. note:: 
   Learn more about the method in the :doc:`installation` reference.


.. _configuration-section:

Configuration
---------------------------------------------------------

Use the ``init_schema`` method to configure the system so that it knows how to partition and compare feature vectors.

Here is an example of how to call the ``init_schema`` method.

.. literalinclude:: init_schema_example.py
  :language: python

This is the response from ``init_schema``.

.. literalinclude:: init_schema_response.py
  :language: python

.. note:: 
   Learn more about the method in the :doc:`configuration <init-schema>` reference.


.. _index-section:

Index
---------------------------------------------------------

Use the ``index`` method to add items to the Recsplain system so that it has items to partition and compare.

Here is an example of how to call the ``index`` method.

.. literalinclude:: data_index_example.py
  :language: python

This is the response from ``index``.

.. literalinclude:: data_index_response.py
  :language: python

.. note::
   If you do not index items, when you search there will be nothing to check the search against for similarity.

.. note::
   When reusing the index method, using the same id twice creates duplicate entries in the index.

.. note:: 
   Learn more about the method in the :doc:`index <data-index>` reference.


.. _item-section:

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

.. note:: 
   Learn more about the method in the :doc:`item similarity <item-query>` reference.


.. _user-section:

User Preference
---------------------------------------------------------

Use the ``user_query`` method to search by user. 

The method returns explainable recommendations for indexed items that the user likely prefers.

Here is an example of how to call the ``user_query`` method.

.. literalinclude:: user_query_example.py
  :language: python

This is the response from ``user_query``.

.. literalinclude:: user_query_response.py
  :language: python

.. note:: 
   Learn more about the method in the :doc:`user preference <user-query>` reference.


.. toctree::
   :maxdepth: 0
   :titlesonly:
