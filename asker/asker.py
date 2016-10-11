from __future__ import print_function
import sys
from contextlib import contextmanager
import re
from six import moves
from colorama import Fore, Back, Style, Cursor
from getkey import getkey, keys

ANSI_ESC_REGEX = re.compile(r'(\x9B|\x1B\[)[0-?]*[ -\/]*[@-~]')


class Asker(object):
    QUERY_ENDS = (':', '?')
    DEFAULT_FORMAT = ' [{}]'
    SELECTED = '*) '
    UNSELECTED = ' ) '
    WINDOW = 8

    def __init__(self, writer=None, highlighter=None):
        self.writer = writer or Writer()
        self.highlighter = highlighter or Highlighter()

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

    def ask(self, query, default=None, type=None, choices=None, labels=None):
        if choices is not None:
            if type:
                raise ValueError('Cannot use both `choices` and `type`')
            return self.select(query, choices, labels, default=default)
        elif labels:
            raise ValueError('Cannot have labels without choices')
        else:

            return self.input(query, default=default, type=type)

    # Specific question types

    def _validate(self, answers, default=None, type=None):
        for answer in answers:
            if not answer and default is not None:
                return default
            if not type:
                return answer

            try:
                answer = type(answer)
            except Exception as err:
                print(err.args[0], file=sys.stderr)
            else:
                return answer

    def input(self, query, default=None, type=None):
        """Simply ask for user input: compatible with builtin `raw_input`."""
        query = self.format_query(query, default)
        return self._validate(
            self._inputting(query),
            default=default,
            type=type,
        )

    def select(self, query, choices, labels=None, default=None):
        if not choices or len(choices) == 0:
            raise ValueError(
                'Can only select when choices are given, nothing in {!r}'.format(
                    choices
                )
            )
        elif default is not None and default not in choices:
            raise ValueError(
                'Default value {!r} not found in choices {!r}'.format(
                    default, choices
                )
            )
        elif len(choices) == 1:
            result = choices[0]
            query = self.format_query(query, default)
            self.writer.print('{}{} [only choice]'.format(query, result))
            return result
        
        filter = ''

        if not labels:
            labels = choices
        index = 0
        if default is not None:
            index = choices.index(default)
        filtered_labels = list(labels)
        filtered_choices = list(choices)

        # TODO: make scrollable line block so this is all a lot cleaner
        with LineBlock() as block:
            print_at_line = block.print_at
            highlight = self.highlighter.highlight

            def refilter(index):
                if index >= 0:
                    choice = filtered_choices[index]
                print_at_line(0, query + filter)
                if filter == filter.lower():
                    filtered_indices = [i for i, label in enumerate(labels) if
                                        filter in label.lower()]
                else:
                    filtered_indices = [i for i, label in enumerate(labels) if
                                        filter in label]
                filtered_choices[:] = [choices[i] for i in filtered_indices]
                filtered_labels[:] = [highlight(labels[i], filter) for i in
                                      filtered_indices]

                if not filtered_choices:
                    filtered_index = -1
                elif index >= 0 and choice in filtered_choices[:self.WINDOW]:
                    filtered_index = filtered_choices.index(choice)
                else:
                    filtered_index = 0

                if filtered_choices:
                    for i in range(min((self.WINDOW, len(choices)))):
                        if i == filtered_index:
                            print_at_line(
                                i + 1, self.SELECTED + filtered_labels[i]
                            )
                        elif i < len(filtered_labels):
                            print_at_line(
                                i + 1, self.UNSELECTED + filtered_labels[i]
                            )
                        else:
                            print_at_line(i + 1, '')
                    if len(filtered_choices) > self.WINDOW:
                        print_at_line(
                            self.WINDOW + 1,
                            '< {} more: type to filter >'.format(
                                len(filtered_choices) - self.WINDOW
                            )
                        )
                    elif len(choices) > self.WINDOW:
                        print_at_line(self.WINDOW + 1, '')

                else:
                    print_at_line(1,
                                  '< No choices contain {!r} >'.format(filter))
                    for i in range(1, self.WINDOW):
                        print_at_line(i + 1, '')
                print_at_line(filtered_index + 1, '', clear=False)
                return filtered_index

            refilter(0)

            while True:
                old_index = index

                key = getkey()
                if key in {keys.BACKSPACE, keys.DELETE}:
                    filter = filter[:-1]
                    index = refilter(index)
                elif key in {keys.UP, keys.DOWN}:
                    if index >= 0:
                        index += {keys.UP: -1, keys.DOWN: +1}[key]
                        if index < 0:
                            index = 0
                        elif index >= min((self.WINDOW, len(filtered_labels))):
                            index = min((
                                self.WINDOW, len(filtered_labels)
                            )) - 1
                        if 0 <= old_index < len(labels) and index != old_index:
                            print_at_line(
                                old_index + 1,
                                self.UNSELECTED + filtered_labels[old_index]
                            )
                        print_at_line(
                            index + 1,
                            self.SELECTED + filtered_labels[index]
                        )
                elif key in {keys.ENTER, keys.RIGHT}:
                    break
                else:
                    filter += key
                    index = refilter(index)

            if index >= 0:
                print_at_line(0, query + filtered_choices[index])

        return filtered_choices[index]

    def _inputting(self, query):
        while True:
            yield self.writer.input(query)


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
