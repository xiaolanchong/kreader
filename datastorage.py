# -*- coding: utf-8 -*-

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, UnicodeText
from sqlalchemy.orm import sessionmaker
from sqlalchemy.schema import ForeignKey

Base = declarative_base()


class Preference(Base):
    __tablename__ = "preference"

    UserId = Column('user_id', Integer, primary_key=True)
    Settings = Column('settings', String)  # json string


class TextTable(Base):
    __tablename__ = "text"

    TextId = Column('text_id', Integer, primary_key=True, autoincrement=True)
    Title = Column('title', String)
    SourceText = Column('source_text', UnicodeText)
    ParsedText = Column('parsed_text', UnicodeText)
    Glossary = Column('glossary', UnicodeText)
    TotalWords = Column('total_words', Integer)
    UniqueWords = Column('unique_words', Integer)
    Progress = Column('reading_progress', Integer)


class LookupWord(Base):
    __tablename__ = "lookupword"

    LookupId = Column('lookup_id', Integer, primary_key=True, autoincrement=True)
    TextId = Column('text_id', ForeignKey("text.text_id"), nullable=True)
    Word = Column('word', String)
    Definition = Column('definition', String)
    Context = Column('context', String)


class LearnedWord(Base):
    __tablename__ = "learnedword"

    WordId = Column('word_id', Integer, primary_key=True, autoincrement=True)
    TextId = Column('text_id', ForeignKey("text.text_id"), nullable=True)
    Word = Column('word', String)
    Definition = Column('definition', String)
    Context = Column('context', String)


class DataStorage:
    USER_ID = 1

    def __init__(self, path_to_db):
        self.engine = create_engine('sqlite:///' + path_to_db)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    def create_db(self):
        Base.metadata.bind = self.engine
        Base.metadata.create_all()

    # Settings

    def get_preferences(self):
        result = self.session.query(Preference.Settings).filter(Preference.UserId == DataStorage.USER_ID).one_or_none()
        return result[0] if result else None

    def set_preferences(self, preference_string):
        self.session.merge(Preference(UserId=DataStorage.USER_ID, Settings=preference_string))

    # Learned word

    def get_learned_word(self, word):
        result = self.session.query(LearnedWord.WordId, LearnedWord.Word, LearnedWord.De)

    # Text

    def get_all_text_descs(self):
        return self.session.query(TextTable.TextId, TextTable.Title,
                                  TextTable.TotalWords, TextTable.UniqueWords, TextTable.Progress).all()

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
        progress = 0

        self.session.query(TextTable).\
            filter(TextTable.TextId == text_id).\
            update({
                TextTable.Title: title, TextTable.SourceText: source_text,
                TextTable.ParsedText: parsed_text, TextTable.Glossary: glossary,
                TextTable.TotalWords: total_words, TextTable.UniqueWords: unique_words,
                TextTable.Progress: progress})
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
