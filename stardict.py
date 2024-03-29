#!/usr/bin/python
# -*- coding: utf-8 -*-
import struct
import gzip


class IfoFileException(Exception):
    """Exception while parsing the .ifo file.
    Now version error in .ifo file is the only case raising this exception.
    """

    def __init__(self, description="IfoFileException raised"):
        """Constructor from a description string.

        Arguments:
        - `description`: a string describing the exception condition.
        """
        self._description = description

    def __str__(self):
        """__str__ method, return the description of exception occured.

        """
        return self._description


class IfoFileReader(object):
    """Read information from .ifo file and parse the information a dictionary.
    The structure of the dictionary is shown below:
    {key, value}
    """

    def __init__(self, filename):
        """Constructor from filename.

        Arguments:
        - `filename`: the filename of .ifo file of stardict.
        May raise IfoFileException during initialization.
        """
        self._ifo = dict()
        with open(filename, "r", encoding="utf8") as ifo_file:
            self._ifo["dict_title"] = ifo_file.readline()  # dictionary title
            line = ifo_file.readline()  # version info
            key, equal, value = line.partition("=")
            key = key.strip()
            value = value.strip()
            # check version info, raise an IfoFileException if error encountered
            if key != "version":
                raise IfoFileException("Version info expected in the second line of {!r:s}!".format(filename))
            if value != "2.4.2" and value != "3.0.0":
                raise IfoFileException("Version expected to be either 2.4.2 or 3.0.0, but {!r:s} read!".format(value))
            self._ifo[key] = value
            # read in other information in the file
            for line in ifo_file:
                key, equal, value = line.partition("=")
                key = key.strip()
                value = value.strip()
                self._ifo[key] = value
            # check if idxoffsetbits should be discarded due to version info
            if self._ifo["version"] == "3.0.0" and "idxoffsetbits" in self._ifo:
                del self._ifo["version"]

    def get_ifo(self, key):
        """Get configuration value.

        Arguments:
        - `key`: configuration option name
        Return:
        - configuration value corresponding to the specified key if exists, otherwise False.
        """
        if key not in self._ifo:
            return False
        return self._ifo[key]


class IdxFileReader(object):
    """Read dictionary indexes from the .idx file and store the indexes in a list and a dictionary.
    The list contains each entry in the .idx file, with subscript indicating the entry's origin index in .idx file.
    The dictionary is indexed by word name, and the value is an integer or a list of integers pointing to
    the entry in the list.
    """

    def __init__(self, filename, compressed=False, index_offset_bits=32):
        """

        Arguments:
        - `filename`: the filename of .idx file of stardict.
        - `compressed`: indicate whether the .idx file is compressed.
        - `index_offset_bits`: the offset field length in bits.
        """
        if compressed:
            with gzip.open(filename, "rb") as index_file:
                self._content = index_file.read()
        else:
            with open(filename, "rb") as index_file:
                self._content = index_file.read()
        self._offset = 0
        self._index = 0
        self._index_offset_bits = index_offset_bits
        self._word_idx = dict()
        self._index_idx = list()
        for word_str_bytes, word_data_offset, word_data_size, index in self:
            word_str = word_str_bytes.decode('utf8')
            self._index_idx.append((word_str, word_data_offset, word_data_size))
            if word_str in self._word_idx:
                if isinstance(self._word_idx[word_str], list):
                    self._word_idx[word_str].append(len(self._index_idx)-1)
                else:
                    self._word_idx[word_str] = [self._word_idx[word_str], len(self._index_idx)-1]
            else:
                self._word_idx[word_str] = len(self._index_idx)-1
        del self._content
        del self._index_offset_bits
        del self._index

    def __iter__(self):
        """Define the iterator interface.

        """
        return self

    def __next__(self):
        """Define the iterator interface.

        """
        if self._offset == len(self._content):
            raise StopIteration
        end = self._content.find(b'\0', self._offset)
        word_str = self._content[self._offset: end]
        self._offset = end+1
        if self._index_offset_bits == 64:
            word_data_offset, = struct.unpack("!I", self._content[self._offset:self._offset+8])
            self._offset += 8
        elif self._index_offset_bits == 32:
            word_data_offset, = struct.unpack("!I", self._content[self._offset:self._offset+4])
            self._offset += 4
        else:
            raise ValueError
        word_data_size, = struct.unpack("!I", self._content[self._offset:self._offset+4])
        self._offset += 4
        self._index += 1
        return word_str, word_data_offset, word_data_size, self._index

    def get_index_by_num(self, number):
        """Get index information of a specified entry in .idx file by origin index.
        May raise IndexError if number is out of range.

        Arguments:
        - `number`: the origin index of the entry in .idx file
        Return:
        A tuple in form of (word_str, word_data_offset, word_data_size)
        """
        if number >= len(self._index_idx):
            raise IndexError("Index out of range! Accessing the {:d} index but totally {:d}"
                             .format(number, len(self._index_idx)))
        return self._index_idx[number]

    def get_index_by_word(self, word_str):
        """Get index information of a specified word entry.

        Arguments:
        - `word_str`: name of word entry.
        Return:
        Index information corresponding to the specified word if exists, otherwise False.
        The index information returned is a list of tuples, in form of [(word_data_offset, word_data_size) ...]
        """
        if word_str not in self._word_idx:
            return False
        number = self._word_idx[word_str]
        index = list()
        if isinstance(number, list):
            for n in number:
                index.append(self._index_idx[n][1:])
        else:
            index.append(self._index_idx[number][1:])
        return index

    def get_all_words(self):
        return self._word_idx.keys() 


class SynFileReader(object):
    """Read infomation from .syn file and form a dictionary as below:
    {synonym_word: original_word_index}, in which 'original_word_index' could be a integer or
    a list of integers.

    """
    def __init__(self, filename):
        """Constructor.

        Arguments:
        - `filename`: The filename of .syn file of stardict.
        """
        self._syn = dict()
        with open(filename, "rb") as syn_file:
            content = syn_file.read()
        offset = 0
        while offset < len(content):
            end = content.find(b"\0", offset)
            synonym_word = content[offset:end]
            offset = end
            original_word_index = struct.unpack("!I", content[offset:offset+4])
            offset += 4
            if synonym_word in self._syn:
                if isinstance(self._syn[synonym_word], list):
                    self._syn[synonym_word].append(original_word_index)
                else:
                    self._syn[synonym_word] = [self._syn[synonym_word], original_word_index]
            else:
                self._syn[synonym_word] = original_word_index

    def get_syn(self, synonym_word):
        """

        Arguments:
        - `synonym_word`: synonym word.
        Return:
        If synonym_word exists in the .syn file, return the corresponding indexes, otherwise False.
        """
        if synonym_word not in self._syn:
            return False
        return self._syn[synonym_word]


class DictFileReader(object):
    """Read the .dict file, store the data in memory for querying.
    """

    def __init__(self, filename, dict_ifo, dict_index, compressed=False):
        """Constructor.

        Arguments:
        - `filename`: filename of .dict file.
        - `dict_ifo`: IfoFileReader object.
        - `dict_index`: IdxFileReader object.
        """
        self._dict_ifo = dict_ifo
        self._dict_index = dict_index
        self._compressed = compressed
        self._offset = 0
        if self._compressed:
            with gzip.open(filename, "rb") as dict_file:
                self._dict_file = dict_file.read()
        else:
            with open(filename, "rb") as dict_file:
                self._dict_file = dict_file.read()

    def get_dict_by_word(self, word):
        """Get the word's dictionary data by it's name.

        Arguments:
        - `word`: word name.
        Return:
        The specified word's dictionary data, in form of dict as below:
        {type_identifier: infomation, ...}
        in which type_identifier can be any character in "mlgtxykwhnrWP".
        """
        result = list()
        indexes = self._dict_index.get_index_by_word(word)
        if not indexes:
            return []
        sametypesequence = self._dict_ifo.get_ifo("sametypesequence")
        for index in indexes:
            self._offset = index[0]
            size = index[1]
            if sametypesequence:
                result.append(self._get_entry_sametypesequence(size))
            else:
                result.append(self._get_entry(size))
        return result
    def get_dict_by_index(self, index):
        """Get the word's dictionary data by it's index information.

        Arguments:
        - `index`: index of a word entry in .idx file.'
        Return:
        The specified word's dictionary data, in form of dict as below:
        {type_identifier: infomation, ...}
        in which type_identifier can be any character in "mlgtxykwhnrWP".
        """
        word, offset, size = self._dict_index.get_index_by_num(index)
        self._offset = offset
        sametypesequence = self._dict_ifo.get_ifo("sametypesequence")
        if sametypesequence:
            return self._get_entry_sametypesequence(size)
        else:
            return self._get_entry(size)

    def get_all_words(self):
        return self._dict_index.get_all_words()

    def _get_entry(self, size):
        result = dict()
        read_size = 0
        start_offset = self._offset
        while read_size < size:
            type_identifier = struct.unpack("!c", self._dict_file[self._offset:self._offset+1])
            if type_identifier in "mlgtxykwhnr":
                result[type_identifier] = self._get_entry_field_null_trail()
            else:
                result[type_identifier] = self._get_entry_field_size()
            read_size = self._offset - start_offset
        return result

    def _get_entry_sametypesequence(self, size):
        start_offset = self._offset
        result = dict()
        sametypesequence = self._dict_ifo.get_ifo("sametypesequence")
        for k in range(0, len(sametypesequence)):
            if sametypesequence[k] in "mlgtxykwhnr":
                if k == len(sametypesequence)-1:
                    result[sametypesequence[k]] = self._get_entry_field_size(size - (self._offset - start_offset))
                else:
                    result[sametypesequence[k]] = self._get_entry_field_null_trail()
            elif sametypesequence[k] in "WP":
                if k == len(sametypesequence)-1:
                    result[sametypesequence[k]] = self._get_entry_field_size(size - (self._offset - start_offset))
                else:
                    result[sametypesequence[k]] = self._get_entry_field_size()
        return result

    def _get_entry_field_null_trail(self):
        end = self._dict_file.find(b'\0', self._offset)
        result = self._dict_file[self._offset:end]
        self._offset = end+1
        return result

    def _get_entry_field_size(self, size=None):
        if size is None:
            size = struct.unpack("!I", self._dict_file[self._offset:self._offset+4])
            self._offset += 4
        result = self._dict_file[self._offset:self._offset+size]
        self._offset += size
        return result


def read_idx_file(filename):
    """

    Arguments:
    - `filename`:
    """
    index_file = IdxFileReader(filename)
    for word_str in index_file._word_idx:
        print (word_str, ": ", index_file.get_index_by_word(word_str))
    for index in range(0, len(index_file._index_idx)):
        print (index, ": ", index_file.get_index_by_num(index)[0])


def read_ifo_file(filename):
    """

    Arguments:
    - `filename`:
    """
    ifo_file = IfoFileReader(filename)
    for key in ifo_file._ifo:
        print(key, " :", ifo_file._ifo[key])


def read_dict_info():
    """
    """
    ifo_file = "stardict-cedict-gb-2.4.2/cedict-gb.ifo"
    idx_file = "stardict-cedict-gb-2.4.2/cedict-gb.idx"
    dict_file = "stardict-cedict-gb-2.4.2/cedict-gb.dict.dz"
    ifo_reader = IfoFileReader(ifo_file)
    idx_reader = IdxFileReader(idx_file)
    dict_reader = DictFileReader(dict_file, ifo_reader, idx_reader, True)
    print(dict_reader.get_dict_by_index(31933))
    print(dict_reader.get_dict_by_word("鼻饲法"))


# read_ifo_file("stardict-cedict-gb-2.4.2/cedict-gb.ifo")
# read_idx_file("stardict-cedict-gb-2.4.2/cedict-gb.idx")
if __name__ == '__main__':
    read_dict_info()
