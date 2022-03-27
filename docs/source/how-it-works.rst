How it works
========================

The recsplain system is a Python package that you can use as a webserver or with Python bindings.

Easy Setup
------------------------

It is just three easy steps to get started.

First, install the package.

Second, configure the system with your search filters, encoders, and metric. 

Third, index the items from you database that you want to use in the system for checking similarity.

That is it. You can start making recommendations!

.. note::
   Try the :doc:`quickstart<quickstart>` or :doc:`get-started<get started>`!

Make recommendations in two different ways.

- search by item for similar items based on item features
- search by user for items the user is most likely to prefer based on their history with the items

.. note::
   Learn more about recsplain by :doc:`exploring<explore>` more about how the system works.

Custom configuration
------------------------

The recsplain system is customizable in several important ways.

Similarity check
************************

First, customize how the system organizes and compares the items in your database. Simply send your configuration data to the system.

.. note::
   If you are using recsplain as a web server, you send the data in the body of a POST request. If you are using it with Python bindings, you call the configuration method and pass your configuration data as an argument.

The configuation data is comprised of your filters, encoders, and metric.

Filters are hard filters. Use them to control which items are checked for similarity each time you run an item or user query.

.. note::
   The system uses the hard filters to separate the indexed items into partitions. When searching, the system checks whether the search item or user is similar to the items within a particular partition **only if** the search item or user fits the filter criteria for that partition.

Encoders are soft filters. Use them to control how the system checks for similarity.

.. note::
   The system uses encoders to determine how to check for similarity within each partition.

Data Index
************************

Second, customize the data by indexing data from your database. The recsplain makes it easy to index the items from your database that you want to include in the recommendation engine.

This way you can make recommendations based on your actual data.

.. note::
   If you are using recsplain as a web server, you send the item data in the body of a POST request. If you are using it with Python bindings, call the indexing method and pass your item data as an argument.

.. note::
   Index only the data that you want to include as possible recommendations.


Query multiple ways
------------------------

Recommend items by checking for similarity based on an item or a user.

When you search by item or user, you send the system data about the seach item or user. 

The search item data consists of an id and values for item features that correspond to the filters and encoders. 

The user data consists of a user id and an item history, like a purchase history, where each item in the history is and id for an indexed item.

.. note::
   If you are using recsplain as a web server, you send the seach data in the body of a POST request. If you are using it with Python bindings, call the search method and pass your item data as an argument.

.. note::
   The system has separate methods for item and user searches.


Understand results
------------------------

Each time you search by item or user, the system recommends items by comparing item features to see how similiar the features are to one another.

The system returns items it deems similar to the search item or user, the degree of similar of each result, and optional explanations for each item in the results.

The system returns the items in an array ordered by most to least similar. The first item in the array is the item that is most similar and the last item in the array is the least similar.

The degree of similarity is measured using the distance between the items where the distance is measured based on vector representations of the items.

.. note::
   A vector is . . .

When searching by item, similarity consists of comparing the search item vector to the vector for each item in the database.

When searching by user, similarity consists of creating an item vector for the user based on the user's history with the item and comparing this user vector to the item vector for each indexed item.

For each item in the array, the system also returns an array of distances telling you how similar each item is to the search item or user.

Optionally, the system also returns an array of explanations consisting of more granular result data from which the system derived the final recommendations and overall distances.




