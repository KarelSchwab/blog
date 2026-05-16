## Instantiation

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

```python
counter = Counter("mississippi") 
counter["s"]
# >> 4
counter["x"] # Note how we don't get a KeyError
# >> 0
```

### Subtract

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

### Elements

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

### Most common

```python
counter = Counter("mississippi")
# >> Counter({'i': 4, 's': 4, 'p': 2, 'm': 1})

# If n is not specified, all the items are returned
print(counter.most_common())
# >> [('i', 4), ('s', 4), ('p', 2), ('m', 1)]

print(counter.most_common(2))
# >> [('i', 4), ('s', 4)]
```

### Total

```python
counter = Counter("mississippi")
# >> Counter({'i': 4, 's': 4, 'p': 2, 'm': 1})

print(counter.total())
# >> 11
```

## Arithmetic

### Addition

```python
counter_1 = Counter("mississippi")
# >> Counter({'i': 4, 's': 4, 'p': 2, 'm': 1})
counter_2 = Counter(p=10, m=3, x=5, y=-2)
# >> Counter({'p': 10, 'x': 5, 'm': 3})
counter_3 = counter_1 + counter_2
# >> Counter({'p': 12, 'x': 5, 'm': 4, 'i': 4, 's': 4})
```

### Subtraction

```python
counter_1 = Counter("mississippi")
# >> Counter({'i': 4, 's': 4, 'p': 2, 'm': 1})
counter_2 = Counter(p=1, m=2, s=2, x=5, y=-3)
# >> Counter({'x': 5, 'm': 2, 's': 2, 'p': 1, 'y': -3})
counter_3 = counter_1 - counter_2
# >> Counter({'i': 4, 'y': 3, 's': 2, 'p': 1})
```

### Intersection

```python
counter_1 = Counter("mississippi")
# >> Counter({'i': 4, 's': 4, 'p': 2, 'm': 1})
counter_2 = Counter("mmmiss")
# >> Counter({'m': 3, 's': 2, 'i': 1})
counter_3 = counter_1 & counter_2
# >> Counter({'s': 2, 'm': 1, 'i': 1})
```

### Union

```python
counter_1 = Counter("mississippi")
# >> Counter({'i': 4, 's': 4, 'p': 2, 'm': 1})
counter_2 = Counter("mmmissx")
# >> Counter({'m': 3, 's': 2, 'i': 1, 'x': 1})
counter_3 = counter_1 | counter_2
# >> Counter({'i': 4, 's': 4, 'm': 3, 'p': 2, 'x': 1})
```

