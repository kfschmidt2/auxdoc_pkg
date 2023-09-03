# __init__.py

import logging

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)
log.debug(' Initializing auxdoc package')

from .literals import *
from .loremipsum import *
from .classes import AUXDoc
from .classes import Layout
from .classes import Page
from .classes import Cell
from .classes import XRef
from .funcs import convertToPts
from .demo import runDemo
from .demo import copyResourceFile
from .demo import copyResourceFiles
from .html_writer import renderDoc as renderHTML
from .html_writer import getCellAsSVG
from .html_writer import getPageAsSVG


