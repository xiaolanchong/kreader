# -*- coding: utf-8 -*-

from flask import Flask, jsonify, render_template, redirect, request, abort
from collections import namedtuple
import logging
import json

from ktokenizer import KTokenizer, Paragraph, tokenize
from compositedict import CompositeDictionary
from datastorage import DataStorage
from googledict import GoogleDictionary

app = Flask(__name__)

datastorage = DataStorage("../_kreader_files/kreader.db")
datastorage.create_db()

ktokenizer = None
composite_dict = CompositeDictionary(True)
google_dict = GoogleDictionary()

Textdesc = namedtuple('Textdesc', ['id', 'title', 'total_words', 'unique_words'])

@app.route("/")
def start_page():
    textdescs = [Textdesc(id=id, title=title,
                          total_words=total_words, unique_words=unique_words) for
                          id, title, total_words, unique_words, progress in datastorage.get_all_text_descs()]
    html = render_template('main.htm', textdescs=textdescs)
    return html

@app.route("/addtext")
def add_text():
    html = render_template('add_text.htm')
    return html

@app.route("/showtext")
def show_text():
    text_id = request.args.get('id', None, type=int)
    if text_id:
      title, parsed_text_json = datastorage.get_parsed_text_no_glossary(text_id)

      html = render_template('show_text.htm', tokens=parsed_text_json, glossary='', title=title)
      return html
    abort(404)

@app.route("/submittext", methods=['POST'])
def submit_text():
    global ktokenizer

    if ktokenizer is None:
        ktokenizer = KTokenizer( KTokenizer.MECAB)

    title=request.form['title']
    source_text=request.form['submitted_text']
    sentences = source_text.split('\n')

    parsed_text, glossary, total_words, unique_words = tokenize(ktokenizer, lambda : sentences)
    glossary = ''
    parsed_text_json = json.dumps(parsed_text)
    glossary_json = json.dumps(glossary)
    datastorage.add_text(title=title, source_text=source_text, \
                         parsed_text=parsed_text_json, glossary=glossary_json,\
                         total_words=total_words, unique_words=unique_words)

    logging.info('Added text: in size=%i, out chunks=%i, sentence#=%i, '
                 'total words#=%i, unique words#=%i',
                          len(source_text), len(parsed_text),
                          len(sentences), total_words, unique_words)

    return redirect('/')

@app.route("/edittext")
def edit_text():
    text_id = request.args.get('id', None, type=int)
    if text_id:
      title, text = datastorage.get_source_text(text_id)

      html = render_template('edit_text.htm', text=text, text_id=text_id, title=title)
      return html
    abort(404)

@app.route("/updatetext", methods=['POST'])
def update_text():
    global ktokenizer
    if ktokenizer is None:
        ktokenizer = KTokenizer(KTokenizer.MECAB)

    title=request.form['title']
    text_id=request.form['text_id']  # TODO: process errors
    source_text=request.form['submitted_text']
    sentences = source_text.split('\n')

    parsed_text, glossary, total_words, unique_words = tokenize(ktokenizer, lambda : sentences)
    parsed_text_json = json.dumps(parsed_text)
    glossary=''
    glossary_json = json.dumps(glossary)
    datastorage.update_text(text_id=text_id, title=title, source_text=source_text, \
                         parsed_text=parsed_text_json, glossary=glossary_json,\
                         total_words=total_words, unique_words=unique_words)

    logging.info('Update text: in size=%i, out chunks=%i, sentence#=%i, '
                 'total words#=%i, unique words#=%i',
                          len(source_text), len(parsed_text),
                          len(sentences), total_words, unique_words)

    return redirect('/')

@app.route("/set_preferences")
def set_preferences():
    preferences_str = request.args.get('preferences', '', type=str)
    if(len(word)):
        datastorage.set_preferences(preferences_str)


@app.route("/get_word_definition")
def get_word_definition():
    word = request.args.get('word', '', type=str)
    pos  = request.args.get('pos', '', type=str)
    if(len(word) == 0):
        return jsonify(records=[])

    definitions = composite_dict.get_definitions(word)
    pronunciation_url = google_dict.get_pronunciation_url(word, 'ko')
    return jsonify(definitions=definitions, pronunciation=pronunciation_url)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000, debug=True)