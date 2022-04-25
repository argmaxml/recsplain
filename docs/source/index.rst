.. argmaxml documentation master file, created by
   sphinx-quickstart on Thu Mar 17 16:08:47 2022.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

The Recsplain system
=====================

Recsplain is an Explainable recommendation framework.
---------------------------------------------------------

The Recsplain system makes recommendations and explains them. 

Here is an example of a recommendation with explanations. 
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

.. image:: images/explanations.png

The ids array order the recommended items by index position from most to least recommended where the lowest index position is the most recommended.

The values in the distance and explanations arrays correspond to the values in the ids array and each other's values by index position.

How is it done? 
---------------------------------------------------------

Recsplain composes feature-vectors and weighs them.

 .. image:: images/diagram-1.png

We have plenty of encoders built in - see :doc:`encoders-list`
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


The Field types and the schema
---------------------------------------------------------

	
Filter fields (with examples)
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

Encoder fields (“Fuzzy” matching)
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

User Encoders (Optional, just for user2item - see diagram 2)
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

 .. image:: images/diagram-2.png

.. note:: 
   **ArgMaxML** created Recsplain. We are focused on creating software the enables you to integrate recommendation engines into your product to increase customer engagement.

.. toctree::
   :maxdepth: 1