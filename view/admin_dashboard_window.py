import sys
from PyQt5.QtWidgets import (
    QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, 
    QApplication, QTabWidget, QFrame, QGridLayout, QGroupBox,
    QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from constants import MASTER_STYLESHEET

class AdminDashboardWindow(QWidget):
    
    def __init__(self):
        super().__init__()
        self.kpi_widgets = {}
        self.user_table = None
        self.chart_widgets = {}
        self.init_ui()

    def init_ui(self):
        # --- Configuración de la Ventana ---
        self.setWindowTitle("Panel de Administración")
        self.setMinimumSize(800, 700)
        self.setStyleSheet(MASTER_STYLESHEET)
        
        # --- Creación de Widgets ---
        self.title_label = QLabel("Dashboard de Administrador")
        self.title_label.setObjectName("titleLabel")
        self.title_label.setAlignment(Qt.AlignCenter)

        self.tabs = QTabWidget()
        self.summary_tab = self._create_summary_tab()
        self.users_tab = self._create_users_tab()
        self.tabs.addTab(self.summary_tab, "Resumen Global")
        self.tabs.addTab(self.users_tab, "Detalle por Usuario")
        
        self.logout_button = QPushButton("Cerrar Sesión (Admin)")
        self.logout_button.setObjectName("logoutButton")

        # --- Layout Principal ---
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        main_layout.addWidget(self.title_label)
        main_layout.addWidget(self.tabs)
        main_layout.addWidget(self.logout_button, 0, Qt.AlignRight)
        self.setLayout(main_layout)

    def _create_summary_tab(self) -> QWidget:
        tab_widget = QWidget()
        main_layout = QVBoxLayout(tab_widget)
        main_layout.setContentsMargins(15, 15, 15, 15)
        
        kpi_group = QGroupBox("Estadísticas Globales")
        kpi_layout = QGridLayout(kpi_group)
        
        kpi_labels = {
            "total_users": QLabel("Total de Usuarios:"),
            "total_practice_attempts": QLabel("Intentos de Práctica (Totales):"),
            "total_final_attempts": QLabel("Intentos de Examen Final (Totales):"),
            "avg_practice_score": QLabel("Promedio Práctica (Global):"),
            "avg_final_score": QLabel("Promedio Final (Global):")
        }
        kpi_values = {
            "total_users": QLabel("0"), "total_practice_attempts": QLabel("0"),
            "total_final_attempts": QLabel("0"), "avg_practice_score": QLabel("0.0 %"),
            "avg_final_score": QLabel("0.0 %")
        }
        self.kpi_widgets = kpi_values
        
        kpi_layout.addWidget(kpi_labels["total_users"], 0, 0)
        kpi_layout.addWidget(kpi_values["total_users"], 0, 1)
        kpi_layout.addWidget(kpi_labels["avg_practice_score"], 0, 2)
        kpi_layout.addWidget(kpi_values["avg_practice_score"], 0, 3)
        kpi_layout.addWidget(kpi_labels["total_practice_attempts"], 1, 0)
        kpi_layout.addWidget(kpi_values["total_practice_attempts"], 1, 1)
        kpi_layout.addWidget(kpi_labels["total_final_attempts"], 2, 0)
        kpi_layout.addWidget(kpi_values["total_final_attempts"], 2, 1)
        kpi_layout.addWidget(kpi_labels["avg_final_score"], 1, 2)
        kpi_layout.addWidget(kpi_values["avg_final_score"], 1, 3)
        
        chart_group = QGroupBox("Desempeño Global por Nivel de Pregunta")
        chart_layout = QVBoxLayout(chart_group)
        figure_level = Figure(figsize=(7, 4), dpi=100)
        canvas_level = FigureCanvas(figure_level)
        ax_level = figure_level.add_subplot(111)
        self.chart_widgets = {"canvas": canvas_level, "ax": ax_level}
        chart_layout.addWidget(canvas_level)

        main_layout.addWidget(kpi_group)
        main_layout.addWidget(chart_group)
        return tab_widget

    def _create_users_tab(self) -> QWidget:
        tab_widget = QWidget()
        main_layout = QVBoxLayout(tab_widget)
        main_layout.setContentsMargins(15, 15, 15, 15)
        
        info_label = QLabel("Haz doble clic en un usuario para ver su historial detallado.")
        info_label.setAlignment(Qt.AlignCenter)
        
        self.user_table = QTableWidget()
        self.user_table.setColumnCount(5)
        self.user_table.setHorizontalHeaderLabels([
            "Usuario", "Intentos Práctica", "Intentos Final", 
            "Promedio Práctica (%)", "Último Nivel Final"
        ])
        self.user_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.user_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.user_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.user_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        main_layout.addWidget(info_label)
        main_layout.addWidget(self.user_table)
        return tab_widget

    # --- Métodos para el Controlador ---
    def update_data(self, data: dict):
        stats = data.get("global_stats", {})
        self.kpi_widgets["total_users"].setText(str(stats.get("total_users", 0)))
        self.kpi_widgets["total_practice_attempts"].setText(str(stats.get("total_practice_attempts", 0)))
        self.kpi_widgets["total_final_attempts"].setText(str(stats.get("total_final_attempts", 0)))
        self.kpi_widgets["avg_practice_score"].setText(f"{stats.get('avg_practice_score', 0.0):.1f} %")
        self.kpi_widgets["avg_final_score"].setText(f"{stats.get('avg_final_score', 0.0):.1f} %")

        ax = self.chart_widgets["ax"]
        canvas = self.chart_widgets["canvas"]
        level_data = data.get("global_level_performance", {})
        
        labels, percentages = [], []
        for level, scores in level_data.items():
            if scores["total"] > 0:
                labels.append(level)
                percent = (scores["correct"] / scores["total"]) * 100
                percentages.append(percent)

        ax.clear()
        if labels:
            ax.bar(labels, percentages, color="#007bff")
            ax.set_ylabel("Precisión Global (%)")
            ax.set_ylim(0, 100)
            ax.set_title("Precisión de todas las preguntas respondidas por nivel")
        canvas.draw()
        
        user_details = data.get("user_details", [])
        self.user_table.setRowCount(len(user_details))
        
        for row, user in enumerate(user_details):
            self.user_table.setItem(row, 0, QTableWidgetItem(user.get("username")))
            self.user_table.setItem(row, 1, QTableWidgetItem(str(user.get("practice_attempts"))))
            self.user_table.setItem(row, 2, QTableWidgetItem(str(user.get("final_attempts"))))
            self.user_table.setItem(row, 3, QTableWidgetItem(f"{user.get('avg_practice_score', 0.0):.1f} %"))
            self.user_table.setItem(row, 4, QTableWidgetItem(user.get("last_final_level")))