# -*- coding: iso-8859-1 -*-

"""
krop: A tool to crop PDF files

You can use command line arguments in addition to (or, to a degree, instead of) the graphical interface.

For instance, to automatically undo 4 pages print onto a single page:
    krop --go --grid=2x2 file.pdf
To additionally trim each of these pages:
    krop --go --grid=2x2 --trim --trim-use=all file.pdf

Copyright (C) 2010-2020 Armin Straub, http://arminstraub.com
"""

"""
This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 3 of the License, or
(at your option) any later version.
"""

import sys

from krop.version import __version__
from krop.config import KDE
from PySide2.QtUiTools import QUiLoader
from PyQt5 import QtCore
from krop.viewerselections import ViewerSelections #,ViewerSelectionItem, aspectRatioFromStr

from PyQt5.QtCore import *
from PyQt5.QtGui import *
# QApplication now resides in the new QtWidgets
from PyQt5.QtWidgets import *

import numpy as np

#import PySide2
from PySide2.QtCore import QFile
from krop.qt import QApplication

from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QAction
from PyQt5.QtCore import pyqtSignal, Qt

def main():
    from argparse import ArgumentParser, RawTextHelpFormatter
    parser = ArgumentParser(prog='krop', description=__doc__,
            formatter_class=RawTextHelpFormatter)

    parser.add_argument('-v', '--version', action='version', version='%(prog)s ' + __version__)

    parser.add_argument('file', nargs='?', help='PDF file to open')
    parser.add_argument('-o', '--output', help='where to save the cropped PDF')
    parser.add_argument('--whichpages', help='which pages (e.g. "1-5" or "1,3-") to include in cropped PDF (default: all)')
    parser.add_argument('--rotate', type=int, choices=[0,90,180,270], help='how much to rotate the cropped pdf clockwise (default: 0)')
    parser.add_argument('--optimize', choices=['gs', 'no'], help='whether to optimize the final PDF using ghostscript (default: previous choice)')

    parser.add_argument('--grid', help='if set to 2x3, for instance, creates a 2x3 grid of selections on initial page; if only one number is specified, the number of columns/rows is determined according to whether the page is landscape or portrait')

    parser.add_argument('--initialpage', help='which page to open initially (default: 1)')
    parser.add_argument('--selections', type=str, choices=['all', 'evenodd', 'individual'], help='to which pages should selections apply')
    parser.add_argument('--exceptions', help='pages (e.g. "1-5" or "1,3-") which require individual selections')

    parser.add_argument('--trim', action='store_true', help='if specified, will auto trim initial selections')
    parser.add_argument('--trim-use', type=str, choices=['initial', 'all'], help='whether to inspect only the initial page or all pages (slow!) when auto trimming (default: previous value)')
    parser.add_argument('--trim-padding', help='how much padding to include when auto trimming (default: previous value)')

    parser.add_argument('--go', action='store_true', help='output PDF without opening the krop GUI (using the choices supplied on the command line); if used in a script without X server access, you can run krop using xvfb-run')

    parser.add_argument('--no-kde', action='store_true', help='do not use KDE libraries (default: use if available)')
    parser.add_argument('--no-qt5', action='store_true', help='do not use PyQt5 instead of PyQt4 (default: use PyQt5 if available)')
    parser.add_argument('--no-PyPDF2', action='store_true', help='do not use PyPDF2 instead of pyPdf (default: use PyPDF2 if available)')

    args = parser.parse_args()

    # start the GUI
    if KDE:
        #TODO also use PyKDE5 once more easily available
        from PyKDE4.kdecore import ki18n, KCmdLineArgs, KAboutData
        from PyKDE4.kdeui import KApplication
        appName     = "krop"
        catalog     = ""
        programName = ki18n("krop")
         
        aboutData = KAboutData(appName, catalog, programName, __version__)
         
        KCmdLineArgs.init(aboutData)
        app = KApplication()
    else:
        from krop.qt import QApplication
        app = QApplication(sys.argv)
        app.setApplicationName("krop")

    app.setOrganizationName("arminstraub.com")
    app.setOrganizationDomain("arminstraub.com")

    from krop.mainwindow import MainWindow
    window=MainWindow()

    if args.file is not None:
        fileName = args.file
        try:
            fileName = fileName.decode(sys.stdin.encoding or sys.getdefaultencoding())
        except AttributeError:
            # not necessary (or possible) in python3, which uses unicode
            pass
        window.openFile(fileName)

    if args.output is not None:
        window.ui.editFile.setText(args.output)
    if args.whichpages is not None:
        window.ui.editWhichPages.setText(args.whichpages)
    if args.rotate is not None:
        window.ui.comboRotation.setCurrentIndex({0:0,90:2,180:3,270:1}[args.rotate])
    if args.optimize is not None:
        window.ui.checkGhostscript.setChecked(args.optimize == "gs")
    if args.selections is not None:
        if args.selections == "all":
            window.ui.radioSelAll.setChecked(True)
        elif args.selections == "evenodd":
            window.ui.radioSelEvenOdd.setChecked(True)
        elif args.selections == "individual":
            window.ui.radioSelIndividual.setChecked(True)
    if args.exceptions is not None:
        window.ui.editSelExceptions.setText(args.exceptions)
        window.slotSelExceptionsChanged()
    if args.initialpage is not None:
        window.ui.editCurrentPage.setText(args.initialpage)
        window.slotCurrentPageEdited(args.initialpage)
    if args.trim_use is not None:
        window.ui.checkTrimUseAllPages.setChecked(args.trim_use == "all")
    if args.trim_padding is not None:
        window.ui.editPadding.setText(args.trim_padding)

    # args.grid is specified as 2x3 for 2 cols, 3 rows
    if args.grid:
        window.createSelectionGrid(args.grid)

    if args.trim:
        window.slotTrimMarginsAll()

    # shut down on ctrl+c when pressed in terminal (not gracefully, though)
    # http://stackoverflow.com/questions/4938723/
    import signal
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    if args.go:
        #  sys.stdout.write('kropping...\n')
        from krop.qt import QTimer
        QTimer.singleShot(0, window.slotKrop)
        QTimer.singleShot(0, window.close)
    else:
        #window.show()
        #window.slotFitInView(window.ui.actionFitInView.isChecked())

        # create + add action to window toolbar
        my_widget = MyWidget()
        #my_widget.show()
        action = QAction("add_anki", window)
        window.ui.toolBar.addAction(action)
        action.triggered.connect(lambda x=1: my_widget.slot_anki(1))
        #action.triggered.emit(1)
        #window.setCentralWidget(my_widget)

        
        b1 = QToolButton()
        b1.setText("ndi")
        b1.clicked.connect(lambda x=2,win=window: my_widget.slot_ndi(x,win))
        window.ui.toolBar.addWidget(b1)
        
        b2 = QToolButton()
        b2.setText("min-width")
        b2.clicked.connect(lambda x=3: my_widget.slot_width(3))
        window.ui.toolBar.addWidget(b2)
        
        window.show()
        window.slotFitInView(window.ui.actionFitInView.isChecked())
    # using exec_ because exec is a reserved keyword before python 3
    sys.exit(app.exec_())


# custom widget class extends QWidget, create instance and add to main window or other container widget
from PyQt5.QtWidgets import QMessageBox, QToolButton
import csv
class MyWidget(QWidget):
    # signal
    signal_emitted = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        # Create a label and add it to the my_widget's layout
        #self.label = QLabel("add_ anki")
        #self.label2 = QLabel("ndi_")
        #self.label3 = QLabel("min_ width")
        #self.button_1 = QPushButton("b1")
        #self.button_2 = QPushButton("b2")
        #self.button_3 = QPushButton("b3")

        #layout = QVBoxLayout(self)
        #layout.addWidget(self.label)
        #layout.addWidget(self.label2)
        #layout.addWidget(self.label3)
        #self.filename = None
        #self.mapper()

        # Create a vertical layout and add the buttons
        #layout.addWidget(self.button_1)
        #layout.addWidget(self.button_2)
        #layout.addWidget(self.button_3)

    def mapper(self):
        # multiple signals to one slot fnc
        # Create a signal mapper
        self.signal_mapper = QSignalMapper(self)

        # Create a set of buttons and map them to integer values
        self.button_1 = QPushButton("Button 1")
        self.signal_mapper.setMapping(self.button_1, 1)
        self.button_2 = QPushButton("Button 2")
        self.signal_mapper.setMapping(self.button_2, 2)
        self.button_3 = QPushButton("Button 3")
        self.signal_mapper.setMapping(self.button_3, 3)

        # Connect the buttons to the signal mapper
        self.button_1.clicked.connect(self.signal_mapper.map)
        self.button_2.clicked.connect(self.signal_mapper.map)
        self.button_3.clicked.connect(self.signal_mapper.map)

        # Connect the signal mapper to the slot function
        self.signal_mapper.mapped[int].connect(self.slot)

        # Create a vertical layout and add the buttons
        layout = QVBoxLayout(self)
        layout.addWidget(self.button_1)
        layout.addWidget(self.button_2)
        layout.addWidget(self.button_3)

    def triggered(self):
        sender = QtCore.QObject.sender()
        if sender == self.actionOpMode1:
            # do something
            pass
        elif sender == self.actionOpMode2:
            # do something else
            pass

    def slot(self,n):
        nn = str(n)
        if n == 1: 
            print('open file')
            QMessageBox.about(self, "open file", nn)
            fileName = QFileDialog.getOpenFileName(self,
                self.tr("Open PDF"), "", self.tr("PDF Files (*.pdf)"));
            fileName = fileName[0]
            self.send_anki(fileName)
            return
        elif n == 2:
            print('ndi ', n)
            QMessageBox.about(self, "ndi", nn)
            return
        elif n==3:
            print('min width ', n)
            QMessageBox.about(self, "width", nn)
            return
        

    def slot_anki(self,n):
        QMessageBox.about(self, "open file", str(n))
        if n != 1: return
        fileName = QFileDialog.getOpenFileName(self,
             self.tr("Open PDF"), "", self.tr("PDF Files (*.pdf)"));
        fileName = fileName[0]
        self.send_anki(fileName)
    def send_anki(self,fileName):
        # anki connect
        pass

    def slot_ndi(self,n,win):
        #if n != 2: return
        print('ndi: ', n)
        QMessageBox.about(self, "open file", str(n))
        with open("rects-pts.csv",'r') as f:
            reader = csv.reader(f)
            rects = [ row for row in reader]
        print(rects[-1])
        _,imgwidth,imgheight = str(rects[-1]).split(',')
        #imgwidth = rects[-1].split(',')[-2]
        #imgheight = rects[-1].split(',')[-1]
            

        #for i,( x,y,w,h) in enumerate(rects):
        #    sel = win.selections.addSelection()
        #    r = sel.boundingRect()
        #    w_ = r.width()
        #    h_ = r.height()
        #    p0 = QPointF(r.left()+w_, r.top()+h_)
        #    sel.setBoundingRect(p0, p0 + QPointF(w_, h_))
        #    #sel = self.selections.addSelection()
        #    #r = sel.boundingRect() #QRectF(point,x,y)
        #    #w = r.width()/cols
        #    #h = r.height()/rows
        #    #p0 = QPointF(r.left()+i*w, r.top()+j*h)
        #    #sel.setBoundingRect(p0, p0 + QPointF(w, h))
        #    x,y,w,h = map(float, [x,y,w,h])
        #    print(f"{i}: {x},{y},{w},{h}")
        #    pagesize = win.viewer._pdfdoc.page(0).pageSize() #cropValues(0) )
        #    print('size ', pagesize )
        #    r = QRectF(x,y,w,h) # x,y, w,h
        #    sel = win.selections.addSelection(r)
        #    p0 = QPointF(x, y+h)
        #    sel.setBoundingRect(p0, QPointF(x+w,y) )  #topleft, bottomright
        #    # png:ocr -> pdf-inch -(resolution factor)> img-px
        #    #win.selections.addSelection(r)
        #    #p0 = QPointF(x+w, y+h)
        #    #p0 = QPointF(x-50, y-50)
        #    win.selections.addSelection().setBoundingRect(p0, p0 + QPointF(w-50, h-50))
        #    #win.selections.addSelection().setBoundingRect(


        pagesize = win.viewer._pdfdoc.page(0).pageSize() #cropValues(0) )
        print('pdf size ', pagesize )
        print('image size',imgwidth, imgheight)
        pdf_width, pdf_height = pagesize.width(), pagesize.height()
        ii = imgheight.strip().rstrip("'")
        ii = ii[:-2]
        print("iii", ii)
        image_width, image_height = float(imgwidth), float(ii)

        # Create a transformation matrix to map coordinates from the image to the PDF
        matrix = np.array([[pdf_width / image_width, 0, 0],
                   [0, pdf_height / image_height, 0],
                   [0, 0, 1]])

        # Define a function to transform coordinates from the image to the PDF
        def map_to_pdf(x, y):
            # Apply the transformation matrix to the coordinates
            transformed_coords = np.dot(matrix, np.array([x, y, 1]))
            return transformed_coords[0], transformed_coords[1]
        
        # png:ocr -> pdf-inch -(resolution factor)> img-px
        # pixel -> mm
        dtop, dright, dbottom, dleft = win.getPadding()
        padw, padh = pdf_width - (dleft-dright), pdf_height - (dtop-dbottom)
        scale_pad_w , scale_pad_h = map_to_pdf(padw,padh)
        print(f"_pad: {dtop}, {dright}, {dbottom}, {dleft}")
        print(f"_padscale: {scale_pad_w} {scale_pad_h}")
        for i,( x,y,w,h) in enumerate(rects[:-1]):
            x,y,w,h = map(float, [x,y,w,h])
            print(f"{i}_img: {x}, {y}, {x+w}, {y+h}")
            *topleft, = map_to_pdf(x,y)
            *btmright, = map_to_pdf( (x+w), (y+h))
            print(f"{i}_pdf: {topleft}, {btmright}")
            rec = QRectF( *topleft, *btmright)
            rt=rec.translated(2,2)
            win.selections.addSelection(rt)
            continue
            
            dtop, dright, dbottom, dleft = win.getPadding()
            padw, padh = pdf_width - (dleft-dright), pdf_height - (dtop-dbottom)
            print(f"{i}_pad: {dtop}, {dright}, {dbottom}, {dleft}")
            scalex, scaley = pdf_width/image_width, pdf_height/image_height
            #dpi=72
            #scalex, scaley = image_width/dpi, image_height/dpi
            #sx,sy,sw,sh = (x+4)*scalex, (y-4)*scaley, (w+4)*scalex, (h+4)*scaley
            sx,sy,sw,sh = x*scalex+4, y*scaley+4, w*scalex+4, h*scaley+4
            #sx,sy,sw,sh = x,pdf_height- y, w, pdf_height-h
            #sx,sy,sw,sh = x*scalex,pdf_height-( y*scaley), w*scalex, pdf_height-(h*scaley)
            print(f"{i}_scaled: {sx}, {sy}, {sw}, {sh}")
            sr = QRectF(sx,sy,sw,sh) # x,y, w,h
            win.selections.addSelection(sr)
            continue
            ###
            xp,yp = map(lambda i: i*72/300, [x,y])
            wp,hp = w*(pdf_width/(image_width-50)), h*(pdf_height/(image_height-50))
            print(f"{i}_pdf: {xp}, {yp}, {wp}, {hp}")
            r = QRectF(xp,yp,wp,hp) # x,y, w,h
            print('coords',r.getCoords() )
            #win.selections.addSelection(r)
            #sel = win.selections.addSelection(r)
            p0 = QPointF(xp, yp+hp)
            win.selections.addSelection().setBoundingRect(p0, p0+QPointF(wp,hp) )  #topleft, bottomright
            #win.selections.addSelection(r)
            #p0 = QPointF(x+w, y+h)
            #p0 = QPointF(x-50, y-50)
            #win.selections.addSelection().setBoundingRect(p0, p0 + QPointF(w-50, h-50))
            #win.selections.addSelection().setBoundingRect(
        win.pdfScene.update()
        print("num rects",i)

    def send_ndi(self,fileName):
        # change the number of dilations
        pass

    def slot_width(self,n):
        QMessageBox.about(self, "open file", str(n))
        if n != 3: return
    def send_width(self,fileName):
        # min width for contour
        pass

#    def mouseReleaseEvent(self, QMouseEvent):
#        print('(m', QMouseEvent.pos().x(), ', ', QMouseEvent.pos().y(), ')')

#monkey
def mnk_mouseReleaseEvent(self,e):
    print('(m',e.pos().x(), ', ',e.pos().y(), ')')
    ViewerSelections.mouseReleaseEvent(self,e)

#ViewerSelections.mouseReleaseEvent = mnk_mouseReleaseEvent
def monkeypatch_method(cls):
    def decorator(func):
        setattr(cls, func.__name__, func)
        return func
    return decorator

@monkeypatch_method(ViewerSelections)
def mouseReleaseEvent(self, args):
    return print('(m',args.pos().x(), ', ',args.pos().y(), ')')


if __name__=="__main__":
    main()

