The `Counter` class, part of the `collections` package, does well... what the name says. It counts things.
And by things I mean any hashable objects. In a `Counter` the hashable objects are the keys and their counts
are the values. Under the hood it is just a Python dictionary with some niceties to allow us to easily
keep count of objects stored within.

<u>Read more about hashable objects in my posts called 
[Hashable objects in Python](https://karelschwab.com/hashable-objects-in-python).</u>

**_NOTE:_** The values (counts) stored in the `Counter` can be positive or negative as well as any data type 
that supports addition and subtraction. However, the documentation warns that not all methods work with 
all data types. See the *Note* at the bottom of the `Counter` section in the
[official docs](https://docs.python.org/3/library/collections.html#collections.Counter).

## Instantiation

You can instantiate an empty `Counter` or by supplying an **iterable** (*str*, *list*, *etc*) or a **map** (dict, kwargs):

```python
from collections import Counter

# Empty Counter
counter = Counter() 
# >> Counter()

# Counter from a str
counter = Counter("mississippi") 
# >> Counter({'i': 4, 's': 4, 'p': 2, 'm': 1})

# Counter from a list
counter = Counter(["A", "B", "C", "D"]) 
# >> Counter({'A': 1, 'B': 1, 'C': 1, 'D': 1})

# Counter from a dict
counter = Counter({ "Apple": 3, "Banana": 5 }) 
# >> Counter({'Banana': 5, 'Apple': 3})

# Counter from kwargs
counter = Counter(red=255, green=100, blue=200) 
# >> Counter({'red': 255, 'blue': 200, 'green': 100})
```

## Accessing counts

You can access the counts via indexing / subscription:

```python
counter = Counter("mississippi") 
counter["s"]
# >> 4
counter["x"] # Note how we don't get a KeyError
# >> 0
```

**Note:** If we try to access a key that is not in the `Counter`, 0 is returned. With a normal `dict` we would
get a `KeyError`.

## Working with the counts

We can manipulate the counts through the use of the `update` and `subtract` methods:

### Subtract

Examples of using the `subtract` method:

```python
counter = Counter("mississippi") 
# >> Counter({'i': 4, 's': 4, 'p': 2, 'm': 1})
counter.subtract("i")
# >> Counter({'s': 4, 'i': 3, 'p': 2, 'm': 1})

counter = Counter("mississippi") 
# >> Counter({'i': 4, 's': 4, 'p': 2, 'm': 1})
counter.subtract("iis")
# >> Counter({'s': 3, 'i': 2, 'p': 2, 'm': 1})

counter = Counter("mississippi") 
# >> Counter({'i': 4, 's': 4, 'p': 2, 'm': 1})
counter.subtract({"s": 3})
# >> Counter({'i': 4, 'p': 2, 'm': 1, 's': 1})

counter = Counter("mississippi") 
# >> Counter({'i': 4, 's': 4, 'p': 2, 'm': 1})
counter.subtract(s=3, p=1, m=1)
# >> Counter({'i': 4, 's': 1, 'p': 1, 'm': -1})
```

### Update

Examples of using the `update` method:

```python
counter = Counter("mississippi") 
# >> Counter({'i': 4, 's': 4, 'p': 2, 'm': 1})
counter.update("i")
# >> Counter({'i': 5, 's': 4, 'p': 2, 'm': 1})

counter = Counter("mississippi") 
# >> Counter({'i': 4, 's': 4, 'p': 2, 'm': 1})
counter.update("iis")
# >> Counter({'i': 6, 's': 5, 'p': 2, 'm': 1})

counter = Counter("mississippi") 
# >> Counter({'i': 4, 's': 4, 'p': 2, 'm': 1})
counter.update({"s": 3})
# >> Counter({'s': 7, 'i': 4, 'p': 2, 'm': 1})

counter = Counter("mississippi") 
# >> Counter({'i': 4, 's': 4, 'p': 2, 'm': 1})
counter.update(s=3, p=1, m=1)
# >> Counter({'s': 7, 'i': 4, 'm': 3, 'p': 3})
```

## Useful Methods

In addition to handling the counts for us, `Counter` also has a few methods that are quite useful.

- `elements`: Returns an iterator that repeats each element as many times as its count

```python
counter = Counter("mississippi") 
# >> Counter({'i': 4, 's': 4, 'p': 2, 'm': 1})

# We can get a list of all the elements
print(list(counter.elements()))
# >> ['m', 'i', 'i', 'i', 'i', 's', 's', 's', 's', 'p', 'p']

# We can get a sorted list of elements (most frequent to least frequent)
print(sorted(counter.elements()))
# >> ['i', 'i', 'i', 'i', 'm', 'p', 'p', 's', 's', 's', 's']

# We can get a sorted list of elements (least frequent to most frequent)
print(sorted(counter.elements(), reverse=True))
# >> ['s', 's', 's', 's', 'p', 'p', 'm', 'i', 'i', 'i', 'i']
```

- `most_common`: Return a list of the *n* most common elements and their counts in tuples

```python
counter = Counter("mississippi")
# >> Counter({'i': 4, 's': 4, 'p': 2, 'm': 1})

# If n is not specified, all the items are returned
print(counter.most_common())
# >> [('i', 4), ('s', 4), ('p', 2), ('m', 1)]

print(counter.most_common(2))
# >> [('i', 4), ('s', 4)]
```

- `total`: Returns the sum of all the counts

```python
counter = Counter("mississippi")
# >> Counter({'i': 4, 's': 4, 'p': 2, 'm': 1})

print(counter.total())
# >> 11
```

Since `Counter` is a subclass of `dict` it also has access to the common dictionary function like `keys`,
`values`, `items`, and `clear`. We can also remove an item entirely by using `del`:

```python
counter = Counter("mississippi") 
# >> Counter({'i': 4, 's': 4, 'p': 2, 'm': 1})

del counter["i"]
# >> Counter({'s': 4, 'p': 2, 'm': 1})
```

## Arithmetic and other operations

### Addition

We can add two `Counter`s together in the following way:

```python
counter_1 = Counter("mississippi")
# >> Counter({'i': 4, 's': 4, 'p': 2, 'm': 1})
counter_2 = Counter(p=10, m=3, x=5, y=-2)
# >> Counter({'p': 10, 'x': 5, 'm': 3})
counter_3 = counter_1 + counter_2
# >> Counter({'p': 12, 'x': 5, 'm': 4, 'i': 4, 's': 4})
```

**Note:** Only positive counts are added to the newly created counter.

### Subtraction

We can also subtract a `Counter` from another:

```python
counter_1 = Counter("mississippi")
# >> Counter({'i': 4, 's': 4, 'p': 2, 'm': 1})
counter_2 = Counter(p=1, m=2, s=2, x=5, y=-3)
# >> Counter({'x': 5, 'm': 2, 's': 2, 'p': 1, 'y': -3})
counter_3 = counter_1 - counter_2
# >> Counter({'i': 4, 'y': 3, 's': 2, 'p': 1})
```

**Note:** Only positive counts are kept in the resulting counter. Also note how the *y* was *-3* before
the subtraction and that its sign was flipped to *+* during the operation, ending up as a positive *3*.

### Intersection

We can use `&` to check where two counters have the same objects and what the smallest counts for the
overlapping objects are:

```python
counter_1 = Counter("mississippi")
# >> Counter({'i': 4, 's': 4, 'p': 2, 'm': 1})
counter_2 = Counter("mmmiss")
# >> Counter({'m': 3, 's': 2, 'i': 1})
counter_3 = counter_1 & counter_2
# >> Counter({'s': 2, 'm': 1, 'i': 1})
```

**Note:** *m* comes from `counter_1` while both *s* and *i* come from `counter_2` because their counts were the
smallest.

### Union

We can use `|` to get the largest counts from two `Counter`s. This returns a new `Counter` where all the unique 
objects from each are included as well as the largest of the two in the cases where there are overlapping objects:

```python
counter_1 = Counter("mississippi")
# >> Counter({'i': 4, 's': 4, 'p': 2, 'm': 1})
counter_2 = Counter("mmmissx")
# >> Counter({'m': 3, 's': 2, 'i': 1, 'x': 1})
counter_3 = counter_1 | counter_2
# >> Counter({'i': 4, 's': 4, 'm': 3, 'p': 2, 'x': 1})
```

**Note:** *i*, *s*, and *p* all come from `counter_1` while *m* and *x* both come from `counter_2`.

