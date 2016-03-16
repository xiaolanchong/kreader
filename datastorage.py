
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class Text(Base):
    __tablename__ = "text"

    TextId = Column('text_id', Integer, primary_key=True)
    #UserId = Column('user_id', Integer, ForeignKey("user.user_id"), nullable=False)
    Title = Column('title', String)
    SourceText = Column('source_text', Text, primary_key=True)
    ParsedText = Column('parsed_text', Text, primary_key=True)

class LookupWord(Base):
    __tablename__ = "lookupword"

    TextId = Column('lookup_id', Integer, primary_key=True)
    Word = Column('word', String)
    Definition = Column('definition')
    Context = Column('context')

class DataStorage:
   def __init__(self):
      self.engine = create_engine('sqlite:///test.db')

   def create_db(self):
      Base.metadata.bind = engine
      Base.metadata.create_all()

   def get_all_texts(self):
      return []

   def get_parsed_text(self, text_id):
      return ''

   def add_text(self, title, source_text, parsed_text):
      pass

   def delete_text(self, text_id):
      pass

