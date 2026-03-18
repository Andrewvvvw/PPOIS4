from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QFormLayout,
    QLineEdit,
    QSpinBox,
    QDialogButtonBox,
    QMessageBox
)


class AddBookDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Добавить книгу")
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        self.edit_title = QLineEdit()
        self.edit_author = QLineEdit()
        self.edit_publisher = QLineEdit()

        self.spin_volumes = QSpinBox()
        self.spin_volumes.setRange(1, 1000000)

        self.spin_run = QSpinBox()
        self.spin_run.setRange(1, 1000000000)

        form_layout.addRow("Название книги:", self.edit_title)
        form_layout.addRow("ФИО автора:", self.edit_author)
        form_layout.addRow("Издательство:", self.edit_publisher)
        form_layout.addRow("Число томов:", self.spin_volumes)
        form_layout.addRow("Тираж:", self.spin_run)

        layout.addLayout(form_layout)

        self.buttons = QDialogButtonBox()
        self.buttons.addButton(QDialogButtonBox.StandardButton.Ok)
        self.buttons.addButton(QDialogButtonBox.StandardButton.Cancel)
        self.buttons.accepted.connect(self.validate_and_accept)
        self.buttons.rejected.connect(self.reject)
        layout.addWidget(self.buttons)

    def validate_and_accept(self):
        if not self.edit_title.text().strip() or \
                not self.edit_author.text().strip() or \
                not self.edit_publisher.text().strip():
            QMessageBox.warning(self, "Ошибка", "Все текстовые поля должны быть заполнены")
            return
        self.accept()

    def get_data(self) -> dict:
        return {
            "title": self.edit_title.text().strip(),
            "author": self.edit_author.text().strip(),
            "publisher": self.edit_publisher.text().strip(),
            "volumes": self.spin_volumes.value(),
            "print_run": self.spin_run.value()
        }