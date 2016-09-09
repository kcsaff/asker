import pkg_resources
try:
    __version__ = pkg_resources.require('asker')[0].version
except:
    __version__ = 'DEV'


from .asker import Asker

ask = Asker().ask
