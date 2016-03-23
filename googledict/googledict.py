# -*- coding: utf-8 -*-

from pprint import pprint

from http.client import  HTTPSConnection
from urllib.parse import quote

import json
import time
import calendar
import re

def get_current_token(request):
    epoch_time = calendar.timegm(time.gmtime())
    return get_stateless_token(request, epoch_time)

def get_stateless_token(request, epoch_time):
    """
    Calculates the token of the given request to send it to the server side
    request:    unicode request string
    epoch_time: number of seconds since 1st Jan, 1970 when the token is calculated
    """
    var_a = request
    MAX_CHAR_SIZE = 4 # UTF16 -> UTF8, in bytes
    var_d  = [None] * len(var_a) * MAX_CHAR_SIZE;
    var_e = 0
    var_f = 0
    while var_f < len(var_a):
        var_char = ord(var_a[var_f])
        if( 128 > var_char):
            var_d[var_e] = var_char
            var_e += 1
        else:
            if( 2048 > var_char ):
                var_d[var_e] = (var_char >> 6) | 192
                var_e += 1
            else:

                if 55296 == (var_char & 64512) and \
                   (var_f + 1) < (len(var_a))  and \
                   56320 == (var_a[var_f+1] & 64512)  :
                    var_f += 1
                    var_char = 65536 + ((var_char & 1023) << 10) + (var_a[var_f] & 1023)
                    var_d[var_e] = (var_char >> 18) | 240
                    var_e +=1
                    var_d[var_e] = (var_char >> 12) & 63 | 128
                    var_e +=1
                else:
                    var_d[var_e] = (var_char >> 12) | 224
                    var_e += 1

                var_d[var_e] = (var_char >> 6) & 63 | 128
                var_e += 1

            var_d[var_e] = (var_char & 63) | 128
            var_e += 1

        var_f += 1

    del var_d[var_e:]

    var_tkk = int(epoch_time//3600)
    var_a = var_tkk

    for var_e in var_d:
        var_a += var_e
        #var_a = &RLVb(var_a)
        var_dr = (var_a<<(10+(64-32)))>>(64-32) #scalar (var_a<<(10+(64-32)))>>(64-32)
        var_a = (var_a + var_dr) & 4294967295
        var_a = (var_a - 4294967296) if (var_a > 2147483647) else var_a #2**31-1 and 2*32 corrections
        var_dr = (4294967296+(var_a)) >> 6 if var_a < 0 else var_a >> 6 #>>>
        if (var_a<0):
            var_a=((4294967296 + var_a) ^ var_dr) - 4294967296
        elif(var_dr<0):
            var_a=((4294967296+var_dr) ^ var_a)-4294967296
        else:
            var_a = var_a ^ var_dr

    var_db = (var_a<<(3+(64-32)))>>(64-32) #scalar (var_a<<(3+(64-32)))>>(64-32)
    var_a = var_a + var_db & 4294967295
    var_db = (2**32+(var_a)) >> 11 if var_a < 0 else var_a >> 11 #>>>
    var_a = var_a ^ var_db
    var_db = (var_a<<(15+(64-32)))>>(64-32) #scalar (var_a<<(15+(64-32)))>>(64-32)
    var_a = var_a + var_db & 4294967295
    var_a = var_a - 4294967296 if var_a > 2147483647  else var_a

    if (0 > var_a):
        var_a = (var_a & 2147483647) + 2147483648

    var_a %= 1000000 #1E6

    return "{0}.{1}".format(var_a,(var_a ^ var_tkk))

class GoogleDictionary():
    def __init__(self):
        host = 'translate.google.com'
        self.connection = HTTPSConnection(host)
        self.empty_comma = re.compile(r',(?=,)')

    def lookup(self, lookedup_word, src_language='ru', dst_language='en'):
        token = get_current_token(lookedup_word)

        url = '/translate_a/single?client=t&sl={0}&tl={1}&hl=en&dt=at&dt=bd&dt=ex&' \
              'dt=ld&dt=md&dt=qca&dt=rw&dt=rm&dt=ss&dt=t&ie=UTF-8&oe=UTF-8&otf=2&' \
              'rom=1&ssel=3&tsel=3&kc=1&tk={2}&q={3}'.format(src_language, dst_language, token, quote(lookedup_word))
        self.connection.request("GET", url)
        response = self.connection.getresponse()
        response_content = response.read().decode('utf8')
        #json_obj = json.loads(self.empty_comma.subn('', response_content)[0].replace(u'\xA0', u' ').replace('[,', '[1,'))
        response_content = response_content.replace(',,', ',"",');
        response_content = response_content.replace(',,', ',"",');
        response_content = response_content.replace('[,', '["",');
        response_content = response_content.replace(',]', ',""]');
        response_content = response_content.replace('\xA0', ' ')
        #fixed_content = self.empty_comma.subn('', response_content)[0].replace('\xA0', ' ')

        return json.loads(response_content)

    def unpack(self, json_obj):
        window_content = json_obj[0]
        if len(json_obj) > 1:
            article_by_pos = json_obj[1]
            defs = {}
            for article in article_by_pos:
                pos = article[0]
                definition = article[1]
                defs[pos] = definition
        else:
            defs = { 'unk', window_content[0][0] }

        return defs

    def get_pronunciation_url(self, word, language):
        secret_token = get_current_token(word)
        url="https://translate.google.com/translate_tts?ie=UTF-8&client=t&tk={0}&tl={1}&q={2}".format(secret_token, language, quote(word))
        return url

    def get_sound_file(self, word, language):
        url = self.get_pronunciation_url(word, language)
        self.connection.request("GET", url)
        response = self.connection.getresponse()
        return response.read()


def main():
    word = '따각따각'
    gdict = GoogleDictionary()
    json = gdict.lookup(word, 'ko', 'en')
    #pprint(json)
    res = gdict.unpack(json)
    print('Final lookup result:')
    pprint(res)

    print(gdict.get_pronunciation_url('오늘', 'ko'))
    f = gdict.get_sound_file('오늘', 'ko')
    open('test.mp3', mode='wb').write(f)


def test_token():
    epoch_time = 1458008272
    assert( get_stateless_token('zen', epoch_time) == '251755.391521' )
    assert( get_stateless_token('longitude', epoch_time) == '767898.891280' )
    assert( get_stateless_token('선', epoch_time) == '735.404693' )
    assert( get_stateless_token('津巴布韦', epoch_time) == '240091.362449' )
    assert( get_stateless_token('протектор', epoch_time) == '513963.129441' )

    epoch_time = 1458030626
    assert( get_stateless_token('протектор', epoch_time) == '48152.430600' )
    assert( get_stateless_token('津巴布韦', epoch_time) == '158069.280421' )
    assert( get_stateless_token('longitude', epoch_time) == '397943.15463' )

if __name__ == '__main__':
    test_token()
    main()
