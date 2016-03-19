# -*- coding: utf-8 -*-

from flask import Flask, jsonify, render_template, redirect, request, abort
from collections import namedtuple
import logging
import json

from ktokenizer import KTokenizer, Paragraph, tokenize
from ezsajeon import EzSajeon
from datastorage import DataStorage

app = Flask(__name__)

datastorage = DataStorage("../_kreader_files/kreader.db")
datastorage.create_db()

ktokenizer = None
ezsajeon = None

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
      title, parsed_text_json, glossary = datastorage.get_parsed_text(text_id)

      html = render_template('show_text.htm', tokens=parsed_text_json, glossary=glossary, title=title)
      return html
    abort(404)

@app.route("/submittext", methods=['POST'])
def submit_text():
    global ktokenizer, ezsajeon
    if ktokenizer is None:
        ezsajeon = EzSajeon()
        ktokenizer = KTokenizer(ezsajeon.get_definition, KTokenizer.MECAB)

    title=request.form['title']
    source_text=request.form['submitted_text']
    sentences = source_text.split('\n')

    parsed_text, glossary, total_words, unique_words = tokenize(ktokenizer, lambda : sentences)
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

@app.route("/get_word_definition")
def get_word_definition():
    word = request.args.get('word', '', type=str)
    if(len() == 0):
        return jsonify(records=[])

    definition = ezsajeon.get_definition(word)
    return jsonify(definition=definition)





if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000, debug=True)