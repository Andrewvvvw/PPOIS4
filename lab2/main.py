import sys
from PySide6.QtWidgets import QApplication
from model.db_handler import DatabaseHandler
from controller.main_controller import MainController
from view.main_window import MainWindow


def main():
    app = QApplication(sys.argv)

    db = DatabaseHandler("library.db")
    db.clear_database()

    controller = MainController(view=None, db_handler=db)
    window = MainWindow(controller)
    controller.view = window

    controller.load_main_data()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
