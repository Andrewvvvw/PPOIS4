from PySide6.QtCore import QAbstractTableModel, Qt
from typing import List, Any
from model.book import Book

class BookTableModel(QAbstractTableModel):
    def __init__(self, books: List[Book] = None):
        super().__init__()
        self.books = books or []
        self.headers = ["Название", "Автор", "Издательство", "Томов", "Тираж", "Итого томов"]

    def rowCount(self, parent=None) -> int:
        return len(self.books)

    def columnCount(self, parent=None) -> int:
        return len(self.headers)

    def data(self, index, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
        if not index.isValid() or role != Qt.ItemDataRole.DisplayRole:
            return None

        book = self.books[index.row()]
        col = index.column()

        if col == 0:
            return book.title
        elif col == 1:
            return book.author
        elif col == 2:
            return book.publisher
        elif col == 3:
            return book.volumes
        elif col == 4:
            return book.print_run
        elif col == 5:
            return book.total_volumes
        return None

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
        if role == Qt.ItemDataRole.DisplayRole and orientation == Qt.Orientation.Horizontal:
            return self.headers[section]
        return None

    def update_data(self, new_books: List[Book]):
        self.beginResetModel()
        self.books = new_books
        self.endResetModel()