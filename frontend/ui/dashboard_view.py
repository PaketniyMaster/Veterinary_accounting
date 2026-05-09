from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QFrame, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView)
from PyQt6.QtCore import Qt, QDate, QDateTime
from PyQt6.QtGui import QColor, QFont
from frontend.api_client import APIClient

class StatCard(QFrame):
    """Стильная карточка для отображения статистики"""
    def __init__(self, title, value, color_hex):
        super().__init__()
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {color_hex};
                border-radius: 10px;
            }}
            QLabel {{
                color: white;
                background: transparent;
            }}
        """)
        self.setMinimumHeight(100)
        
        layout = QVBoxLayout(self)
        
        title_label = QLabel(title)
        title_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.value_label = QLabel(str(value))
        self.value_label.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        self.value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout.addWidget(title_label)
        layout.addWidget(self.value_label)

    def update_value(self, new_value):
        self.value_label.setText(str(new_value))

class DashboardView(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(20)

        # --- 1. ЗАГОЛОВОК И КНОПКА ОБНОВЛЕНИЯ ---
        header_layout = QHBoxLayout()
        title = QLabel("Обзор клиники (Сегодня)")
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        
        refresh_btn = QPushButton(" Обновить данные")
        refresh_btn.setMinimumHeight(35)
        refresh_btn.clicked.connect(self.load_data)
        
        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(refresh_btn)
        self.layout.addLayout(header_layout)

        # --- 2. КАРТОЧКИ СТАТИСТИКИ (Метрики) ---
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(15)
        
        self.card_appointments = StatCard("Приемов сегодня", "0", "#2980b9") # Синий
        self.card_waiting = StatCard("Ожидают в очереди", "0", "#f39c12")   # Оранжевый
        self.card_pets = StatCard("Всего пациентов", "0", "#27ae60")        # Зеленый
        self.card_doctors = StatCard("Врачей в базе", "0", "#8e44ad")       # Фиолетовый
        
        cards_layout.addWidget(self.card_appointments)
        cards_layout.addWidget(self.card_waiting)
        cards_layout.addWidget(self.card_pets)
        cards_layout.addWidget(self.card_doctors)
        self.layout.addLayout(cards_layout)

        # --- 3. ТАБЛИЦА БЛИЖАЙШИХ ПРИЕМОВ (Очередь) ---
        subtitle = QLabel("Ближайшие записи (Очередь)")
        subtitle.setStyleSheet("font-size: 18px; font-weight: bold; margin-top: 10px;")
        self.layout.addWidget(subtitle)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Время", "Пациент", "Врач", "Статус"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setDefaultSectionSize(40)
        self.layout.addWidget(self.table)

        self.load_data()

    def load_data(self):
        """Загружаем данные из API и высчитываем статистику"""
        # Загружаем сырые данные
        pets = APIClient.get_pets()
        doctors = APIClient.get_doctors()
        
        today_str = QDate.currentDate().toString("yyyy-MM-dd")
        appointments_today = APIClient.get_appointments_by_date(today_str)

        # 1. Обновляем карточки
        self.card_pets.update_value(len(pets) if pets else 0)
        self.card_doctors.update_value(len(doctors) if doctors else 0)
        self.card_appointments.update_value(len(appointments_today) if appointments_today else 0)
        
        # Считаем, сколько животных сейчас сидят в коридоре (Ожидают)
        waiting_count = sum(1 for a in appointments_today if a.get('status') == 'Ожидает')
        self.card_waiting.update_value(waiting_count)

        # 2. Обновляем таблицу очереди (Показываем только актуальные приемы)
        # Отфильтруем отмененные и завершенные
        active_appointments = [a for a in appointments_today if a.get('status') not in ['Завершен', 'Отменен']]
        
        # Сортируем по времени (чтобы ближайшие были сверху)
        active_appointments.sort(key=lambda x: x.get('date_time'))

        self.table.setRowCount(len(active_appointments))
        
        # Создаем словарь врачей для быстрого поиска ФИО по ID
        doctors_dict = {d['id']: d['full_name'] for d in doctors} if doctors else {}

        for row, appt in enumerate(active_appointments):
            # Время
            dt = QDateTime.fromString(appt['date_time'], Qt.DateFormat.ISODate)
            time_str = dt.time().toString("HH:mm")
            
            # Данные
            pet_name = appt.get('pet_name', f"ID: {appt.get('pet_id')}")
            doc_name = doctors_dict.get(appt.get('doctor_id'), "Неизвестно")
            status = appt.get('status', 'Запланировано')

            self.table.setItem(row, 0, QTableWidgetItem(time_str))
            self.table.setItem(row, 1, QTableWidgetItem(pet_name))
            self.table.setItem(row, 2, QTableWidgetItem(doc_name))
            
            # Подкрашиваем статус
            status_item = QTableWidgetItem(status)
            if status == "Ожидает":
                status_item.setForeground(QColor("#f39c12"))
                font = status_item.font()
                font.setBold(True)
                status_item.setFont(font)
            
            self.table.setItem(row, 3, status_item)