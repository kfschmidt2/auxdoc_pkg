'''
    docaux
    Python library to facilitate the creation of reports in various formats. 

'''
import os
import shutil
from math import floor
import json
import pkg_resources
import copy
import logging
import base64
from auxdoc.literals import *

def convertToPts(val, units):
    '''Convert unit measures to pt'''
    pts = -1
    if units == UNIT_INCHES:
        pts = val * PT_PER_IN
    elif units == UNIT_CM:
        pts = val * PT_PER_IN / CM_PER_IN
    return pts



        
def renderAUXDoc(doc_json_file, layout_json_file = LAYOUT_LETTER_LANDSCAPE):
    logging.info("Rendering the UDOC: "+str(doc_json_file) + ", layout: "+str(layout_json_file))    
    udoc = compileUDoc(doc_json_file, layout_json_file)
    renderHTML(udoc, "/localdata/tmpreport", "ubi_report")
    return udoc

        
'''
NOTES:
pip install git+https://github.com/user/project.git@version

General considerations:
   (Pre-processed file, perhaps asciidoc) --> DOM (paginated, linked) + layout --> rendered output (html, pptx, etc.)

Pre-processed elements:
 - Sections
 - pages
 - figures
 - tables
 - listings
 - equations
 - footnotes
 - endnotes
 - references
 - index entries


dom page types:
 - page_title
 - page_text
 - page_oneup (table, figure or listing)
 - page_twoup (tables, figures, both)
 - TOC
 - Bibliography
 - Endnotes
 - index
 -

cell types:
 - text
 - image static
 - image carousel
 - animation

other data types:
 - inline anchor (ref, numbered equation, inline equation, footnote, etc.) 
 - inline modifier (font color, size, weight, other markup)
'''
