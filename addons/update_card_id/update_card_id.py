from anki.hooks import addHook
from aqt import mw
from aqt.qt import QAction
from aqt.utils import tooltip

from anki import hooks

from anki.hooks import addHook
from aqt import mw
from aqt.qt import QAction
import datetime

# adds creation date to dates field of template_basic note type

def update_card_id(note):
    field_name = "dates"
    target_note_type = ["template_basic",
                        "template_field_hidden copy",
                        "berkeley-Cloze-SansForgetica",
                        "berkeley-notes-link",
                        "berekeley-basic-test",
                        "berkeley-Cloze"]
                        # Replace this with the desired note type name

    # Check if the note type matches the target note type
    if note.model()['name'] not in target_note_type:
        return

    if field_name not in note:
        return

    card_id = note.id
    note[field_name] = str(card_id)
    note['dates'] = datetime.datetime.fromtimestamp(card_id/1000).strftime('%m/%d/%y')
    note.flush()

def update_selected_cards(browser):
    selected_notes = browser.selectedNotes()
    for note_id in selected_notes:
        note = mw.col.get_note(note_id)
        update_card_id(note)


def on_setup_menus(browser):
    action = QAction("Update CardId", browser)
    action.triggered.connect(lambda: update_selected_cards(browser))
    browser.form.menuEdit.addAction(action)


addHook("browser.setupMenus", on_setup_menus)


