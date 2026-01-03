import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from model import SessionLocal
from model import User, Question
from controller.user_controller import UserController
from controller.test_controller import TestController

from view.login_window import LoginWindow
from view.main_menu_window import MainMenuWindow
from view.test_window import TestWindow
from view.results_window import ResultsWindow
from view.dashboard_window import DashboardWindow
from view.admin_dashboard_window import AdminDashboardWindow
from view.user_detail_window import UserDetailWindow

class AppController:
    
    def __init__(self):
        self.app = QApplication(sys.argv)
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
        self.app.setLayoutDirection(Qt.LeftToRight)
        
        self.db_session = SessionLocal()
        
        self.user_controller = UserController(self.db_session)
        self.test_controller = TestController(self.db_session)
        
        self.login_window = LoginWindow()
        self.main_menu_window = MainMenuWindow()
        self.test_window = TestWindow()
        self.results_window = ResultsWindow()
        self.dashboard_window = DashboardWindow()
        self.admin_dashboard_window = AdminDashboardWindow()
        self.user_detail_window = UserDetailWindow()
        
        self.connect_signals()
        print("Controladores y Vistas listos.")

    def run(self):
        print("AppController.run() llamado.")
        self.login_window.show()
        try:
            sys.exit(self.app.exec_())
        except SystemExit:
            print("Cerrando la aplicación...")
        finally:
            self.db_session.close()
            print("Sesión de base de datos cerrada.")

    def connect_signals(self):
        # LoginWindow
        self.login_window.login_button.clicked.connect(self.handle_login)
        self.login_window.register_button.clicked.connect(self.handle_register)
        
        # MainMenuWindow
        self.main_menu_window.practice_button.clicked.connect(self.handle_start_practice)
        self.main_menu_window.final_button.clicked.connect(self.handle_start_final)
        self.main_menu_window.dashboard_button.clicked.connect(self.handle_show_dashboard)
        self.main_menu_window.logout_button.clicked.connect(self.handle_logout)
        
        # TestWindow
        self.test_window.next_button.clicked.connect(self.handle_submit_answer)
        
        # ResultsWindow
        self.results_window.menu_button.clicked.connect(self.show_main_menu)
        
        # DashboardWindow
        self.dashboard_window.menu_button.clicked.connect(self.show_main_menu)
        
        # --- (NUEVO) Conexiones de AdminDashboardWindow ---
        self.admin_dashboard_window.logout_button.clicked.connect(self.handle_logout)
        self.admin_dashboard_window.user_table.cellDoubleClicked.connect(self.handle_show_user_detail)
        self.user_detail_window.close_button.clicked.connect(self.user_detail_window.hide)
        
        print("Señales conectadas.")

    # --- SLOTS (Métodos de manejo) ---
    
    def handle_login(self):
        """
        (ACTUALIZADO) Redirige al admin a su dashboard.
        """
        self.login_window.show_error("")
        username, password = self.login_window.get_credentials()
        
        resultado = self.user_controller.login_user(username, password)
        
        if isinstance(resultado, User):
            
            # --- (NUEVO) Redirección de Admin ---
            if resultado.username == 'admin':
                print("Login de Admin exitoso.")
                self.handle_show_admin_dashboard()
            # --- Fin del cambio ---
            else:
                print(f"Login de usuario exitoso para: {resultado.username}")
                self.test_controller.set_current_user(resultado)
                self.show_main_menu()
        else:
            self.login_window.show_error(resultado)

    def handle_register(self):
        self.login_window.show_error("")
        username, password = self.login_window.get_credentials()
        resultado = self.user_controller.register_user(username, password)
        if isinstance(resultado, User):
            self.login_window.clear_fields()
            self.login_window.show_success_message(
                "Registro Exitoso",
                f"Usuario '{username}' creado. Ahora puedes iniciar sesión."
            )
        else:
            self.login_window.show_error(resultado)

    def show_main_menu(self):
        """
        (ACTUALIZADO) Ahora también oculta el dashboard de admin.
        """
        print("Mostrando menú principal...")
        user = self.test_controller.current_user
        if not user: return
        
        counts = self.user_controller.get_attempt_counts(user)
        self.main_menu_window.update_info(user.username, counts)
        
        # Ocultamos todas las demás ventanas
        self.login_window.hide()
        self.test_window.hide()
        self.results_window.hide()
        self.dashboard_window.hide()
        self.admin_dashboard_window.hide() # <-- (NUEVO)
        
        self.main_menu_window.show()

    def handle_logout(self):
        """
        (ACTUALIZADO) Cierra sesión desde cualquier dashboard.
        """
        print("Cerrando sesión...")
        self.test_controller.set_current_user(None) # Limpia el usuario
        
        # Oculta todas las ventanas de sesión
        self.main_menu_window.hide()
        self.admin_dashboard_window.hide() 
        self.user_detail_window.hide()
        
        # Muestra el login
        self.login_window.clear_fields()
        self.login_window.show()

    
    def handle_show_admin_dashboard(self):
        """Obtiene datos globales y muestra el dashboard de admin."""
        print("Mostrando dashboard de admin...")
        
        # 1. Obtener los datos globales
        admin_data = self.test_controller.get_admin_dashboard_data()
        
        # 2. Actualizar la vista del dashboard de admin
        self.admin_dashboard_window.update_data(admin_data)
        
        # 3. Ocultar login y mostrar dashboard
        self.login_window.hide()
        self.admin_dashboard_window.show()
        self.admin_dashboard_window.showMaximized()
    
    def handle_show_user_detail(self, row, column):
        """
        Se activa con el doble clic en la tabla de admin.
        Abre la ventana de detalle para el usuario de esa fila.
        """
        # Obtenemos el item de la primera columna (columna 0), que es el username
        username_item = self.admin_dashboard_window.user_table.item(row, 0)
        if not username_item:
            return # No hay item en esa celda
            
        username = username_item.text()
        print(f"Abriendo detalles para el usuario: {username}")
        
        # 1. Pedir al controlador que busque TODOS los datos de este usuario
        detail_data = self.test_controller.get_user_detail_data(username)
        
        if "error" in detail_data:
            print(f"Error: {detail_data['error']}")
            # Aquí podríamos mostrar un QMessageBox al admin
            return
            
        # 2. Cargar esos datos en la ventana de detalle
        self.user_detail_window.update_data(detail_data)
        
        # 3. Mostrar la ventana de detalle (como una ventana modal/emergente)
        self.user_detail_window.show()
        
    def handle_start_practice(self):
        print("Iniciando examen de práctica...")
        resultado = self.test_controller.start_new_test('practice')
        if isinstance(resultado, Question):
            self.show_test_window(resultado)
        else:
            self.main_menu_window.show_error(resultado)

    def handle_start_final(self):
        print("Iniciando examen final...")
        resultado = self.test_controller.start_new_test('final')
        if isinstance(resultado, Question):
            self.show_test_window(resultado)
        else:
            self.main_menu_window.show_error(resultado)
            
    def handle_show_dashboard(self):
        print("Mostrando dashboard de usuario...")
        dashboard_data = self.test_controller.get_dashboard_data()
        self.dashboard_window.update_data(dashboard_data)
        self.main_menu_window.hide()
        self.dashboard_window.show()
        self.dashboard_window.showMaximized()
        
    def show_test_window(self, first_question: Question):
        print(f"Mostrando ventana de examen con pregunta: {first_question.text[:20]}...")
        nums = self.test_controller.get_current_question_number()
        self.test_window.display_question(first_question, nums[0], nums[1])
        self.main_menu_window.hide()
        self.test_window.show()

    def handle_submit_answer(self):
        self.test_window.stop_timer()
        selected_id = self.test_window.get_selected_option_id()
        time_taken = self.test_window.get_time_taken()
        self.test_controller.save_answer(selected_id, time_taken)
        next_question = self.test_controller.get_next_question()
        if next_question:
            nums = self.test_controller.get_current_question_number()
            self.test_window.display_question(next_question, nums[0], nums[1])
        else:
            self.show_results()

    def show_results(self):
        results = self.test_controller.finish_test()
        print(f"Examen terminado. Resultados: {results}")
        self.test_window.hide()
        self.results_window.display_results(results)
        self.results_window.show()