# FastAPI
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

In order to perform authentication for users so that each user has access to only their todos, for routing we can create a folder called `router` inside this create a python file for authentication. In this python file we have to import `APIRouter`, which lets us route from our main.py file to authentication python file. Then create an object of APIRouter then, like we used in the main file instead of app use the router object. we define a function to handle this request. Then in the main.py file we need to include this router using from `folder_name import file_name  
`Then include the router for the main app object using `.include_router(file_name.route_name)` method.   
the auth file looks like:

```javaScript
from fastapi import APIRouter
router = APIRouter()
@router.get("/auth/")
async def get_user():
    return {'user':'authenticated'}
```

And in the main file:

```javaScript
from routers import auth
app = FastAPI()
app.include_router(auth.router)
```

By doing the above we can see the endpoint inside the auth.py file in the swagger when we run the main.py file using uvicorn.

Similarly we can create a file to replace our todo logic and utilize the router. so for this we create a separate todos.py file and place all the logic inside that. So the file looks like:

```javaScript
from fastapi import APIRouter
from fastapi import Depends, HTTPException, Path
from pydantic import BaseModel, Field
from database import LocalSession
from typing import Annotated
from sqlalchemy.orm import Session
import models
from starlette import status
router = APIRouter()
def get_db():
    db = LocalSession()
    try:
        yield db
    finally:
        db.close()
db_dependency = Annotated[Session, Depends(get_db)]
class TodoRequest(BaseModel):
    title: str = Field(min_length=3)
    description: str = Field(min_length=3, max_length=100)
    priority: int = Field(gt=0, lt=6)
    complete: bool
```

```javaScript
@router.get("/", status_code=status.HTTP_200_OK)
async def get_all_todos(db: db_dependency):
    return db.query(models.Todos).all()
 
@router.get("/todo-by-id/{todo_id}", status_code=status.HTTP_200_OK)
async def get_todo_by_id(
    db: db_dependency,
    todo_id: int = Path(gt=0, description="id must be greater than 0"),
):
    todo_model = db.query(models.Todos).filter(models.Todos.id == todo_id).first()
    if todo_model is not None:
        return todo_model
    else:
        raise HTTPException(status_code=404, detail="Todo not found")
 
 
@router.post("/todo", status_code=status.HTTP_201_CREATED)
async def add_todo_item(db: db_dependency, todo: TodoRequest):
    try:
        todo_model = models.Todos(**todo.model_dump())
        db.add(todo_model)
        db.commit()
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to add todo")
```

```javaScript
@router.put("/todo/update/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(db: db_dependency, todo: TodoRequest, todo_id: int = Path(gt=0)):
    current_todo = db.query(models.Todos).filter(models.Todos.id == todo_id).first()
    if current_todo is None:
        raise HTTPException(status_code=404, detail="Todo doesnot exist")
    current_todo.title = todo.title
    current_todo.description = todo.description
    current_todo.priority = todo.priority
    current_todo.complete = todo.complete
    db.add(current_todo)
    db.commit()
 
 
@router.delete("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(db: db_dependency, todo_id: int = Path(gt=0)):
    todo_to_delete = db.query(models.Todos).filter(models.Todos.id == todo_id).first()
    if todo_to_delete is None:
        raise HTTPException(status_code=404, detail="Todo not found!")
    db.query(models.Todos).filter(models.Todos.id == todo_id).delete()
    db.commit()
```

Now the main file looks like:

```javaScript
from fastapi import FastAPI
from routers import auth, todos
from database import engine
import models
 
app = FastAPI()
app.include_router(auth.router)
app.include_router(todos.router)
models.Base.metadata.create_all(bind=engine)
```

We need to utilize one to many relationships to establish a relationship between user and their todo items. That is one user may have many todos. To establish the relationship, we need to modify the todos table, we need to add an owner column, which is the foreign key for the user table. The id of the user table will become the value (foreign key) in the owner column. By default, fastapi cannot enhance the structure of a table, so for now we will modify the table manually by deleting the database. and running the project again after making the changes.

First let's create a table inside our models.py file for the users:

```javaScript
class Users(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True)
    user_name = Column(String, unique=True)
    first_name = Column(String)
    last_name = Column(String)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    role = Column(String)
```

Then modify the todos table to add the owner. We need to import the ForeignKey class from the sqlalchemy and use the constructor to create a foreign key reference. To this constructor we pass the table\_name.column\_name as a string. i.e:  
`from sqlalchemy import ForeignKey`  
`owner = Column(Integer, ForeignKey("users.id"))` 

**NOTE**: The request\_object.model\_dump() will not work if the field name of the model and request object are not identical, in that case we need to manually add the data from the request object to each field.

To encrypt the password and save it to the database we use 2 libraries which are bcrypt and passlib. For both of them to work together we use a specific version of bcrypt which is 4.0.1\. The commands to install them are:

```javaScript
pip install passlib
pip install bcrypt==4.0.1
```

**NOTE**: You should use == when installing a specific version of a package.  
To use this first we need to import CryptoContext from passlib.context. Then create an object of CryptoContext with bcrypt scheme.  
The code will look like:

```javaScript
from passlib.context import CryptoContext
bycrypt_context = CryptoContext(schemes=['bcrypt'], deprecated='auto')
```

to hash the value of password we use `bcrypt_context.hash(password)`

In the controller function:

```javaScript
create_user_model = Users(
        email = user.email,
        user_name = user.username,
        first_name = user.first_name,
        last_name = user.last_name,
        hashed_password = bcrypt_context.hash(user.password),
        role = user.role,
        is_active = True
    )
```

Here we don't know the bcypt hash used for encrypting the password. Only the encrypted text is stored in the database. When authenticating the user, we accept the user's password and compare it with using bcrypts verify method. If it returns true the user is authenticated. Else the user is not authenticated.  
eg:  
`bcrypt_context.verify(password, user.hashed_password)`  
For every file in the router, we need to add dependency injection code.

After following the previous steps, we need an endpoint to authenticate the user. We are going to user JWT authentication. For this first we need to install `python-multipart` module. We will not be using normal forms. We will be using OAuth2 password request form.   
To utilize this we need to import OAuth2PasswordRequestForm from fastapi. We then need to use dependency injection for the login endpoint.

```javaScript
from fastapi.security import OAuth2PasswordRequestForm
@router.post("/token/")
async def login_for_refresh_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db:db_dependency):
        return 'token'
```

The above shown is a skeleton structure for the api endpoint. This will show a particular form with multiple fields in the swagger. In this form we only need to send the username and password.   
To authenticate the user we can use a helper function, which takes the username and password and authenticate the user. It looks like:

```javaScript
def authenticate_user(username:str, password:str, db):
    user = db.query(Users).filter(Users.username == username).first()
    if not user:
        return False
    if not bcrypt_context.verify(password, user.hashed_password):
        return False
    return True
```

We can call this function inside the token generation endpoint using:  
`user = authenticate_user(form_data.username, form_data.password, db)`   

**JWT (JSON WEB TOKEN)** is a way to securely transmitting the data between two or more parties using a Json object. Each JWT can be trusted because they can be digitally signed which allows the server to know if the JWT has been changed at all by the client. **JWT is an authentication method.** When the client provides the credentials for login to the server the server returns a text which has the information about the user. By default, the content in the json token is not encryped i.e anyone can read the contents. If we want to make is secure we need to encrypt it. With each request to the server the client sends the JWT token to identify itself to the server, the server verifies this token and determines whether to proceed with the request or not.  
A JWT token has 3 parts separated by . They are:

1\. Header: The header has 2 parts, the algorithm for signing and type of token. The jwt header is encoded into base64 to make the first part of JWT token

  
2\. Payload: The payload consists of data. This data contains claims. There are 3 types of claims.

* Registered: Claims that are predefined, they are recommended but not mandatory. The top 3 registered claims are  
   1. ISS : Issuer, this identified the issuer who issued the JWT  
   2. SUB: Subject, It holds the statements about the subjects. The subject value must be scoped either locally or globally unique. It is like an ID for the json webtoken.  
   3. EXP: Expiration time, this claim makes sure that the current date and time is before the expiration date and time of token. Expiration is not mandatory but useful. One careful thing to note is make the token always expire after certain amount of time. Otherwise, anyone with the token will have access.  
   The payload is also encoded to base64 to create the second part of the JWT.
* Public
* Private

3\. Signature: Created by using the algorithm in the header to encode the header and payload with a secret. The secret can be any text that is stored inside of the server.

The JWT signature looks like:

```javaScript
HMACSHA256(
  base64UrlEncode(header) + "." + base64UrlEncode(payload),
  secret
)
```

The JSON webtoken string is completely unique to the client that has been authenticated.  
Usually, the authenticated user sends this JWT token in **authorization** header using the **bearer** schema. The JWT is safe as long as the client does not know the secret key. Even though we can easily decode the JWT token and see the data we cannot change it. If we change something in the payload and send it to the server, the server can easily identify that something is changed in the token because when verifying it will not be able to pass the integrity check.

**NOTE**: Two separate servers can authenticate the same user with the same JWT token if they use the same secret key and algorithm  
JWT's are popular in modern microservices arhitecture.

To generate JWT token we need to first install a python package which is "python-jose\[cryptography\]". The command is :  
`pip install "python-jose[cryprography]"`   
Then import the jwt from jose module. Then we need to set a secret and an algorithm. To create a random hex 32 bit string we can use the openssl command line tool. If we are using windows package managers like scoop or chocolatey we can directly install with the `scoop install openssl `

command. The command to generate secret key is :

`openssl rand -hex 32` 

After generating the key set the returned value to a string. The next step is to specify the algorithm. We use **HS256** commonly for generating the jwt token. The secret and the algorithm will work together to have a unique signature to make sure that JWT is secured and authorized. After this we can create a helper function to accept the username, userid and a time delta which sets the expiration of the token. We then encode this information using the secret key and algorithm.

The helper function looks like:

```javaScript
from datetime import timedelta, datetime, timezone
from jose import jwt
 
SECRET_KEY = 'my_random_secret_key'
ALGORITHM = 'HS256'
def create_access_token(username:str, user_id:int, expires_delta:timedelta):
    encode = {'sub':username, 'id:user_id'}
    expires = datetime.now(timezone.utc) + expires_delta
    encode.update({'exp':expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)
```

We can call this function in our authentication endpoint to generate the token and return this token to the client.

`return create_access_token(username=user.user_name, user_id=user.id, expires_delta=timedelta(minutes=20))` .   
Our current token endpoint looks like:

```javaScript
class Token(BaseModel):
    access_token:str
    token_type:str
 
@router.post("/token/", response_model=Token)
async def login_for_refresh_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db:db_dependency):
        user = authenticate_user(form_data.username, form_data.password, db)
        if not user:
            return 'Failed to authenticate user'
        token_str = create_access_token(username=user.user_name, user_id=user.id, expires_delta=timedelta(minutes=20))
        return{
            "access_token":token_str,
            "token_type":"bearer"
        }
```

Here we created a response model for sending the jwt token to the client, we can set a response model in the routing annotation using the **response\_model** parameter.

jwt.io is a website which lets us see the information in the jwt token. We can paste the jwt token and see the details of the token.

Decoding a jwt is the only way to authenticate a jwt. When the user logs in we create send a jwt token with the user id. Then for each endpoint which requires authentication we pass the jwt token. This jwt token is decoded to authenticate the user. To enable jwt decoding we first need to import `OAuth2PasswordBearer `from fastapi.security module. We then need to pass the token url to this constructor. We then define a utility function for other api endpoints to verify the user. The function will have 2 arguments, the bearer token which is an Annotated type of string and depends upon the oauth bearer object. Then inside the function body we extract the payload by using the jwt.decode() method. To this method we pass token, secret key and the algorithms (as a list) as argument. From this payload we extract the subject which is in sub key, and the user id in the id key.

We also can JWTError when there are exceptions in decoding the JWT. For this import JWTError from jose. The utility function now looks like:

```javaScript
async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_name:str = payload.get('sub')
        user_id:int = payload.get('id')
        if user_id is None or user_name is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Unauthorized')
        return {"username":user_name, "id":user_id}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Unauthorized')
```

We can add prefix and tag for the api files so that we can distinctly identify them. For this we need to pass the prefix and tag parameter to the APIRouter() constructor. eg:

```javaScript
router = APIRouter(
    prefix='/auth',
    tags=['auth']
)
```

After we make this change, we can remove the auth from the api route for the auth requests. Also, we need to change the token url in:  
`oauth2_bearer = OAuth2PasswordBearer(tokenUrl="auth/token")` 

We can use the` get_current_user()` function defined in our auth.py file to authenticate user with jwt. Then we need to inject the dependency to our to-do routes.  
`user_dependency = Annotated[dict, Depends(get_current_user)]  
`The create todo function looks like:

```javaScript
@router.post("/todo", status_code=status.HTTP_201_CREATED)
async def add_todo_item(user:user_dependency, db: db_dependency, todo: TodoRequest):
    if user is None:
        raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED, detail = 'Authentication failed')
    try:
        todo_model = models.Todos(**todo.model_dump(), owner_id = user.get('id'))
        db.add(todo_model)
        db.commit()
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to add todo")
```

  
We can similarly add this to all the todo routes. Now the get all todos will look like:

```javaScript
@router.get("/", status_code=status.HTTP_200_OK)
async def get_all_todos(user: user_dependency,db: db_dependency):
     if user is None:
          raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED, detail = 'Authentication failed')
    return db.query(models.Todos).filter(models.Todos.owner_id == user.get('id')).all()
```

We can chain multiple filters together. eg: ` todo_model = db.query(models.Todos).filter(models.Todos.id == todo_id).filter(models.Todos.owner_id == user.get('id')).first()`

The updated get todo by id function looks like:

```javaScript
@router.get("/todo-by-id/{todo_id}", status_code=status.HTTP_200_OK)
async def get_todo_by_id(
    user: user_dependency,
    db: db_dependency,
    todo_id: int = Path(gt=0, description="id must be greater than 0"),
):
    if user is None:
        raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED, detail = 'Authentication failed')
    todo_model = db.query(models.Todos).filter(models.Todos.id == todo_id).filter(models.Todos.owner_id == user.get('id')).first()
    if todo_model is not None:
        return todo_model
    else:
        raise HTTPException(status_code=404, detail="Todo not found")
```

Now the update todo mehtod looks like:

  
```javaScript
@router.put("/todo/update/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(user: user_dependency,db: db_dependency, todo: TodoRequest, todo_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED, detail = 'Authentication failed')
    current_todo = db.query(models.Todos).filter(models.Todos.id == todo_id).filter(models.Todos.owner_id == user.get('id')).first()
    if current_todo is None:
        raise HTTPException(status_code=404, detail="Todo doesnot exist")
    current_todo.title = todo.title
    current_todo.description = todo.description
    current_todo.priority = todo.priority
    current_todo.complete = todo.complete
    db.add(current_todo)
    db.commit()
```

The delete method will now look like:

```javaScript
@router.delete("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(user:user_dependency, db: db_dependency, todo_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED, detail = 'Authentication failed')
    todo_to_delete = db.query(models.Todos).filter(models.Todos.id == todo_id).filter(models.Todos.owner_id == user.get('id')).first()
    if todo_to_delete is None:
        raise HTTPException(status_code=404, detail="Todo not found!")
    db.query(models.Todos).filter(models.Todos.id == todo_id).delete()
    db.commit()
```

To identify the admin from other users we can also encode the role of the user with jwt. We also need to get the user role when decoding the jwt token. Then we can create a separate router for admin. In this we can provide an endpoint to get all the todos and delete a tpdo of any user based on the todo id. The admin router will look like:

```javaScript
from sys import prefix
from fastapi import APIRouter
from fastapi import Depends, HTTPException, Path
from pydantic import BaseModel, Field
from database import LocalSession
from typing import Annotated
from sqlalchemy.orm import Session
import models
from starlette import status
from .auth import get_current_user
 
router = APIRouter(
    prefix="/admin",
    tags=["admin"]
)
 
 
def get_db():
    db = LocalSession()
    try:
        yield db
    finally:
        db.close()
 
 
db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]
 
@router.get("/todo", status_code=status.HTTP_200_OK)
async def read_all(user:user_dependency, db:db_dependency):
    if user is None or user.get('role')!='admin':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Not authorized')
    return db.query(models.Todos).all()
```

```javaScript
    
@router.delete("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(user:user_dependency, db:db_dependency, todo_id:int = Path(gt=0)):
    if user is None or user.get('role') != 'admin':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='not authorized')
    todo_model = db.query(models.Todos).filter(models.Todos.id == todo_id).first()
    if todo_model is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Todo not found')
    db.query(models.Todos).filter(models.Todos.id == todo_id).delete()
    db.commit()
```

Similarly, we can create a router to handle the users. The user route will look like:

```javaScript
from posixpath import curdir
from fastapi import APIRouter
from fastapi import Depends, HTTPException, Path
from pydantic import BaseModel, Field
from database import LocalSession
from typing import Annotated
from sqlalchemy.orm import Session
import models
from starlette import status
from .auth import bcrypt_context, get_current_user
 
router = APIRouter(
    prefix="/users",
    tags=["Users"],
)
 
def get_db():
    db = LocalSession()
    try:
        yield db
    finally:
        db.close()
 
class ChangePassword(BaseModel):
    old_password: str = Field(min_length=8, max_length=36)
    new_password: str = Field(min_length=8, max_length=36)
 
db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]
 
```

```javaScript
@router.get("/me/", status_code=status.HTTP_200_OK)
async def get_my_information(user: user_dependency, db:db_dependency):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    current_user = db.query(models.Users).filter(models.Users.id == user.get("id")).first()
    if current_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return current_user
    
```

```javaScript
@router.put("/change_password/", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(user:user_dependency, db:db_dependency, password_change: ChangePassword):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    current_user = db.query(models.Users).filter(models.Users.id == user.get("id")).first()
    if current_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if not bcrypt_context.verify(password_change.old_password, current_user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    current_user.hashed_password = bcrypt_context.hash(password_change.new_password)
    db.add(current_user)
    db.commit()
```

SQLite is suitable for individual devices where only local storage of data is needed. It is a simple, economical and efficient database for these purposes. For small and medium size applications, it works well. MySQL and Postgres SQL are commonly used production databases. They focus on concepts such as scalability, concurrency and control. They are only suitable where you have thousands of users. If your application has a limited number of users, you can choose SQLite. If it is beginning to scale you can always easily to switch to a production database such as Postgres or MySQL. SQLite is a file-based database, which means that the entire database is stored as a file along with the code. For production databases they have a dedicated server and port, you need to make sure that the database is running, and you have authentication linking to the DBMS. For production databases separate deployment is required for the DBMS.

PostgreSQL is a production ready open-source relational database management system. It is secure, scalable and requires a server. 

After installing PostgreSQL, we need to open pgadmin and login with the password you set during the installation. Then register a new server by right clicking on the servers tab. You will be shown an option to configure the server by setting the name and choosing the server group. There is a default servers' group which we can choose for now. Then navigate to the connection tab and choose a hostname which is localhost. Then choose a username and password. The default username is Postgres. The server group will store databases, login and group roles. The first thing we need to check after creating a server is check if you have a superuser in the login and group roles. You can view the privileges of the super user by right-clicking on the super user and clicking on the properties. The super user will have complete privileges in the database.

If you want, you can create a new user or role by right clicking on the login/group roles tab and clicking on create, then we can set up the details of a new user and configure the privileges. To create a database, we can right click on the database and set a database name and owner. By default, when you create a database, you are automatically connected to the database, if you are not connected you can right click on the database and click on the connect option.

After creating the database under schemas, we can see the tables in the database. We need to create the tables inside of this. Alternatively, we can the query tool by clicking on the database icon beside the filter icon in the object explorer tab or user the keyboard shortcut of `alt+shift+q` . This will also open a query editor where you can run the SQL queries to do all kinds of operations in the database. 

We can use the below queries to create tables. 

```javaScript
DROP TABLE IF EXISTS todos;
 
CREATE TABLE users (
id SERIAL,
email VARCHAR(200) DEFAULT NULL,
user_name VARCHAR(45) DEFAULT NULL,
first_name VARCHAR(45) DEFAULT NULL,
last_name VARCHAR(45) DEFAULT NULL,
hashed_password VARCHAR(200) DEFAULT NULL,
is_active boolean DEFAULT NULL,
role VARCHAR(45) DEFAULT NULL,
PRIMARY KEY(id)
);
 
DROP TABLE IF EXISTS todos;
CREATE TABLE todos(
id SERIAL,
title VARCHAR(200) DEFAULT NULL,
description VARCHAR(200) DEFAULT NULL,
priority INTEGER DEFAULT NULL,
complete boolean DEFAULT NULL,
owner_id INTEGER DEFAULT NULL,
PRIMARY KEY(id),
FOREIGN KEY(owner_id) REFERENCES users(id)
);
```

The SERIAL type in Postgres is an integer type that auto increments. VARCHAR datatype is similar to varchars in other databases; it says that we are storing a string of fixed length in this.

To connect our fast Api application with the Postgres database we need to install a python package. We can install that using:

`pip install psycopg2-binary`   
Then in our database.py file we need to change the database URL. The format for creating the URL is:

`postgres://username:password@hostname/database_name`  
Our connection string looks like:

`postgres://postgres:admin%401234@localhost/TodoApplicationDatabase` 

For postgres we don't need to specify the connect\_args paramaters when creating the engine.   
**NOTE: If your password has @ characters you need to user %40 instead.**

**NOTE: The default port of Postgres is 5432**

MySQL is an opensource data management system, it requires a server. It is a production ready database.

To install MySQL on windows we need to download the mysql community installer. You can install the 32-bit installer which is available even if your system is 64 bits. After opening the installer choose the full installtation. Follow the steps in the installation screen. You will be asked to choose the server configuration such as port number once all the dependent packages are installed. You can leave it to default. Then you will be asked to setup a password. Set up an admin user with role as DBAdmin and set the password.

After installation of MySQL you can start up the MySQL workbench and login using the credentials, you have configured during the setup. Then to create a database/schema on the left side tab click on the schemas tab and right click to create a new schema, by default MySQL allows only small case letters in the schema name, so create a name for the schema and click on apply.

```javaScript
use todoapplicationdatabase;
DROP TABLE IF EXISTS `users`;
 
CREATE TABLE `users` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `email` varchar(200) DEFAULT NULL,
  `user_name` varchar(45) DEFAULT NULL,
  `first_name` varchar(45) DEFAULT NULL,
  `last_name` varchar(45) DEFAULT NULL,
  `hashed_password` varchar(200) DEFAULT NULL,
  `is_active` int(1) DEFAULT NULL,
  `role` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=latin1;
 
DROP TABLE IF EXISTS `todos`;
 
CREATE TABLE `todos` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `title` varchar(200) DEFAULT NULL,
  `description` varchar(200) DEFAULT NULL,
  `priority` int(1) DEFAULT NULL,
  `complete` int(1) DEFAULT NULL,
  `owner_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  FOREIGN KEY (`owner_id`) REFERENCES users(`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=latin1;
```

Use the above script in the query tab and execute it to create tables for our application.

You can also use the GUI to create tables which will give the above scripts.

To connect our fast api application with the MySQL database we need to use a package called `pymysql` . To install this, we can use `pip install pymysql` . The connection string for the database is:

`mysql+pymysql://user:password@hostname:port_number/database_name`

So, the connection string will look like:

```javaScript
MYSQL_URL =(
    "mysql+pymysql://root:admin1234@127.0.0.1:3306/todoapplicationdatabase"
)
```

and change the url of the database inside the create\_engine function like we did for Postgres.

**Alembic** is a lightweight database migration tool which is used along with SQL alchemy. Migration tools allow us to plan, transfer and upgrade resources within databases. Alembic allows you to change a SQL Alchemy database table after it has been created. Currently SQL Alchemy will only create new database tables for us, not enhance any. If we want to modify any table, we need to delete the entire table and then run our application where SQL alchemy will create a new table. By doing this all the previous data will be gone. Alembic provides the creation and invocation of change management scripts. This allows you to be able to create migration environments and be able to change data however you like. 

Alembic is a powerful migration tool that allows us to modify our database schemas. As our application evolves, our database will need to evolve as well. Alembic helps us to be able to keep modifying our database to keep up with the rapid development requirements. We will be using alembic on tables that already have data in them. This allows us to be able to continually create additional content that works within our application.

We need to install alembic to use it in our project. For this we use:

`pip install alembic` 

Once you install alembic in our project we can use alembic commands inside our project.

1\. `alembic init folder_name` : Initializes a new environment. 

2\. `alembic revision -m 'message'` : Creates a new revision for the environment. This is where we will have all the scripts that change and migrate our database. This will generate a unique revision id. 

3\. `alembic upgrade revision_id` : We can make the changes to the database by using this command and the revision id that was generated during the alembic revision command. This will enhance our database. 

4\. `alembic downgrade -1`: The opposite of upgrade. This will downgrade our migration to our database.

Once we initialize alembic we can see a `alembic.ini` file and an alembic directory. These are created automatically by alembic and keep the data integrity of the application.   
`alembic.ini` is the file which it will look for once we invoke alembic. It is the configuration file for alembic specific project. The `alembic directory` has all the environmental properties for alembic. It holds all the revisions of your application. This is where we call the migrations for upgrading and downgrading. 

To set up alembic first install alembic with pip command. Then initialize alembic using:

`alembic init folder_name`   
for example `alembic init alembic` where alembic is the folder name which I use. After this we can see the alembic folder and alembic.ini file in the project root. When you open the alembic.ini file you can see various configuration options. Inside this we need to modify SQL alchemy database URL to our database URL.

The alembic folder has various sub folders. The versions folder will have the various versions for upgrading and downgrading the database. Inside the alembic folder we need to open the env.py file and import the models. Then We need to assign our models.Base.metadata to target\_metadata. It will be by default set to None. We need to modify it.  
so the line will look like:  
`target_metadata = models.Base.metadata` 

If we want logging we need to remove the if condition from this:

```javaScript
if config.config_file_name is not None:
    fileConfig(config.config_file_name)
```

Alembic revision is how we create a new alembic file where we can add some type of database upgrade. For example, when we run   
`alembic revision -m "create phone number on users table"`   
This will create a new file where we can write the upgrade code. It will also have revision id along with the file.   
Alembic upgrade is how we actually run the migration. Inside the created file we can write an upgrade function which return None. For example if we want to add a phone number column, we must add the column in the models and then we can use:

```javaScript
def upgrade() -> None:
    op.add_column('users', sa.Column('phone_number', sa.String(), nullable=True)
```

This will create a new phone number column in our user's table. 

**NOTE**: All the previous data will not change when we run an alembic upgrade.  
To make the changes permanent we can run `alembic upgrade revision_id` . This will successfully implement the change in the upgrade functionality.

We can create a downgrade function which is the opposite of upgrade function. For example, if we want to drop the phone number column from the users table we can use:

```javaScript
def downgrade() -> None:
    op.drop_column('users', 'phone_number')
```

This code will revert our database to remove the last migration change. Previous data in the table will not change unless it is in the phone number column (since we are removing the column altogether).  
To downgrade a migration we can use:

`alembic downgrade -1` 

This will revert to the last migration. 

```javaScript
"""creating phone_number field in users
 
Revision ID: db4fc2a6cee6
Revises: 
Create Date: 2025-10-28 07:17:04.711702
 
"""
from typing import Sequence, Union
 
from alembic import op
import sqlalchemy as sa
 
 
# revision identifiers, used by Alembic.
revision: str = 'db4fc2a6cee6'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None
 
 
def upgrade() -> None:
    """Upgrade schema."""
    pass
 
 
def downgrade() -> None:
    """Downgrade schema."""
    pass
```

This is what a file will look like after creating a revision.

If you don't define the downgrade operation there is no way you can revert back the changes you performed in the upgrade. If you define a downgrade function we can directly call the `alembic downgrade -1` command. Below shown is the complete revision file:

```javaScript
"""creating phone_number field in users
 
Revision ID: db4fc2a6cee6
Revises: 
Create Date: 2025-10-28 07:17:04.711702
 
"""
from typing import Sequence, Union
 
from alembic import op
import sqlalchemy as sa
 
 
# revision identifiers, used by Alembic.
revision: str = 'db4fc2a6cee6'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None
 
 
def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('users', sa.Column('phone_number', sa.String(length=15), nullable=True))
 
 
def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('users', 'phone_number')
```

  
**NOTE:** We are using alembic to enhance the existing tables. If you don't have a table, you can just define a new model in SQL Alchemy and this will create a new table by default when running your application.