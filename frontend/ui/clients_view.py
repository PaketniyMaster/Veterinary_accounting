import re
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
                             QTableWidgetItem, QHeaderView, QLabel, QPushButton,
                             QDialog, QLineEdit, QFormLayout, QMessageBox)
from PyQt6.QtCore import Qt
from frontend.api_client import APIClient
from frontend.ui.client_card import ClientCardDialog

class AddClientDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Новый клиент")
        self.setFixedSize(320, 200) 


        layout = QFormLayout(self)

        self.name_input = QLineEdit()
        self.phone_input = QLineEdit()
        self.email_input = QLineEdit()

        self.phone_input.setInputMask("+7 (999) 999-99-99;_")
        
        # --- ИСПРАВЛЕНИЕ КУРСОРОВ: Привязываем событие смены позиции курсора ---
        self.phone_input.cursorPositionChanged.connect(self.auto_fix_cursor)

        layout.addRow("ФИО:", self.name_input)
        layout.addRow("Телефон:", self.phone_input)
        layout.addRow("Email:", self.email_input)

        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Сохранить")
        cancel_btn = QPushButton("Отмена")

        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addRow(btn_layout)

        save_btn.clicked.connect(self.accept)   
        cancel_btn.clicked.connect(self.reject) 

    def auto_fix_cursor(self, old, new):
        """Автоматически ставит курсор в начало номера, если поле еще пустое"""
        # Считаем, сколько цифр реально введено (код страны '7' уже есть)
        digits_only = ''.join(filter(str.isdigit, self.phone_input.text()))
        if len(digits_only) <= 1 and new != 4:
            self.phone_input.setCursorPosition(4) # 4 - это позиция сразу после "+7 ("

    def get_data(self):
        email_text = self.email_input.text().strip()
        return {
            "full_name": self.name_input.text().strip(),
            "phone": self.phone_input.text(),
            "email": email_text if email_text else None 
        }

class ClientsView(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)

        # ВЕРХНЯЯ ПАНЕЛЬ (Заголовок + Кнопки)
        header_layout = QHBoxLayout()
        title = QLabel("Список клиентов (Владельцы)")
        title.setStyleSheet("font-size: 20px; font-weight: bold;")
        
        # --- НОВАЯ КНОПКА УДАЛЕНИЯ ---
        del_btn = QPushButton("  Удалить")
        del_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        del_btn.setStyleSheet("""
            QPushButton { background-color: #e74c3c; color: white; font-weight: bold; padding: 8px 15px; border-radius: 5px; } 
            QPushButton:hover { background-color: #c0392b; }
        """)
        del_btn.clicked.connect(self.delete_selected_client) # Привязываем функцию

        add_btn = QPushButton("  + Добавить клиента")
        add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        add_btn.setStyleSheet("QPushButton { background-color: #27ae60; color: white; font-weight: bold; padding: 8px 15px; border-radius: 5px; } QPushButton:hover { background-color: #2ecc71; }")
        add_btn.clicked.connect(self.open_add_dialog)

        header_layout.addWidget(title)
        header_layout.addStretch() 
        header_layout.addWidget(del_btn) # Добавляем на слой
        header_layout.addWidget(add_btn) 
        layout.addLayout(header_layout)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "ФИО Владельца", "Телефон", "Email"])
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.setAlternatingRowColors(True)
        
        # --- ИСПРАВЛЕНИЕ РЕДАКТИРОВАНИЯ ---
        # 1. Запрещаем прямое редактирование ячеек (таблица только для чтения)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        # 2. При клике будет выделяться вся строка целиком, а не одна ячейка (удобно для будущего открытия карточки)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)


        layout.addWidget(self.table)
        self.table.itemDoubleClicked.connect(self.open_client_card)
        self.load_data()

    def open_client_card(self, item):
        """Открывает детальную карточку при двойном клике на строку"""
        row = item.row()
        client_id = int(self.table.item(row, 0).text())
        client_name = self.table.item(row, 1).text()
        client_phone = self.table.item(row, 2).text()

        # Открываем диалоговое окно карточки клиента
        dialog = ClientCardDialog(client_id, client_name, client_phone, self)
        dialog.exec()

    def show_message(self, title, text, icon=QMessageBox.Icon.Information):
        msg = QMessageBox(self)
        msg.setWindowTitle(title)
        msg.setText(text)
        msg.setIcon(icon)

        msg.exec()

    def load_data(self):
        clients = APIClient.get_clients()
        self.table.setRowCount(len(clients))
        
        for row, client in enumerate(clients):
            self.table.setItem(row, 0, QTableWidgetItem(str(client.get("id"))))
            self.table.setItem(row, 1, QTableWidgetItem(client.get("full_name") or "—"))
            self.table.setItem(row, 2, QTableWidgetItem(client.get("phone") or "—"))
            self.table.setItem(row, 3, QTableWidgetItem(client.get("email") or "—"))

    def open_add_dialog(self):
        dialog = AddClientDialog(self)
        if dialog.exec(): 
            data = dialog.get_data()
            
            if not data["full_name"] or data["phone"] == "+7 (   )    -  -  ":
                self.show_message("Ошибка", "Поля ФИО и Телефон обязательны для заполнения!", QMessageBox.Icon.Warning)
                return
            
            if data["email"]:
                email_pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
                if not re.match(email_pattern, data["email"]):
                    self.show_message("Ошибка", "Неверный формат Email!", QMessageBox.Icon.Warning)
                    return
            
            result = APIClient.create_client(data)
            if result:
                self.load_data() 
                self.show_message("Успех", "Клиент успешно добавлен!")
            else:
                self.show_message("Ошибка", "Не удалось сохранить клиента. Возможно, такой номер телефона уже есть.", QMessageBox.Icon.Critical)
    
    def confirm_action(self, title, text):
        """Вспомогательное окно для подтверждения действий (светлая тема)"""
        msg = QMessageBox(self)
        msg.setWindowTitle(title)
        msg.setText(text)
        msg.setIcon(QMessageBox.Icon.Question)
        msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        msg.button(QMessageBox.StandardButton.Yes).setText("Да, удалить")
        msg.button(QMessageBox.StandardButton.No).setText("Отмена")

        return msg.exec() == QMessageBox.StandardButton.Yes

    def delete_selected_client(self):
        """Функция удаления выбранного клиента"""
        selected_items = self.table.selectedItems()
        if not selected_items:
            self.show_message("Внимание", "Пожалуйста, выделите клиента в таблице для удаления!", QMessageBox.Icon.Warning)
            return

        # Получаем номер выделенной строки
        row = selected_items[0].row()
        # Извлекаем ID (0-я колонка) и ФИО (1-я колонка)
        client_id = int(self.table.item(row, 0).text())
        client_name = self.table.item(row, 1).text()

        # Спрашиваем подтверждение
        if self.confirm_action("Удаление", f"Вы уверены, что хотите удалить клиента\n'{client_name}'?\n\nВнимание: Все его питомцы также будут удалены из базы!"):
            # Отправляем запрос на сервер
            if APIClient.delete_client(client_id):
                self.load_data() # Обновляем таблицу
                self.show_message("Успех", "Клиент успешно удален.")
            else:
                self.show_message("Ошибка", "Не удалось удалить клиента.", QMessageBox.Icon.Critical)
    

