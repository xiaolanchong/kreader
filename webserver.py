# -*- coding: utf-8 -*-

from flask import Flask, jsonify, render_template, redirect, request, abort, Response
from collections import namedtuple
from io import StringIO
import csv
import re
import logging
import json
import datetime

from ktokenizer import KTokenizer, tokenize
from compositedict import CompositeDictionary
from datastorage import DataStorage
from settings import Settings
from googledict import GoogleDictionary

app = Flask(__name__)

datastorage = DataStorage("../_kreader_files/kreader.db")
datastorage.create_db()

ktokenizer = None
composite_dict = CompositeDictionary(True)
google_dict = GoogleDictionary()

Textdesc = namedtuple('Textdesc', ['id', 'title', 'total_words', 'unique_words'])
Worddesc = namedtuple('Worddesc', ['id', 'word', 'definitions', 'added_min_ago', 'title',
                                   'left_context', 'context_word', 'right_context'])

@app.teardown_request
def remove_session(ex=None):
    datastorage.remove_session()

@app.route("/")
def start_page():
    textdescs = [Textdesc(id=id, title=title,
                          total_words=total_words, unique_words=unique_words) for
                          id, title, total_words, unique_words in datastorage.get_all_text_descs()]
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
        settings = Settings.load(datastorage)
        html = render_template('show_text.htm', tokens=parsed_text_json, glossary='',
                               title=title, text_id=text_id, **settings)
        return html
    else:
        abort(404)


@app.route("/submittext", methods=['POST'])
def submit_text():
    global ktokenizer

    if ktokenizer is None:
        ktokenizer = KTokenizer(KTokenizer.MECAB)

    title=request.form['title']
    source_text=request.form['submitted_text']
    sentences = source_text.split('\n')

    parsed_text, glossary, total_words, unique_words = tokenize(ktokenizer, lambda : sentences)
    glossary = ''
    parsed_text_json = json.dumps(parsed_text)
    glossary_json = json.dumps(glossary)
    datastorage.add_text(title=title, source_text=source_text,
                         parsed_text=parsed_text_json, glossary=glossary_json,
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
      title, text, tag = datastorage.get_source_text(text_id)

      html = render_template('edit_text.htm', text=text, text_id=text_id, title=title, tag=tag)
      return html
    abort(404)


@app.route("/updatetext", methods=['POST'])
def update_text():
    global ktokenizer
    if ktokenizer is None:
        ktokenizer = KTokenizer(KTokenizer.MECAB)

    title = request.form['title']
    text_id = request.form['text_id']  # TODO: process errors
    source_text = request.form['submitted_text']
    tag = request.form['tag']
    sentences = source_text.split('\n')

    parsed_text, glossary, total_words, unique_words = tokenize(ktokenizer, lambda: sentences)
    parsed_text_json = json.dumps(parsed_text)
    glossary = ''
    glossary_json = json.dumps(glossary)
    datastorage.update_text(text_id=text_id, title=title, tag=tag, source_text=source_text,
                            parsed_text=parsed_text_json, glossary=glossary_json,
                            total_words=total_words, unique_words=unique_words)

    logging.info('Update text: in size=%i, out chunks=%i, sentence#=%i, '
                 'total words#=%i, unique words#=%i',
                 len(source_text), len(parsed_text),
                 len(sentences), total_words, unique_words)

    return redirect('/')


@app.route("/settings", methods=['GET'])
def settings():
    args = Settings.load(datastorage)
    html = render_template('settings.htm', **args)
    return html


def get_new_words(start, number):
    for word_id, word, when_added, context, context_start, context_word_len, title, _ in \
            datastorage.get_new_words(start, number):
        added_min_ago = (datetime.datetime.utcnow() - when_added).total_seconds() // 60
        definitions = composite_dict.get_definitions(word)
        if context_word_len and context_start:
            left_context = context[:context_start]
            context_word = context[context_start:context_start+context_word_len]
            right_context = context[context_start+context_word_len:]
        else:
            # fallback mode, no position, try to find
            idx = context.find(word)
            if idx != -1:
                left_context = context[:idx]
                context_word = context[idx:idx + len(word)]
                right_context = context[idx + len(word):]
            else:
                left_context = context
                context_word = ''
                right_context = ''
        yield Worddesc(id=word_id, word=word, added_min_ago=added_min_ago,
                       definitions=definitions, title=title,
                       left_context=left_context, context_word=context_word, right_context=right_context)


@app.route("/new_words")
def new_words():
    start = request.args.get('start', 0, type=int)
    number = request.args.get('number', 20, type=int)
    worddescs = list(get_new_words(start, number))
    total = datastorage.get_word_number()
    html = render_template('new_words.htm', worddescs=worddescs, total=total, start=start)
    return html


# ---------------------------------
# ---------- RESTful API ----------


@app.route('/text/<text_id>', methods=['DELETE'])
def delete_text(text_id):
    datastorage.delete_text(text_id)
    return ''


@app.route("/settings", methods=['PUT'])
def set_settings():
    try:
        Settings.save(datastorage, request.form)
        return ''
    except AttributeError:
        abort(400)


@app.route("/definition/<word>", methods=['GET'])
def word_definition(word):
    if len(word) == 0:
        return jsonify(records=[])

    definitions = composite_dict.get_definitions(word)
    already_added = datastorage.word_exists(word)
    return jsonify(definitions=definitions, already_added=already_added)


@app.route("/new_word/<word>", methods=['PUT', 'DELETE'])
def add_or_delete_new_word(word):
    if request.method == 'DELETE':
        word_id = request.form.get('word_id', None, type=int)
        datastorage.delete_new_word(word_id)
    else:
        text_id = request.form.get('text_id', None, type=int)
        context = request.form.get('context', '')
        context_start = request.form.get('context_start', type=int)
        context_word_len = request.form.get('context_word_len', type=int)
        if len(word) == 0:
            abort(404)

        datastorage.add_new_word(word, text_id, context, context_start, context_word_len)
    return ''


def get_csv_words(start, number):
    re_hanja = re.compile("([\u4E00-\u9FFF-]{2,})", re.MULTILINE | re.UNICODE)
    outbuffer = StringIO()
    writer = csv.writer(outbuffer, dialect='excel', quoting=csv.QUOTE_MINIMAL)
    for _, word, _, context, _, tag in datastorage.get_new_words(start=start, number=number):
        definitions = composite_dict.get_definitions(word)
        definition = '\n'.join(definitions)
        m_hanja = re_hanja.findall(definition)
        hanja = ', '.join(m_hanja)
        writer.writerow([word, hanja, definition, context, tag])
    return outbuffer.getvalue()


@app.route('/download_words', methods=['GET'])
def download_words():
    start = request.form.get('start', None, type=int)
    number = request.form.get('number', None, type=int)
    content = get_csv_words(start, number)
    response = Response(content, mimetype='text/csv')
    response.headers['Content-Type'] = 'application/force-download'
    response.headers['Content-disposition'] = 'attachment; filename=words.csv'
    return response


@app.route('/sound/<word>', methods=['GET'])
def get_sound(word):
    abort(402)
    # sound is broken
    #content, content_type = google_dict.get_sound_file(word, 'ko')

    #response = make_response(content)
    #response.headers['Content-Type'] = content_type
    #return response


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000, debug=True)