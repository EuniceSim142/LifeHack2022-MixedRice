
from sqlalchemy import create_engine, Column, Integer, String, Boolean, Float
from sqlalchemy.sql import select, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.schema import PrimaryKeyConstraint
from sqlalchemy.orm import sessionmaker

import os
import pandas as pd
import numpy as np


########## DB Utility Functions

# Create a base for the models to build upon.
Base = declarative_base()

# Session, Engine
def session_engine_from_connection_string(conn_string):
    '''
    Takes in a DB Connection String
    Return a tuple: (session, engine)

    e.g. session, engine = session_engine_from_connection_string(string)
    '''
    if conn_string is None:
        path = os.path.join(
            os.getcwd(), "postgres.db"
        )
        conn_string = "sqlite:///" + path.replace("\\", "\\\\")
    engine = create_engine(conn_string)
    Base.metadata.bind = engine
    DBSession = sessionmaker(bind=engine)
    return DBSession(), engine

# Convert DF into Table Objects
def convert_df_to_lst_of_table_objects(df, Table):
    '''
    Takes in a dataframe (each column name aligned to a DB table's column name)
    and convert it into a list of Table objects
    '''
    return [Table(**{k: v for k, v in row.items() if not np.array(pd.isnull(v)).any()}) for row in df.to_dict("records")]


########## DB Tables

class User(Base):
    __tablename__ = "user"

    uuid = Column(Integer, primary_key=True)
    high_score = Column(Integer)


class Item(Base):
    __tablename__ = "item"

    item_name = Column(String, primary_key=True)
    category = Column(String)
    disposal_instruction = Column(String)
    image_url = Column(String)
    additional_instruction = Column(String)
    is_recyclable = Column(Boolean)
    num_browsed = Column(Integer)

class Bin(Base):
    __tablename__ = "bin"

    id = Column(Integer, primary_key=True)

    latitude = Column(Float)
    longitude = Column(Float)
    location = Column(String)