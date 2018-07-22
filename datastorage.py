# -*- coding: utf-8 -*-

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, UnicodeText, DateTime
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session
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
    UserId = Column('user_id', ForeignKey("user.user_id"), nullable=True)
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
    ContextStart = Column('context_start', Integer)
    ContextWordLen = Column('context_word_len', Integer)

Session = None

class DataStorage:
    USER_ID = 1

    def __init__(self, path_to_db):
        global Session	
        self.engine = create_engine('sqlite:///' + path_to_db)
        Session = scoped_session(sessionmaker(bind=self.engine))

    def create_db(self):
        Base.metadata.bind = self.engine
        Base.metadata.create_all()

    def remove_session(self):
        Session.remove()

    # Settings

    def get_preferences(self):
        result = Session.query(Preference.Settings).filter(Preference.UserId == DataStorage.USER_ID).one_or_none()
        return result[0] if result else None

    def set_preferences(self, preference_string):
        Session.merge(Preference(UserId=DataStorage.USER_ID, Settings=preference_string))
        Session.commit()

    # New words

    def get_new_words(self, start=0, number=100):
        query = Session.query(NewWord.WordId, NewWord.Word, NewWord.WhenAdded,
                                   NewWord.Context, NewWord.ContextStart, NewWord.ContextWordLen,
                                   TextTable.Title, TextTable.Tag) \
                             .filter(NewWord.UserId == DataStorage.USER_ID) \
                             .outerjoin(TextTable, NewWord.TextId == TextTable.TextId)
        if start is not None:
            query = query.offset(start)
        if number is not None:
            query = query.limit(number)
        return query.all()

    def add_new_word(self, word, text_id, context, context_start, context_word_len):
        if self.word_exists(word):
            raise AttributeError(word + ' already added')
        new_word = NewWord(Word=word, UserId=DataStorage.USER_ID, TextId=text_id,
                           WhenAdded=datetime.datetime.utcnow(),
                           Context=context, ContextStart=context_start, ContextWordLen=context_word_len)
        Session.add(new_word)
        Session.commit()
        return new_word.WordId

    def delete_new_word(self, word_id):
        Session.query(NewWord). \
               filter(NewWord.WordId == word_id). \
               filter(NewWord.UserId == DataStorage.USER_ID). \
               delete()

    def word_exists(self, word):
        result = Session.query(NewWord.WordId) \
                             .filter(NewWord.UserId == DataStorage.USER_ID) \
                             .filter(NewWord.Word == word) \
                             .one_or_none()
        return result is not None

    def get_word_number(self):
        result = Session.query(NewWord.WordId) \
                             .filter(NewWord.UserId == DataStorage.USER_ID) \
                             .count()
        return result

    # Text

    def get_all_text_descs(self):
        return Session.query(TextTable.TextId, TextTable.Title,
                                  TextTable.TotalWords, TextTable.UniqueWords).all()

    def get_parsed_text(self, text_id):
        res = Session.query(TextTable.Title, TextTable.ParsedText, TextTable.Glossary). \
                          filter(TextTable.TextId == text_id). \
                          one()
        return res

    def get_parsed_text_no_glossary(self, text_id):
        res = Session.query(TextTable.Title, TextTable.ParsedText). \
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
        tag = kwargs['tag']

        new_text = TextTable(UserId=DataStorage.USER_ID,
                             Title=title, SourceText=source_text, Tag=tag,
                             ParsedText=parsed_text, Glossary=glossary,
                             TotalWords=total_words, UniqueWords=unique_words)
        Session.add(new_text)
        Session.commit()
        return new_text.TextId

    def get_source_text(self, text_id):
        query_res = Session.query(TextTable.Title, TextTable.SourceText, TextTable.Tag). \
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
        tag = kwargs['tag']

        Session.query(TextTable).\
            filter(TextTable.TextId == text_id).\
            update({
                TextTable.Title: title, TextTable.Tag: tag,
                TextTable.SourceText: source_text,
                TextTable.ParsedText: parsed_text, TextTable.Glossary: glossary,
                TextTable.TotalWords: total_words, TextTable.UniqueWords: unique_words})
        Session.commit()

    def delete_text(self, text_id):
        Session.query(TextTable). \
               filter(TextTable.TextId == text_id). \
               delete()


if __name__ == "__main__":
    ds = DataStorage('test.db')
    add_res = ds.add_text(title='title1', source_text='Source text value',
                          parsed_text='<parsed>Source</parsed')
    print(add_res)
