# -*- coding: utf-8 -*-

from flask import Flask, jsonify, render_template

from ktokenizer import KTokenizer, Paragraph
from ezsajeon import EzSajeon
import json

app = Flask(__name__)

ktokenizer = None
ezsajeon = None

@app.route("/")
def start_page():
    global ktokenizer, ezsajeon
    if ktokenizer is None:
        ezsajeon = EzSajeon()
        ktokenizer = KTokenizer(ezsajeon.get_definition, KTokenizer.MECAB)
    tokens, glossary = get_data(ktokenizer)
   # text_json = json.dumps(text_objs, sort_keys=True, indent=3)
    html = render_template('kreader.htm', tokens=tokens, glossary=glossary)
    return html

@app.route("/add_text")
def add_text():
    return

@app.route("/get_word_definition")
def get_word_definition():
    word = request.args.get('word', '', type=str)
    if(len() == 0):
        return jsonify(records=[])

    definition = ezsajeon.get_definition(word)
    return jsonify(definition=definition)


def get_data(ktokenizer):
    text_objs = []
    glossary = {}

    path = '..\_kreader_files\hp1_1.txt'
    with open(path, encoding='utf8') as f:
        for line in f.readlines():
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