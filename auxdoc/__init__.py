# __init__.py

import logging

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)
log.info('Initializing auxdoc')

from .literals import *
from .classes import AUXDoc
from .classes import Layout
from .classes import Page
from .classes import Cell
from .classes import XRef
from .funcs import convertToPts
from .funcs import renderHTML
from .funcs import getCellAsSVG
from .funcs import getPageAsSVG
from .funcs import convertToPts
from .loremipsum import LIPSUM_SHORT
from .loremipsum import LIPSUM_SUBTITLE
from .loremipsum import LIPSUM_MED
from .loremipsum import LIPSUM_LONG
