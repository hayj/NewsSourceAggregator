import sys, os
sys.path.append("/".join(os.path.abspath(__file__).split("/")[0:-2]))
from sqlalchemy import Column, ForeignKey, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    email = Column(String(250), nullable=False)
    password = Column(String(250), nullable=True)
    token = Column(String(250), nullable=False)
    fb = Column(Boolean(), nullable=False, default=False)
    fb_id = Column(String(250), nullable=True, default=None)


#if __name__ == "__main__":


engine = create_engine('sqlite:///sqlalchemy_example_auth.db')
Base.metadata.create_all(engine)
