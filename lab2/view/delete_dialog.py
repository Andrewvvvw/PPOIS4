from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QFormLayout,
    QLineEdit,
    QSpinBox,
    QComboBox,
    QDialogButtonBox,
    QLabel,
    QHBoxLayout
)


class DeleteDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Удаление записей")
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.edit_title = QLineEdit()
        self.edit_author = QLineEdit()
        self.edit_publisher = QLineEdit()

        self.spin_v_min = QSpinBox()
        self.spin_v_max = QSpinBox()
        self.spin_v_max.setRange(0, 100000)

        self.spin_run_val = QSpinBox()
        self.spin_run_val.setRange(0, 10 ** 9)
        self.combo_run_mode = QComboBox()
        self.combo_run_mode.addItems(["more", "less"])

        self.spin_total_val = QSpinBox()
        self.spin_total_val.setRange(0, 10 ** 9)
        self.combo_total_mode = QComboBox()
        self.combo_total_mode.addItems(["more", "less"])

        form.addRow("По названию книги:", self.edit_title)
        form.addRow("По ФИО автора:", self.edit_author)
        form.addRow("По издательству:", self.edit_publisher)

        vol_layout = QHBoxLayout()
        vol_layout.addWidget(QLabel("от"))
        vol_layout.addWidget(self.spin_v_min)
        vol_layout.addWidget(QLabel("до"))
        vol_layout.addWidget(self.spin_v_max)
        form.addRow("Число томов:", vol_layout)

        run_layout = QHBoxLayout()
        run_layout.addWidget(self.combo_run_mode)
        run_layout.addWidget(self.spin_run_val)
        form.addRow("Тираж:", run_layout)

        total_layout = QHBoxLayout()
        total_layout.addWidget(self.combo_total_mode)
        total_layout.addWidget(self.spin_total_val)
        form.addRow("Итого томов:", total_layout)

        layout.addLayout(form)

        self.buttons = QDialogButtonBox()
        self.buttons.addButton(QDialogButtonBox.StandardButton.Ok)
        self.buttons.addButton(QDialogButtonBox.StandardButton.Cancel)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        layout.addWidget(self.buttons)

    def get_data(self) -> dict:
        data = {}
        if self.edit_title.text().strip():
            data["title"] = self.edit_title.text().strip()
        if self.edit_author.text().strip():
            data["author"] = self.edit_author.text().strip()
        if self.edit_publisher.text().strip():
            data["publisher"] = self.edit_publisher.text().strip()

        if self.spin_v_max.value() > 0:
            data["v_min"] = self.spin_v_min.value()
            data["v_max"] = self.spin_v_max.value()

        if self.spin_run_val.value() > 0:
            data["run_val"] = self.spin_run_val.value()
            data["run_mode"] = self.combo_run_mode.currentText()

        if self.spin_total_val.value() > 0:
            data["total_val"] = self.spin_total_val.value()
            data["total_mode"] = self.combo_total_mode.currentText()

        return data