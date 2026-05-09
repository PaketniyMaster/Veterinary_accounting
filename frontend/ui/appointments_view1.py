from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
                             QTableWidgetItem, QHeaderView, QLabel, QPushButton,
                             QDialog, QComboBox, QDateTimeEdit, QFormLayout, QMessageBox, QDateEdit, QTextEdit, QLineEdit)
from PyQt6.QtCore import Qt, QTime, QDate, QDateTime
from PyQt6.QtGui import QColor
from frontend.api_client import APIClient

class AddAppointmentDialog(QDialog):
    def __init__(self, doctors, pets, initial_doctor_id=None, initial_dt=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Запись на прием")
        self.setFixedSize(400, 250)
        
        self.doctors = doctors
        self.pets = pets

        layout = QFormLayout(self)
        layout.setSpacing(15) # Добавляем воздух между строками формы

        self.doctor_combo = QComboBox()
        for doc in self.doctors:
            self.doctor_combo.addItem(doc['full_name'], doc['id'])
        
        if initial_doctor_id:
            idx = self.doctor_combo.findData(initial_doctor_id)
            if idx != -1: self.doctor_combo.setCurrentIndex(idx)

        self.pet_combo = QComboBox()
        for pet in self.pets:
            self.pet_combo.addItem(f"{pet['name']} (ID: {pet['id']})", pet['id'])

        self.dt_edit = QDateTimeEdit(QDateTime.currentDateTime())
        self.dt_edit.setCalendarPopup(True)
        if initial_dt:
            self.dt_edit.setDateTime(initial_dt)

        layout.addRow("Врач:", self.doctor_combo)
        layout.addRow("Питомец:", self.pet_combo)
        layout.addRow("Дата и время:", self.dt_edit)

        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Записать")
        save_btn.setStyleSheet("background-color: #27ae60; color: white; font-weight: bold; padding: 10px; border-radius: 5px;")
        cancel_btn = QPushButton("Отмена")
        cancel_btn.setStyleSheet("padding: 10px;")
        
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addRow(btn_layout)

        save_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)

    def get_data(self):
        # ИСПРАВЛЕНО: Теперь берем данные из правильных выпадающих списков
        return {
            "pet_id": self.pet_combo.currentData(),
            "doctor_id": self.doctor_combo.currentData(),
            "date_time": self.dt_edit.dateTime().toPyDateTime().isoformat(),
            "status": "Запланировано"
        }

class MedicalRecordDialog(QDialog):
    """Окно Электронной медицинской карты (Рабочее место врача)"""
    def __init__(self, appointment_id, current_data, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Карточка приема (Запись #{appointment_id})")
        self.setFixedSize(500, 600)
        self.appointment_id = appointment_id
        self.current_data = current_data

        layout = QFormLayout(self)
        layout.setSpacing(15)

        # Выводим информацию кто на приеме
        info_label = QLabel(f"<b>Пациент:</b> {current_data.get('pet_name', 'Неизвестно')} (ID: {current_data.get('pet_id')})")
        info_label.setStyleSheet("font-size: 16px; margin-bottom: 10px;")
        layout.addRow(info_label)

        # 1. Статус приема
        self.status_combo = QComboBox()
        self.status_combo.addItems(["Запланировано", "Ожидает", "На приеме", "Завершен", "Отменен"])
        self.status_combo.setCurrentText(current_data.get('status', 'Запланировано'))

        # 2. Многострочные поля для врача
        self.anamnesis_input = QTextEdit()
        self.anamnesis_input.setPlaceholderText("Опишите жалобы и анамнез...")
        self.anamnesis_input.setText(current_data.get('anamnesis', ''))

        self.diagnosis_input = QLineEdit()
        self.diagnosis_input.setPlaceholderText("Предварительный или точный диагноз")
        self.diagnosis_input.setText(current_data.get('diagnosis', ''))

        self.treatment_input = QTextEdit()
        self.treatment_input.setPlaceholderText("Назначения, процедуры, препараты...")
        self.treatment_input.setText(current_data.get('treatment', ''))

        layout.addRow("Статус:", self.status_combo)
        layout.addRow("Анамнез:", self.anamnesis_input)
        layout.addRow("Диагноз:", self.diagnosis_input)
        layout.addRow("Назначения:", self.treatment_input)

        # Кнопки
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Сохранить карту")
        save_btn.setStyleSheet("background-color: #27ae60; color: white; padding: 10px; font-weight: bold; border-radius: 5px;")
        
        # Кнопка удаления переехала сюда!
        delete_btn = QPushButton("Отменить прием (Удалить)")
        delete_btn.setStyleSheet("background-color: #e74c3c; color: white; padding: 10px; font-weight: bold; border-radius: 5px;")

        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(delete_btn)
        layout.addRow(btn_layout)

        save_btn.clicked.connect(self.accept)
        delete_btn.clicked.connect(self.delete_appointment)

    def delete_appointment(self):
        """Специальный код завершения окна (2), чтобы мы знали, что нажата кнопка удаления"""
        self.done(2)

    def get_data(self):
        """Собираем данные для обновления"""
        return {
            "pet_id": self.current_data['pet_id'],
            "doctor_id": self.current_data['doctor_id'],
            "date_time": self.current_data['date_time'],
            "status": self.status_combo.currentText(),
            "anamnesis": self.anamnesis_input.toPlainText(),
            "diagnosis": self.diagnosis_input.text(),
            "treatment": self.treatment_input.toPlainText()
        }

class AppointmentsView(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        
        self.doctors = []
        self.time_slots = []
        
        curr = QTime(9, 0)
        while curr <= QTime(18, 0):
            self.time_slots.append(curr.toString("HH:mm"))
            curr = curr.addSecs(30 * 60)

        header = QHBoxLayout()
        header.setSpacing(15)
        
        date_label = QLabel("Расписание на:")
        date_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        
        self.date_picker = QDateEdit(QDate.currentDate())
        self.date_picker.setCalendarPopup(True)
        self.date_picker.setDisplayFormat("dd.MM.yyyy")
        self.date_picker.setMinimumWidth(150)
        self.date_picker.dateChanged.connect(self.load_schedule)
        
        refresh_btn = QPushButton(" Обновить")
        refresh_btn.setMinimumHeight(35)
        refresh_btn.clicked.connect(self.load_schedule)
        
        header.addWidget(date_label)
        header.addWidget(self.date_picker)
        header.addStretch()
        header.addWidget(refresh_btn)
        self.layout.addLayout(header)

        self.table = QTableWidget()
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.cellDoubleClicked.connect(self.handle_cell_click)
        
        # --- УЛУЧШЕНИЕ ВИЗУАЛА: Убираем зебру, добавляем сетку ---
        self.table.setAlternatingRowColors(False) 
        self.table.setShowGrid(True)
        self.table.verticalHeader().setDefaultSectionSize(60) # Еще чуть выше строки
        self.table.horizontalHeader().setMinimumSectionSize(200)
        
        # Стиль для сетки, чтобы она была видна в темной теме
        self.table.setStyleSheet("gridline-color: #3d3d3d;") 

        self.layout.addWidget(self.table)
        self.load_schedule()

    def load_schedule(self):
        self.doctors = APIClient.get_doctors()
        if not self.doctors: return

        self.table.setColumnCount(len(self.doctors))
        self.table.setRowCount(len(self.time_slots))
        self.table.setHorizontalHeaderLabels([d['full_name'] for d in self.doctors])
        self.table.setVerticalHeaderLabels(self.time_slots)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        self.table.clearContents()

        selected_date = self.date_picker.date().toString("yyyy-MM-dd")
        appointments = APIClient.get_appointments_by_date(selected_date)

        for appt in appointments:
            col = -1
            for i, doc in enumerate(self.doctors):
                if doc['id'] == appt['doctor_id']:
                    col = i
                    break
            
            # Парсим время, отсекая лишнее (секунды/микросекунды)
            dt_raw = appt['date_time']
            # Берем только часть с временем HH:mm
            try:
                time_part = dt_raw.split('T')[1][:5] 
            except IndexError:
                time_part = ""

            row = -1
            if time_part in self.time_slots:
                row = self.time_slots.index(time_part)

            if col != -1 and row != -1:
                pet_name = appt.get('pet_name', 'Без имени')
                status = appt.get('status', 'Запланировано')
                
                display_text = f"🐾 {pet_name.upper()}\n({status})"
                item = QTableWidgetItem(display_text)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                
                # --- УМНАЯ РАСКРАСКА ПО СТАТУСУ ---
                if status == "Завершен":
                    bg_color = "#27ae60"  # Зеленый
                elif status == "Ожидает":
                    bg_color = "#f39c12"  # Оранжевый
                elif status == "На приеме":
                    bg_color = "#9b59b6"  # Фиолетовый
                elif status == "Отменен":
                    bg_color = "#7f8c8d"  # Серый
                else:
                    bg_color = "#3498db"  # Синий (по умолчанию для Запланировано)
                
                item.setBackground(QColor(bg_color))
                item.setForeground(QColor("#ffffff")) # Белый текст везде
                
                font = item.font()
                font.setBold(True)
                item.setFont(font)
                
                # Прячем ID записи внутри ячейки
                item.setData(Qt.ItemDataRole.UserRole, appt['id'])
                
                self.table.setItem(row, col, item)

    def handle_cell_click(self, row, col):
        existing_item = self.table.item(row, col)

        # СЦЕНАРИЙ 1: ЯЧЕЙКА ЗАНЯТА (Открываем Медкарту)
        if existing_item and existing_item.data(Qt.ItemDataRole.UserRole) is not None:
            appt_id = existing_item.data(Qt.ItemDataRole.UserRole) 
            
            # 1. Скачиваем свежие данные с бэкенда
            appt_data = APIClient.get_appointment(appt_id)
            if not appt_data:
                QMessageBox.critical(self, "Ошибка", "Не удалось загрузить данные приема.")
                return

            # 2. Открываем окно Медкарты
            dialog = MedicalRecordDialog(appt_id, appt_data, self)
            result = dialog.exec()

            # Если врач нажал "Сохранить карту" (result == 1)
            if result == QDialog.DialogCode.Accepted:
                new_data = dialog.get_data()
                if APIClient.update_appointment(appt_id, new_data):
                    self.load_schedule()
                    QMessageBox.information(self, "Успех", "Медицинская карта сохранена!")
                else:
                    QMessageBox.critical(self, "Ошибка", "Не удалось сохранить данные.")
            
            # Если администратор нажал "Отменить прием" (result == 2)
            elif result == 2:
                msg = QMessageBox(self)
                msg.setWindowTitle("Отмена записи")
                msg.setText("Удалить этот прием из расписания?")
                msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                if msg.exec() == QMessageBox.StandardButton.Yes:
                    if APIClient.delete_appointment(appt_id):
                        self.load_schedule()
                        QMessageBox.information(self, "Успех", "Запись отменена.")
            return 

        # СЦЕНАРИЙ 2: ЯЧЕЙКА СВОБОДНА (Создание записи)
        if col >= len(self.doctors): return
        doctor = self.doctors[col]
        time_slot = self.time_slots[row]
        
        dt = QDateTime(self.date_picker.date(), QTime.fromString(time_slot, "HH:mm"))
        
        pets = APIClient.get_pets() 
        dialog = AddAppointmentDialog(self.doctors, pets, doctor['id'], dt, self)
        if dialog.exec():
            data = dialog.get_data()
            if APIClient.create_appointment(data):
                self.load_schedule()
                QMessageBox.information(self, "Успех", "Запись успешно создана!")