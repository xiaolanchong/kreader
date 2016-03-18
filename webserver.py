# -*- coding: utf-8 -*-

from flask import Flask, jsonify, render_template, redirect, request, abort
from collections import namedtuple
import logging
import json

from ktokenizer import KTokenizer, Paragraph
from ezsajeon import EzSajeon
from datastorage import DataStorage

app = Flask(__name__)

datastorage = DataStorage("../_kreader_files/kreader.db")
datastorage.create_db()

ktokenizer = None
ezsajeon = None

Textdesc = namedtuple('Textdesc', ['id', 'title'])

@app.route("/")
def start_page():
    textdescs = [Textdesc(id=id, title=title) for id, title in datastorage.get_all_text_descs()]
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


    #print(list(request.form.keys()))
    title=request.form['title']
    source_text=request.form['submitted_text']
    sentences = source_text.split('\n')

    parsed_text, glossary = tokenize(ktokenizer, lambda : sentences)
    parsed_text_json = json.dumps(parsed_text)
    glossary_json = json.dumps(glossary)
    datastorage.add_text(title, source_text, parsed_text_json, glossary_json)

    logging.info('Added text: in size=%i, out chunks=%i, sentence#=%i, words#=%i',
                          len(source_text), len(parsed_text),
                          len(sentences), len(glossary.keys()))

   # print('Submitted text: ', title, len(text))

    #return redirect('show_text.html', tokens=tokens, glossary=glossary, title=title)
    return redirect('/')

"""
@app.route("/get_text")
def add_text_page():
    global ktokenizer, ezsajeon
    if ktokenizer is None:
        ezsajeon = EzSajeon()
        ktokenizer = KTokenizer(ezsajeon.get_definition, KTokenizer.MECAB)
    tokens, glossary = get_data(ktokenizer, get_text_from_file)
   # text_json = json.dumps(text_objs, sort_keys=True, indent=3)
    html = render_template('kreader.htm', tokens=tokens, glossary=glossary)
    return html

"""

@app.route("/get_word_definition")
def get_word_definition():
    word = request.args.get('word', '', type=str)
    if(len() == 0):
        return jsonify(records=[])

    definition = ezsajeon.get_definition(word)
    return jsonify(definition=definition)


def get_text_from_file():
    path = '..\_kreader_files\hp1_1.txt'
    with open(path, encoding='utf8') as f:
       for line in f.readlines():
           yield line

def tokenize(ktokenizer, text_getter):
    text_objs = []
    glossary = {}

    for line in text_getter():
            line_objs = ktokenizer.parse(line)
            lookedup_words = ktokenizer.get_lookedup_words()
            glossary.update(lookedup_words)

            text_objs.extend(line_objs)
            text_objs.append(Paragraph())

    if len(text_objs):
        text_objs.pop()

    return [obj.jsonify() for obj in text_objs], glossary


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000, debug=True)