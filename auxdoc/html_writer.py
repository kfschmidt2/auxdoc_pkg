import os


def renderDoc(udoc, outdir, fileprefix):
    logging.info("rendering to HTML: "+str(udoc))
    
    # check that the directory exists
    if not os.path.exists(outdir):
        logging.debug("Creating directory: "+outdir)
        os.makedirs(apath)        
    
    # render each page
    pageno = 1;
    for p in udoc.pages:
        ofile_svg = outdir + "/" + fileprefix + "_p" + str(pageno) + ".svg"
        logging.debug("rendering page: "+str(pageno) + " to file: "+ofile_svg)
        svgstr = getPageAsSVG(p, udoc.docdir)
        fid = open(ofile_svg, 'w')
        fid.write(svgstr)
        fid.close()        
        pageno += 1

def getCellAsSVG(cell, docdir, units):

    print("getCellAsSVG: "+str(cell))
    w = convertToPts(cell.width, units)
    h = convertToPts(cell.height, units)
    x = convertToPts(cell.x, units)
    y = convertToPts(cell.y, units)
    divclass = cell.cell_class
    
    svg = []

    if cell.cell_type == Cell.CELLTYPE_TEXT:
        # default to text type        
        fo_open = '<foreignObject '+ \
            'x="' + str(x) + 'px" y="' + str(y) + 'px" ' + \
            'width="' + str(w) + 'px" height="' + str(h) + 'px" >\n'        
        div_open = '     <div class="' + divclass + '" xmlns="http://www.w3.org/1999/xhtml">\n'
        div_close = '\n     </div>\n'
        fo_close = '</foreignObject>\n'
        svg = fo_open + div_open + cell.content + div_close + fo_close

    elif cell.cell_type == Cell.CELLTYPE_IMAGE:
        src = docdir + '/' + cell.content
        fname, ext = os.path.splitext(src)
        if ext.lower() == ".svg":
            svg = open(src).read()
        else:
            b64 = base64.b64encode(open(src).read())
    
            svg = '<image '
            svg += 'x="' + str(x) + 'px" y="' + str(y) + 'px" ' 
            svg += 'width="' + str(w) + 'px" height="' + str(h) + 'px" '
            svg += ' xlink:href="data:image/' + ext.lower()[1:len(ext)] + ';base64,' + b64 +'" />'
        
    elif cell.cell_type == Cell.CELLTYPE_RECT:
        svg = '<rect x="' + str(x) + 'px" y="' + str(y) + 'px" ' + \
	    'width="' + str(w) + 'px" height="' + str(h) +'px" ' + \
	    'style="fill:' + str(bg_color) + ';stroke:blue;stroke-width:5;' + \
	    'fill-opacity:' + str(bg_alpha) + ';stroke-opacity:0.9" />\n'
        
    else:
        raise Exception("Unhandled cell type: "+cell_type)                

    return svg
    
        
def getPageAsSVG(page, docdir):
    '''Returns this page as a single svg image according to the layout and cell contents'''
    w = convertToPts(page.width, page.units)
    h = convertToPts(page.height, page.units)
    svg_open = '<svg '+ \
        'width="'+ str(w)+'px" '+ \
            'height="'+str(h)+ 'px" '+ \
            'xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">\n'
    svg_close = '</svg>\n'

    svg_style = '<style>\n'
    fnt = ""
    for f in page.fonts:
        svg_style += '    '+page.fonts[f] +';\n'

    for c in page.cell_classes:
        if page.cell_classes[c]['cell_type'] == Cell.CELLTYPE_TEXT:
            svg_style += '    .'+ c + ' ' + page.cell_classes[c]['style'] + '\n'
    svg_style += '</style>\n'
        
    svg_body = " "
    svg_cells = ""
    for cname in page.cells.keys():
        body = getCellAsSVG(page.cells[cname], docdir, page.units)        
        svg_body += body
    svg = svg_open + svg_style + svg_body + svg_close                    
    return svg
