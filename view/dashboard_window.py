import sys
from PyQt5.QtWidgets import (
    QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, 
    QApplication, QTabWidget, QFrame, QGridLayout, QGroupBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from constants import MASTER_STYLESHEET

class DashboardWindow(QWidget):
    
    def __init__(self):
        super().__init__()
        self.practice_widgets = {}
        self.final_widgets = {}
        self.init_ui()

    def init_ui(self):
        # --- Configuración de la Ventana ---
        self.setWindowTitle("Simulador de Examen - Mi Progreso")
        self.setMinimumSize(700, 650)
        self.setStyleSheet(MASTER_STYLESHEET)
        
        # --- Creación de Widgets ---
        self.title_label = QLabel("Mi Progreso")
        self.title_label.setObjectName("titleLabel")
        self.title_label.setAlignment(Qt.AlignCenter)

        self.tabs = QTabWidget()
        self.practice_tab = self._create_stats_tab("practice_stats")
        self.final_tab = self._create_stats_tab("final_stats")
        self.tabs.addTab(self.practice_tab, "Estadísticas de Práctica")
        self.tabs.addTab(self.final_tab, "Estadísticas de Examen Final")
        
        self.menu_button = QPushButton("Volver al Menú Principal")

        # --- Layout (Organización) ---
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        main_layout.addWidget(self.title_label)
        main_layout.addWidget(self.tabs)
        main_layout.addWidget(self.menu_button)
        self.setLayout(main_layout)

    def _create_stats_tab(self, widget_key: str) -> QWidget:
        tab_widget = QWidget()
        main_layout = QVBoxLayout(tab_widget)
        main_layout.setContentsMargins(15, 15, 15, 15)
        
        stats_group = QGroupBox("Resumen General")
        stats_layout = QGridLayout(stats_group)
        
        lbl_attempts = QLabel("Intentos:")
        lbl_remaining = QLabel("Restantes:")
        lbl_avg_score = QLabel("Promedio:")
        lbl_high_score = QLabel("Mejor Puntaje:")
        val_attempts = QLabel("0")
        val_remaining = QLabel("N/A")
        val_avg_score = QLabel("0.0 %")
        val_high_score = QLabel("0.0 %")
        lbl_last_level = QLabel("Último Nivel:")
        val_last_level = QLabel("N/A")

        stats_layout.addWidget(lbl_attempts, 0, 0)
        stats_layout.addWidget(val_attempts, 0, 1)
        stats_layout.addWidget(lbl_remaining, 1, 0)
        stats_layout.addWidget(val_remaining, 1, 1)
        stats_layout.addWidget(lbl_avg_score, 0, 2)
        stats_layout.addWidget(val_avg_score, 0, 3)
        stats_layout.addWidget(lbl_high_score, 1, 2)
        stats_layout.addWidget(val_high_score, 1, 3)
        
        if widget_key == "final_stats":
            stats_layout.addWidget(lbl_last_level, 2, 0)
            stats_layout.addWidget(val_last_level, 2, 1, 1, 3)
        
        charts_layout = QHBoxLayout()
        figure_time = Figure(figsize=(3, 3), dpi=90)
        canvas_time = FigureCanvas(figure_time)
        ax_time = figure_time.add_subplot(111)
        figure_level = Figure(figsize=(3, 3), dpi=90)
        canvas_level = FigureCanvas(figure_level)
        ax_level = figure_level.add_subplot(111)
        charts_layout.addWidget(canvas_time)
        charts_layout.addWidget(canvas_level)

        main_layout.addWidget(stats_group)
        main_layout.addLayout(charts_layout)
        
        widget_refs = {
            "val_attempts": val_attempts, "val_remaining": val_remaining,
            "val_avg_score": val_avg_score, "val_high_score": val_high_score,
            "val_last_level": val_last_level, "canvas_time": canvas_time,
            "ax_time": ax_time, "canvas_level": canvas_level, "ax_level": ax_level
        }
        
        if widget_key == "practice_stats":
            self.practice_widgets = widget_refs
        else:
            self.final_widgets = widget_refs
            
        return tab_widget

    def update_data(self, data: dict):
        self._update_tab_ui(
            widgets=self.practice_widgets, stats=data.get("practice_stats", {}), tab_type="practice"
        )
        self._update_tab_ui(
            widgets=self.final_widgets, stats=data.get("final_stats", {}), tab_type="final"
        )
        
    def _update_tab_ui(self, widgets: dict, stats: dict, tab_type: str):
        if not widgets or not stats: return
            
        widgets["val_attempts"].setText(str(stats.get("attempts_count", 0)))
        widgets["val_remaining"].setText(str(stats.get("attempts_remaining", "N/A")))
        widgets["val_avg_score"].setText(f"{stats.get('avg_score', 0.0):.1f} %")
        widgets["val_high_score"].setText(f"{stats.get('high_score', 0.0):.1f} %")
        if tab_type == "final":
            widgets["val_last_level"].setText(stats.get("last_level", "N/A"))

        ax_time = widgets["ax_time"]
        canvas_time = widgets["canvas_time"]
        scores_over_time = stats.get("scores_over_time", [])
        
        ax_time.clear()
        if scores_over_time:
            ax_time.plot(range(1, len(scores_over_time) + 1), scores_over_time, marker='o', linestyle='-')
            ax_time.set_xlabel("Intentos")
            ax_time.set_ylabel("Puntaje (%)")
            ax_time.set_ylim(0, 100)
            ax_time.set_xticks(range(1, len(scores_over_time) + 1))
        ax_time.set_title("Puntaje por Intento")
        canvas_time.draw()

        ax_level = widgets["ax_level"]
        canvas_level = widgets["canvas_level"]
        level_data = stats.get("performance_by_level", {})
        
        labels, percentages, colors = [], [], []
        for level, scores in level_data.items():
            if scores["total"] > 0:
                labels.append(level[:5] + ".")
                percent = (scores["correct"] / scores["total"]) * 100
                percentages.append(percent)
                colors.append('#28a745' if percent >= 70 else '#dc3545')

        ax_level.clear()
        if labels:
            ax_level.bar(labels, percentages, color=colors)
            ax_level.set_ylabel("Precisión (%)")
            ax_level.set_ylim(0, 100)
        ax_level.set_title("Precisión por Nivel")
        canvas_level.draw()