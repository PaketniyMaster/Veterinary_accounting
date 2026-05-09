import sys
import os
import qtawesome as qta
import qdarktheme # ДОБАВЛЕН ИМПОРТ ГЛОБАЛЬНОЙ ТЕМЫ
from frontend.ui.doctors_view import DoctorsView
# Добавляем корневую папку проекта в пути поиска Python
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from frontend.ui.appointments_view import AppointmentsView
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QHBoxLayout, 
                             QVBoxLayout, QPushButton, QStackedWidget, QLabel)
from PyQt6.QtCore import Qt, QSize
from frontend.ui.clients_view import ClientsView
from frontend.ui.dashboard_view import DashboardView
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ветеринарная клиника - Учет пациентов")
        self.resize(1024, 768)

        self.is_dark_theme = True # Флаг текущей темы

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 1. ЛЕВОЕ БОКОВОЕ МЕНЮ
        sidebar = QWidget()
        sidebar.setFixedWidth(220)
        
        # Оставляем только базовый стиль для кнопок меню. 
        # Все цвета фона теперь контролирует qdarktheme!
        sidebar.setStyleSheet("""
            QPushButton {
                text-align: left;
                padding: 12px 15px;
                font-size: 15px;
                border-radius: 8px;
                border: none;
            }
            QPushButton:checked {
                background-color: #0fbbc9;
                color: white;
                font-weight: bold;
            }
        """)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(10, 30, 10, 20)
        sidebar_layout.setSpacing(5)

        logo_label = QLabel("VET CLINIC")
        logo_label.setStyleSheet("color: #0fbbc9; font-size: 20px; font-weight: bold; padding-bottom: 20px;")
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sidebar_layout.addWidget(logo_label)

        self.btn_dashboard = self.create_nav_button("Главная", "fa5s.home")
        self.btn_clients = self.create_nav_button("Пациенты", "fa5s.paw")
        self.btn_doctors = self.create_nav_button("Врачи", "fa5s.user-md")
        self.btn_appointments = self.create_nav_button("Расписание", "fa5s.calendar-alt")
        
        for btn in [self.btn_dashboard, self.btn_clients, self.btn_doctors, self.btn_appointments]:
            btn.setCheckable(True)
            sidebar_layout.addWidget(btn)
        
        self.btn_dashboard.setChecked(True)
        sidebar_layout.addStretch()

        # --- КНОПКА ПЕРЕКЛЮЧЕНИЯ ТЕМЫ ---
        self.btn_theme = QPushButton("  Светлая тема")
        self.btn_theme.setIcon(qta.icon("fa5s.sun", color="#f1c40f"))
        self.btn_theme.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_theme.clicked.connect(self.toggle_theme)
        sidebar_layout.addWidget(self.btn_theme)

        # 2. ПРАВАЯ ЧАСТЬ (Стек экранов)
        self.stacked_widget = QStackedWidget()
        self.dashboard_page = DashboardView()
        self.stacked_widget.addWidget(self.dashboard_page)

        self.clients_page = ClientsView()
        self.stacked_widget.addWidget(self.clients_page)
        # --- ДОБАВЛЯЕМ ОКНО ВРАЧЕЙ ---
        self.doctors_page = DoctorsView()
        self.stacked_widget.addWidget(self.doctors_page)    
        self.appointments_page = AppointmentsView()
        self.stacked_widget.addWidget(self.appointments_page)

        main_layout.addWidget(sidebar)
        main_layout.addWidget(self.stacked_widget)

        self.btn_dashboard.clicked.connect(lambda: self.switch_page(0, self.btn_dashboard))
        self.btn_clients.clicked.connect(lambda: self.switch_page(1, self.btn_clients))
        self.btn_doctors.clicked.connect(lambda: self.switch_page(2, self.btn_doctors)) # Новая строка
        self.btn_appointments.clicked.connect(lambda: self.switch_page(3, self.btn_appointments)) # Индекс стал 3

    def create_nav_button(self, text, icon_name):
        btn = QPushButton(f"  {text}")
        btn.setIcon(qta.icon(icon_name)) # Иконки теперь сами подстроятся под тему
        btn.setIconSize(QSize(20, 20))
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        return btn

    def switch_page(self, index, active_button):
        self.stacked_widget.setCurrentIndex(index)
        for btn in [self.btn_dashboard, self.btn_clients, self.btn_doctors, self.btn_appointments]: # Добавили btn_doctors
            btn.setChecked(False)
        active_button.setChecked(True)

    def create_page_stub(self, title_text):
        page = QWidget()
        layout = QVBoxLayout(page)
        label = QLabel(title_text)
        label.setStyleSheet("font-size: 28px; font-weight: bold;")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)
        return page

    def toggle_theme(self):
        """Мгновенно меняет глобальную тему всего приложения"""
        if self.is_dark_theme:
            # Включаем светлую
            qdarktheme.setup_theme("light", custom_colors={"primary": "#0fbbc9"})
            self.btn_theme.setText("  Темная тема")
            self.btn_theme.setIcon(qta.icon("fa5s.moon", color="#34495e"))
            self.is_dark_theme = False
        else:
            # Включаем темную
            qdarktheme.setup_theme("dark", custom_colors={"primary": "#0fbbc9"})
            self.btn_theme.setText("  Светлая тема")
            self.btn_theme.setIcon(qta.icon("fa5s.sun", color="#f1c40f"))
            self.is_dark_theme = True

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # ПРИ ЗАПУСКЕ ПРИЛОЖЕНИЯ АКТИВИРУЕМ ТЕМНУЮ ТЕМУ
    qdarktheme.setup_theme("dark", custom_colors={"primary": "#0fbbc9"})
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec())