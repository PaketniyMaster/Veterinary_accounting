from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTableWidget, QTableWidgetItem, 
                             QHeaderView, QFormLayout, QLineEdit, QComboBox, QMessageBox)
from PyQt6.QtCore import Qt
from frontend.api_client import APIClient

class AddPetDialog(QDialog):
    """Всплывающее окно для добавления питомца"""
    def __init__(self, client_id, parent=None):
        super().__init__(parent)
        self.client_id = client_id
        self.setWindowTitle("Новый питомец")
        self.setFixedSize(320, 220)

        
        layout = QFormLayout(self)

        self.name_input = QLineEdit()
        
        # Делаем выпадающий список для видов животных (как и обсуждали ранее)
        self.species_input = QComboBox()
        self.species_input.addItems(["Собака", "Кот", "Грызун", "Птица", "Рептилия", "Другое"])
        
        self.breed_input = QLineEdit()

        layout.addRow("Кличка:", self.name_input)
        layout.addRow("Вид:", self.species_input)
        layout.addRow("Порода:", self.breed_input)

        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Сохранить")
        cancel_btn = QPushButton("Отмена")

        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addRow(btn_layout)

        save_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)

    def get_data(self):
        """Формируем данные для отправки на сервер"""
        return {
            "client_id": self.client_id,
            "name": self.name_input.text().strip(),
            "species": self.species_input.currentText(),
            "breed": self.breed_input.text().strip() or None
        }

class ClientCardDialog(QDialog):
    """Главная карточка клиента с его питомцами"""
    def __init__(self, client_id, client_name, client_phone, parent=None):
        super().__init__(parent)
        self.client_id = client_id
        self.setWindowTitle(f"Карточка клиента: {client_name}")
        self.resize(700, 500) # Делаем окно достаточно просторным


        layout = QVBoxLayout(self)

        # 1. ШАПКА С ИНФОРМАЦИЕЙ О КЛИЕНТЕ
        header_layout = QHBoxLayout()
        info_label = QLabel(f"Владелец: {client_name}   |   Телефон: {client_phone}")
        info_label.setStyleSheet("font-size: 18px; font-weight: bold; background-color: transparent;")
        
        # --- НОВАЯ КНОПКА ---
        del_pet_btn = QPushButton(" Удалить")
        del_pet_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        del_pet_btn.setStyleSheet("QPushButton { background-color: #e74c3c; color: white; font-weight: bold; padding: 8px 15px; border-radius: 5px; } QPushButton:hover { background-color: #c0392b; }")
        del_pet_btn.clicked.connect(self.delete_selected_pet)

        add_pet_btn = QPushButton(" + Добавить питомца")
        add_pet_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        add_pet_btn.setStyleSheet("QPushButton { background-color: #27ae60; color: white; font-weight: bold; padding: 8px 15px; border-radius: 5px; } QPushButton:hover { background-color: #2ecc71; }")
        add_pet_btn.clicked.connect(self.open_add_pet_dialog)

        header_layout.addWidget(info_label)
        header_layout.addStretch()
        header_layout.addWidget(del_pet_btn) # Добавили на слой
        header_layout.addWidget(add_pet_btn)
        layout.addLayout(header_layout)

        # 2. ТАБЛИЦА ПИТОМЦЕВ
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "Кличка", "Вид", "Порода"])
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setAlternatingRowColors(True)
        
        
        layout.addWidget(self.table)

        # Загружаем животных при открытии карточки
        self.load_pets()

    def load_pets(self):
        pets = APIClient.get_pets_by_client(self.client_id)
        self.table.setRowCount(len(pets))
        
        for row, pet in enumerate(pets):
            self.table.setItem(row, 0, QTableWidgetItem(str(pet.get("id"))))
            self.table.setItem(row, 1, QTableWidgetItem(pet.get("name")))
            self.table.setItem(row, 2, QTableWidgetItem(pet.get("species")))
            self.table.setItem(row, 3, QTableWidgetItem(pet.get("breed") or "—"))

    def show_message(self, title, text, icon=QMessageBox.Icon.Information):
        """Вспомогательная функция для красивых светлых уведомлений"""
        msg = QMessageBox(self)
        msg.setWindowTitle(title)
        msg.setText(text)
        msg.setIcon(icon)
        msg.setStyleSheet("""
            QMessageBox { background-color: #ffffff; }
            QLabel { color: #2c3e50; font-size: 14px; background-color: transparent; border: none; }
            QPushButton { background-color: #ecf0f1; color: #2c3e50; padding: 5px 15px; border-radius: 4px; border: none; font-weight: bold; }
            QPushButton:hover { background-color: #bdc3c7; }
        """)
        msg.exec()

    def open_add_pet_dialog(self):
        dialog = AddPetDialog(self.client_id, self)
        if dialog.exec():
            data = dialog.get_data()
            if not data["name"]:
                # Используем нашу новую красивую функцию вместо стандартной
                self.show_message("Ошибка", "Кличка питомца обязательна для заполнения!", QMessageBox.Icon.Warning)
                return
            
            if APIClient.create_pet(data):
                self.load_pets() # Обновляем таблицу животных
                self.show_message("Успех", "Питомец успешно добавлен!")
            else:
                self.show_message("Ошибка", "Не удалось добавить питомца.", QMessageBox.Icon.Critical)
    
    def confirm_action(self, title, text):
        """Вспомогательное окно для подтверждения действий"""
        msg = QMessageBox(self)
        msg.setWindowTitle(title)
        msg.setText(text)
        msg.setIcon(QMessageBox.Icon.Question)
        msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        msg.button(QMessageBox.StandardButton.Yes).setText("Да, удалить")
        msg.button(QMessageBox.StandardButton.No).setText("Отмена")
        return msg.exec() == QMessageBox.StandardButton.Yes

    def delete_selected_pet(self):
        """Функция удаления выбранного питомца"""
        selected_items = self.table.selectedItems()
        if not selected_items:
            self.show_message("Внимание", "Пожалуйста, выделите питомца в таблице для удаления!", QMessageBox.Icon.Warning)
            return

        row = selected_items[0].row()
        pet_id = int(self.table.item(row, 0).text())
        pet_name = self.table.item(row, 1).text()

        if self.confirm_action("Удаление", f"Вы уверены, что хотите удалить питомца '{pet_name}'?"):
            if APIClient.delete_pet(pet_id):
                self.load_pets() # Обновляем таблицу
                self.show_message("Успех", "Питомец успешно удален.")
            else:
                self.show_message("Ошибка", "Не удалось удалить питомца.", QMessageBox.Icon.Critical)