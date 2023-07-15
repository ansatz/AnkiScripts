from aqt.qt import *
from anki.hooks import addHook
from aqt.utils import tooltip
from anki.utils import timestampID
import re

def createDuplicate(self):
    mw = self.mw
    # Get deck of first selected card
    cids = self.selectedCards()
    if not cids:
        tooltip(_("No cards selected."), period=2000)
        return
    did = mw.col.db.scalar(
        "select did from cards where id = ?", cids[0])
    deck = mw.col.decks.get(did)
    if deck['dyn']:
        tooltip(_("Cards can't be duplicated when they are in a filtered deck."), period=2000)
        return
    
    # Set checkpoint
    mw.progress.start()
    mw.checkpoint("merge notes")
    self.model.beginReset()

    # read notes
    src=[]
    for nid in self.selectedNotes():
        # print "Found note: %s" % (nid)
        note = mw.col.getNote(nid)
        n = note["src_merge"]
        nn = re.split('<br>|\n', n)
        src.extend(nn)

    # write notes
    uniq = list(set(src))
    #uniq = [ re.replace(  for i in uniq ]
    SRCT = "\n".join( map(str,uniq))
    for nid in self.selectedNotes():
        # print "Found note: %s" % (nid)
        note = mw.col.getNote(nid)
        note["src_merge"] = SRCT
        note.flush() #save changes

#        model = note._model
#        
#        # Assign model to deck
#        mw.col.decks.select(deck['id'])
#        mw.col.decks.get(deck)['mid'] = model['id']
#        mw.col.decks.save(deck)
#
#        # Assign deck to model
#        mw.col.models.setCurrent(model)
#        mw.col.models.current()['did'] = deck['id']
#        mw.col.models.save(model)
#        
#        # Create new note
#        note_copy = mw.col.newNote()
#        # Copy tags and fields (all model fields) from original note
#        note_copy.tags = note.tags
#        note_copy.fields = note.fields
#
#        # Refresh note and add to database
#        note_copy.flush()
#        mw.col.addNote(note_copy)
#         

    # Reset collection and main window
    self.model.endReset()
    mw.col.reset()
    mw.reset()
    mw.progress.finish()

    tooltip(_(f"Notes merged.\n {SRCT}"), period=1000)

def setupMenu(self):
    menu = self.form.menuEdit
    menu.addSeparator()
    a = menu.addAction('src_field_merge')
    #a.setShortcut(QKeySequence("Ctrl+Alt+C"))
    a.triggered.connect(lambda _, b=self: onCreateDuplicate(b))

def onCreateDuplicate(self):
    createDuplicate(self)

addHook("browser.setupMenus", setupMenu)
