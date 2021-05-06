from dataclasses import dataclass
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
import enum

# class LinkType(enum.Enum):
#     public = 'public'
#     auth = 'auth'
#     private = 'private'

Base = declarative_base()

class User(Base):
  __tablename__ = "user"

  id = Column(String, primary_key=True)
  links = relationship("Link")


# marked as dataclass for auto-serialization 
@dataclass
class Link(Base):
  __tablename__ = "link"

  id: int
  creator_id: str
  url: str
  short_id: str
  visibility: str
  counter: int

  id = Column(Integer, primary_key=True)
  creator_id = Column(String, ForeignKey('user.id'), nullable=False)
  url = Column(String, nullable=False)
  short_id = Column(String, nullable=False, unique=True)
  visibility = Column(String, nullable=False)
  counter = Column(Integer, nullable=False)
