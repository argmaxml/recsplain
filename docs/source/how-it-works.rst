How it works
================

The recsplain system is a tabular similarity search server. It predicts item similarity and user preferences 

It predicts item similarity using encoders and recommends items for users based on the user's previous relationship with relevant items.

Install it into your project to have your very own engine for searching for similar items and making good recommendations. 


Install
--------------

Install the system using the PyPI package manager

Use it as a web server or with Python bindings to call the methods directly from the package.

.. note:: 
   Learn :doc:`how to install recsplain<installation>`.


Configure
--------------

After installing the package, configure the system and index your data.

Configure the system to tell it how to:

- partition the items into separate containers 
- compare items within the same partition 

To configure the system, input your preferences using ``init_schema``.

Input ``filters``, ``encoders``, and ``metric``.

``filters`` are hard filters and are used to separate or exclude items for comparison

``encoders`` are soft filters and are used to control how the system compares items to determine similarity.

``metric`` is . . .

.. note::
    Read more about :doc:`configuring recsplain<configuration>`.

Here is an example configuration.

.. literalinclude:: init_schema_example.json
  :language: JSON
    
.. note::
    The example is what you send in a POST body to the `init_schema` server route or pass as an argument to the `init_schema` method.

Index
---------------

Add items from your database to the recsplain system.

Search
---------------

Search your items and recommend items to users.