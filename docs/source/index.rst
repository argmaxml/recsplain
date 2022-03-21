.. argmaxml documentation master file, created by
   sphinx-quickstart on Thu Mar 17 16:08:47 2022.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

recsplain
==============
recsplain is a tabular similarity search server

Use it to recommend items to users based on their preferences. 

Recommendations are more likely to be successful if based on user preference.

This benefits both the person making the recommendation and the user. 

The recommender is more likely to increase conversions by making more valuable recommendations to users, and users
more easily find the items they prefer.

A teacher could use the recsplain system to recommend healthy snacks to students based on each student's tastes to make 
it more likely that the student actually eats healthy.

A recruiter could recommend candidates to companies based on the company's needs and the candidates qualifications to 
make it more likely that the recruiter makes a successful match.

The applications are virtually endless.

The recsplain system predicts user preferences based on a user's profile and previous relationship with relevant items 
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

The recsplain system is easy to install and to customize to suit your needs.

You can use it to create your very own recommendation engine.

Configure the system to make recommendations based on your needs. You can use filters to categorically exclude data from the recommendations. You can use encoders to dictate how the system checks the similarity.

After configuring, index a list of items based on their features values.

After indexing, you can search by item to get other items most similar to it. 

You also can search by user to get the items the user most likely prefers.

You also can save your custom similarity search models to disk and load your custom similarity search models from disk.

.. note:: 
   **ArgMaxML** created recsplain. We are focused on creating software the enables you to integrate recommendation engines into your product to increase customer engagement.


.. toctree::
   :maxdepth: 2

   Welcome <welcome>