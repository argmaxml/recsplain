Encoders
================

Recsplain comes with a variety of encoders. 

.. note:: 
   The code for the encoders is in `encoders.py <https://github.com/argmaxml/recsplain/blob/master/recsplain/encoders.py>`_

Here is the list.

NumericEncoder
"""""""""
Use on numeric data.

OneHotEncoder
"""""""""
Use on categorical data. First category is saved for "unknown" entries.

StrictOneHotEncoder
"""""""""
Use on categorical data. No "unknown" category.

OrdinalEncoder
"""""""""
Used on ordinal data.

BinEncoder
"""""""""
Use on binarized data.

BinOrdinalEncoder
"""""""""
Use on binarized ordinal data.

HierarchyEncoder
"""""""""
Use on hierarchical data.

NumpyEncoder
"""""""""
User defined encoder as numpy array.

JSONEncoder
"""""""""
User defined encoder as json.

QwakEncoder
"""""""""
Use with qwak data format.
