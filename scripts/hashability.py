# class Student:
#     def __init__(self, student_number: str, email: str) -> None:
#         self.student_number = student_number
#         self.email = email
#
#     # def __eq__(self, value: object, /) -> bool:
#     #     return isinstance(value, Student) and self.student_number == value.student_number and self.email == value.email
#     #
#     # def __hash__(self) -> int:
#     #     return hash((self.student_number, self.email))
#
#     def __str__(self) -> str:
#         return f"{self.student_number}"
#
#
# student = Student("ST123", "st123@email.com")
# print(id(student))
# student_2 = Student("ST123", "st123@email.com")
# print(student == student_2)

from collections import Counter

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


book_1 = Book("9780547928227", "The Hobbit")
book_2 = Book("9780547928227", "The Hobbit - 75th Aniversary Edition")
print(hash(book_1))
print(hash(book_2))
print(book_1 == book_2)

book_counter = Counter([book_1, book_2])
print(book_counter)
#

