import sys
from PyQt5.QtWidgets import (
    QWidget, QLabel, QPushButton, QVBoxLayout, 
    QApplication, QSpacerItem, QSizePolicy, QFrame, QGroupBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from constants import MASTER_STYLESHEET

class ResultsWindow(QWidget):
    
    def __init__(self):
        super().__init__()
        self.breakdown_labels = [] 
        self.init_ui()

    def init_ui(self):
        # --- Configuración de la Ventana ---
        self.setWindowTitle("Simulador de Examen - Resultados")
        self.setFixedSize(400, 480)
        self.setStyleSheet(MASTER_STYLESHEET)
        
        # --- Creación de Widgets ---
        self.title_label = QLabel("Examen Finalizado")
        self.title_label.setObjectName("titleLabel")
        self.title_label.setAlignment(Qt.AlignCenter)

        # Frame para los resultados principales
        self.results_group = QGroupBox("Resultado General")
        results_layout = QVBoxLayout(self.results_group)
        results_layout.setSpacing(10)
        
        self.level_label = QLabel("Nivel: Aprobado")
        self.level_label.setObjectName("levelLabel")
        self.level_label.setAlignment(Qt.AlignCenter)
        
        self.score_label = QLabel("Puntaje: 100%")
        self.score_label.setObjectName("scoreLabel")
        self.score_label.setAlignment(Qt.AlignCenter)
        
        results_layout.addWidget(self.level_label)
        results_layout.addWidget(self.score_label)

        # --- Frame para el desglose ---
        self.breakdown_group = QGroupBox("Desglose por Nivel")
        self.breakdown_layout = QVBoxLayout(self.breakdown_group)
        self.breakdown_layout.setContentsMargins(15, 15, 15, 15)
        self.breakdown_layout.setSpacing(8)
        
        # (El contenido se añadirá dinámicamente)

        # Botón para volver al menú
        self.menu_button = QPushButton("Volver al Menú Principal")

        # --- Layout (Organización) ---
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(30, 20, 30, 30)
        main_layout.setSpacing(15)
        
        main_layout.addWidget(self.title_label)
        main_layout.addWidget(self.results_group)
        main_layout.addWidget(self.breakdown_group)
        main_layout.addStretch()
        main_layout.addWidget(self.menu_button)
        
        self.setLayout(main_layout)

    def _clear_layout(self, layout):
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()

    # --- Métodos para el Controlador ---
    def display_results(self, results: dict):
        score = results.get("score", 0)
        level = results.get("level", "N/A")
        correct = results.get("correct", 0)
        total = results.get("total", 0)
        level_scores = results.get("level_scores", {})
        
        self.level_label.setText(f"{level}")
        self.score_label.setText(f"Puntaje: {score}%")

        self._clear_layout(self.breakdown_layout)
        
        level_order = ["Beginner", "Elementary", "Pre-intermediate", "Intermediate", "Upper-intermediate", "Advanced"]
        
        for level_name in level_order:
            scores = level_scores.get(level_name)
            if scores and scores["total"] > 0:
                text = f"{level_name}: {scores['correct']} / {scores['total']}"
                label = QLabel(text)
                self.breakdown_layout.addWidget(label)
        
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        self.breakdown_layout.addWidget(separator)
        
        total_text = f"Total: {correct} / {total}"
        total_label = QLabel(total_text)
        total_label.setFont(QFont(self.font().family(), 11, QFont.Bold))
        self.breakdown_layout.addWidget(total_label)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ResultsWindow()
    test_results = {
        "score": 75.0, "level": "Intermediate", "correct": 30, "total": 40,
        "level_scores": {
            "Beginner": {"correct": 5, "total": 5}, "Elementary": {"correct": 6, "total": 7},
            "Pre-intermediate": {"correct": 7, "total": 8}, "Intermediate": {"correct": 8, "total": 10},
            "Upper-intermediate": {"correct": 2, "total": 5}, "Advanced": {"correct": 2, "total": 5}
        }
    }
    window.display_results(test_results)
    window.show()
    sys.exit(app.exec_())