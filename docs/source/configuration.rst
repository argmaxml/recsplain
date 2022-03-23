
Configuration
=================

Configure the recsplain system using ``init_schema``.

The ``init_schema`` method takes your ``filters``, ``encoders``, and ``metric`` and creates `partitions` based on those inputs.

Filters
****************

``filters`` are hard filters and are used to separate or exclude items for comparison

The two most common hard filters are location and language.


Encoders
****************

``encoders`` are soft filters and are used to control how the system compares items to determine similarity.

-List of them
-Weight

Metric
****************

``metric`` is . . .


Partitions
****************

A partition is an instance of the similarity server. The number of partitions is based on the number of values your `init_schema` has for `filters`.


Vector Size
****************
- Adds an extra for each

Feature Sizes
****************
- Adds an extra for each

Total Items
****************


