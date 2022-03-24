What is recsplain
=====================

The recsplain system is a tabular similarity search server that calculates item similarity and recommends items based on user preferences. 

Recommendation system
-------------------------------------------
Use the system to compare and recommend items from your database to your users.

- search by item to find similar items in your database based on item features
- recommend items to users based on how items compare to a user's purchase history

One common application of recsplain is in online stores where the system recommends products to customers based on items the customer already bought from the store.  

.. note::
   The recommendation system is not limited to just online stores. The applications are virtually endless. 

Create your own
-------------------------------------------
Use recsplain to create your very own recommendation engine.

It is easy to install and customize to suit your needs.

Configure the system to make recommendations based on your needs by using: 

- filters to categorically exclude and separate data for comparisons
- encoders to dictate how the system checks whether items are similar

After configuring the system, easily index a list of items from your database to start making recommendations.

Make recommendations
-------------------------------------------
Start making recommendations by item or by user by either using the system as a webserver or calling the methods from the recsplain code itself. 

Search by item to get similar items ordered by most to least similar, their distances from the search item based on the item vectors, and explanations about the recommendations.

Search by user to get items the user most likely prefers ordered from most to least likely based on the user's order history, each item's distance from the user based on the user's vector, and explanations about the recommendations.

Use explanations
-------------------------------------------
The recsplain system explains it recommendations so that you can better understand its recommendations.

By setting the ``explian`` value to ``1`` when running an item or user query, the recsplain system returns explanations.

The explanations are the distances for each field in the encoders that you set when configuring the system.

Get started
-------------------------------------------
Read about :doc:`how-it-works<how it works> or just :doc:`get-started<get started>`!
