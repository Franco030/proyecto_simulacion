# Simulador de Examen de Inglés (Arquitectura MVC)

Este proyecto es una aplicación de escritorio completa, desarrollada en Python, que simula un examen de inglés para evaluar y ubicar el nivel de competencia de un usuario. La aplicación sigue una estricta arquitectura Modelo-Vista-Controlador (MVC) y utiliza SQLAlchemy para la gestión de la base de datos y PyQt5 para la interfaz gráfica.

Incluye dashboards detallados tanto para el usuario como para un administrador, aprovechando al máximo los datos recopilados de cada intento.

## Características Principales

  * **Doble Modo de Simulación:**
      * **Práctica:** Un examen de 20 preguntas seleccionadas *totalmente al azar* del banco de 80.
      * **Examen Final:** Un examen de 40 preguntas seleccionadas mediante **muestreo estratificado** (un número específico de preguntas de cada nivel de dificultad).
  * **Sistema de Calificación Dual:**
      * **Práctica:** Asigna un nivel estimado (Beginner, Intermediate, etc.) basado en el puntaje porcentual final.
      * [cite\_start]**Examen Final:** Utiliza una lógica de ubicación detallada basada en el **número de fallos por sección** [cite: 510-522], tal como lo requieren los documentos del proyecto.
  * **Gestión de Usuarios:** Sistema completo de registro e inicio de sesión con hashing de contraseñas (`bcrypt`).
  * **Panel de Administrador:**
      * Inicio de sesión especial con el usuario `admin` (contraseña: `admin123`).
      * **Dashboard Global:** Muestra KPIs de toda la plataforma (total de usuarios, total de intentos, promedios globales).
      * **Análisis por Nivel:** Gráfico de precisión global, mostrando el porcentaje de aciertos para cada nivel de pregunta (Beginner, etc.) en toda la plataforma.
      * **Tabla de Usuarios:** Lista de todos los usuarios registrados con sus estadísticas clave.
  * **Visor de Detalles de Usuario:**
      * Al hacer doble clic en un usuario en el panel de admin, se abre una ventana dedicada.
      * Muestra **cada intento** que el usuario ha realizado.
      * Al seleccionar un intento, se muestra una tabla detallada con **cada pregunta**, la respuesta del usuario, el tiempo de respuesta y si fue correcta.
  * **Dashboard de Usuario:**
      * Sistema de pestañas para "Práctica" y "Examen Final".
      * Muestra estadísticas clave (mejor puntaje, promedio, intentos restantes).
      * Gráfico de "Puntaje por Intento" (gráfico de líneas).
      * Gráfico de "Precisión por Nivel" (gráfico de barras).
  * **Banco de Preguntas:**
      * [cite\_start]Utiliza un banco de 80 reactivos[cite: 616].
      * Soporte completo para **imágenes** en las preguntas.
  * **Lógica de Examen:**
      * [cite\_start]Temporizador de 1 minuto por pregunta[cite: 625].
      * El botón "Siguiente" se deshabilita hasta que se selecciona una opción.
      * Las opciones de respuesta se barajan (aleatorizan) cada vez que se muestran.

-----

## Stack Tecnológico

  * **Lenguaje:** Python 3.x
  * **Interfaz Gráfica (UI):** PyQt5
  * **Base de Datos (ORM):** SQLAlchemy
  * **Base de Datos (Desarrollo):** SQLite
  * **Base de Datos (Producción):** Preparado para MySQL
  * **Driver MySQL:** `pymysql` (debe ser instalado para producción)
  * **Gráficos (Dashboards):** `matplotlib`
  * **Seguridad:** `bcrypt` (para hashing de contraseñas)

-----

## Instalación y Puesta en Marcha

Sigue estos pasos para ejecutar el proyecto en un entorno de desarrollo.

### 1\. Prerrequisitos

Asegúrate de tener Python 3 instalado. Se recomienda usar un entorno virtual:

```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

### 2\. Instalación de Dependencias

Crea un archivo `requirements.txt` con el siguiente contenido:

```
PyQt5
SQLAlchemy
matplotlib
bcrypt
pymysql
```

Luego, instala las dependencias:

```bash
pip install -r requirements.txt
```

### 3\. Creación y Población de la Base de Datos

El proyecto está configurado para usar SQLite por defecto. Para crear la base de datos, las tablas, las preguntas y el usuario administrador, simplemente ejecuta:

```bash
python populate_db.py
```

Esto creará un archivo `simulator.db` en la raíz del proyecto y te notificará que el usuario `admin` ha sido creado.

### 4\. (Opcional) Poblar con Datos de Simulación

Para probar los dashboards de administrador y usuario, puedes ejecutar el script de simulación. Este script crea 3+ usuarios falsos (ej. `ana_gomez`) con la contraseña `pass123` y genera un historial de exámenes falso para ellos.

**¡Importante\!** Debes correr `populate_db.py` *antes* de correr este script.

```bash
python populate_simulated_users.py
```

### 5\. Ejecutar la Aplicación

Una vez que la base de datos esté poblada, inicia la aplicación principal:

```bash
python main.py
```

Puedes iniciar sesión con:

  * **Usuario Administrador:** `admin` / `admin123`
  * **Usuario Simulado:** `ana_gomez` / `pass123`

-----

## Arquitectura de la Solución (MVC)

El proyecto está estrictamente separado en tres módulos (carpetas) que representan el patrón **Modelo-Vista-Controlador**.

### Modelo (`model/`)

  * **Qué es:** Es la capa de datos. Define la *estructura* de nuestra información.
  * **Archivos Clave:** `database.py` (configura el motor y la sesión de SQLAlchemy) y `models.py` (define las clases `User`, `Question`, `TestAttempt`, etc.).
  * **Responsabilidad:** Interactuar con la base de datos. No sabe nada de la interfaz gráfica ni de las reglas de negocio. Solo sabe cómo guardar y recuperar datos.

### Vista (`view/`)

  * **Qué es:** Es la capa de presentación (la UI). Es "pasiva" o "tonta".
  * **Archivos Clave:** `login_window.py`, `test_window.py`, `admin_dashboard_window.py`, etc.
  * **Responsabilidad:** Mostrar widgets (botones, tablas, gráficos) al usuario y emitir "señales" (como `login_button.clicked`) cuando el usuario interactúa. *No toma decisiones*.

### Controlador (`controller/`)

  * **Qué es:** Es el "cerebro" de la aplicación. Actúa como el intermediario que une el Modelo y la Vista.
  * **Archivos Clave:**
      * `user_controller.py`: Maneja la lógica de negocio para registrar y autenticar usuarios.
      * `test_controller.py`: El cerebro principal. Maneja la lógica de iniciar exámenes, seleccionar preguntas, calificar respuestas y recopilar datos para los dashboards.
      * `app_controller.py`: El "Orquestador". Es el único controlador que habla directamente con las ventanas de la Vista.

### ¿Cómo se Conectan los Módulos? (Flujo de Ejemplo)

Tomemos como ejemplo el **Login del Admin** y la apertura de su dashboard:

1.  **Vista:** El usuario escribe `admin` / `admin123` en `LoginWindow` y presiona el botón. La Vista emite la señal `login_button.clicked`.
2.  **Controlador (Orquestador):** `AppController`, que estaba "escuchando" esa señal, activa su función `handle_login()`.
3.  **Controlador (Lógica):** `AppController` llama a `self.user_controller.login_user('admin', 'admin123')`.
4.  **Controlador (Lógica) -\> Modelo:** `UserController` consulta al Modelo (`db.execute(select(User)...)`) para encontrar un usuario con ese nombre.
5.  **Modelo -\> Controlador (Lógica):** El Modelo devuelve el objeto `User` de 'admin', incluyendo su `password_hash`.
6.  **Controlador (Lógica):** `UserController` usa `bcrypt.checkpw` para verificar la contraseña. Como es correcta, devuelve el objeto `User` a `AppController`.
7.  **Controlador (Orquestador):** `AppController` recibe el objeto `User` y ve que `username == 'admin'`. Toma una decisión: "No debo mostrar el menú de usuario, debo mostrar el dashboard de admin".
8.  **Controlador (Orquestador) -\> Controlador (Lógica):** Llama a `self.test_controller.get_admin_dashboard_data()`.
9.  **Controlador (Lógica) -\> Modelo:** `TestController` realiza múltiples consultas complejas al Modelo (`TestAttempt`, `AttemptAnswer`, `User`) para recopilar todas las estadísticas globales.
10. **Modelo -\> Controlador (Lógica):** El Modelo devuelve los datos crudos.
11. **Controlador (Lógica):** `TestController` procesa los datos y devuelve un gran diccionario de estadísticas a `AppController`.
12. **Controlador (Orquestador) -\> Vista:** `AppController` llama a `self.admin_dashboard_window.update_data(stats_dict)`.
13. **Vista:** `AdminDashboardWindow` recibe el diccionario y lo usa para rellenar sus tablas y dibujar sus gráficos.
14. **Controlador (Orquestador) -\> Vista:** Finalmente, `AppController` llama a `self.login_window.hide()` y `self.admin_dashboard_window.show()`.

-----

## Modelo de Base de Datos

El modelo de datos fue diseñado para ser normalizado y capturar cada pieza de información relevante para un análisis detallado.

  * **`User`**: Almacena a los usuarios.
  * **`Question`**: El reactivo. Su `level` (ej. "Beginner") es la columna más importante para la lógica de calificación.
  * **`Option`**: Las 4+ opciones de una pregunta. La columna `is_correct` (Booleano) es la clave para la calificación.
  * **`TestAttempt`**: El "encabezado" de un examen. Registra quién lo hizo (`user_id`), qué tipo fue (`test_type`), y el resultado final (`score_percentage`, `assigned_level`).
  * **`AttemptAnswer`**: La tabla más detallada. Es el "cuerpo" de un examen. Cada fila es una sola respuesta a una sola pregunta. Lo más importante:
      * `selected_option_id`: Nos dice qué respondió el usuario.
      * `time_taken_seconds`: Nos permite calcular el tiempo total del examen y ver qué preguntas tomaron más tiempo.

-----

## Retos de Desarrollo y Soluciones

Durante el desarrollo, surgieron varios retos complejos que requirieron soluciones específicas.

### 1\. Reto: Lógica de Calificación Dual

  * [cite\_start]**Problema:** El Simulador de Práctica es 100% aleatorio, pero el Examen Final necesita un número específico de preguntas de cada nivel para que la calificación por fallos [cite: 510-522] funcione.
  * **Solución:** Se implementaron dos lógicas de selección de preguntas en `TestController`:
      * **Práctica:** Usa `random.sample(all_questions, 20)` para una selección simple y rápida.
      * **Final:** Usa **Muestreo Estratificado**. El controlador itera sobre un diccionario `strata = {"Beginner": 5, "Elementary": 7, ...}`, consulta en la BD las preguntas de *ese* nivel y toma una muestra aleatoria de esa sub-lista. Luego une todas las muestras y las baraja.

### 2\. Reto: El Bug de Calificación "0%"

  * **Problema:** Durante las pruebas, todos los exámenes (aunque las respuestas fueran correctas) devolvían un puntaje de 0%.
  * **Análisis:** Se descubrió un bug de transacciones de SQLAlchemy. La función `save_answer` (llamada en cada clic de "Siguiente") añadía las respuestas a la *sesión*, pero no las escribía en la BD. Luego, `finish_test` intentaba *leer* las respuestas de la BD (que aún estaba vacía), contaba 0 correctas, y *luego* hacía `commit()`, guardando las respuestas correctas junto con el puntaje incorrecto de 0.
  * **Solución:** Se añadió un `db.session.commit()` al **inicio** de la función `finish_test`. Esto fuerza a SQLAlchemy a escribir todas las respuestas "pendientes" en la base de datos *antes* de que la misma función intente leerlas y calificarlas.

### 3\. Reto: Identificación Robusta de Respuestas

  * **Problema:** El sistema para identificar qué `QRadioButton` seleccionó el usuario era frágil. Inicialmente, se comparaba el *texto* del botón, lo cual fallaba.
  * **Solución:** Se implementó una solución robusta usando `QButtonGroup`. En `display_question`, vinculamos el ID de la base de datos de la opción directamente al botón:
      * `self.button_group.setId(radio_button, option.id)`
  * Para obtener la respuesta, simplemente le preguntamos al grupo por el ID, eliminando cualquier comparación de texto:
      * `checked_id = self.button_group.checkedId()`

### 4\. Reto: Dashboards Detallados y Eficientes

  * **Problema:** Cargar el historial completo de un usuario, o de *todos* los usuarios, puede ser lento y complejo.
  * **Solución:** Se dividió la lógica en el `TestController`:
      * `get_admin_dashboard_data()`: Realiza varias consultas agregadas (`func.count`, `func.avg`) para obtener los KPIs globales rápidamente, y luego itera sobre todos los usuarios para crear la tabla.
      * `get_user_detail_data(username)`: Esta función solo se llama *bajo demanda* (cuando el admin hace doble clic). Usa `selectinload` de SQLAlchemy para cargar de forma eficiente todo el árbol de objetos de un solo usuario (Intentos -\> Respuestas -\> Opciones y Preguntas) y los procesa para la ventana de detalle.