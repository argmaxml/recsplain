Introduction
====================================


TRecSys Documentation
----------------------------
TRecSys is a tabular similarity search server. Install it into your project to have your very own recommendation engine. 

You can:

- customize the filters, encoders, and user encoders for the similarity search server.
- index a list of items based on feature values
- search by item to get the other items most similar to it 
- save your custom similarity search models to disk
- load your custom similarity search models from disk


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
