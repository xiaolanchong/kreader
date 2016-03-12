# -*- coding: utf-8 -*-

from jinja2 import Environment, PackageLoader
import json
from ktokenizer import KTokenizer, Paragraph
from sajeon import Sajeon

env = Environment(loader=PackageLoader('main', 'templates'))
template = env.get_template('kreader.htm')



def get_data(ktokenizer):
    text_objs = []
    with open('hp1_full.txt', encoding='utf8') as f:
        for line in f.readlines():
            line_objs = ktokenizer.parse(line)

            text_objs.extend(line_objs)
            text_objs.append(Paragraph())

    if len(text_objs):
        text_objs.pop()

    return [obj.jsonify() for obj in text_objs]


def get_test_data(ktokenizer):
    source = '프리벳가 4번지에 살고 있는 더즐리 부부는 자신들이 정상적이라는 ' \
             '것을 아주 자랑스럽게 여기는 사람들이었다.'
    return ktokenizer.parse(source)

def main():
    sajeon = Sajeon()
    ktokenizer = KTokenizer(sajeon.get_definition)

    text_objs = get_data(ktokenizer)
    #text_objs = get_test_data(ktokenizer)
    html = template.render(text=json.dumps(text_objs, sort_keys=True, indent=3))
    with open('index.htm', mode='w', encoding='utf8') as f:
        f.write(html)

if __name__ == '__main__':
    main()
