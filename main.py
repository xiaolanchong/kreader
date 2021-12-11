# -*- coding: utf-8 -*-

from jinja2 import Environment, PackageLoader
import json
from ktokenizer import KTokenizer, Paragraph
from ezsajeon import EzSajeon

env = Environment(loader=PackageLoader('main', 'templates'))
template = env.get_template('word_extraction.htm')


def get_data(ktokenizer):
    text_objs = []
    with open('hp1_1.txt', encoding='utf8') as f:
        for line in f.readlines():
            line_objs = ktokenizer.parse(line)

            text_objs.extend(line_objs)
            text_objs.append(Paragraph())

    if len(text_objs):
        text_objs.pop()

    return [obj.jsonify() for obj in text_objs]


def main():
    ezsajeon = EzSajeon()
    ktokenizer = KTokenizer(ezsajeon.get_definition)

    text_objs = get_data(ktokenizer)
    html = template.render(text=json.dumps(text_objs, sort_keys=True, indent=3))
    with open('index.htm', mode='w', encoding='utf8') as f:
        f.write(html)


if __name__ == '__main__':
    main()
