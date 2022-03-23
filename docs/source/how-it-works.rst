How it works
================

recsplain is a tabular similarity search server

The recsplain system comes with a variety of encoders

The recsplain system predicts user preferences based on previous relationship with relevant items 
where the features of the items are taken into consideration.

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
