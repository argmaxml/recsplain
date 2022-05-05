.. argmaxml documentation master file, created by
   sphinx-quickstart on Thu Mar 17 16:08:47 2022.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Recsplain System 🦖 
==========================================

The Recsplain System makes recommendations and explains them. 

Install it in your app, use it with your data, and customize it how you want.

Explainable Recommendations
---------------------------------------------------------

Here is an example recommendation with explanations. 

The example query is for items in the US that are low in price and in the meat category. 

You can see the request and response in the image below. 

.. image:: images/explanations.png

The response body in the image above contains the recommendations and explanations.

The recommendations are in the ids array. The ids are ordered by index position from most to least recommended. The lowest index position is the most recommended.

The explanations are in the distance and explanations arrays. The values in those arrays correspond to the values in the ids array by index position.

How It Works 
---------------------------------------------------------

Recsplain turns items into weighted feature vectors.

.. image:: images/diagram-1.png

The the system compares feature vectors to one another to calculate how similar they are.

 .. image:: images/diagram-3.png

Recsplain can compare feature vectors using different encoders. The encoder type dictates how items are compared to one another.

.. note:: 
   Check out our built-in :doc:`encoders-list`.


Field Types & Schema
---------------------------------------------------------

Configure the Recsplain system to customize how you want it to compare items for similarity.

Here is an example configuration.

.. literalinclude:: init_schema_example.py
  :language: python
	
1. Filter Fields

The filter fields are hard filters. They separate items into different partitions. Only items within the same partition are compared to one another.
 
The example above creates two partitions. One for US items and another for EU.

2. Encoder Fields

The encoder fields are soft filters for fuzzy matching. They determine how item features are compared within a partition.
 
The example above selects the one-hot encoder for each of item feature, price and catgory.

.. note:: 
   Learn more about the one-hot and other available :doc:`encoders-list`.

3. User Encoders

When recommending items for a user, Recsplain has special encoders you should use.

 .. image:: images/diagram-2.png

.. note:: 
   Learn more about the one-hot and other available :doc:`encoders-list`.

.. note:: 
   **ArgMaxML** created Recsplain. We are focused on creating software the enables you to integrate recommendation engines into your product to increase customer engagement.

.. toctree::
   :maxdepth: 0
   :titlesonly: