
Configuration
=================

``filters`` are hard filters and are used to separate or exclude items for comparison

``encoders`` are soft filters and are used to control how the system compares items to determine similarity.

``metric`` is . . .

The two most common hard filters are location and language.

The `init_schema` method takes your ``filters``, ``encoders``, and ``metric`` and creates `partitions` based on those inputs.

.. note:: 
    A partition is an instance of the similarity server. The number of partitions is based on the number of values your `init_schema` has for `filters`.
