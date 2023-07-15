from aqt import mw
from aqt.qt import *
from aqt.utils import showInfo
from anki.hooks import addHook
from anki.utils import intTime

def change_tags(browser, n_days=7):
    # Get the selected cards
    selected_card_ids = browser.selected_cards()

    # Calculate the timestamp for n days ago
    days_ago = intTime() - (n_days * 86400)

    for card_id in selected_card_ids:
        card = mw.col.getCard(card_id)

        # Check if the card was reviewed in the last n days
        if card.mod > days_ago:
            is_buried = bool(mw.col.find_cards(f"cid:{card_id} is:buried"))

            if is_buried:
                # Change the tag from __select__ to __filter__ if the card is marked and buried
                if "__select__" in card.note().tags:
                    card.note().delTag("__select__")
                    card.note().addTag("__filter__")
                    card.note().flush()
            else:
                # Change the tag from __filter__ to __select__ if the card is marked and not buried
                if "__filter__" in card.note().tags:
                    card.note().delTag("__filter__")
                    card.note().addTag("__select__")
                    card.note().flush()

    showInfo("Tags have been updated!")

def on_setup_menus(browser):
    menu = browser.form.menuEdit
    menu.addSeparator()
    action = menu.addAction('Update Tags2')
    action.triggered.connect(lambda _, b=browser: change_tags(b))

addHook("browser.setupMenus", on_setup_menus)

