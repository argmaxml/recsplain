Introduction
====================================

You can:

- customize the filters, encoders, and user encoders for the similarity search server.
- index a list of items based on feature values
- search by item to get the other items most similar to it 
- save your custom similarity search models to disk
- load your custom similarity search models from disk

The recsplain system comes with a variety of encoders

For instance, taking the food example, the recsplain system can take a student's profile of nut allergies and snack order history of ordering 
sweet fruits and see that the student is more likely to eat healthy if presented with sweet fruits instead of other foods and that the student
should be recommended foods with nuts. 

To understand a user's profile previous relationship with the item, the recsplain system creates a vector for each user based on the 
user's profile and history with the items.

Each user vector is a numerical vector where the vector positions and values in an n-dimensional space convey the user's profile and relationship history with the items. 

The vector is used to compare the user to items by looking for the distance between the user vector and item.

The closer the distance, the more likely the user will prefer the item.

Taking the snacks example, if a student has a profile of nut allergies and previously ordered a banana three times, an apple one time, and never ordered carrots, 
the recsplain system creates a vector representation of that user based on their allergies and order history. 

.. note::
   One way to think about it is that the user vector is a nut allergy, three bananas, and one apple. 

The recsplain system compares the characteristics of the user vector to the characteristics of the items to calculate the distance.


Filters
--------------------

HARD FILTERS. USUALLY BY GEO OR LANGUAGE

What they are
Why use them
How to use them
Examples

Encoders
------------------

What they are
Why use them
How to use them
Examples

User Encoders
------------------

What they are
Why use them
How to use them
Examples

Index Values
------------------

each item should be a dict mapping an item feature to its value.

What does it mean to index values (what are the values)
Why do it
How to do it
Examples

Query
----------------

Gets a single item and returns its k nearest neighbors.
What does it mean to save to disk
When do it
Why do it
How to do it


Save Model
----------------

Save your custom similarity search models to disk.
What does it mean to save to disk
When do it
Why do it
How to do it

Load Model
-----------------

Load your custom similarity search models from disk.

What does it mean to load from disk (where does it load to)
When do it
Why do it
How to do it
