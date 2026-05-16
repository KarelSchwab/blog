For a more in-depth look at Hashability, see the dedicated [post](https://karelschwab.com/blog/hashable-objects-in-python/)

# Example of creating a Book class that is Hashable via the ISBN number

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

Here we can see that the Counter sees the two books as the same thanks to its hash:

```python title="python"
from collections import Counter

book_1 = Book("9780547928227", "The Hobbit")
book_2 = Book("9780547928227", "The Hobbit - 75th Anniversary Edition")

book_counter = Counter([book_1, book_2])
# >> Counter({The Hobbit - 9780547928227: 2})
```
