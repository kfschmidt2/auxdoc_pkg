import os
import pkgutil
import logging
from auxdoc.classes import AUXDoc, Page, Layout, Cell
from auxdoc.loremipsum import *
from auxdoc.html_writer import renderDoc as renderHTML

DEFAULT_OUTDIR = "./auxdoc_testdoc"
CONTENTSDIR = "contents"
IMGFILES = ["IMG_0554.jpg", "IMG_0693.jpg", "IMG_1665.jpg", "dog_logo.png", "blood-test.svg"]
MOVFILES = "IMG_6379.MOV"
    
def copyResourceFile(resource_file_name, to_dir):
        data = pkgutil.get_data(__package__, "demo/"+resource_file_name)
        ofile = open(to_dir + "/" + resource_file_name, 'wb')
        ofile.write(data)
        ofile.close()

def copyResourceFiles(to_dir = DEFAULT_OUTDIR):
    contents_dir = to_dir +"/"+CONTENTSDIR
    
    if not os.path.exists(contents_dir):
        os.makedirs(contents_dir)

    for f in IMGFILES:
        copyResourceFile(f, contents_dir)
    

def runDemo(to_dir = DEFAULT_OUTDIR):
    # copy the resource files
    copyResourceFiles()
            
    adoc = AUXDoc()
    pg = adoc.addPage("titlepage")    
    adoc.setTitle("For the Love of Dogs")
    adoc.setSubTitle("A sample auxdoc report")
    adoc.setAuthors("Sachem, Jasmine, Melody and Mufasa")
    adoc.setPageContent(1, "logo", DEFAULT_OUTDIR + "/" + CONTENTSDIR +"/dog_logo.png")

    pg = adoc.addPage("oneup")        
    adoc.setPageContent(2, "title", "Big and Small")
    adoc.setPageContent(2, "header", "[Page Header]")
    adoc.setPageContent(2, "subtitle", "You have to love them all")
    adoc.setPageContent(2, "fig1", DEFAULT_OUTDIR + "/" + CONTENTSDIR +"/" +IMGFILES[0] )
    adoc.setPageContent(2, "figure_legend_title", "An image of two dogs")
    adoc.setPageContent(2, "figure_legend", "This is the legend body text. It should be in the same font and format as the body text")
    adoc.setPageContent(2, "logo", DEFAULT_OUTDIR + "/" + CONTENTSDIR +"/" +IMGFILES[4] )

    pg = adoc.addPage("text3col")
    adoc.setPageContent(3, "header", "Page header")
    adoc.setPageContent(3, "title", "Three Col Test")
    adoc.setPageContent(3, "subtitle", "Lorem ipsum test should spill out of col1")
    adoc.setPageContent(3, "col1", LIPSUM_LONG)

    jstr = adoc.getContentJSON()
    logging.info("Content JSON of the doc is: "+jstr)

    # write the HTML file
    renderHTML(adoc, DEFAULT_OUTDIR, "auxdoc_report", show_layout = True)
