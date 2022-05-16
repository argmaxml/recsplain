.. argmaxml documentation master file, created by
   sphinx-quickstart on Thu Mar 17 16:08:47 2022.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Recsplain System 🦖 
==========================================

The Recsplain System makes recommendations and explains them. 

It recommends items based on tem similarity or user preferences. It explains the recommendations in terms of overall similarity and feature-to-feature similarity.

Install it in your app, use it with your data, and customize it how you want.

Explainable Recommendations
---------------------------------------------------------

Here is an example of an item similarity search. The search is for items in the US that are in the meat category and also low in price.

You can see the request and response in the image below. 

.. image:: images/explanations.png

The response body in the image above contains the recommendations and explanations.

The recommendations are in the ids array. 

The ids are ordered by index position from most to least recommended. The lowest index position is the most recommended.

The explanations are in the distance and explanations arrays. The values in those arrays correspond to the values in the ids array by index position.

The distances explain item similarity based on all features and weights. 

The explanations provide more granularity by giving you distances for each feature.

How It Works 
---------------------------------------------------------

For item similarity, Recsplain turns the items into weighted feature vectors.

.. image:: images/diagram-1.png

The system compares the item feature vectors to one another to calculate how similar they are.

.. image:: images/diagram-4.png

For user preferences, Recsplain turns the user into an item feature vector based on the user's previous history with the items. 

.. image:: images/diagram-2.png

.. note::
   For example, a customer of an online store who bought two cookies and a glass of milk has an item feature vector that is a blend of the item vectors for two cookies and milk.

The system compares the user's item feature vector to the indexed item feature vectors to calculate how similar the items are those the items in the user's history. The more similar, the higher the recommendation.

.. image:: images/diagram-3.png


.. note::
   To a customer who previously bought two cookies and a glass of milk, the system recommends other items that have similar features to those purchases.



Field Types & Schema
---------------------------------------------------------

Use the field types and schema to configure the Recsplain filters and encoders. 

Filters determine which items are compared to one another. Encoders determine how they are compared. 

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

.. note:: 
   Learn more about the one-hot and other available :doc:`encoders-list`.

.. note:: 
   **ArgMaxML** created Recsplain. We are focused on creating software the enables you to integrate recommendation engines into your product to increase customer engagement.

.. toctree::
   :maxdepth: 0
   :titlesonly: