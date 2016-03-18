
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, UnicodeText, Enum
from sqlalchemy.orm import sessionmaker
from sqlalchemy.schema import ForeignKey
import enum

Base = declarative_base()

class Theme(enum.Enum):
   default = 'default'
   noir = 'noir'

class Preference(Base):
    __tablename__ = "preference"

    UserId = Column('user_id', Integer, primary_key=True)
    ThemeEn = Column('theme', String)

class TextTable(Base):
    __tablename__ = "text"

    TextId = Column('text_id', Integer, primary_key=True, autoincrement=True)
    Title = Column('title', String)
    SourceText = Column('source_text', UnicodeText)
    ParsedText = Column('parsed_text', UnicodeText)
    Glossary = Column('glossary', UnicodeText)

class LookupWord(Base):
    __tablename__ = "lookupword"

    LookupId = Column('lookup_id', Integer, primary_key=True, autoincrement=True)
    TextId = Column('text_id', ForeignKey("text.text_id"), nullable=True)
    Word = Column('word', String)
    Definition = Column('definition', String)
    Context = Column('context', String)

class DataStorage:
   def __init__(self, path_to_db):
      self.engine = create_engine('sqlite:///' + path_to_db)
      Session = sessionmaker(bind=self.engine)
      self.session = Session()

   def create_db(self):
      Base.metadata.bind = self.engine
      Base.metadata.create_all()

   def get_preferences():
      pass

   def set_preferences():
      pass

   # Text table

   def get_all_text_descs(self):
      return self.session.query(TextTable.TextId, TextTable.Title).all()

   def get_parsed_text(self, text_id):
      res = self.session.query(TextTable.Title, TextTable.ParsedText, TextTable.Glossary). \
                          filter(TextTable.TextId==text_id). \
                          one()
      return res

   def add_text(self, title, source_text, parsed_text, glossary):
      new_text = TextTable(Title=title, SourceText=source_text, \
                           ParsedText=parsed_text, Glossary=glossary)
      self.session.add(new_text)
      self.session.commit()
      return new_text.TextId

   def delete_text(self, text_id):
      self.session.query(TextTable). \
               filter(TextTable.TextId==text_id). \
               delete()

   def change_title(self, text_id, new_title):
      self.session.query(TextTable). \
                 where(TextId.text_id==text_id).\
                 values(Title=new_title)

   # Lookup table

   def add_lookup(self, text_id, word, definition, context):
      new_lookup = LookupWord(TextId=text_id, Word=word,
                            Definition=definition, Context=context)
      self.session.add(new_lookup)
      self.session.commit()
      return new_lookup.LookupId

   def get_lookups(self, text_id):
      self.session.query(LookupWord.LookupId, LookupWord.Word,
                         LookupWord.Definition, LookupWord.Context). \
                 filter(TextTable.TextId==text_id). \
                 values(Title=text_id)
      return new_text.text_id




if __name__ == "__main__":
    ds = DataStorage()
    #ds.create_db()
    res = ds.add_text('title1', 'Source text value', '<parsed>Source</parsed')
    print(res)