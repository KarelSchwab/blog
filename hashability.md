For the short-form version of this post, have a look at its [short](https://karelschwab.com/short/creating-a-hashable-object-in-python/).

## What does it mean for an object to be hashable

An object in Python is **hashable** if a numeric value (hash) can be calculated for it. The hash cannot change 
during the lifetime of the object and should also be usable when the object is compared for equality. 

You can get the hash of an object by using the `hash` function:

```python title="python"
hash(object)
# >> 1532586
```

**_NOTE:_** If an object is not hashable, a TypeError will be raised

## Hashable vs Unhashable types

Many types in Python are hashable by default. A rule of thumb is that an object is most likely hashable if its
content cannot change without reassignment. For example, lists and dictionaries can have more items added to
them without the need to create a new `list` or `dict` whereas a `str` can only be updated by having a new 
instance created. This means lists and dictionaries are not hashable, but strings are.

| Type      | Hashable?                             |
|-----------|---------------------------------------|
| int       | Yes                                   |
| float     | Yes                                   |
| bool      | Yes                                   |
| str       | Yes                                   |
| frozenset | Yes                                   |
| bytes     | Yes                                   |
| None      | Yes                                   |
| tuple     | Yes, if all its elements are hashable |
| list      | No                                    |
| dict      | No                                    |
| set       | No                                    |
| bytearray | No                                    |

## Why hashability matters

The real power of hashing comes into play when we work with *hash-based* collections such as sets and 
dictionaries. In these collections, items can be looked up using their hashes instead of iterating over all 
the elements and checking each one individually. Because we know the hash of an object we can fetch the object 
from a collection directly resulting in a *constant time `O(1)` lookup*. 

## Example: Making a Python class hashable

Let's look at a hypothetical scenario where we want to keep track of books in a `Counter` from the `collections`
Python module. The issue is that we have multiple different bookstores entering book details into our database, 
which leads to inconsistencies. For example, bookstore 1 creates a book entry entitled "The Hobbit" while 
bookstore 2 creates an entry for the same book called "The Hobbit - 75th Anniversary Edition".

<u>Read more about the `Counter` class in my post called 
[Python Counter](https://karelschwab.com/blog/python-counter/).</u>

Let's create our `Book` class where we will be storing the book information:

```python title="python"
class Book:
    def __init__(self, isbn: str , title: str) -> None:
        self.isbn = isbn
        self.title = title

    def __repr__(self) -> str:
        return f"{self.title} - {self.isbn}"
```

**_NOTE:_** I've used `__repr__` for this example because it displays nicely when we print out the `Counter`.

We can then create our two book instances and load them into our `Counter`:

```python title="python"
from collections import Counter

book_1 = Book("9780547928227", "The Hobbit")
book_2 = Book("9780547928227", "The Hobbit - 75th Anniversary Edition")

book_counter = Counter([book_1, book_2])
# >> Counter({The Hobbit - 9780547928227: 1, The Hobbit - 75th Anniversary Edition - 9780547928227: 1})
```

Note how our `Counter` contains two entries, one for each book with a count of 1. We don't want this to be 
the case because they are the same book. We instead want to have one book with a count of 2. When we look at 
the hashes of our two book instances our problem becomes clear:

```python title="python"
book_1 = Book("9780547928227", "The Hobbit")
book_2 = Book("9780547928227", "The Hobbit - 75th Anniversary Edition")

hash(book_1)
# >> 7971003730177

hash(book_2)
# >> 7971003726089

book_1 == book_2
# >> False
```

The hashes are different and the book therefore gets added to our `Counter` twice. By default, custom objects
in Python have their *identity* `id` used as their *hash* as long as the object does not have `__eq__` defined.

You can see an object's *identity* like this:

```python title="python"
id(book_1)
# >> 138214733565968
id(book_2)
# >> 138214733500560
```

Let's add `__eq__` to our `Book` class so that we can check two books for equality based on their *ISBN* 
instead of the default *identity*:


```python title="python"
class Book:
    def __init__(self, isbn: str , title: str) -> None:
        self.isbn = isbn
        self.title = title

    def __eq__(self, value: object, /) -> bool:
        return isinstance(value, Book) and self.isbn == value.isbn

    def __repr__(self) -> str:
        return f"{self.title} - {self.isbn}"
```

Our code where we check book 1 and 2 for equality (`book_1 == book_2`) now results in `True`. That is exactly
what we want. However, we now run into a different issue. When trying to compute the hash for each of our
book instances we now see `TypeError: unhashable type: 'Book'`. This is because of the `__eq__` method we added
to our Book class. When `__eq__` is defined on an object and we do not explicitly define a `__hash__` method, 
Python automatically sets `__hash__` to `None` to avoid incorrect behaviour where two objects are equal 
(based on our `__eq__` logic) but they have different hashes. That is exactly what's happening in our case. 
We have two books that appear equal but will have completely different hashes because we have not told Python 
how the hashes should be calculated (the default behaviour of using `id` will be used).

Let's fix it by defining our own `__hash__` method on our `Book` class to specify that the *ISBN* string should be
used to calculate the hash:

```python title="python"
class Book:
    def __init__(self, isbn: str , title: str) -> None:
        self.isbn = isbn
        self.title = title

    def __eq__(self, value: object, /) -> bool:
        return isinstance(value, Book) and self.isbn == value.isbn

    def __hash__(self) -> int:
        return hash(self.isbn)

    def __repr__(self) -> str:
        return f"{self.title} - {self.isbn}"
```

If we have a look at our hashes and equality check now we should see that they match and that the two objects
are equal:

```python title="python"
book_1 = Book("9780547928227", "The Hobbit")
book_2 = Book("9780547928227", "The Hobbit - 75th Anniversary Edition")

hash(book_1)
# >> 2082949608248145613

hash(book_2)
# >> 2082949608248145613

book_1 == book_2
# >> True
```

The `Counter` should now also work as expected because the hashes match up correctly:


```python title="python"
from collections import Counter

book_1 = Book("9780547928227", "The Hobbit")
book_2 = Book("9780547928227", "The Hobbit - 75th Anniversary Edition")

book_counter = Counter([book_1, book_2])
# >> Counter({The Hobbit - 9780547928227: 2})
```

**_NOTE:_** The name of the first book added appears in the `Counter`. If we add `book_2` first and print 
`book_counter` again we would see `Counter({The Hobbit - 75th Anniversary Edition - 9780547928227: 2})`

And there we have it. We can now add as many books to our `Counter` as we want, and as long as the *ISBN*s
are the same the book will not be added as a new book but instead have its counter value incremented.
