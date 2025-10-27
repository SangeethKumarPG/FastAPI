from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# SQL_ALCHEMY_DATABASE_URL = "sqlite:///./todo.db"
# POSTGRES_URL = (
#     "postgresql://postgres:admin%40123@localhost:5432/TodoApplicationDatabase"
# )

MYSQL_URL = "mysql+pymysql://root:admin1234@127.0.0.1:3306/todoapplicationdatabase"
# engine = create_engine(
#     SQL_ALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
# )

# engine = create_engine(POSTGRES_URL)
engine = create_engine(MYSQL_URL)
LocalSession = sessionmaker(autoflush=False, autocommit=False, bind=engine)
Base = declarative_base()
