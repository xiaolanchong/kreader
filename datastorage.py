# -*- coding: utf-8 -*-

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, UnicodeText, DateTime
from sqlalchemy.orm import sessionmaker
from sqlalchemy.schema import ForeignKey
import datetime

Base = declarative_base()


class User(Base):
    __tablename__ = "user"

    UserId = Column('user_id', Integer, primary_key=True, autoincrement=True)
    Name = Column('name', String, nullable=False)
    Mail = Column('mail', String)
    Password = Column('password', String)
    Salt = Column('salt', String)


class Preference(Base):
    __tablename__ = "preference"

    UserId = Column('user_id', Integer, primary_key=True)
    Settings = Column('settings', String)  # json string


class TextTable(Base):
    __tablename__ = "text"

    TextId = Column('text_id', Integer, primary_key=True, autoincrement=True)
    UserId = Column('user_id', ForeignKey("user.text_id"), nullable=True)
    Title = Column('title', String)
    Tag = Column('tag', String, default='')
    SourceText = Column('source_text', UnicodeText)
    ParsedText = Column('parsed_text', UnicodeText)
    Glossary = Column('glossary', UnicodeText)
    TotalWords = Column('total_words', Integer)
    UniqueWords = Column('unique_words', Integer)


class NewWord(Base):
    __tablename__ = "newword"

    WordId = Column('word_id', Integer, primary_key=True, autoincrement=True)
    UserId = Column('user_id', Integer, ForeignKey('user.user_id'))
    Word = Column('word', String)
    TextId = Column('text_id', ForeignKey("text.text_id"), nullable=True)
    WhenAdded = Column('when_added', DateTime)
    Context = Column('context', String)


class DataStorage:
    USER_ID = 1

    def __init__(self, path_to_db):
        self.engine = create_engine('sqlite:///' + path_to_db)
        sessionMaker = sessionmaker(bind=self.engine)
        self.session = sessionMaker()

    def create_db(self):
        Base.metadata.bind = self.engine
        Base.metadata.create_all()

    # Settings

    def get_preferences(self):
        result = self.session.query(Preference.Settings).filter(Preference.UserId == DataStorage.USER_ID).one_or_none()
        return result[0] if result else None

    def set_preferences(self, preference_string):
        self.session.merge(Preference(UserId=DataStorage.USER_ID, Settings=preference_string))
        self.session.commit()

    # New words

    def get_new_words(self, start=0, number=100):
        query = self.session.query(NewWord.WordId, NewWord.Word, NewWord.WhenAdded, NewWord.Context,
                                   TextTable.Title, TextTable.Tag) \
                             .filter(NewWord.UserId == DataStorage.USER_ID) \
                             .outerjoin(TextTable, NewWord.TextId == TextTable.TextId)
        if start is not None:
            query = query.offset(start)
        if number is not None:
            query = query.limit(number)
        return query

    def add_new_word(self, word, text_id, context):
        if self.word_exists(word):
            raise AttributeError(word + ' already added')

        new_word = NewWord(Word=word, Context=context, UserId=DataStorage.USER_ID, TextId=text_id,
                           WhenAdded=datetime.datetime.utcnow())
        self.session.add(new_word)
        self.session.commit()
        return new_word.WordId

    def delete_new_word(self, word_id):
        self.session.query(NewWord). \
               filter(NewWord.WordId == word_id). \
               filter(NewWord.UserId == DataStorage.USER_ID). \
               delete()

    def word_exists(self, word):
        result = self.session.query(NewWord.WordId) \
                             .filter(NewWord.UserId == DataStorage.USER_ID) \
                             .filter(NewWord.Word == word) \
                             .one_or_none()
        return result is not None

    def get_word_number(self):
        result = self.session.query(NewWord.WordId) \
                             .filter(NewWord.UserId == DataStorage.USER_ID) \
                             .count()
        return result

    # Text

    def get_all_text_descs(self):
        return self.session.query(TextTable.TextId, TextTable.Title,
                                  TextTable.TotalWords, TextTable.UniqueWords).all()

    def get_parsed_text(self, text_id):
        res = self.session.query(TextTable.Title, TextTable.ParsedText, TextTable.Glossary). \
                          filter(TextTable.TextId == text_id). \
                          one()
        return res

    def get_parsed_text_no_glossary(self, text_id):
        res = self.session.query(TextTable.Title, TextTable.ParsedText). \
                          filter(TextTable.TextId == text_id). \
                          one()
        return res

    def add_text(self, **kwargs):
        title = kwargs['title']
        source_text = kwargs['source_text']
        parsed_text = kwargs['parsed_text']
        glossary = kwargs['glossary']
        total_words = kwargs.get('total_words', 0)
        unique_words = kwargs.get('unique_words', 0)

        new_text = TextTable(Title=title, SourceText=source_text,
                             ParsedText=parsed_text, Glossary=glossary,
                             TotalWords=total_words, UniqueWords=unique_words,
                             Progress=0)
        self.session.add(new_text)
        self.session.commit()
        return new_text.TextId

    def get_source_text(self, text_id):
        query_res = self.session.query(TextTable.Title, TextTable.SourceText). \
                          filter(TextTable.TextId == text_id). \
                          one_or_none()
        if query_res is None:
            raise KeyError('Text with key={0} not found'.format(text_id))
        else:
            return query_res

    def update_text(self, **kwargs):
        text_id = kwargs['text_id']
        title = kwargs['title']
        source_text = kwargs['source_text']
        parsed_text = kwargs['parsed_text']
        glossary = kwargs['glossary']
        total_words = kwargs.get('total_words', 0)
        unique_words = kwargs.get('unique_words', 0)

        self.session.query(TextTable).\
            filter(TextTable.TextId == text_id).\
            update({
                TextTable.Title: title, TextTable.SourceText: source_text,
                TextTable.ParsedText: parsed_text, TextTable.Glossary: glossary,
                TextTable.TotalWords: total_words, TextTable.UniqueWords: unique_words})
        self.session.commit()

    def delete_text(self, text_id):
        self.session.query(TextTable). \
               filter(TextTable.TextId == text_id). \
               delete()


if __name__ == "__main__":
    ds = DataStorage('test.db')
    add_res = ds.add_text(title='title1', source_text='Source text value',
                          parsed_text='<parsed>Source</parsed')
    print(add_res)
