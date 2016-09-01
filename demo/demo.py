import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, BASE_DIR)

from asker import ask

alist = [
    'Giant Aardvarks',
    'Godzillas',
    'Artichokes',
    'Lambskins',
    'Cowbells',
    'Yesteryears',
    'Petunias',
    'Forests',
    'Petty Arts',
    'Giant Can-openers',
    'Neophytes',
    'Lost Children',
    'Kindly Maids',
    'The Worst',
    'Genocides',
    'Bluebells',
    'Hydras',
    'Cornucopias',
    'Men',
    'Tiny Little Eyes',
]

if __name__ == '__main__':
    a = ask('What is this? ')
    print('you said: {!r}'.format(a))
    b = ask('What is this again? ', 'a cat')
    print('you said: {!r}'.format(b))
    c = ask('What are these? ', choices=alist)
    print('you said: {!r}'.format(c))
