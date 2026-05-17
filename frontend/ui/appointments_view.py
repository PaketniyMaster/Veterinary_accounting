from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
                             QTableWidgetItem, QHeaderView, QLabel, QPushButton,
                             QDialog, QComboBox, QDateTimeEdit, QFormLayout, 
                             QMessageBox, QCalendarWidget, QStackedWidget,
                             QTextEdit, QLineEdit)
from PyQt6.QtCore import Qt, QTime, QDate, QDateTime
from PyQt6.QtGui import QColor, QFont
from frontend.api_client import APIClient

class AddAppointmentDialog(QDialog):
    """Окно для создания новой записи (для регистратуры)"""
    def __init__(self, doctors, pets, initial_doctor_id=None, initial_dt=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Запись на прием")
        self.setFixedSize(400, 250)
        
        self.doctors = doctors
        self.pets = pets

        layout = QFormLayout(self)
        layout.setSpacing(15)

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
    """Главный виджет расписания со стопкой экранов"""
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)

        # Создаем "стопку" экранов
        self.stacked_widget = QStackedWidget()
        self.layout.addWidget(self.stacked_widget)

        # Данные для сетки расписания
        self.doctors = []
        self.time_slots = []
        curr = QTime(9, 0)
        while curr <= QTime(18, 0):
            self.time_slots.append(curr.toString("HH:mm"))
            curr = curr.addSecs(30 * 60)

        # Собираем обе "страницы"
        self.setup_calendar_page()
        self.setup_daily_page()

        # По умолчанию показываем календарь
        self.stacked_widget.setCurrentWidget(self.calendar_page)

    def setup_calendar_page(self):
        """Страница 1: Большой календарь на месяц"""
        self.calendar_page = QWidget()
        layout = QVBoxLayout(self.calendar_page)

        title = QLabel("Выберите дату для просмотра расписания")
        title.setStyleSheet("font-size: 20px; font-weight: bold; margin-bottom: 10px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.calendar = QCalendarWidget()
        self.calendar.setGridVisible(True)
        self.calendar.setVerticalHeaderFormat(QCalendarWidget.VerticalHeaderFormat.NoVerticalHeader) 
        
        self.calendar.setStyleSheet("""
            QCalendarWidget QWidget { alternate-background-color: #2c2c2c; }
            QCalendarWidget QToolButton { color: white; font-size: 14px; font-weight: bold; }
        """)

        # При клике на дату открываем расписание
        self.calendar.clicked.connect(self.show_daily_schedule)

        layout.addWidget(title)
        layout.addWidget(self.calendar)
        self.stacked_widget.addWidget(self.calendar_page)

    def setup_daily_page(self):
        """Страница 2: Сетка с врачами и временем"""
        self.daily_page = QWidget()
        layout = QVBoxLayout(self.daily_page)

        # Панель управления
        header = QHBoxLayout()

        back_btn = QPushButton("← Назад в календарь")
        back_btn.setStyleSheet("background-color: #7f8c8d; color: white; padding: 8px; border-radius: 4px; font-weight: bold;")
        back_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        back_btn.clicked.connect(self.show_calendar)

        self.daily_date_label = QLabel("Расписание на: ")
        self.daily_date_label.setStyleSheet("font-size: 18px; font-weight: bold; margin-left: 15px;")

        refresh_btn = QPushButton(" Обновить")
        refresh_btn.setMinimumHeight(35)
        refresh_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        refresh_btn.clicked.connect(self.load_schedule)

        header.addWidget(back_btn)
        header.addWidget(self.daily_date_label)
        header.addStretch()
        header.addWidget(refresh_btn)
        layout.addLayout(header)

        # Сетка расписания
        self.table = QTableWidget()
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.cellDoubleClicked.connect(self.handle_cell_click)
        
        self.table.setAlternatingRowColors(False)
        self.table.setShowGrid(True)
        self.table.verticalHeader().setDefaultSectionSize(60)
        self.table.horizontalHeader().setMinimumSectionSize(200)
        self.table.setStyleSheet("gridline-color: #3d3d3d;")

        layout.addWidget(self.table)
        self.stacked_widget.addWidget(self.daily_page)

    def show_calendar(self):
        self.stacked_widget.setCurrentWidget(self.calendar_page)

    def show_daily_schedule(self, date):
        self.daily_date_label.setText(f"Расписание на: {date.toString('dd.MM.yyyy')}")
        self.stacked_widget.setCurrentWidget(self.daily_page)
        self.load_schedule()

    def load_schedule(self):
        self.doctors = APIClient.get_doctors()
        
        # 1. Если врачей нет вообще (все удалены), очищаем таблицу и выходим
        if not self.doctors: 
            self.table.setColumnCount(0)
            self.table.clearContents()
            return

        # 2. ПРИНУДИТЕЛЬНЫЙ СБРОС КОЛОНОК (Это заставит PyQt6 удалить старые данные)
        self.table.setColumnCount(0)

        # 3. Строим новую сетку с актуальным количеством врачей
        self.table.setColumnCount(len(self.doctors))
        self.table.setRowCount(len(self.time_slots))
        self.table.setHorizontalHeaderLabels([d['full_name'] for d in self.doctors])
        self.table.setVerticalHeaderLabels(self.time_slots)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        self.table.clearContents()

        selected_date = self.calendar.selectedDate().toString("yyyy-MM-dd")
        appointments = APIClient.get_appointments_by_date(selected_date)

        for appt in appointments:
            col = -1
            for i, doc in enumerate(self.doctors):
                if doc['id'] == appt['doctor_id']:
                    col = i
                    break

            dt_raw = appt['date_time']
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

                # Умная раскраска по статусу
                if status == "Завершен": bg_color = "#27ae60"
                elif status == "Ожидает": bg_color = "#f39c12"
                elif status == "На приеме": bg_color = "#9b59b6"
                elif status == "Отменен": bg_color = "#7f8c8d"
                else: bg_color = "#3498db"

                item.setBackground(QColor(bg_color))
                item.setForeground(QColor("#ffffff"))

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
            
            appt_data = APIClient.get_appointment(appt_id)
            if not appt_data:
                QMessageBox.critical(self, "Ошибка", "Не удалось загрузить данные приема.")
                return

            dialog = MedicalRecordDialog(appt_id, appt_data, self)
            result = dialog.exec()

            if result == QDialog.DialogCode.Accepted:
                new_data = dialog.get_data()
                if APIClient.update_appointment(appt_id, new_data):
                    self.load_schedule()
                    QMessageBox.information(self, "Успех", "Медицинская карта сохранена!")
                else:
                    QMessageBox.critical(self, "Ошибка", "Не удалось сохранить данные.")
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
        
        dt = QDateTime(self.calendar.selectedDate(), QTime.fromString(time_slot, "HH:mm"))
        
        pets = APIClient.get_pets() 
        dialog = AddAppointmentDialog(self.doctors, pets, doctor['id'], dt, self)
        if dialog.exec():
            data = dialog.get_data()
            if APIClient.create_appointment(data):
                self.load_schedule()
                QMessageBox.information(self, "Успех", "Запись успешно создана!")