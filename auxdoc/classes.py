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

logging.basicConfig(level=logging.DEBUG, encoding='utf-8')

class XRef:

    def __init__(self, source, target):
        self.source = source
        self.target = target


    
'''
A Cell is an object containing layout information for rendering on the page as well as the
content to be rendered
'''
class Cell:
    CELLTYPE_IMAGE = "celltype_image"
    CELLTYPE_TEXT = "celltype_text"
    CELLTYPE_RECT = "celltype_rect"
    
    def __init__(self, layout_props):
        self.layout_props = layout_props
        self.cell_type = []
        self.content = ""
        
        logging.debug("layout_props is: "+str(layout_props))
        
        # get the basic required params
        try:
            self.cell_class = layout_props['cell_class']
            self.cell_name = layout_props['cell_name']
            self.cell_instance_id = layout_props['cell_instance_id']
            self.width = layout_props['width']
            self.height = layout_props['height']
            self.x = layout_props['x']
            self.y = layout_props['y']

        except:
            raise Exception("Basic cell parameters are missing: width, height, x, y, cell_class, cell_name, cell_instance_id")
            

    def __str__(self):
        rstr = "Cell[props:"+str(self.layout_props)+"\ncontent:"+str(self.content)[0:20]+"... "
        return rstr
    def __unicode__(self):
        return self.__str__()
    def __repr__(self):
        return self.__str__()


    
'''
A Page is an object containing a collection of Cells populated with content from the document json after instantiation.
Some references to the layout and other properties are maintained for housekeeping.
'''
class Page:

    def __init__(self, page_template_name, pg_json, cell_classes, fonts, pagenumber = -1):
        self.page_template_name = page_template_name
        self.pg_json = pg_json
        self.page_no = pagenumber
        self.width = []
        self.height = []
        self.units = []
        self.cells = {}
        self.cell_classes = cell_classes
        self.fonts = fonts
        print("cell_classes = "+str(self.cell_classes))

        # parse the cells 
        cells = pg_json['cells']
        for c in cells:
            newcell = Cell(c)
            newcell.cell_type = self.cell_classes[newcell.cell_class]['cell_type']
            self.cells[newcell.cell_name] = newcell
            
        # for use later
        self.doc_json = [] 

        
    def __str__(self):
        ret = "Page["
        ret += "layout: "+layout
        ret += ", page_no: "+str(self.page_no)
        ret += "]"
        return ret
    
    def __unicode__(self):
        return self.__str__()
    def __repr__(self):
        return self.__str__()
               
    def dump(self):
        '''Returns a string with all the contents of the page for debugging'''
        rstr = "Page["
        for c in self.cells:
            rstr += str(c)
        return rstr + "]"

    def mergeContent(self, doc_page):
        logging.debug("mergeContent()")
        self.doc_json = doc_page
        for entry in doc_page.keys():            
            if entry != "page_template":
                c = self.cells[entry]
                cont = doc_page[entry]
                c.content = cont
                print("Set cell "+entry+" content to: "+doc_page[entry])
            
    

class Layout:

    
    def __init__(self, lo_json):
        self.lo_json = lo_json
        self.layout_name = lo_json['layout_name']
        self.page_width = lo_json['page_width']
        self.page_height = lo_json['page_height']
        self.cell_classes = lo_json['cell_classes']
        self.units = lo_json['units']
        self.fonts = lo_json['fonts']
        self.page_templates = {}
        logging.debug ("Layout(): ")
        
        # parse and add the page templates
        pgs = lo_json['page_templates']
        pgtnames = pgs.keys()        
        for pgtname in pgtnames:
            pgt_json = pgs[pgtname]            
            page_temp_obj = Page(pgtname, pgt_json, self.cell_classes, self.fonts)
            page_temp_obj.width = self.page_width
            page_temp_obj.height = self.page_height
            page_temp_obj.units = self.units

            
            self.page_templates[pgtname] = page_temp_obj
        self.checkLayout()
        logging.debug("Layout "+self.layout_name+" was successfully parsed with page templates: "+str(self.page_templates.keys())) 
            
    def checkLayout(self):
        # check that all cell classes are defined
        logging.debug("... layout check was successful")

    @staticmethod
    def getLayout(layout_ref = LAYOUT_LETTER_LANDSCAPE):
        retlayout = []
        lo_json = []
        layout_file = layout_ref
        if layout_ref == LAYOUT_LETTER_LANDSCAPE:
            lfile = pkg_resources.resource_filename("auxdoc", LAYOUT_DIR + "/" + LAYOUT_LETTER_LANDSCAPE)            
            lo_json = json.loads(open(lfile, 'r').read())
        elif os.path.isfile(layout_ref):
            lo_json = json.loads(open(lfile, 'r').read())
        else:
            raise Exception("Layout or layout file not recognized: "+layout_ref)
        retlayout = Layout(lo_json)
        return retlayout

            
    def getStyleForCellClass(self, cell_class):
        ret = None
        for c in self.cell_classes:
            if c['cell_class'] == cell_class:
                ret = c['style']                
        return ret
    
    def getBlankPage(self, page_template_name):
        ret = None
        for p in self.page_templates.keys():
            if page_template_name == p:
                ret = copy.deepcopy(self.page_templates[p])
        return ret

        
class AUXDoc:
    '''AUXDoc is an object containing a renderable merge of content + layout '''
    
    def __init__(self, doc_file = DEFAULT_AUXDOC):
        dfile = []        
        if os.path.isfile(doc_file):
            dfile = doc_file             
        elif doc_file == DEFAULT_AUXDOC:
            dfile = pkg_resources.resource_filename("auxdoc", LAYOUT_DIR + "/" + DEFAULT_AUXDOC)            
        else:
            raise Exception("Auxdoc file not found: "+doc_file)

        self.layout = Layout.getLayout()        
        self.units = UNIT_INCHES
                
    def __str__(self):
        rstr = "AUXDOC[title:"+str(dir(self))+"]"
        return rstr
        
    def __repr__(self):
        return self.__str__()

    def addPage(page_template, page_contents):
        logging.debug("addPage("+page_template+"): "+page_contents)
        pg = layout.getBlankPage(page_template)
        pg.mergeContent(docp)
        pg.page_no = len(self.pages) +1
        self.pages.append(pg)        
        return pg
        
    def loadAUXDoc(self, doc_file):
        '''Create a new, renderable document merging the content in doc_file with the layout '''
        logging.info("Loading AUXDoc: "+str(doc_file))            
        self.docdir = os.path.dirname(doc_json_file)
        self.doc_json = json.loads(open(lfile, 'r').read())
        self.title = doc['title']
        self.subtitle = doc['subtitle']
        self.authors = doc['authors']
        
        # create pages and merge content
        for docp in self.doc_json['pages']:
            self.addPage(docp['page_template'], docp)
            
        logging.debug("... finished loadAUXDoc successfully.")        
            
    
