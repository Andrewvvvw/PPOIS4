from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTableView,
    QTreeView,
    QPushButton,
    QLabel,
    QSpinBox,
    QToolBar,
    QStackedWidget,
    QMessageBox,
    QFileDialog
)
from PySide6.QtGui import QAction, QStandardItemModel, QStandardItem
from view.table_model import BookTableModel


class MainWindow(QMainWindow):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.setWindowTitle("Библиотека")
        self.resize(800, 600)

        self.table_model = BookTableModel()
        self.tree_model = QStandardItemModel()
        self.tree_model.setHorizontalHeaderLabels(["Записи (Книги)"])

        self._setup_ui()
        self._setup_menu_and_toolbar()

    def _setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        self.stacked_widget = QStackedWidget()

        self.table_view = QTableView()
        self.table_view.setModel(self.table_model)
        self.table_view.horizontalHeader().setStretchLastSection(True)
        self.stacked_widget.addWidget(self.table_view)

        self.tree_view = QTreeView()
        self.tree_view.setModel(self.tree_model)
        self.stacked_widget.addWidget(self.tree_view)

        main_layout.addWidget(self.stacked_widget)

        pagination_layout = QHBoxLayout()

        self.btn_first = QPushButton("<< Первая")
        self.btn_prev = QPushButton("< Пред")
        self.btn_next = QPushButton("След >")
        self.btn_last = QPushButton("Последняя >>")

        self.btn_first.clicked.connect(self.controller.first_page)
        self.btn_prev.clicked.connect(self.controller.prev_page)
        self.btn_next.clicked.connect(self.controller.next_page)
        self.btn_last.clicked.connect(self.controller.last_page)

        self.spin_size = QSpinBox()
        self.spin_size.setRange(1, 100)
        self.spin_size.setValue(10)
        self.spin_size.valueChanged.connect(self.controller.set_page_size)

        self.lbl_stats = QLabel("Страница: 1/1 | Всего записей: 0")

        pagination_layout.addWidget(self.btn_first)
        pagination_layout.addWidget(self.btn_prev)
        pagination_layout.addWidget(QLabel("Записей на стр:"))
        pagination_layout.addWidget(self.spin_size)
        pagination_layout.addWidget(self.lbl_stats)
        pagination_layout.addWidget(self.btn_next)
        pagination_layout.addWidget(self.btn_last)

        main_layout.addLayout(pagination_layout)

    def _setup_menu_and_toolbar(self):
        menubar = self.menuBar()
        file_menu = menubar.addMenu("Файл")
        view_menu = menubar.addMenu("Вид")
        records_menu = menubar.addMenu("Записи")

        toolbar = QToolBar("Главная панель")
        self.addToolBar(toolbar)

        actions = [
            ("Добавить", self.open_add_dialog, records_menu),
            ("Поиск", self.open_search_dialog, records_menu),
            ("Удалить", self.open_delete_dialog, records_menu),
            ("Экспорт XML", self.export_xml, file_menu),
            ("Импорт XML", self.import_xml, file_menu),
            ("Таблица/Дерево", self.toggle_view, view_menu)
        ]

        for name, slot, menu in actions:
            action = QAction(name, self)
            action.triggered.connect(slot)
            menu.addAction(action)
            toolbar.addAction(action)

    def update_table(self, books):
        self.table_model.update_data(books)
        self._update_tree(books)

    def _update_tree(self, books):
        self.tree_model.removeRows(0, self.tree_model.rowCount())
        for book in books:
            root_item = QStandardItem(f"Книга: {book.title}")
            root_item.setEditable(False)

            fields = [
                f"Автор: {book.author}",
                f"Издательство: {book.publisher}",
                f"Томов: {book.volumes}",
                f"Тираж: {book.print_run}",
                f"Итого томов: {book.total_volumes}"
            ]

            for field in fields:
                child_item = QStandardItem(field)
                child_item.setEditable(False)
                root_item.appendRow(child_item)

            self.tree_model.appendRow(root_item)
        self.tree_view.expandAll()

    def update_pagination_labels(self, current_page, total_pages, total_records):
        self.lbl_stats.setText(f"Страница: {current_page}/{total_pages} | Всего записей: {total_records}")

        self.btn_first.setEnabled(current_page > 1)
        self.btn_prev.setEnabled(current_page > 1)
        self.btn_next.setEnabled(current_page < total_pages)
        self.btn_last.setEnabled(current_page < total_pages)

    def toggle_view(self):
        current_idx = self.stacked_widget.currentIndex()
        self.stacked_widget.setCurrentIndex((current_idx + 1) % 2)

    def open_add_dialog(self):
        from view.add_dialog import AddBookDialog
        dialog = AddBookDialog(self)
        if dialog.exec():
            data = dialog.get_data()
            self.controller.add_record(data)

    def open_search_dialog(self):
        from view.search_dialog import SearchDialog
        dialog = SearchDialog(self.controller, self)
        dialog.exec()

    def open_delete_dialog(self):
        from view.delete_dialog import DeleteDialog
        dialog = DeleteDialog(self)
        if dialog.exec():
            conditions = dialog.get_data()
            if not conditions:
                QMessageBox.information(self, "Инфо", "Условия удаления не заданы.")
                return

            deleted_count = self.controller.delete_records(conditions)

            if deleted_count > 0:
                QMessageBox.information(self, "Успех", f"Удалено записей: {deleted_count}")
            else:
                QMessageBox.warning(self, "Результат", "Записи по данным условиям не найдены.")

    def export_xml(self):
        filename, _ = QFileDialog.getSaveFileName(self, "Сохранить в XML", "", "XML Files (*.xml)")
        if filename:
            try:
                self.controller.export_to_xml(filename)
                QMessageBox.information(self, "Успех", "Данные успешно экспортированы.")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить файл: {str(e)}")

    def import_xml(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Открыть XML", "", "XML Files (*.xml)")
        if filename:
            try:
                self.controller.import_from_xml(filename)
                QMessageBox.information(self, "Успех", "Данные успешно импортированы и добавлены в БД.")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить файл: {str(e)}")