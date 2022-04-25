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

.. image:: images/explanations.png

The recommeded items are in the ids array. The ids are ordered by index position from most to least recommended. The lowest index position is the most recommended.

The values in the distance and explanations arrays correspond to the values in the ids array by index position.

How It Works 
---------------------------------------------------------

Recsplain composes feature-vectors and weighs them.

 .. image:: images/diagram-1.png

We have plenty of encoders built in. Check out our :doc:`encoders-list`.


Field Types & Schema
---------------------------------------------------------
	
1. Filter fields (with examples)

2. Encoder fields (“Fuzzy” matching)

3. User Encoders (Optional, just for user2item - see diagram 2)

 .. image:: images/diagram-2.png

.. note:: 
   **ArgMaxML** created Recsplain. We are focused on creating software the enables you to integrate recommendation engines into your product to increase customer engagement.

.. toctree::
   :maxdepth: 0
   :titlesonly: