from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QGridLayout,
                               QLineEdit, QSpinBox, QComboBox, QPushButton,
                               QLabel, QTableView, QHeaderView)
from view.table_model import BookTableModel


class SearchDialog(QDialog):
    def __init__(self, controller, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.setWindowTitle("Поиск книг")
        self.resize(900, 600)

        self.current_page = 1
        self.page_size = 10
        self.total_found = 0
        self.total_pages = 1

        self.table_model = BookTableModel()
        self._setup_ui()

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        filter_group = QGridLayout()

        self.in_title = QLineEdit()
        self.in_author = QLineEdit()
        self.in_publisher = QLineEdit()

        self.in_v_min = QSpinBox()
        self.in_v_max = QSpinBox()
        self.in_v_max.setMaximum(100000)

        self.in_run_val = QSpinBox()
        self.in_run_val.setMaximum(10 ** 9)
        self.in_run_mode = QComboBox()
        self.in_run_mode.addItems(["more", "less"])

        self.in_total_val = QSpinBox()
        self.in_total_val.setMaximum(10 ** 9)
        self.in_total_mode = QComboBox()
        self.in_total_mode.addItems(["more", "less"])

        filter_group.addWidget(QLabel("Название:"), 0, 0)
        filter_group.addWidget(self.in_title, 0, 1)
        filter_group.addWidget(QLabel("Автор:"), 0, 2)
        filter_group.addWidget(self.in_author, 0, 3)

        filter_group.addWidget(QLabel("Издательство:"), 1, 0)
        filter_group.addWidget(self.in_publisher, 1, 1)
        filter_group.addWidget(QLabel("Томов (от/до):"), 1, 2)
        h_vol = QHBoxLayout()
        h_vol.addWidget(self.in_v_min)
        h_vol.addWidget(self.in_v_max)
        filter_group.addLayout(h_vol, 1, 3)

        filter_group.addWidget(QLabel("Тираж (>/<):"), 2, 0)
        h_run = QHBoxLayout()
        h_run.addWidget(self.in_run_mode)
        h_run.addWidget(self.in_run_val)
        filter_group.addLayout(h_run, 2, 1)

        filter_group.addWidget(QLabel("Итого (>/<):"), 2, 2)
        h_tot = QHBoxLayout()
        h_tot.addWidget(self.in_total_mode)
        h_tot.addWidget(self.in_total_val)
        filter_group.addLayout(h_tot, 2, 3)

        main_layout.addLayout(filter_group)

        btn_search = QPushButton("Найти")
        btn_search.clicked.connect(self.perform_search)
        main_layout.addWidget(btn_search)

        self.results_table = QTableView()
        self.results_table.setModel(self.table_model)
        self.results_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        main_layout.addWidget(self.results_table)

        pager = QHBoxLayout()

        self.btn_first = QPushButton("<< Первая")
        self.btn_prev = QPushButton("< Пред")
        self.btn_next = QPushButton("След >")
        self.btn_last = QPushButton("Последняя >>")

        self.spin_size = QSpinBox()
        self.spin_size.setRange(1, 100)
        self.spin_size.setValue(10)

        self.lbl_info = QLabel("Страница: 1/1 | Найдено записей: 0")

        self.btn_first.clicked.connect(self.first_page)
        self.btn_prev.clicked.connect(lambda: self.change_page(-1))
        self.btn_next.clicked.connect(lambda: self.change_page(1))
        self.btn_last.clicked.connect(self.last_page)
        self.spin_size.valueChanged.connect(self.change_size)

        pager.addWidget(self.btn_first)
        pager.addWidget(self.btn_prev)
        pager.addWidget(QLabel("Записей на стр:"))
        pager.addWidget(self.spin_size)
        pager.addWidget(self.lbl_info)
        pager.addWidget(self.btn_next)
        pager.addWidget(self.btn_last)

        main_layout.addLayout(pager)

    def get_filters(self):
        return {
            "title": self.in_title.text().strip() or None,
            "author": self.in_author.text().strip() or None,
            "publisher": self.in_publisher.text().strip() or None,
            "v_min": self.in_v_min.value() if self.in_v_max.value() > 0 else None,
            "v_max": self.in_v_max.value() if self.in_v_max.value() > 0 else None,
            "run_val": self.in_run_val.value() if self.in_run_val.value() > 0 else None,
            "run_mode": self.in_run_mode.currentText(),
            "total_val": self.in_total_val.value() if self.in_total_val.value() > 0 else None,
            "total_mode": self.in_total_mode.currentText()
        }

    def perform_search(self):
        self.current_page = 1
        self._update_results()

    def change_size(self, size):
        self.page_size = size
        self.current_page = 1
        self._update_results()

    def change_page(self, delta):
        self.current_page += delta
        self._update_results()

    def first_page(self):
        self.current_page = 1
        self._update_results()

    def last_page(self):
        self.current_page = self.total_pages
        self._update_results()

    def _update_results(self):
        filters = self.get_filters()
        books, total = self.controller.execute_search(filters, self.current_page, self.page_size)
        self.total_found = total
        self.table_model.update_data(books)

        self.total_pages = max(1, (total + self.page_size - 1) // self.page_size)

        self.lbl_info.setText(f"Страница: {self.current_page}/{self.total_pages} | Найдено записей: {total}")

        self.btn_first.setEnabled(self.current_page > 1)
        self.btn_prev.setEnabled(self.current_page > 1)
        self.btn_next.setEnabled(self.current_page < self.total_pages)
        self.btn_last.setEnabled(self.current_page < self.total_pages)