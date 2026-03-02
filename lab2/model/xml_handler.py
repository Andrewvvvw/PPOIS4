import xml.dom.minidom as minidom
import xml.sax as sax
from model.book import Book


class XmlHandler:
    @staticmethod
    def save_to_xml(books: list[Book], filename: str):
        doc = minidom.Document()

        root = doc.createElement("library")
        doc.appendChild(root)

        for book_obj in books:
            book_node = doc.createElement("book")

            def create_element(name, value):
                node = doc.createElement(name)
                node.appendChild(doc.createTextNode(str(value)))
                return node

            book_node.appendChild(create_element("title", book_obj.title))
            book_node.appendChild(create_element("author", book_obj.author))
            book_node.appendChild(create_element("publisher", book_obj.publisher))
            book_node.appendChild(create_element("volumes", book_obj.volumes))
            book_node.appendChild(create_element("print_run", book_obj.print_run))
            book_node.appendChild(create_element("total_volumes", book_obj.total_volumes))

            root.appendChild(book_node)

        with open(filename, "w", encoding="utf-16") as f:
            f.write(doc.toprettyxml(indent="  "))


class BookSaxHandler(sax.ContentHandler):
    def __init__(self):
        self.books = []
        self.current_data = {}
        self.current_tag = ""
        self.buffer = ""

    def startElement(self, tag, attributes):
        self.current_tag = tag
        self.buffer = ""

    def characters(self, content):
        self.buffer += content.strip()

    def endElement(self, tag):
        if tag == "book":
            book = Book(
                title=self.current_data.get("title", ""),
                author=self.current_data.get("author", ""),
                publisher=self.current_data.get("publisher", ""),
                volumes=int(self.current_data.get("volumes", 0)),
                print_run=int(self.current_data.get("print_run", 0))
            )
            self.books.append(book)
        elif tag != "library":
            self.current_data[tag] = self.buffer
        self.current_tag = ""


class XmlLoader:
    @staticmethod
    def load_from_xml(filename: str) -> list[Book]:
        handler = BookSaxHandler()
        parser = sax.make_parser()
        parser.setContentHandler(handler)
        parser.parse(filename)
        return handler.books
