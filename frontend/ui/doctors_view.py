from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
                             QTableWidgetItem, QHeaderView, QLabel, QPushButton,
                             QDialog, QLineEdit, QFormLayout, QMessageBox)
from PyQt6.QtCore import Qt
from frontend.api_client import APIClient

class AddDoctorDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Новый врач")
        self.setFixedSize(300, 150)

        layout = QFormLayout(self)
        self.name_input = QLineEdit()
        self.specialization_input = QLineEdit()

        layout.addRow("ФИО:", self.name_input)
        layout.addRow("Специализация:", self.specialization_input)

        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Сохранить")
        cancel_btn = QPushButton("Отмена")
        
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addRow(btn_layout)

        save_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)

    def get_data(self):
        return {
            "full_name": self.name_input.text().strip(),
            "specialization": self.specialization_input.text().strip()
        }

class DoctorsView(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)

        # Верхняя панель
        header_layout = QHBoxLayout()
        title = QLabel("Список врачей")
        title.setStyleSheet("font-size: 20px; font-weight: bold;") # Оставляем только размер
        
        del_btn = QPushButton(" Удалить")
        del_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        del_btn.setStyleSheet("background-color: #e74c3c; color: white; font-weight: bold; padding: 8px 15px; border-radius: 5px;")
        del_btn.clicked.connect(self.delete_selected_doctor)

        add_btn = QPushButton(" + Добавить врача")
        add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        add_btn.setStyleSheet("background-color: #27ae60; color: white; font-weight: bold; padding: 8px 15px; border-radius: 5px;")
        add_btn.clicked.connect(self.open_add_dialog)

        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(del_btn)
        header_layout.addWidget(add_btn)
        layout.addLayout(header_layout)

        # Таблица
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["ID", "ФИО Врача", "Специализация"])
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setAlternatingRowColors(True)
        layout.addWidget(self.table)

        self.load_data()

    def show_message(self, title, text, icon=QMessageBox.Icon.Information):
        msg = QMessageBox(self)
        msg.setWindowTitle(title)
        msg.setText(text)
        msg.setIcon(icon)
        msg.exec()

    def load_data(self):
        doctors = APIClient.get_doctors()
        self.table.setRowCount(len(doctors))
        for row, doc in enumerate(doctors):
            self.table.setItem(row, 0, QTableWidgetItem(str(doc.get("id"))))
            self.table.setItem(row, 1, QTableWidgetItem(doc.get("full_name")))
            self.table.setItem(row, 2, QTableWidgetItem(doc.get("specialization")))

    def open_add_dialog(self):
        dialog = AddDoctorDialog(self)
        if dialog.exec():
            data = dialog.get_data()
            if not data["full_name"] or not data["specialization"]:
                self.show_message("Ошибка", "Все поля обязательны для заполнения!", QMessageBox.Icon.Warning)
                return
            
            if APIClient.create_doctor(data):
                self.load_data()
                self.show_message("Успех", "Врач успешно добавлен!")
            else:
                self.show_message("Ошибка", "Не удалось добавить врача.", QMessageBox.Icon.Critical)

    def delete_selected_doctor(self):
        selected = self.table.selectedItems()
        if not selected:
            self.show_message("Внимание", "Выделите врача для удаления!", QMessageBox.Icon.Warning)
            return

        row = selected[0].row()
        doc_id = int(self.table.item(row, 0).text())
        doc_name = self.table.item(row, 1).text()

        msg = QMessageBox(self)
        msg.setWindowTitle("Удаление")
        msg.setText(f"Удалить врача '{doc_name}'?")
        msg.setIcon(QMessageBox.Icon.Question)
        msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if msg.exec() == QMessageBox.StandardButton.Yes:
            if APIClient.delete_doctor(doc_id):
                self.load_data()
                self.show_message("Успех", "Врач удален.")
            else:
                self.show_message("Ошибка", "Не удалось удалить врача.", QMessageBox.Icon.Critical)