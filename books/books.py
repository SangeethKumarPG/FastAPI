from fastapi import FastAPI, Body

app = FastAPI()

BOOKS = [
    {"title":"Title One", "author":"Author One", "category":"Science" },
    {"title":"Title Two", "author":"Author Two", "category":"Science" },
    {"title":"Title Three", "author":"Author Three", "category":"History" },
    {"title":"Title Four", "author":"Author Four", "category":"Math" },
    {"title":"Title Five", "author":"Author Five", "category":"Geography" },
]

@app.get('/books')
async def get_books():
    return BOOKS

@app.get("/books/{dynamic_parameter}")
async def read_all_books(dynamic_parameter):
    return {
        'dynamic_parameter':dynamic_parameter
    }

@app.get("/mybook/{book_name}")
async def get_my_book(book_name:str):
    for book in BOOKS:
        if book.get('title').casefold() == book_name.casefold():
            return {"my_favourite_book":book}
        
@app.get("/books/search/")
async def get_book_by_category(category :str):
    books_in_category = []
    for book in BOOKS:
        if book.get('category').casefold() == category.casefold():
            books_in_category.append(book)
    return books_in_category

@app.get('/books/by_author/{book_author}')
async def read_author_category_by_query(book_author:str, book_category:str):
    books = []
    for book in BOOKS:
        if book.get('author').casefold() == book_author and book.get('category').casefold() == book_category:
            books.append(book)
    return books

@app.post('/books/create/')
async def create_new_book(new_book=Body()):
    BOOKS.append(new_book)
    return new_book

@app.put('/books/update')
async def update_book(updated_book=Body()):
    for i in range(len(BOOKS)):
        if BOOKS[i].get('title').casefold() == updated_book.get('title').casefold():
            BOOKS[i] = updated_book
            return {"message":"Book updated"}
    return {"message":"no book found"}

@app.delete("/books/delete_book/{book_title}")
async def delete_book_by_title(book_title:str):
    for i in range(len(BOOKS)):
        if BOOKS[i].get('title').casefold() == book_title.casefold():
            BOOKS.pop(i)
            return {"message":"Book Deleted!"}
    return {"message":"Book not found!"}