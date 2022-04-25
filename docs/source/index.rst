.. argmaxml documentation master file, created by
   sphinx-quickstart on Thu Mar 17 16:08:47 2022.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

The Recsplain system
=====================

1. Recsplain is an Explainable recommendation framework.

The Recsplain system makes recommendations and explains them. 

Here is an example of a recommendation with explanations. 

.. image:: images/explanations.png
   :width: 200px
   :height: 100px
   :scale: 50 %
   :alt: alternate text
   :align: right

The ids array order the recommended items by index position from most to least recommended where the lowest index position is the most recommended.

The values in the distance and explanations arrays correspond to the values in the ids array and each other's values by index position.

2. How is it done? 

Recsplain composes feature-vectors and weighs them.

 .. image:: images/explanations.png
   :width: 200px
   :height: 100px
   :scale: 50 %
   :alt: alternate text
   :align: right

	2.1 We have plenty of encoders built in - see :doc:`encoders-list`

3. The Field types and the schema
	
   3.1 Filter fields (with examples)
	
   3.2 Encoder fields (“Fuzzy” matching)
	
   3.3 User Encoders (Optional, just for user2item - see diagram 2)

.. note:: 
   **ArgMaxML** created Recsplain. We are focused on creating software the enables you to integrate recommendation engines into your product to increase customer engagement.
