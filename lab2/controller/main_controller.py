import math
from model.book import Book
from model.db_handler import DatabaseHandler
from model.xml_handler import XmlHandler, XmlLoader


class MainController:
    def __init__(self, view, db_handler: DatabaseHandler):
        self.view = view
        self.db = db_handler
        self.current_page = 1
        self.records_per_page = 10
        self.total_records = 0
        self.total_pages = 1

    def update_pagination_stats(self):
        self.total_records = self.db.get_total_count()
        self.total_pages = math.ceil(self.total_records / self.records_per_page)
        if self.total_pages == 0:
            self.total_pages = 1
        if self.current_page > self.total_pages:
            self.current_page = self.total_pages

    def load_main_data(self):
        self.update_pagination_stats()
        offset = (self.current_page - 1) * self.records_per_page
        books = self.db.get_books_page(limit=self.records_per_page, offset=offset)
        self.view.update_table(books)
        self.view.update_pagination_labels(self.current_page, self.total_pages, self.total_records)

    def set_page_size(self, size: int):
        self.records_per_page = size
        self.current_page = 1
        self.load_main_data()

    def next_page(self):
        if self.current_page < self.total_pages:
            self.current_page += 1
            self.load_main_data()

    def prev_page(self):
        if self.current_page > 1:
            self.current_page -= 1
            self.load_main_data()

    def first_page(self):
        self.current_page = 1
        self.load_main_data()

    def last_page(self):
        self.current_page = self.total_pages
        self.load_main_data()

    def add_record(self, book_data: dict):
        book = Book(**book_data)
        self.db.add_book(book)
        self.load_main_data()

    def delete_records(self, conditions: dict) -> int:
        deleted_count = self.db.delete_books(**conditions)
        self.load_main_data()
        return deleted_count

    def execute_search(self, conditions: dict, page: int, size: int):
        return self.db.search_books(**conditions, limit=size, offset=(page - 1) * size)

    def export_to_xml(self, filename: str):
        books = self.db.get_all_books()
        XmlHandler.save_to_xml(books, filename)

    def import_from_xml(self, filename: str):
        books = XmlLoader.load_from_xml(filename)
        self.db.clear_database()
        for book in books:
            self.db.add_book(book)
        self.current_page = 1
        self.load_main_data()