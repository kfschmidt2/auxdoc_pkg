import os
import logging
from .literals import *
from .classes import *
import traceback

SHOW_LAYOUT = True
PAGE_SUBDIR = "page_files"


def renderDoc(udoc, outdir, fileprefix, show_layout = False):
    logging.info("rendering to HTML: "+str(udoc) + " to directory: "+outdir)

    # vars
    global SHOW_LAYOUT
    global PAGE_SUBDIR
    
    # check that the directory exists
    page_outdir = outdir + '/' + PAGE_SUBDIR
    if not os.path.exists(page_outdir):
        logging.debug("Creating directory: "+page_outdir)
        os.makedirs(page_outdir)        
    
    # render each page
    for p in udoc.pages:
        ofile_div = page_outdir + "/" + fileprefix + "_p" + str(p.page_no) + ".html"
        logging.debug("rendering page: "+str(p.page_no) + " to file: "+ofile_div)
        divstr = getPageAsDIV(p)
        fid = open(ofile_div, 'w')
        fid.write(divstr)
        fid.close()        

    # create the navigation page
    headstr = getMainHead(udoc, fileprefix)
    bodystr = getMainBody(udoc, fileprefix)
    html_str = '<HTML>\n' + headstr + bodystr + '</HTML>\n'
    ofile_html = outdir + "/" + fileprefix + ".html"
    if not os.path.exists(outdir):
        os.makedirs(outdir)    
    logging.debug("writing html navigation file: "+ofile_html)
    fid = open(ofile_html, 'w')
    fid.write(html_str)
    fid.close()        

def getMainBody(udoc, fileprefix):
    open_body = "  <BODY>\n"
    close_body = "  </BODY>\n"
    body = '<div id="contentdiv" tabindex=0 style="bakground: red; width=400; height=500">\n' + \
        '</div>'
    
    bodystr = open_body + body + close_body
    return bodystr
    
def getMainHead(udoc, fileprefix):
    incl_jquery = '  <script src="https://code.jquery.com/jquery-1.11.3.min.js"></script>\n'    

    fxn_vars = '\n  let curpage = 0\n' + \
        '  let maxpage='+str(len(udoc.pages))+'\n' + \
        '  let file_prefix="' + PAGE_SUBDIR + '/' + fileprefix + '_p"\n\n'

    fxn_onload = \
    '''
      $( document ).ready(function() {
           $("#contentdiv").load(file_prefix + "1.html");
           document.addEventListener("keydown", pageCycle, true);
           document.getElementById("contentdiv").addEventListener("keydown", pageCycle, true);    
      });       
    '''
    
    fxn_pagecycle = \
    '''
    function pageCycle(e) {
      if (e.keyCode === 37) {
          // left arrow key is pressed    
          if (curpage === 0) {
          curpage = maxpage - 1
          } else {
             curpage = (curpage - 1) % maxpage
          }
    
        } else if (e.keyCode === 39) {
          // Right arrow key is pressed
          button = "right"
          curpage = (curpage + 1) % maxpage
        }
      newfile = file_prefix + (curpage+1) + ".html"
      alert("event captured: "+e + " file is: "+newfile)              
      $("#contentdiv").load(newfile);    
    }
    

    '''

    headstr = '<HEAD>\n'
    headstr += incl_jquery    
    headstr += '  <SCRIPT>\n'
    headstr += fxn_vars
    headstr += fxn_onload
    headstr += fxn_pagecycle
    headstr += '   </SCRIPT>\n'
    headstr += '</HEAD>\n'        
    return headstr
    
    

def getPageAsDIV(page):
    '''Returns this page as a single div according to the layout and cell contents'''
    w = convertToPts(page.width, page.units)
    h = convertToPts(page.height, page.units)

    div_border = ''

    if SHOW_LAYOUT:
        div_border = 'style="border:1px solid red" '
        
    div_open = '<div '+ \
        'width="'+ str(w)+'px" '+ \
        'height="'+str(h)+ 'px" '+ \
        div_border + '>\n'
    
    div_close = '</div>\n'

    div_style = '<style>\n'
    fnt = ""
    for f in page.fonts:
        div_style += '    '+page.fonts[f] +';\n'

    if SHOW_LAYOUT:
        div_style += '    div { border: 1px solid #0000FF; }\n'


    for c in page.cell_classes:
        if page.cell_classes[c]['cell_type'] == Cell.CELLTYPE_TEXT:
            div_style += '    .'+ c + ' ' + page.cell_classes[c]['style'] + '\n'

    div_style += '   div { position: absolute; }\n'
    div_style += '</style>\n'
        
    div_body = ""
    div_cells = ""
    print("page.page_contents is: "+str(page.page_contents))
    for cname in page.cells.keys():
        content = ""
        try:
            content = page.page_contents[cname]
            try:
                body = getCellAsDIV(page.cells[cname], content, page.units)        
                div_body += body
            except:
                traceback.print_exc()
        except:
            logging.debug("No content found for cell: "+cname+" ...skipping.")
        
            
    div = div_style + div_open + div_body + div_close                    
    return div



# DIV generation methods

def getPosStyle(x, y, w, h):
    posstyle = 'style=" top: '+str(y) + '; ' + \
        ' left: '+str(x) + '; ' + \
        ' width: '+str(w) + '; ' + \
        ' height: '+str(h) + ';"'
    return posstyle


def getTextCellAsDIV(cell_coords, content, class_name):
    x, y, w, h = cell_coords
    divclass = class_name
    div = '    <div class="'+ divclass +'" '
    div += getPosStyle(x, y, w, h)
    div += '>\n'
    div += content
    div += '\n    </div>\n'
    return div

def getRectCellAsDIV(cell_coords, content, class_name):
    x, y, w, h = cell_coords

    divclass = class_name
    div = '    <div class="'+ divclass +'" '
    div += getPosStyle(x, y, w, h)
    div += '>\n'
    div += content
    div += '\n    </div>\n'
    return div


def getImageCellAsDIV(cell_coords, content, class_name):
    x, y, w, h = cell_coords
    div = ""
    src = content
    fname, ext = os.path.splitext(src)

    # check that the src exists
    if not os.path.exists(src):
        raise Exception("The image file: "+src+" was not found")
    
    if ext.lower() == ".svg" and False:  # disable inline svg and treat all svg as images 
        sourcesvg = open(src).read()
        if '?>' in sourcesvg:
            namespace_idx = sourcesvg.index('?>')
            sourcesvg = sourcesvg[(namespace_idx+2):]
        div = '<div x="' + str(x) + 'px" y="' + str(y) + 'px" ' 
        div += 'width="' + str(w) + 'px" height="' + str(h) + 'px" >\n'
        div += sourcesvg
        div += '\n</div>\n'
    else:
        print("about to encode src file: "+src)
        ftype = ext.lower()[1:]
        if ftype == 'svg':
            ftype = 'svg+xml'
        b64_bytes = base64.b64encode(open(src, 'rb').read())
        b64 = b64_bytes.decode('ascii')

        div = '    <div class="'+ class_name +'" '
        div += getPosStyle(x, y, w, h)
        div += '>\n'
        div += '    <image width="' + str(w) + '" height="' + str(h) + \
            '" src="data:image/' + ftype + ';base64,' + b64 +'" />\n'
        div += '    </div>\n'



    return div


def getCellAsDIV(cell, content, units):
    coords = getCellCoords(cell, units)
    cell_class = cell.cell_class
    
    div = ""

    if cell.cell_type == Cell.CELLTYPE_TEXT:
        div = getTextCellAsDIV(coords, content, cell_class)
    elif cell.cell_type == Cell.CELLTYPE_IMAGE:
        div = getImageCellAsDIV(coords, content, cell_class)        
    elif cell.cell_type == Cell.CELLTYPE_RECT:
        div = getRectCellAsDIV(coords, content, cell_class)        
    else:
        raise Exception("Unhandled cell type: "+cell_type)                

    return (div+'\n')


    
def getCellCoords(cell, units):
    w = convertToPts(cell.width, units)
    h = convertToPts(cell.height, units)
    x = convertToPts(cell.x, units)
    y = convertToPts(cell.y, units)
    ret = [x, y, w, h]
    return ret


def convertToPts(val, units):
    '''Convert unit measures to pt'''
    pts = -1
    if units == UNIT_INCHES:
        pts = val * PT_PER_IN
    elif units == UNIT_CM:
        pts = val * PT_PER_IN / CM_PER_IN
    return pts






# SVG generation methods
# DEPRECATED

def getPageAsSVG(page):
    '''Returns this page as a single svg image according to the layout and cell contents'''
    w = convertToPts(page.width, page.units)
    h = convertToPts(page.height, page.units)

    svg_border = ""

    if SHOW_LAYOUT:
        svg_border = 'style="border:1px solid red" '
        
    svg_open = '<svg '+ \
        'width="'+ str(w)+'px" '+ \
            'height="'+str(h)+ 'px" '+ \
            svg_border + \
            'xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">\n'
    svg_close = '</svg>\n'

    svg_style = '<style>\n'
    fnt = ""
    for f in page.fonts:
        svg_style += '    '+page.fonts[f] +';\n'

    if SHOW_LAYOUT:
        svg_style += '    div { border: 1px solid #0000FF; }\n'


    for c in page.cell_classes:
        if page.cell_classes[c]['cell_type'] == Cell.CELLTYPE_TEXT:
            svg_style += '    .'+ c + ' ' + page.cell_classes[c]['style'] + '\n'
    svg_style += '</style>\n'
        
    svg_body = ""
    svg_cells = ""
    print("page.page_contents is: "+str(page.page_contents))
    for cname in page.cells.keys():
        content = ""
        try:
            content = page.page_contents[cname]
            try:
                body = getCellAsSVG(page.cells[cname], content, page.units)        
                svg_body += body
            except:
                traceback.print_exc()
        except:
            logging.debug("No content found for cell: "+cname+" ...skipping.")
        
            
    svg = svg_open + svg_style + svg_body + svg_close                    
    return svg



def getTextCellAsSVG(cell_coords, content, class_name):
    x, y, w, h = cell_coords
    divclass = class_name

    fo_open = '<foreignObject '+ \
        'x="' + str(x) + 'px" y="' + str(y) + 'px" ' + \
        'width="' + str(w) + 'px" height="' + str(h) + 'px" >\n'        
    div_open = '     <div class="' + divclass + '" xmlns="http://www.w3.org/1999/xhtml">\n'
    div_close = '\n     </div>\n'
    fo_close = '</foreignObject>\n'
    svg = fo_open + div_open + content + div_close + fo_close    
    return svg

def getRectCellAsSVG(cell_coords, content, class_name):
    x, y, w, h = cell_coords

    svg = '<rect x="' + str(x) + 'px" y="' + str(y) + 'px" ' + \
	'width="' + str(w) + 'px" height="' + str(h) +'px" ' + \
	'style="fill:' + str(bg_color) + ';stroke:blue;stroke-width:5;' + \
	'fill-opacity:' + str(bg_alpha) + ';stroke-opacity:0.9" />\n'
        
    return svg
    
def getImageCellAsSVG(cell_coords, content, class_name):
    x, y, w, h = cell_coords
    svg = ""
    src = content
    fname, ext = os.path.splitext(src)

    # check that the src exists
    if not os.path.exists(src):
        raise Exception("The image file: "+src+" was not found")
    
    if ext.lower() == ".svg":   
        sourcesvg = open(src).read()
        if '?>' in sourcesvg:
            namespace_idx = sourcesvg.index('?>')
            sourcesvg = sourcesvg[(namespace_idx+2):]
        svg = '<image x="' + str(x) + 'px" y="' + str(y) + 'px" ' 
        svg += 'width="' + str(w) + 'px" height="' + str(h) + 'px" >\n'
        #svg += '<rect x="0" y="0" width="20" height="30" />\n'
        svg += sourcesvg
        svg += '\n</image>\n'
    else:
        print("about to encode src file: "+src)
        b64_bytes = base64.b64encode(open(src, 'rb').read())
        b64 = b64_bytes.decode('ascii')
        svg = '<image '
        svg += 'x="' + str(x) + 'px" y="' + str(y) + 'px" ' 
        svg += 'width="' + str(w) + 'px" height="' + str(h) + 'px" '
        #svg += ' xlink:href="data:image/' + ext.lower()[1:] + ';base64,' + b64 +'" />'
        svg += ' src="data:image/' + ext.lower()[1:] + ';base64,' + b64 +'" />'
        
    return svg
    

def getCellAsSVG(cell, content, units):
    coords = getCellCoords(cell, units)
    cell_class = cell.cell_class
    
    svg = ""

    if cell.cell_type == Cell.CELLTYPE_TEXT:
        svg = getTextCellAsSVG(coords, content, cell_class)
    elif cell.cell_type == Cell.CELLTYPE_IMAGE:
        svg = getImageCellAsSVG(coords, content, cell_class)        
    elif cell.cell_type == Cell.CELLTYPE_RECT:
        svg = getRectCellAsSVG(coords, content, cell_class)        
    else:
        raise Exception("Unhandled cell type: "+cell_type)                

    return svg




