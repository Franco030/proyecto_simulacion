import sys
from PyQt5.QtWidgets import (
    QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, 
    QApplication, QFrame, QGridLayout, QGroupBox,
    QTableWidget, QTableWidgetItem, QHeaderView, QListWidget, QListWidgetItem
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor
from constants import MASTER_STYLESHEET

class UserDetailWindow(QWidget):
    
    def __init__(self):
        super().__init__()
        self.user_data = {}
        self.init_ui()

    def init_ui(self):
        # --- Configuración de la Ventana ---
        self.setWindowTitle("Detalle de Usuario")
        self.setMinimumSize(900, 600)
        self.setStyleSheet(MASTER_STYLESHEET)
        
        # --- Widgets Principales ---
        self.username_label = QLabel("Historial de Usuario: [Nombre]")
        self.username_label.setObjectName("titleLabel")

        # --- Columna Izquierda: Lista de Intentos ---
        left_panel = QGroupBox("Intentos Registrados")
        left_layout = QVBoxLayout(left_panel)
        self.attempts_list = QListWidget()
        left_layout.addWidget(self.attempts_list)

        # --- Columna Derecha: Detalles del Intento ---
        right_panel = QGroupBox("Detalle del Intento Seleccionado")
        right_layout = QVBoxLayout(right_panel)

        kpi_layout = QGridLayout()
        self.kpi_score = QLabel("Puntaje: N/A")
        self.kpi_level = QLabel("Nivel: N/A")
        self.kpi_time = QLabel("Tiempo Total: N/A")
        
        # Aplicar estilo de KPI
        self.kpi_score.setStyleSheet("font-weight: bold;")
        self.kpi_level.setStyleSheet("font-weight: bold;")
        self.kpi_time.setStyleSheet("font-weight: bold;")

        kpi_layout.addWidget(self.kpi_score, 0, 0)
        kpi_layout.addWidget(self.kpi_level, 0, 1)
        kpi_layout.addWidget(self.kpi_time, 0, 2)
        right_layout.addLayout(kpi_layout)

        # Tabla de Respuestas
        self.detail_table = QTableWidget()
        self.detail_table.setColumnCount(5)
        self.detail_table.setHorizontalHeaderLabels([
            "Nivel", "Pregunta (Inicio)", "Respuesta Seleccionada", 
            "Tiempo (seg)", "Resultado"
        ])
        self.detail_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.detail_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.detail_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.detail_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.detail_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.detail_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        
        right_layout.addWidget(self.detail_table)
        
        self.close_button = QPushButton("Cerrar")
        
        # --- Layout Principal ---
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        
        content_layout = QHBoxLayout()
        content_layout.addWidget(left_panel, 1)
        content_layout.addWidget(right_panel, 3)
        
        main_layout.addWidget(self.username_label, 0, Qt.AlignCenter)
        main_layout.addLayout(content_layout)
        main_layout.addWidget(self.close_button, 0, Qt.AlignRight)
        
        self.attempts_list.currentItemChanged.connect(self.display_attempt_detail)
        self.close_button.clicked.connect(self.close)

    def display_attempt_detail(self, current_item: QListWidgetItem, previous_item: QListWidgetItem):
        if not current_item:
            return

        attempt_id = current_item.data(Qt.UserRole)
        attempt_data = None
        for att in self.user_data.get("attempts", []):
            if att["id"] == attempt_id:
                attempt_data = att
                break
        
        if not attempt_data:
            return

        self.kpi_score.setText(f"Puntaje: {attempt_data['score']}%")
        self.kpi_level.setText(f"Nivel: {attempt_data['level']}")
        
        total_seconds = attempt_data['total_time_seconds']
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        self.kpi_time.setText(f"Tiempo Total: {minutes}m {seconds}s")

        answers = attempt_data.get("answers", [])
        self.detail_table.setRowCount(len(answers))
        
        for row, ans in enumerate(answers):
            is_correct = ans["is_correct"]
            color = QColor(230, 255, 230) if is_correct else QColor(255, 230, 230) # Verde o Rojo pálido
            
            items = [
                QTableWidgetItem(ans["question_level"]),
                QTableWidgetItem(ans["question_text"]),
                QTableWidgetItem(ans["selected_option"]),
                QTableWidgetItem(str(ans["time_taken"])),
                QTableWidgetItem("Correcto" if is_correct else "Incorrecto")
            ]
            
            for col, item in enumerate(items):
                item.setBackground(color)
                self.detail_table.setItem(row, col, item)

    # --- Método para el Controlador ---
    def update_data(self, data: dict):
        self.user_data = data
        username = data.get("username", "N/A")
        self.username_label.setText(f"Historial de Usuario: {username}")
        
        self.attempts_list.clear()
        self.detail_table.setRowCount(0)
        self.kpi_score.setText("Puntaje: N/A")
        self.kpi_level.setText("Nivel: N/A")
        self.kpi_time.setText("Tiempo Total: N/A")
        
        attempts = data.get("attempts", [])
        if not attempts:
            self.attempts_list.addItem("Este usuario no tiene intentos registrados.")
            return

        for attempt in attempts:
            label = f"[{attempt['type']}] - {attempt['date']} - {attempt['score']}%"
            list_item = QListWidgetItem(label)
            list_item.setData(Qt.UserRole, attempt['id'])
            self.attempts_list.addItem(list_item)
            
        self.attempts_list.setCurrentRow(0)