from http import HTTPStatus
from typing import Optional
from fastapi import FastAPI, Body, Path, Query, HTTPException
from pydantic import BaseModel, Field
from starlette import status

app = FastAPI()


class Book:
    id: int
    title: str
    description: str
    author: str
    rating: int
    publish_date: int

    def __init__(self, id, title, description, author, rating, publish_date):
        self.id = id
        self.title = title
        self.description = description
        self.author = author
        self.rating = rating
        self.publish_date = publish_date


BOOKS = [
    Book(1, "Computer Science Pro", "A very nice book", "Coding With Roby", 5, 2013),
    Book(2, "Be Fast With FastAPI", "A great book", "Coding With Roby", 5, 2014),
    Book(3, "Master Endpoints", "An awesome book", "Coding With Roby", 5, 2009),
    Book(4, "HP1", "Book Description", "Author 1", 2, 2015),
    Book(5, "HP2", "Book Description", "Author 2", 1, 2015),
    Book(6, "HP3", "Book Description", "Author 3", 3, 2015),
]


class BookRequest(BaseModel):
    id: Optional[int] = Field(
        description="Id is not required for creating a book, but it is required for updating",
        default=None,
    )
    title: str = Field(min_length=3)
    author: str = Field(min_length=1)
    description: str = Field(min_length=1, max_length=100)
    rating: int = Field(gt=0, lt=6)
    publish_date: int = Field(gt=1000, lt=2025)
    model_config = {
        "json_schema_extra": {
            "example": {
                "title": "A new book",
                "author": "John Doe",
                "description": "This is a new book",
                "rating": 4,
                "publish_date": 2015,
            }
        }
    }


@app.get("/books", status_code=status.HTTP_200_OK)
async def get_all_books():
    return BOOKS


@app.get("/books/{book_id}", status_code=status.HTTP_200_OK)
async def get_book_by_id(book_id: int = Path(gt=0)):
    for book in BOOKS:
        if book.id == book_id:
            return book
    raise HTTPException(status_code=404, detail="requested book not found")


@app.get("/books-by-rating", status_code=status.HTTP_200_OK)
async def get_books_by_rating(rating: int = Query(gt=0, lt=6)):
    print(f"Rating received: {rating}")
    books_with_rating = [book for book in BOOKS if book.rating == rating]
    return books_with_rating


@app.post("/create-book", status_code=status.HTTP_201_CREATED)
async def create_book(book_request: BookRequest):
    new_book = Book(**book_request.model_dump())
    BOOKS.append(find_book_id(new_book))


@app.put("/update-book", status_code=status.HTTP_204_NO_CONTENT)
async def update_book(book_request: BookRequest):
    book_changed = False
    for i in range(len(BOOKS)):
        if BOOKS[i].id == book_request.id:
            BOOKS[i] = book_request
            book_changed = True
    if not book_changed:
        raise HTTPException(status_code=404, detail="book not found")


@app.delete("/delete-book/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(book_id: int):
    book_deleted = False
    for book in BOOKS:
        if book.id == book_id:
            BOOKS.remove(book)
            book_deleted = True
    if not book_deleted:
        raise HTTPException(status_code=404, detail="book not found")


@app.get("/get-book-by-pub-date/{pub_date}", status_code=status.HTTP_200_OK)
async def get_book_by_publish_date(pub_date: int = Path(gt=1990, lt=2025)):
    books_published = [book for book in BOOKS if book.publish_date == pub_date]
    return books_published


def find_book_id(book: Book):
    book.id = 1 if len(BOOKS) == 0 else BOOKS[-1].id + 1
    return book
