from enum import Enum, auto

from cozy.application_settings import ApplicationSettings
from cozy.architecture.observable import Observable
from cozy.control.db import get_db
from cozy.control.filesystem_monitor import FilesystemMonitor
from cozy.control.importer import Importer, importer as importer_instance
from cozy.media.player import Player
from cozy.model.book import Book
from cozy.model.chapter import Chapter
from cozy.model.library import Library
from cozy.ui.book_element import BookElement


class LibraryViewMode(Enum):
    CURRENT = auto()
    AUTHOR = auto()
    READER = auto()


class LibraryViewModel(Observable):

    def __init__(self):
        super().__init__()

        self._model = Library(get_db())

        self._fs_monitor: FilesystemMonitor = FilesystemMonitor()
        self._application_settings: ApplicationSettings = ApplicationSettings()
        self._importer: Importer = importer_instance
        self._player: Player = Player()

        self._library_view_mode: LibraryViewMode = LibraryViewMode.CURRENT
        self._selected_filter: str = _("All")

        self._connect()

    def _connect(self):
        self._fs_monitor.add_listener(self._on_fs_monitor_event)
        self._application_settings.add_listener(self._on_application_setting_changed)
        self._importer.add_listener(self._on_importer_event)
        self._player.add_listener(self._on_player_event)

    @property
    def books(self):
        return self._model.books

    @property
    def library_view_mode(self):
        return self._library_view_mode

    @library_view_mode.setter
    def library_view_mode(self, value):
        self._library_view_mode = value
        self._notify("library_view_mode")

    @property
    def selected_filter(self):
        return self._selected_filter

    @selected_filter.setter
    def selected_filter(self, value):
        self._selected_filter = value
        self._notify("selected_filter")

    @property
    def is_any_book_in_progress(self):
        return any(book.position > 0 for book in self.books)

    @property
    def authors(self):
        is_book_online = self._fs_monitor.get_book_online
        show_offline_books = not self._application_settings.hide_offline
        swap_author_reader = self._application_settings.swap_author_reader

        authors = {
            book.author if not swap_author_reader else book.reader
            for book
            in self._model.books
            if is_book_online(book) or show_offline_books
        }

        return sorted(authors)

    @property
    def readers(self):
        is_book_online = self._fs_monitor.get_book_online
        show_offline_books = not self._application_settings.hide_offline
        swap_author_reader = self._application_settings.swap_author_reader

        readers = {
            book.reader if not swap_author_reader else book.author
            for book
            in self._model.books
            if is_book_online(book) or show_offline_books
        }

        return sorted(readers)

    def playback_book(self, book: Book):
        # Pause/Play book here
        pass

    def switch_screen(self, screen: str):
        pass

    def display_book_filter(self, book_element: BookElement):
        book = book_element.book
        swap_author_reader = self._application_settings.swap_author_reader
        author = book.author if not swap_author_reader else book.reader
        reader = book.reader if not swap_author_reader else book.author

        hide_offline_books = self._application_settings.hide_offline
        book_is_online = self._fs_monitor.get_book_online(book)

        if hide_offline_books and not book_is_online and not book.downloaded:
            return False

        if self.library_view_mode == LibraryViewMode.CURRENT:
            return True if book.last_played > 0 else False

        if self.selected_filter == _("All"):
            return True
        elif self.library_view_mode == LibraryViewMode.AUTHOR:
            return True if author == self.selected_filter else False
        elif self.library_view_mode == LibraryViewMode.READER:
            return True if reader == self.selected_filter else False

    def display_book_sort(self, book_element1, book_element2):
        if self._library_view_mode == LibraryViewMode.CURRENT:
            return book_element1.book.last_played < book_element2.book.last_played
        else:
            return book_element1.book.name.lower() > book_element2.book.name.lower()

    def _on_fs_monitor_event(self, event, _):
        if event == "storage-online":
            self._notify("authors")
            self._notify("readers")
            self._notify("books-filter")
        elif event == "storage-offline":
            self._notify("authors")
            self._notify("readers")
            self._notify("books-filter")
        elif event == "external-storage-added":
            pass
        elif event == "external-storage-removed":
            pass

    def _on_application_setting_changed(self, event, _):
        if event == "hide-offline":
            self._notify("authors")
            self._notify("readers")
            self._notify("books-filter")
        elif event == "swap-author-reader":
            self._notify("authors")
            self._notify("readers")

    def _on_importer_event(self, event, _):
        if event == "import-finished":
            self._model.invalidate()
            self._notify("authors")
            self._notify("readers")
            self._notify("books")
            self._notify("books-filter")
            self._notify("library_view_mode")

    def _on_player_event(self, event, message):
        if event == "play":
            track_id = message
            book = None

            for b in self._model.books:
                if any(chapter.id == track_id for chapter in b.chapters):
                    book = b
                    break

            if book:
                book.reload()
                self._notify("books-filter")
