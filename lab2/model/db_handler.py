import sqlite3
from typing import List, Optional, Tuple, Any
from model.book import Book


class DatabaseHandler:
    def __init__(self, db_name: str = "library.db"):
        self.db_name = db_name
        self._create_table()

    def _create_table(self):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                           CREATE TABLE IF NOT EXISTS books
                           (
                               id INTEGER PRIMARY KEY AUTOINCREMENT,
                               title TEXT NOT NULL,
                               author TEXT NOT NULL,
                               publisher TEXT NOT NULL,
                               volumes INTEGER NOT NULL,
                               print_run INTEGER NOT NULL,
                               total_volumes INTEGER NOT NULL
                           )
                           """)
            conn.commit()

    def add_book(self, book: Book) -> int:
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                           INSERT INTO books (title, author, publisher, volumes, print_run, total_volumes)
                           VALUES (?, ?, ?, ?, ?, ?)
                           """,
                           (book.title, book.author, book.publisher, book.volumes, book.print_run, book.total_volumes))
            conn.commit()
            return cursor.lastrowid

    def search_books(self,
                     title: Optional[str] = None,
                     author: Optional[str] = None,
                     publisher: Optional[str] = None,
                     v_min: Optional[int] = None,
                     v_max: Optional[int] = None,
                     run_val: Optional[int] = None,
                     run_mode: Optional[str] = None,
                     total_val: Optional[int] = None,
                     total_mode: Optional[str] = None,
                     limit: int = 10,
                     offset: int = 0) -> Tuple[List[Book], int]:

        query = "SELECT id, title, author, publisher, volumes, print_run, total_volumes FROM books WHERE 1=1"
        params: List[Any] = []

        if author:
            if publisher:
                query += " AND author = ? AND publisher = ?"
                params.extend([author, publisher])
            else:
                query += " AND author = ?"
                params.append(author)

        if v_min is not None and v_max is not None:
            query += " AND volumes BETWEEN ? AND ?"
            params.extend([v_min, v_max])

        if title:
            query += " AND title LIKE ?"
            params.append(f"%{title}%")

        if run_val is not None and run_mode:
            op = ">" if run_mode == "more" else "<"
            query += f" AND print_run {op} ?"
            params.append(run_val)

        if total_val is not None and total_mode:
            op = ">" if total_mode == "more" else "<"
            query += f" AND total_volumes {op} ?"
            params.append(total_val)

        count_query = query.replace("SELECT id, title, author, publisher, volumes, print_run, total_volumes",
                                    "SELECT COUNT(*)")

        final_query = query + " LIMIT ? OFFSET ?"
        final_params = params + [limit, offset]

        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute(count_query, params)
            total_found = cursor.fetchone()[0]

            cursor.execute(final_query, final_params)
            rows = cursor.fetchall()

            books = [Book(title=r[1], author=r[2], publisher=r[3],
                          volumes=r[4], print_run=r[5], id=r[0]) for r in rows]

        return books, total_found

    def delete_books(self,
                     author: Optional[str] = None,
                     publisher: Optional[str] = None,
                     v_min: Optional[int] = None,
                     v_max: Optional[int] = None,
                     title: Optional[str] = None,
                     run_val: Optional[int] = None,
                     run_mode: Optional[str] = None,
                     total_val: Optional[int] = None,
                     total_mode: Optional[str] = None) -> int:

        conditions = []
        params = []

        if author:
            if publisher:
                conditions.append("author = ? AND publisher = ?")
                params.extend([author, publisher])
            else:
                conditions.append("author = ?")
                params.append(author)

        if v_min is not None and v_max is not None:
            conditions.append("volumes BETWEEN ? AND ?")
            params.extend([v_min, v_max])

        if title:
            conditions.append("title = ?")
            params.append(title)

        if run_val is not None and run_mode:
            op = ">" if run_mode == "more" else "<"
            conditions.append(f"print_run {op} ?")
            params.append(run_val)

        if total_val is not None and total_mode:
            op = ">" if total_mode == "more" else "<"
            conditions.append(f"total_volumes {op} ?")
            params.append(total_val)

        if not conditions:
            return 0

        query = f"DELETE FROM books WHERE {' OR '.join(conditions)}"

        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            deleted_count = cursor.rowcount
            conn.commit()
            return deleted_count

    def get_total_count(self) -> int:
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM books")
            return cursor.fetchone()[0]

    def get_all_books(self) -> List[Book]:
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, title, author, publisher, volumes, print_run, total_volumes FROM books")
            rows = cursor.fetchall()
            return [Book(title=r[1], author=r[2], publisher=r[3],
                         volumes=r[4], print_run=r[5], id=r[0]) for r in rows]

    def get_books_page(self, limit: int, offset: int) -> List[Book]:
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, title, author, publisher, volumes, print_run, total_volumes FROM books LIMIT ? OFFSET ?",
                (limit, offset))
            rows = cursor.fetchall()
            return [Book(title=r[1], author=r[2], publisher=r[3],
                         volumes=r[4], print_run=r[5], id=r[0]) for r in rows]

    def clear_database(self):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM books")
            cursor.execute("DELETE FROM sqlite_sequence WHERE name='books'")
            conn.commit()
