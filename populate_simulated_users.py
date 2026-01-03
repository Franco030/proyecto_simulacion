# populate_simulated_users.py

import bcrypt
import random
import datetime
from sqlalchemy import select
from sqlalchemy.orm import selectinload, Session  # <-- (NUEVO) Importa Session
from model import SessionLocal, engine, Base
from model import User, Question, Option, TestAttempt, AttemptAnswer

# --- Helper copiado de user_controller.py ---
def hash_password(password: str) -> bytes:
    """Genera un hash seguro para la contraseña."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt)

# --- Helpers copiados de test_controller.py ---
def _estimate_level_by_score(score: float) -> str:
    """Estima un nivel basado en el puntaje porcentual."""
    if score < 30: return "Beginner"
    if score < 50: return "Elementary"
    if score < 70: return "Pre-intermediate"
    if score < 85: return "Intermediate"
    if score < 95: return "Upper-intermediate"
    return "Advanced"

def _calculate_simulated_level(level_performance: dict) -> str:
    """
    Simula la lógica de ubicación basada en el conteo de fallos.
    """
    failures = {}
    for level, data in level_performance.items():
        failures[level] = data["total"] - data["correct"]

    # Aplicar las reglas de ubicación
    if failures.get("Beginner", 0) >= 2:
        return "Beginner"
    if failures.get("Elementary", 0) >= 3:
        return "Elementary"
    if failures.get("Pre-intermediate", 0) >= 3:
        return "Pre-intermediate"
    if failures.get("Intermediate", 0) >= 4:
        return "Intermediate"
    if failures.get("Upper-intermediate", 0) >= 2:
        return "Upper-intermediate"
    if failures.get("Advanced", 0) >= 1:
        return "Advanced"
    return "Advanced"

def get_stratified_questions(all_questions: list) -> list:
    """
    Selecciona 40 preguntas usando muestreo estratificado.
    """
    strata = {
        "Beginner": 5, "Elementary": 7, "Pre-intermediate": 8,
        "Intermediate": 10, "Upper-intermediate": 5, "Advanced": 5,
    }
    
    # Filtramos las preguntas por nivel en un diccionario
    questions_by_level = {level: [] for level in strata}
    for q in all_questions:
        if q.level in questions_by_level:
            questions_by_level[q.level].append(q)

    final_exam_questions = []
    for level, count in strata.items():
        available = questions_by_level[level]
        if len(available) < count:
            selected = available
        else:
            selected = random.sample(available, count)
        final_exam_questions.extend(selected)
    
    random.shuffle(final_exam_questions)
    return final_exam_questions

# --- Lógica Principal de Simulación ---

def create_fake_attempt(user: User, test_type: str, all_questions: list, db: Session, skill: float):
    """
    Crea un intento de examen falso completo, incluyendo respuestas
    y un puntaje final calculado.
    """
    
    print(f"    - Creando intento '{test_type}'...")
    
    # 1. Seleccionar preguntas para este intento
    if test_type == 'practice':
        questions_for_this_attempt = random.sample(all_questions, 20)
    else: # 'final'
        questions_for_this_attempt = get_stratified_questions(all_questions)

    if not questions_for_this_attempt:
        print("      > Error: No se pudieron cargar preguntas.")
        return

    # 2. Crear el registro TestAttempt
    # Simular que el intento ocurrió en los últimos 30 días
    sim_date = datetime.datetime.now() - datetime.timedelta(days=random.randint(0, 30))
    attempt = TestAttempt(
        user_id=user.id,
        test_type=test_type,
        start_time=sim_date
    )
    db.add(attempt)
    # Aún no hacemos commit, lo haremos al final

    # 3. Simular Respuestas
    correct_count = 0
    answers_to_add = []
    all_levels = ["Beginner", "Elementary", "Pre-intermediate", "Intermediate", "Upper-intermediate", "Advanced"]
    level_performance = {level: {"correct": 0, "total": 0} for level in all_levels}

    for q in questions_for_this_attempt:
        if q.level in level_performance:
            level_performance[q.level]["total"] += 1
        
        # El usuario acierta basado en su 'skill'
        is_correct = random.random() < skill
        
        correct_option_id = None
        incorrect_option_ids = []
        
        for opt in q.options:
            if opt.is_correct:
                correct_option_id = opt.id
            else:
                incorrect_option_ids.append(opt.id)

        selected_option_id = None
        if is_correct:
            selected_option_id = correct_option_id
            correct_count += 1
            if q.level in level_performance:
                level_performance[q.level]["correct"] += 1
        else:
            if incorrect_option_ids:
                selected_option_id = random.choice(incorrect_option_ids)
        
        sim_time = random.randint(5, 59)
        
        # Creamos la respuesta y la asociamos al intento
        answer = AttemptAnswer(
            test_attempt=attempt,
            question_id=q.id,
            selected_option_id=selected_option_id,
            time_taken_seconds=sim_time
        )
        answers_to_add.append(answer)

    # 4. Calcular puntaje y nivel
    if test_type == 'practice':
        score = correct_count * 5
        level = _estimate_level_by_score(score)
    else: # 'final'
        score = correct_count * 2.5
        level = _calculate_simulated_level(level_performance)
        
    # 5. Actualizar el intento con el puntaje
    attempt.score_percentage = score
    attempt.assigned_level = level
    
    # 6. Añadir todas las respuestas a la sesión
    db.add_all(answers_to_add)
    
    # 7. Hacer commit de este intento y sus respuestas
    db.commit()


def run_simulation():
    db = SessionLocal()
    try:
        # 1. Cargar todas las preguntas (necesario para simular)
        print("Cargando preguntas de la base de datos...")
        stmt = select(Question).options(selectinload(Question.options))
        all_questions = db.execute(stmt).scalars().all()
        
        if not all_questions:
            print("\n¡ERROR!")
            print("La base de datos no tiene preguntas.")
            print("Por favor, corre 'python populate_db.py' primero.")
            return

        print(f"Se cargaron {len(all_questions)} preguntas.")

        # 2. Definir los usuarios a simular
        # (username, "skill level" (probabilidad de acierto))
        sim_users_data = [
            ("user_test_1", 0.65), # Habilidad media
            ("ana_gomez", 0.85),   # Habilidad alta
            ("carlos_r", 0.40),    # Habilidad baja
            ("maria_lopez", 0.75), # Habilidad media-alta
            ("juan_perez", 0.30),  # Habilidad baja
            ("laura_martin", 0.90),# Habilidad muy alta
            ("diego_sanchez", 0.55),# Habilidad media-baja
            ("sofia_ramirez", 0.80),# Habilidad alta
            ("luis_fernandez", 0.45),# Habilidad baja-media
            ("isabel_torres", 0.70) # Habilidad media-alta
        ]
        
        fake_password = "pass123"
        hashed_password = hash_password(fake_password)
        print(f"Usando contraseña simulada: '{fake_password}'")

        # 3. Iterar y crear datos
        for username, skill in sim_users_data:
            print(f"\nProcesando usuario: {username} (Habilidad: {skill*100}%)")
            
            # Verificar si el usuario ya existe
            user = db.execute(select(User).filter_by(username=username)).scalar_one_or_none()
            
            if not user:
                print(f"  - Creando usuario '{username}'...")
                user = User(username=username, password_hash=hashed_password)
                db.add(user)
                db.commit()
                db.refresh(user)
            else:
                print(f"  - El usuario '{username}' ya existe.")
            
            # Simular un número aleatorio de intentos
            num_practice = random.randint(1, 5) # 1 a 5 intentos de práctica
            num_final = random.randint(0, 2)    # 0 a 2 intentos finales
            
            print(f"  - Simulando {num_practice} intentos de práctica...")
            for _ in range(num_practice):
                create_fake_attempt(user, 'practice', all_questions, db, skill)
                
            print(f"  - Simulando {num_final} intentos finales...")
            for _ in range(num_final):
                create_fake_attempt(user, 'final', all_questions, db, skill)

        print("\n¡Simulación de datos completada!")

    except Exception as e:
        print(f"\nHa ocurrido un error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    # Asegúrate de que las tablas existan (no las crea, pero es buena práctica)
    Base.metadata.create_all(bind=engine, checkfirst=True) 
    run_simulation()