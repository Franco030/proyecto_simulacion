DATABASE_URL = "mysql+pymysql://franquito:edwin@localhost:3306/examen_ingles"

MASTER_STYLESHEET = """
QWidget {
    background-color: #f4f7f6; /* Un gris muy claro para el fondo */
    color: #333;
    font-size: 11pt; /* Usamos 'pt' para mejor escalado */
}

/* --- Títulos --- */
QLabel#titleLabel {
    font-size: 20pt;
    font-weight: bold;
    color: #004a99; /* Azul oscuro */
    padding-bottom: 10px;
}
QLabel#usernameLabel {
    font-size: 14pt;
    font-weight: bold;
    color: #333;
}

/* --- Botones --- */
QPushButton {
    background-color: #007bff; /* Azul primario */
    color: white;
    font-weight: bold;
    padding: 8px 12px;
    border: none;
    border-radius: 4px;
    min-height: 28px; /* Soluciona el bug de texto cortado */
}
QPushButton:hover {
    background-color: #0069d9;
}
QPushButton:disabled {
    background-color: #ccc;
    color: #888;
}
QPushButton#logoutButton {
    background-color: #dc3545; /* Rojo de peligro */
}
QPushButton#logoutButton:hover {
    background-color: #c82333;
}

/* --- Campos de Texto --- */
QLineEdit {
    border: 1px solid #ccc;
    border-radius: 4px;
    padding: 6px;
    min-height: 28px; /* Soluciona el bug de texto cortado */
    background-color: white;
}
QLineEdit:focus {
    border: 1px solid #007bff;
}

/* --- Contenedores y Grupos --- */
QGroupBox {
    background-color: #ffffff;
    border: 1px solid #ddd;
    border-radius: 5px;
    margin-top: 10px; /* Espacio para el título */
    font-weight: bold;
}
QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 5px 10px;
    background-color: #e9ecef;
    border-radius: 5px;
    color: #495057;
}

/* --- Pestañas --- */
QTabWidget::pane {
    border: 1px solid #ddd;
    border-radius: 5px;
    background-color: #ffffff;
    border-top-left-radius: 0px;
}
QTabBar::tab {
    background: #e9ecef;
    border: 1px solid #ddd;
    padding: 10px 20px;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
    font-weight: bold;
    color: #555;
}
QTabBar::tab:selected {
    background: #ffffff;
    border-bottom-color: #ffffff; /* Oculta el borde inferior */
    color: #004a99;
}

/* --- Tablas --- */
QTableWidget {
    border: 1px solid #ddd;
    gridline-color: #e0e0e0;
}
QHeaderView::section {
    background-color: #e9ecef;
    padding: 5px;
    border: none;
    font-weight: bold;
}

/* --- Listas --- */
QListWidget {
    border: 1px solid #ddd;
    background-color: white;
}
QListWidget::item:hover {
    background-color: #f0f8ff; /* Azul claro */
}
QListWidget::item:selected {
    background-color: #007bff;
    color: white;
}
"""