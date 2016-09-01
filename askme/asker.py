from __future__ import print_function
import sys
from contextlib import contextmanager
import re
from six import moves
from colorama import Fore, Back, Style, Cursor

ANSI_ESC_REGEX = re.compile(r'(\x9B|\x1B\[)[0-?]*[ -\/]*[@-~]')


class Asker(object):
    QUERY_ENDS = (':', '?')
    DEFAULT_FORMAT = ' [{}]'

    def __init__(self, writer=None):
        self.writer = writer or Writer()

    def format_query(self, query, default):
        """Format a query that has a default value."""
        if default is not None:
            for query_end in self.QUERY_ENDS:
                if query.rstrip().endswith(query_end):
                    cut = query.rindex(query_end)
                    query = ''.join((
                        query[:cut],
                        self.DEFAULT_FORMAT.format(default),
                        query[cut:]
                    ))
                    return query
        return query

    def ask(self, query, default=None, type=str, choices=None, labels=None):
        if choices:
            raise NotImplemented
        else:
            return self.ask_input(query, default=default, type=type)

    # Specific question types

    def ask_input(self, query, default=None, type=str):
        """Simply ask for user input: compatible with builtin `raw_input`."""
        query = self.format_query(query, default)
        while True:
            answer = self.writer.input(query)
            if not answer and default is not None:
                return default

            try:
                answer = type(answer)
            except Exception as err:
                print(err.args[0], file=sys.stderr)
                continue
            else:
                return answer


class LineBlock(object):
    def __init__(self, writer=None):
        self.writer = writer or Writer()
        self.pos = 0
        self.lens = list()

    def __enter__(self):
        self.pos = 0
        self.lens = list()
        return self

    def __exit__(self, type, value, tb):
        self.print_at(len(self.lens), '')

    def clear(self):
        for i in range(len(self.lens)-1, -1, -1):
            self.print_at(i, '')

    def print_at(self, line, text, clear=True):
        newlen = len(strip_ansi_escape(text))
        while line >= len(self.lens):
            self.lens.append(0)
        oldlen = self.lens[line]
        if clear:
            self.lens[line] = newlen
            if oldlen > newlen:
                text += ' ' * (oldlen - newlen)
        elif newlen > oldlen:
            self.lens[line] = newlen
        while not self.lens[-1]:
            self.lens.pop()
        rel = line - self.pos
        if rel > 0:
            self.writer.down(rel)
        elif rel < 0:
            self.writer.up(rel)
        self.writer.print(text)
        self.writer.up(2)
        self.writer.print('')
        self.pos = line


class Writer(object):
    def __init__(self):
        pass

    def up(self, count):
        self.print(Cursor.UP(count), end='')

    def down(self, count):
        self.print(Cursor.DOWN(count), end='')

    def input(self, query):
        return moves.input(query)

    def print(self, *args, **kwargs):
        return print(*args, **kwargs)

    def error(self, *args, **kwargs):
        kwargs.update(file=sys.stderr)
        return print(*args, **kwargs)

    def clear(self):
        pass


class Highlighter(object):
    HIGHLIGHT_START = Style.BRIGHT
    HIGHLIGHT_STOP = Style.NORMAL

    def highlight(self, text, substring, case=None):
        if not substring:
            return text
        if case is None:
            case = (substring.lower() != substring)
        parts = list()
        search_text = text if case else text.lower()
        substring = substring if case else substring.lower()
        index = 0
        while True:
            found = search_text.find(substring, index)
            if found < 0:
                parts.append(text[index:])
                break
            parts.append(text[index:found])
            index = found + len(substring)
            parts.append(self.HIGHLIGHT_START)
            parts.append(text[found:index])
            parts.append(self.HIGHLIGHT_STOP)
        return ''.join(parts)


def strip_ansi_escape(text):
    return ANSI_ESC_REGEX.sub('', text)
