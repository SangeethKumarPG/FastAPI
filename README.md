# FASTAPI
To create a virtual environment in windows we use python -m venv environment\_name

To install fast api activate the created environment using:
environment\_name\\Scripts\\activate.bat

Then install fastapi using pip. Then we need to install the uvicorn standard server for the webserver. The commands are :

```javaScript
pip install fastapi
pip install "uvicorn[standard]"
```

To create a fast api project simply create a python file, inside that import the fastapi module. Create an app object of the module, use the app object as a decorator for your function definition and specify the endpoint. Define the async function which handles the request. After this to start an application we can use the uvicorn webserver.
`uvicorn filename:app --reload
`This syntax is used for live reload functionality.
The below shown is a sample api for get request.

```javaScript
from fastapi import FastAPI
app = FastAPI()
 
@app.get("/hello_world")
async def hello_world():
    return {
        "message": "Hello World!"
    }
```

To run this we use:
`uvicorn hello_world:app --reload`

There is also a newer syntax to run fast api projects. That is `fastapi run filename.py` . This command run the fastapi in production mode. To run in the dev mode we can use:
`fastapi dev file_name.py`
**NOTE: These commands only work if you install fastapi\[standard\] version.**

fastapi provides swagger(openapi) out of the box. So for that we just need to navigate to the /docs endpoint from the basepath

To pass a dynamic parameter we use {} inside which we set a parameter name. This name is mentioned as the argument to the function, this is accessed as a variable inside the function body.
eg:

```javaScript
@app.get("/book/{dynamic_param}")
async def read_all_books(dynamic_param):
    return {'dynamic_param':dynamic_param}
```

Anything we pass at the end of the /books/ is accepted as a dynamic param.

In case of path parameters the order matters. Suppose you have an api endpoint which is '/books/{dynamic\_parameter}' and '/books/mybook' the first preference is given to the function defined first. So to avoid this we should place the functions which has static path variables first and then only place the functions with dynamic path variables.
It is also possible to enforce a type to the dynamic path variable inside the function argument using the native python syntax.

**NOTE: In the api name or path variables you cannot have spaces, instead you should use %20 for whitespaces.**

Query parameters are parameters we pass at the end of the request by using `?key=value` format. In our fastapi controller to handle this we don't need to define anything in the route, we just need to accept the parameter as an argument to the function. We can use that argument inside the function to get the value. It is also possible to use query parameters with path parameters.

The below shown is an example for this:

```javaScript
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
```

When using post request we use the Body() class to convert the request body to python object which we can utilize to create a new book.
Firstly we need to import the Body() from fastapi.
In the argument of the post function we use `variable_name=Body()` . We then use this variable\_name in the function body and get necessary things from the request.

For example:

```javaScript
@app.post('/books/create/')
async def create_new_book(new_book=Body()):
    BOOKS.append(new_book)
    return new_book
```

PUT method is used to update the data, It can have a request body. We access the request body the same way as we used in the POST request.

Example:

```javaScript
@app.put('/books/update')
async def update_book(updated_book=Body()):
    for i in range(len(BOOKS)):
        if BOOKS[i].get('title').casefold() == updated_book.get('title').casefold():
            BOOKS[i] = updated_book
            return {"message":"Book updated"}
    return {"message":"no book found"}
```

DELETE method can also have request bodies but it is not commonly used. Example of DELETE method in fastapi.

```javaScript
@app.delete("/books/delete_book/{book_title}")
async def delete_book_by_title(book_title:str):
    for i in range(len(BOOKS)):
        if BOOKS[i].get('title').casefold() == book_title.casefold():
            BOOKS.pop(i)
            return {"message":"Book Deleted!"}
    return {"message":"Book not found!"}
```

**Pydantics** is a python library used for data modelling, data parsing and it has efficient error handling. Pydantics is commonly used for data validation and how data is coming to our fastapi application. It is commonly used for data validation. We add validation to each field of the request using pydantics. In the controller function we accept the data in the form of pydantics class object and then convert it into the required python object. Pydantics come preinstalled with the fastapi.

We first need to import the BaseModel from pydantics and create a class by extending the BaseModel to access the request from the client. In the controller function argument we can specify the argument's type as the class we created. This will also provide an example schema for us in the swagger. Inside the function to cast the request to the native python object we use
`**pydantic_object.model_dump()`
If we have a model class we can place the above code inside of the constructor. eg:
`new_book = Book(**book_request.model_dump())`
so the entire controller function looks like:

```javaScript
@app.post("/create-book")
async def create_book(book_request: BookRequest):
    new_book = Book(**book_request.model_dump())
    BOOKS.append(new_book)
```

We can add validation to each field by using the Field() class. Inside the parenthesis we can specify the validation properties so that the data from the client is evaluated against this validation logic. If the condition fails an error message is thrown to the client. We can define properties like min\_length, max\_length for string fields. For integer fields gt, lt etc.

**NOTE**: The validation is done before the code execution reaches the fast api controller function.
The complete code looks like:

```javaScript
from pydantic import BaseModel, Field
from typing import Optional
class BookRequest(BaseModel):
    id:Optional[int] = None
    title:str = Field(min_length=3)
    author: str = Field(min_length=1)
    description: str = Field(min_length=1, max_length=100)
    rating: int = Field(gt=0, lt=6)
@app.post("/create-book")
async def create_book(book_request: BookRequest):
    new_book = Book(**book_request.model_dump())
    BOOKS.append(find_book_id(new_book))
```

To add optional fields we import Optional from the typing module and initialize it to None like shown above. In the above code the id is made an optional field. But in the case of inserting only we don't need id. But incase of updating and deleting we may need the id. To add this in swagger we can use:
` id:Optional[int] = Field(description="Id is not required for creating a book, but it is required for updating", default=None)
`This shows the field description in the schemas section.

In the current default setup the swagger shows the example values based on the type of the field. This is not very useful. Pydantic support setting a custom schema for example. For this inside our model class we define an attribute called model\_config.

```javaScript
    model_config = {
        "json_schema_extra":{
            "example":{
                "title":"A new book",
                "author":"John Doe",
                "description":"This is a new book",
                "rating":4
            }
        }
    }
```


The model class now looks like:

```javaScript
class BookRequest(BaseModel):
    id:Optional[int] = Field(description="Id is not required for creating a book, but it is required for updating", default=None)
    title:str = Field(min_length=3)
    author: str = Field(min_length=1)
    description: str = Field(min_length=1, max_length=100)
    rating: int = Field(gt=0, lt=6)
 
    model_config = {
        "json_schema_extra":{
            "example":{
                "title":"A new book",
                "author":"John Doe",
                "description":"This is a new book",
                "rating":4
            }
        }
    }
```

We can add validation for path parameters using Path. For this we need to import Path from fastapi. We can use condition like lt, gt etc. In the function definition where the argument is defined we can use` parameter_name:type=Path(validation_parameters=value)`. Below shown is an example :

```javaScript
from fastapi import FastAPI, Body, Path
@app.get("/books/{book_id}")
async def get_book_by_id(book_id: int = Path(gt=0)):
    for book in BOOKS:
        if book.id == book_id:
            return book
    return {"message": "Book not found"}
```

In the above example if we send a value less than 0 we will get a 422 unprocessable entity status code.

Like we did validation for path parameters we can set validation for query parameters as well. The implementation is also similar to that of query parameters. For this we need to import Query from fastapi, and in the function arguments define the validation logic. The syntax is :
`query_parameter: data_type = Query(validation_expression=value)`
For example:

```javaScript
from fastapi import FastAPI, Body, Path, Query
@app.get("/books-by-rating")
async def get_books_by_rating(rating: int = Query(gt=0, lt=6)):
    print(f"Rating received: {rating}")
    books_with_rating = [book for book in BOOKS if book.rating == rating]
    return books_with_rating
```


Common status code series:
**1xx**: Information response indicates request is processing.

**2xx**: Success request completely successfully.

**3cc**: Redirection, further action needs to be completed.

**4xx**: Client Errors, error was caused by the client.

**5xx**: Server Errors, error occurred on the server.

**200**: Standard response for a successful GET request where data is returned.

**201**: Created, used for creating a new entity is created using POST request.

**204**: No content, Indicates the request is successful, did not create an entity nor return anything, used for PUT requests.


**400**: Bad request cannot process request due to client error. Commonly used for invalid request methods.

**401**: Unauthorized, indicating the client does not have a valid authentication for target resource.

**404**: Not Found, indicates the client requested resource is not found.
**422**: Unprocessable entity, means that there is a semantic error in the request.


**500**: Internal Server Error, generic response for unexpected issues happened in the server.

We use the HttpException class from fastapi to raise the exceptions. For this first import the HttpException class from fastapi.
To raise the exception we use:
`raise HttpException(status_code=http_status_code, detail='exception details')`
fastapi will automatically send the text provided in the message as a JSON object with the HttpStatus code. For example:

```javaScript
@app.get("/books/{book_id}")
async def get_book_by_id(book_id: int = Path(gt=0)):
    for book in BOOKS:
        if book.id == book_id:
            return book
    raise HTTPException(status_code=404, detail="requested book not found")
```

For sending status code to success responses, we need to use a module called starlette. starlette comes pre-installed with fastapi because fastapi is built with starlette. We need to import status from starlette. Then for each route we specify the status\_code parameter after the endpoint name. The status code mentioned here is the status code which gets generated once the request is processed successfully. The syntax is:
`@app.method("url", status_code=status.HTTP_CODE)`
example:

```javaScript
from starlette import status
@app.get("/books", status_code = status.HTTP_200_OK)
async def get_all_books():
    return BOOKS
```

SQL Alchemy is an ORM in python which let's us interact with the database very easily. To install this we need to use : `pip install sqlalchemy`
After this we need to create a database.py file to handle the database related operations. First we need to add the url of sqlite file like : `SQL_ALCHEMY_DATABASE_URL = 'sqlite:///./todo.db'`
To interact with the database we need a database engine, to create the database engine we need to import create\_engine method from the sqlalchemy module.

```javaScript
from sqlalchemy import create_engine
SQL_ALCHEMY_DATABASE_URL = 'sqlite:///./todo.db'
engine = create_engine(SQL_ALCHEMY_DATABASE_URL, connect_args={'check_same_thread':False})
```

The above code creates a connection. the connect\_args key is used to pass additional arguments when connecting. check\_same\_thread is set explicitly to false to restrict the connections to only the threads which created them.

 If a connection is shared by multiple users, the data getting stored and retrieved might become inconsistent due to race conditons. After the above steps we need to create a session. For this we must import the sessionmaker from the sqlalchemy.orm module. Then we need to bind the session with the engine we created. Also, we can pass additional parameters for the session.

```javaScript
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import sessionmaker
SQL_ALCHEMY_DATABASE_URL = 'sqlite:///./todo.db'
engine = create_engine(SQL_ALCHEMY_DATABASE_URL, connect_args={'check_same_thread':False})
LocalSession = sessionmaker(autoflush=False, autocommit = False, bind=engine)
```

This allows us to have complete control over the transactions.

Next, we need to create a database object which we can interact with. for this import declarative\_base from sqlalchemy.ext.declarative. Then create an object from the declarative\_base.

```javaScript
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
 
SQL_ALCHEMY_DATABASE_URL = "sqlite:///./todo.db"
 
engine = create_engine(
    SQL_ALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
LocalSession = sessionmaker(autoflush=False, autocommit=False, bind=engine)
Base = declarative_base()
```

The entire database.py file looks like this. The Base serves as a base for the ORM models which lets us interact with the database.

To create a table, we create a class as a child class of the Base which we created earlier. Inside this class we can use special attributes. Using these attributes, we can set the properties of the table. The `__tablename__ `attribute is used to set the table name in the database.
To create columns in our table we must import the Column and datatype such as Integer from the sqlalchemy. Then inside our model class we need to define the columns of the table like
`column_name= Column(type, constraints)`
if we want to set the column as primary key we can set the `primary_key = True` as an argument to the column object. Similarly, if we want to create an index for the column, we can set `index=True`.
We also have other types like String and Boolean in sqlalchemy. For Boolean we set the value as True or False but, in the database, it is stored as 0 and 1\. The below shown is a complete example for a todo list:

```javaScript
from database import Base
from sqlalchemy import Column, Integer, String, Boolean
 
class Todos(Base):
    __tablename__='todos'
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(String)
    priority = Column(Integer)
    complete = Column(Boolean, default=False)
```

To connect our api with the database we need to create a main file in which we write all our logic. In this page create an instance of fastapi. Then import the engine from the database.py file and models from the models.py. Then we need to bind the Base from models with the engine. When you run the main file in uvicorn it will automatically create the sqlite database.
The code will look like:

```javaScript
from fastapi import FastAPI
import models
from database import engine
 
app = FastAPI()
 
models.Base.metadata.create_all(bind=engine)
```


Once you install sqlite command line tool and add it into system path, we can use the sqlite3 command to open the db file inside our terminal. Once you open the file you can use the` .schema `command to get the database query that was run in the database. You can also use normal queries to run against the database.
` insert into todos(title, description, priority, complete) values ('Go to store','pick up vegetables', 5, False);`
This will insert a record to the todos table. By default when you select the data from the table you get a view like this:

```javaScript
sqlite> insert into todos(title, description, priority, complete) values ('Feed the dog','He is getting hungry', 5, False);
sqlite> select * from todos;
1|Go to store|pick up vegetables|5|0
2|Cut the lawn|grass is getting long|5|0
3|Feed the dog|He is getting hungry|5|0
```

To make it more clean we can use the` .mode column` . This will display the above table like:

```javaScript
sqlite> .mode column
sqlite> select * from todos;
id  title         description            priority  complete
--  ------------  ---------------------  --------  --------
1   Go to store   pick up vegetables     5         0
2   Cut the lawn  grass is getting long  5         0
3   Feed the dog  He is getting hungry   5         0
```

There are various options like markdown, box, table etc which lets you display the data in various ways.

The yield statement is used for dependency management, it indicates that the code including it and prior to it are executed before sending the response. The code executed after the yield statement is executed after the response is delivered. This let's you create a connection for the incoming request, execute the desired operation and close the connection once response is delivered. yield is typically used to setup resources such as database connections, file handles or authentication contexts. The value yielded is injected to the endpoint or other dependencies at the yield statement. The line after the yield statement is typically used for code cleanup.

```javaScript
def get_db():
    db = LocalSession()
    try:
        yield db
    finally:
        db.close()
```

The shown is an example for the yield. Fast api supports dependency injection through this. Dependency Injection means that we need to perform some operation before we execute the current operation.

To implement dependency injection of our database to a route we first need to import Annotated from typing module. Inside that we specify the Session which is imported from sqlalchemy.orm. Then using the Depends() constructor from fastapi we need to pass the connection setup function.
The below shown is an example:

```javaScript
from fastapi import FastAPI, Depends
from database import engine, LocalSession
from typing import Annotated
from sqlalchemy.orm import Session
import models
app = FastAPI()
 
models.Base.metadata.create_all(bind=engine)
 
def get_db():
    db = LocalSession()
    try:
        yield db
    finally:
        db.close()
@app.get("/")
async def get_all_todos(db:Annotated[Session, Depends(get_db)]):
    return db.query(models.Todos).all()
```

We can further simplify the dependency injection code by assigning the Annotated\[Session, Depends(get\_db)\] to a variable and define the type of db using the variable.

```javaScript
db_dependency = Annotated[Session, Depends(get_db)]
 
@app.get("/")
async def get_all_todos(db: db_dependency):
    return db.query(models.Todos).all()
```


To return all the rows of a table we use :

`db.query(ModelName).all()`
To filter particular rows based on column values we can use:
`db.query(ModelName).filter(ModelName.column_name==value)`

to only return the first match we can chain the `.first()` method.

For inserting data into the database, we can create a pydantic request class and add the validation logic. Then for the controller class we need to pass the request as argument like we did before. Then inside the function body create an object of the model class using the constructor and dump the request data using `**request_object.dump()`. Then add the object using add() method on the database object. example:

```javaScript
@app.post("/todo", status_code = status.HTTP_201_CREATED)
async def add_todo_item(db:db_dependency, todo:TodoRequest):
    todo_model = models.Todos(**todo.model_dump())
    db.add(todo_model)
    db.commit()
```

We are explicitly committing because we had set the auto commit to false.

To update an item, we first need to filter the item from the model and then on the reference of the object update the attributes. Finally add the object to the database instance and commit. The example shows the controller function which update an existing todo.

```javaScript
@app.put("/todo/update/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(db:db_dependency, todo:TodoRequest, todo_id:int=Path(gt=0)):
    current_todo = db.query(models.Todos).filter(models.Todos.id == todo_id).first()
    if current_todo is None:
        raise HTTPException(status_code=404, detail="Todo doesnot exist")
    current_todo.title = todo.title
    current_todo.description = todo.description
    current_todo.priority = todo.priority
    current_todo.complete = todo.complete
    db.add(current_todo)
    db.commit()
```

To delete a row using a condition we can filter the records from the model based on the condition and directly call the `.delete()` method. It is always a good idea to ensure that the record is present before deleting. The below example shows the delete method.

```javaScript
@app.delete("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(db:db_dependency, todo_id:int=Path(gt=0)):
    todo_to_delete = db.query(models.Todos).filter(models.Todos.id == todo_id).first()
    if todo_to_delete is None:
        raise HTTPException(status_code=404, detail='Todo not found!')
    db.query(models.Todos).filter(models.Todos.id == todo_id).delete()
    db.commit()
```

After deleting do a commit so that the transaction is saved into the database.
