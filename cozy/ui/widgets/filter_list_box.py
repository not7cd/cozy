from typing import List

from gi.repository import Gtk

from cozy.ui.list_box_row_with_data import ListBoxRowWithData
from cozy.ui.list_box_separator_row import ListBoxSeparatorRow


class FilterListBox(Gtk.ListBox):
    __gtype_name__ = 'FilterListBox'

    def __init__(self, **properties):
        super().__init__(**properties)

    def populate(self, elements: List[str]):
        self.remove_all_children()

        all_row = ListBoxRowWithData(_("All"), False)
        all_row.set_tooltip_text(_("Display all books"))
        self.add(all_row)
        self.add(ListBoxSeparatorRow())
        self.select_row(all_row)

        for element in elements:
            row = ListBoxRowWithData(element, False)
            self.add(row)

        self.show_all()
