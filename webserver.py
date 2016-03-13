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
        ktokenizer = KTokenizer(ezsajeon.get_definition)
    text_objs = get_data(ktokenizer)
   # text_json = json.dumps(text_objs, sort_keys=True, indent=3)
    html = render_template('kreader.htm', text=text_objs)
    return html

@app.route("/add_text")
def add_text():
    return

def get_data(ktokenizer):
    text_objs = []
    import os.path
    path = '..\_kreader_files\hp1_1.txt'
    with open(path, encoding='utf8') as f:
        for line in f.readlines():
            line_objs = ktokenizer.parse(line)

            text_objs.extend(line_objs)
            text_objs.append(Paragraph())

    if len(text_objs):
        text_objs.pop()

    return [obj.jsonify() for obj in text_objs]


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000, debug=True)