import os
import logging
from .literals import *
from .classes import *
import traceback
import glob

SHOW_LAYOUT = True
PAGE_SUBDIR = "page_files"

DOC_HEAD = ''
DOC_SCRIPT = ''
DOC_BODY = ''

INDT = '   ';

def renderDoc(udoc, outdir, fileprefix, show_layout = False):
    '''
    Renders a valid document to a set of html files in slide format.
    Each page is rendered as a separate, standalone html file located in
    directory outdir/reportpageX.html

    '''
    logging.info("rendering to HTML: "+str(udoc.title) + " to directory: "+outdir)

    # check that the directory exists, create if not
    page_outdir = outdir + '/' + PAGE_SUBDIR
    if not os.path.exists(page_outdir):
        logging.debug("Creating directory: "+page_outdir)
        os.makedirs(page_outdir)        
    
    # render each page
    for p in udoc.pages:
        ofile_div = page_outdir + "/" + fileprefix + "_p" + str(p.page_no) + ".html"
        logging.debug("rendering page: "+str(p.page_no) + " to file: "+ofile_div)
        headstr, divstr = getPageAsDIV(p)
        html = wrapHeadAndBody(headstr, divstr)
        fid = open(ofile_div, 'w')
        fid.write(html)
        fid.close()        

def wrapHeadAndBody(head, body):
    ret = '<HTML>\n'
    ret = '<HEAD>\n'    
    ret += head
    ret += '</HEAD>\n'
    ret += '<BODY>\n'
    ret += body
    ret += '</BODY>\n'
    ret += '</HTML>\n'
    return ret
    
def getPageAsDIV(page):
    
    '''Returns this page as a single div according to the layout and cell contents'''
    w = convertToPts(page.width, page.units)
    h = convertToPts(page.height, page.units)
    head = ''
    body = ''
    
    # setup the head entries
    incl_goog_icon = INDT+'<link rel="stylesheet" href="https://fonts.googleapis.com/icon?family=Material+Icons">\n'

    incl_jquery = INDT+'<script src="http://code.jquery.com/jquery.min.js"></script>\n'

    # add the fonts
    fnts = ''
    for f in page.fonts:
        fnts += INDT+page.fonts[f] +';\n'

    
    # add the cell class style elements 
    cell_styles = '';
    for c in page.cell_classes:
        if page.cell_classes[c]['cell_type'] == Cell.CELLTYPE_TEXT:
            cell_styles += INDT+'.'+ c + ' ' + page.cell_classes[c]['style'] + '\n'

    # default div style and border if nec.        
    div_style = INDT + 'div { \n    position: absolute;\n'
    if SHOW_LAYOUT:
        div_style += INDT + 'border: 1px solid red;\n'

    div_style += INDT + '}\n'

            
    # add the anim button style
    button_style = '\n'+INDT + 'button {\n' + \
                   INDT + INDT + 'border: none;\n' + \
                   INDT + INDT + 'margin-left: 10px;\n' + \
                   INDT + INDT + 'background-color: transparent;\n' + \
                   INDT + '}\n'+ \
                   INDT + '.material-icons {\n'+ \
                   INDT + INDT+'color:rgba(125,125,125,0.5);\n'+ \
                   INDT + INDT+'font-size: 18px;\n'+ \
                   INDT + '}\n'

    button_style += INDT + 'button:hover {\n' + \
                   INDT + INDT + 'background-color: rgba(255,255,255,0.3);\n' + \
                   INDT + '}\n'
    
    button_style += INDT + 'button:hover .material-icons{\n' + \
                   INDT + INDT + 'color: red;\n'+ \
                   INDT + '}\n'                   
    

    # add the navigation event listeners
    page_nav_script = \
        '''
        function keyPressed(e) {
              if (e.keyCode === 37) {
                 // left arrow key is pressed
                 console.log("left arrow pressed");
              } else if (e.keyCode === 39) {
                 // right arrow key is pressed
                 console.log("right arrow pressed");        
             }
         }

         document.addEventListener("keydown", keyPressed, true);
                
        '''





    
    head = incl_jquery + incl_goog_icon + \
        '<STYLE>\n' + fnts + div_style + cell_styles + button_style + '</STYLE>\n' + \
        '<SCRIPT>\n' + page_nav_script + '</SCRIPT>\n'

    
    # build the html
    
    div_open = '<div '+ \
        'width="'+ str(w)+'px" '+ \
        'height="'+str(h)+ 'px" >\n'
    
    div_close = '</div>\n'

    div_body = ""

    #print("page.page_contents is: "+str(page.page_contents))    
    for cname in page.cells.keys():
        content = ""
        try:
            content = page.page_contents[cname]
            try:
                div_body += getCellAsDIV(page.cells[cname], content, page.units)        
            except:
                traceback.print_exc()
        except:
            logging.debug("No content found for cell: "+cname+" ...skipping.")
        
    body = div_open + div_body + div_close 
    return head, body



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

    # switch based on media type: static image, movie, img sequence
    fname, ext = os.path.splitext(content)    
    is_sequence = False
    is_movie = False
    if '*' in content:
        is_sequence = True        
    elif ext in ['.mov', '.mp4']:
        is_movie = True

    if is_sequence:
        div = getAnimationImageDIV(cell_coords, content, class_name)
    else:        
        div = getStaticImageDIV(cell_coords, content, class_name)

    return div

def getImageElement(cell_coords, image_src, img_id):
    x, y, w, h = cell_coords
    ret = ''    
    src = image_src
    fname, ext = os.path.splitext(src)

    srcb64 = getAsBase64Src(src)
    
    ret += '    <image id="'+img_id+'" style="object-fit: contain;" width="' + str(w) + '" height="' + str(h) + \
        '" src="' + srcb64 +'" />\n'
    return ret

def getAsBase64Src(src_file):
    # check that the src exists
    fname, ext = os.path.splitext(src_file)    
    if not os.path.exists(src_file):
        raise Exception("The image file: "+src_file+" was not found")
    print("about to encode src file: "+src_file)
    ftype = ext.lower()[1:]
    if ftype == 'svg':
        ftype = 'svg+xml'    
    b64_bytes = base64.b64encode(open(src_file, 'rb').read())
    b64 = b64_bytes.decode('ascii')
    src_str = 'data:image/' + ftype +';base64,'+b64
    return src_str


def getAnimationImageDIV(cell_coords, content, class_name):
    '''Returns the html for an animation of the images (all embedded)
    including controls, embedded in a single div mapped to the cell coords
    images are displayed in natural order based on directory listing.
    '''
    x, y, w, h = cell_coords
    div = ''
    fname, ext = os.path.splitext(content)

    # get the image files and encode them
    files = glob.glob(content)
    images_src = []
    
    # load and base64 encode the images, store the src strings
    if len(files) == 0:
        raise Exception("Image files were not found: "+content)
    else:
        for f in files:
            srcb64 = getAsBase64Src(f)
            images_src.append(srcb64)

    # make the image tag
    img_html_id = 'anim'+str(x)+str(y)
    img_html = '    <image id="'+img_html_id + '" ' + \
        'style="object-fit: contain;" ' + \
        'width="' + str(w) + '" height="' + str(h) + '" ' + \
        'src="'+images_src[0]+'" />\n'    

    # make the control html
    ctl_html = getAnimControlHTML()
    
    # make the javascript
    js = getAnimControlJS(img_html_id, images_src)
    
    div = '    <div class="'+ class_name +'" '
    div += getPosStyle(x, y, w, h)
    div += '>\n'
    div += img_html
    div += ctl_html
    div += js        
    div += '    </div>\n'
    return div

def getAnimControlHTML():
    icon_play = '<i class="material-icons" onclick="startLoop()">play</button></i>\n'
    icon_pause = '<i class="material-icons" onclick="stopLoop()">pause</button></i>\n'
    
    button_back = INDT+'<button ><i class="material-icons" onclick="decrementImage()">chevron_left</button></i>\n'
    button_fwd = INDT+'<button ><i class="material-icons" onclick="incrementImage()">chevron_right</button></i>\n'
    button_ffwd = INDT+'<button ><i class="material-icons" onclick="speedUp()">add_circle_outline</button></i>\n'
    button_rwd = INDT+'<button ><i class="material-icons" onclick="slowDown()">remove_circle_outline</button></i>\n'
    button_pause = INDT+'<button id="playpause">'+icon_pause+'</button></i>\n'
    button_close = '</i></button>\n'
    html = INDT + '<div id="animctl" style="z-index: 10; position:absolute; bottom: 10; width: 50%; left: 24%; text-align:center; column-gap: 20px;">'
    html += button_rwd + button_back + button_pause + button_fwd + button_ffwd
    html += INDT + '</div>\n'
    
    return html

def getAnimControlJS(img_tag_id, images_src):

    images_arr = '   let images_src = [\n'
    imgcount = 0
    for i in images_src:
        if imgcount > 0:
            images_arr += ', \n'
        images_arr += '      "'+i+'"'
        imgcount += 1
    images_arr += '\n     ];\n'

    fxn_refreshImage = '    function refreshImage() {\n ' + \
        '        document.getElementById("' + img_tag_id + '").src = images_src[localImageIDX];\n' + \
        '        //console.log("image_el.src updated to idx: "+localImageIDX);\n    }\n'

    fxn_showPlayPause  = INDT + ' let play_icon = "<i class=\\"material-icons\\" onclick=\\"startLoop()\\">play_arrow</button></i>\"\n'
    fxn_showPlayPause += INDT + ' let pause_icon = "<i class=\\"material-icons\\" onclick=\\"stopLoop()\\">pause</button></i\>"\n'
    fxn_showPlayPause += INDT + ' function showPlayIcon() {\n' + \
        INDT + INDT + 'document.getElementById("playpause").innerHTML = play_icon;\n' + \
        INDT + '}\n'
    fxn_showPlayPause += INDT + ' function showPauseIcon() {\n' + \
        INDT + INDT + 'document.getElementById("playpause").innerHTML = pause_icon;\n' + \
        INDT + '}\n'
        
    script = \
        '''
          let localImageIDX = 0;
          let numimgs = images_src.length;
          let playon = 1;
          let framedelay = 500;
          let timerid = -1;
        
          function animinit() {
              console.log("document initialized and numimgs is "+numimgs);
              refreshImage();
              startLoop();
          }

          function startLoop() {
              timerid = setInterval(incrementImage, framedelay);
              showPauseIcon();
          }

        
          function stopLoop() {
             clearInterval(timerid);
             showPlayIcon();
          }

         function speedUp() {
           framedelay = framedelay - 100;
           stopLoop();
           startLoop();
         }

         function slowDown() {
           framedelay = framedelay + 100;
           stopLoop();
           startLoop();
         }        
        
           function incrementImage() {
               localImageIDX = (localImageIDX+1) % numimgs;
               // console.log("incrementImage() called and localImageIDX is "+localImageIDX);
               refreshImage();
           }
        
           function decrementImage() {
               if (localImageIDX <= 0) {
                  localImageIDX = numimgs - 1;
               } else {
                  localImageIDX = localImageIDX - 1;
               }
               // console.log("decrementImage() called and localImageIDX is "+localImageIDX);
               refreshImage();
            }

        '''

    
    html = '<SCRIPT>\n' + images_arr + script + fxn_refreshImage + fxn_showPlayPause + '\n    animinit();\n</SCRIPT>\n'
    return html
    

def getStaticImageDIV(cell_coords, content, class_name):
    x, y, w, h = cell_coords
    img_el = getImageElement(cell_coords, content, "I1")
    div = '    <div class="'+ class_name +'" '
    div += getPosStyle(x, y, w, h)
    div += '>\n'
    div += img_el
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




