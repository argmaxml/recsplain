What is Recsplain
=====================

The Recsplain system is a tabular similarity search server that calculates item similarity so that you can recommend items based on item search or user preferences.

Recommendation system
-------------------------------------------

The Recsplain recommendation engine uses machine learning to recommend items based on how similar an item is to another item or how similar an item is to a user's preferences.

After you configure the system and index your items, you can use the system to:

- search by item to find similar items in your database based on item features
- recommend items to users based on the user's history with the items

The applications are virtually endless. 

.. note::
   One common application of Recsplain is in online stores where the system recommends products to customers based on items the customer already bought from the store.  

Create your own
-------------------------------------------

Use Recsplain to create your very own recommendation engine using your configurations and your data.

It is easy to install and customize to suit your needs. You can configure the system to make recommendations based on your needs by using: 

- filters to categorically exclude and separate data for comparisons
- encoders to dictate how the system checks whether items are similar

After configuring the system, easily index a list of items from your database to start recommeding items to your users.

Make recommendations
-------------------------------------------

Use the system as a webserver or by calling the methods from the Recsplain code itself to recommend items by item or by user.  

Search by item to get similar items ordered by most to least similar, their distances from the search item based on the item vectors, and explanations about the recommendations.

Search by user to get items the user most likely prefers ordered from most to least likely, each item's distance from the user based on the user's vector, and explanations about the recommendations.

Use explanations
-------------------------------------------
The Recsplain system explains its recommendations so that you can better understand the results.

The explanations tell you the degree of similarity for each feature so that you can better understand the order of the recommendations and the distance for each item.

The explanations are a more granular type of result than the overall distance value.

Get started
-------------------------------------------
Read about :doc:`how it works<how-it-works>` or just :doc:`get started<get-started>`!
