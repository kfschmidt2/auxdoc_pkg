import os
import logging
from .literals import *
from .classes import *
import traceback

SHOW_LAYOUT = False

def convertToPts(val, units):
    '''Convert unit measures to pt'''
    pts = -1
    if units == UNIT_INCHES:
        pts = val * PT_PER_IN
    elif units == UNIT_CM:
        pts = val * PT_PER_IN / CM_PER_IN
    return pts


def renderDoc(udoc, outdir, fileprefix, show_layout = False):
    logging.info("rendering to HTML: "+str(udoc) + " to directory: "+outdir)
    page_outdir = "/page_svg_files"

    # set the layout flag if indicated
    if show_layout:
        global SHOW_LAYOUT
        SHOW_LAYOUT = True
    
    # check that the directory exists
    if not os.path.exists(outdir + page_outdir):
        logging.debug("Creating directory: "+page_outdir)
        os.makedirs(outdir + page_outdir)        
    
    # render each page
    for p in udoc.pages:
        ofile_svg = outdir + page_outdir + "/" + fileprefix + "_p" + str(p.page_no) + ".svg"
        logging.debug("rendering page: "+str(p.page_no) + " to file: "+ofile_svg)
        svgstr = getPageAsSVG(p)
        fid = open(ofile_svg, 'w')
        fid.write(svgstr)
        fid.close()        

    # create the navigation html
    open_html = "<HTML>\n"
    open_head = "<HEAD>\n"
    open_script = "  <SCRIPT>\n"
    open_body = "  <BODY>\n"

    close_body = "  </BODY>\n"
    close_script = "  </SCRIPT>\n"
    close_head = "</HEAD>\n"
    close_html = "</HTML>\n"

    fxn_vardefs = '\n  let curpage = 0\n' + \
        '  let maxpage='+str(len(udoc.pages))+'\n' + \
        '  let file_prefix=".' + page_outdir + '/' + fileprefix + '_p"\n\n'


    fxn_addEventListener = \
    '''

    function pageCycle(e) {
       alert("event captured: "+e)
        button = "left"
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
        newfile = file_prefix + (curpage+1) + ".svg"
        document.getElementById("svgobj").setAttribute("data", newfile);        
    }
    
    document.addEventListener('keydown', pageCycle, true);
    document.getElementById("svgobj").addEventListener('keydown', pageCycle, true);

    '''

    fxn_addObjectListener = \
    '''    
    document.getElementById("svgobj").addEventListener('keydown', function(e) {
        button = "left"
        if (e.keyCode === 37) {
          alert("left press and curpage is: "+curpage)
    
          // left arrow key is pressed    
          if (curpage <= 0) {
             curpage = (curpage + 5*maxpage) % maxpage
          } else {
             curpage = (curpage - 1) % maxpage
          }
    
        } else if (e.keyCode === 39) {
          // Right arrow key is pressed
          alert("right press and curpage is: "+curpage)    
          button = "right"
          curpage = (curpage + 1) % maxpage
    
        }
        newfile = file_prefix + (curpage+1) + ".svg"
        alert(button +" arrow is pressed, new file is: "+newfile)
        document.getElementById("svgobj").setAttribute("data", newfile);        
    });    

    '''
    
    body = \
'''
    <div id="svgdiv" tabindex=0>
    <object id="svgobj" width="100%" data="page_svg_files/auxdoc_report_p1.svg" type="image/svg+xml" tabindex=1>
    </object>
    </div>
'''    
    
    html_str = open_html + open_head
    html_str += close_head
    html_str += open_body + body 
    html_str += open_script + fxn_vardefs + fxn_addEventListener + fxn_addObjectListener + close_script    
    html_str += close_body
    html_str += close_html

    ofile_html = outdir + "/" + fileprefix + ".html"
    logging.debug("writing html navigation file: "+ofile_html)
    fid = open(ofile_html, 'w')
    fid.write(html_str)
    fid.close()        
    
def getCellCoords(cell, units):
    w = convertToPts(cell.width, units)
    h = convertToPts(cell.height, units)
    x = convertToPts(cell.x, units)
    y = convertToPts(cell.y, units)
    ret = [x, y, w, h]
    return ret


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
    
    if ext.lower() == ".svg_bogs":
        svg = open(src).read()
    else:
        print("about to encode src file: "+src)
        b64_bytes = base64.b64encode(open(src, 'rb').read())
        b64 = b64_bytes.decode('ascii')
        svg = '<image '
        svg += 'x="' + str(x) + 'px" y="' + str(y) + 'px" ' 
        svg += 'width="' + str(w) + 'px" height="' + str(h) + 'px" '
        svg += ' xlink:href="data:image/' + ext.lower()[1:] + ';base64,' + b64 +'" />'
        
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
