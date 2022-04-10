def get_values_nested(d):
    """
    get_values_nested ({'a':'a1','b':['b1', 'b2'],'c':{'c1':['c11','c12']}})
    returns: ['a1','b1', 'b2','c11','c12']
    """
    if type(d) == str:
        return [d]
    elif type(d) == list:
        return d
    elif type(d) == dict:
        return sum([get_values_nested(v) for v in d.values()], [])
    else:
        raise TypeError("Unsupported type " + str(type(d)))


def delistify_tree(tree, a, b):
    if type(tree) == str:
        return tree
    if type(tree) == list:
        return a if a in tree else (b if b in tree else None)
    if type(tree) == dict:
        ret = [(k, delistify_tree(v, a, b)) for k, v in tree.items()]
        return dict(filter(lambda x: x[1], ret))
    else:
        raise TypeError("Unsupported type " + str(type(d)))


def tree_find_depth(tree, a):
    if type(tree) == str:
        return 0 if tree == a else None
    if type(tree) == list:
        return 1 if a in tree else None
    if type(tree) == dict:
        try:
            found = next(filter(lambda v: v is not None, map(lambda v: tree_find_depth(v, a), tree.values())))
        except:
            return None
        return 1 + found
    else:
        raise TypeError("Unsupported type " + str(type(d)))


def are_siblings(tree, a, b):
    if type(tree) == str:
        return False
    if type(tree) == list:
        return a in tree and b in tree
    if type(tree) == dict:
        return any(are_siblings(v, a, b) for v in tree.values())
    else:
        raise TypeError("Unsupported type " + str(type(d)))


def lowest_depth(tree, a, b):
    if a == b:
        return 0
    if are_siblings(tree, a, b):
        return 1
    tree = delistify_tree(tree, a, b)
    print(tree_find_depth(tree, a))
    found_a = tree_find_depth(tree, a)
    found_b = tree_find_depth(tree, b)
    while found_a is not None and found_b is not None:
        for v in tree.values():
            da = tree_find_depth(v, a)
            db = tree_find_depth(v, b)
            if da is not None and db is not None:
                tree = v
                found_a = da
                found_b = db
                break
    return found_a + found_b
