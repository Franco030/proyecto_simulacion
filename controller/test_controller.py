import random
from sqlalchemy import select, func
from sqlalchemy.orm import Session, selectinload
from model import User, Question, TestAttempt, AttemptAnswer, Option

class TestController:
    
    def __init__(self, session: Session):
        self.db_session = session
        self.current_user: User | None = None
        
        # Estado del examen activo
        self.active_test: TestAttempt | None = None
        self.question_list: list[Question] = []
        self.current_question_index: int = -1

    def set_current_user(self, user: User):
        """Establece el usuario que tomará el examen."""
        self.current_user = user

    def start_new_test(self, test_type: str) -> (Question | str):
        """
        Inicia un nuevo intento de examen.
        Usa muestreo estratificado para el examen final.
        """
        if not self.current_user:
            return "No hay usuario activo."

        # 1. Crear y guardar el intento de examen
        try:
            self.active_test = TestAttempt(
                user_id=self.current_user.id,
                test_type=test_type
            )
            self.db_session.add(self.active_test)
            self.db_session.commit()
            self.db_session.refresh(self.active_test)
        except Exception as e:
            self.db_session.rollback()
            return f"Error al crear el intento: {e}"

        # 2. Cargar las preguntas
        self.current_question_index = -1
        self.question_list = []
        
        if test_type == 'practice':
            # --- Lógica de Práctica (Totalmente Aleatorio) ---
            stmt = select(Question).options(
                selectinload(Question.options)
            )
            result = self.db_session.execute(stmt)
            all_questions = result.scalars().all()
            
            if len(all_questions) < 20:
                return "No hay suficientes preguntas en la BD para la práctica."
            self.question_list = random.sample(all_questions, 20)
        
        elif test_type == 'final':
            # --- Lógica de Examen Final (Muestreo Estratificado) ---
            strata = {
                "Beginner": 5,
                "Elementary": 7,
                "Pre-intermediate": 8,
                "Intermediate": 10,
                "Upper-intermediate": 5,
                "Advanced": 5,
            } # Total: 40 preguntas
            
            final_exam_questions = []
            
            try:
                for level, count in strata.items():
                    stmt = select(Question).options(
                        selectinload(Question.options)
                    ).filter_by(level=level)
                    
                    level_questions = self.db_session.execute(stmt).scalars().all()
                    
                    if len(level_questions) < count:
                        print(f"Advertencia: No hay suficientes preguntas de nivel '{level}'. Se usarán {len(level_questions)} en lugar de {count}.")
                        selected = level_questions
                    else:
                        selected = random.sample(level_questions, count)
                    
                    final_exam_questions.extend(selected)
                
                random.shuffle(final_exam_questions)
                self.question_list = final_exam_questions
                
                if len(self.question_list) == 0:
                     return "No se pudieron cargar preguntas para el examen final. Revisa la BD."
                elif len(self.question_list) < 40:
                    print(f"Advertencia: El examen final solo tendrá {len(self.question_list)} preguntas debido a falta de reactivos.")

            except Exception as e:
                return f"Error al construir el examen estratificado: {e}"
        
        else:
            return "Tipo de examen no válido."
        
        # 3. Retornar la primera pregunta
        return self.get_next_question()

    def get_next_question(self) -> Question | None:
        """Avanza al siguiente índice y retorna la pregunta, o None si se acabó."""
        self.current_question_index += 1
        if self.current_question_index < len(self.question_list):
            return self.question_list[self.current_question_index]
        else:
            return None 

    def get_current_question_number(self) -> tuple[int, int]:
        """Retorna (número actual, total de preguntas)"""
        return (self.current_question_index + 1, len(self.question_list))

    def save_answer(self, selected_option_id: int | None, time_taken: int):
        """Guarda la respuesta del usuario para la pregunta actual."""
        if not self.active_test:
            print("Error: No hay examen activo para guardar la respuesta.")
            return

        current_question = self.question_list[self.current_question_index]
        
        if time_taken > 60:
            selected_option_id = None 

        answer = AttemptAnswer(
            test_attempt_id=self.active_test.id,
            question_id=current_question.id,
            selected_option_id=selected_option_id,
            time_taken_seconds=time_taken
        )
        self.db_session.add(answer)

    def finish_test(self) -> dict:
        """
        Calcula la puntuación final y el desglose de puntaje por nivel.
        """
        if not self.active_test:
            return {"error": "No hay examen activo que finalizar."}

        try:
            self.db_session.commit()
        except Exception as e:
            self.db_session.rollback()
            return {"error": f"Error al guardar respuestas pendientes: {e}"}

        # 1. Obtener todas las respuestas
        stmt = select(AttemptAnswer).options(
            selectinload(AttemptAnswer.selected_option),
            selectinload(AttemptAnswer.question)
        ).filter_by(
            test_attempt_id=self.active_test.id
        )
        result = self.db_session.execute(stmt)
        answers = result.scalars().all()
        
        # Lógica de Desglose de Puntaje
        level_scores = {}
        all_levels = ["Beginner", "Elementary", "Pre-intermediate", "Intermediate", "Upper-intermediate", "Advanced"]
        for level in all_levels:
            level_scores[level] = {"correct": 0, "total": 0}

        total_correct_count = 0
        
        for ans in answers:
            if not ans.question:
                continue
                
            level = ans.question.level
            if level in level_scores:
                level_scores[level]["total"] += 1
                
                if ans.selected_option and ans.selected_option.is_correct:
                    level_scores[level]["correct"] += 1
                    total_correct_count += 1
        
        total_questions = len(self.question_list)
        
        # 2. Calcular puntuación y nivel
        if self.active_test.test_type == 'practice':
            score = total_correct_count * 5 
            level = self._estimate_level_by_score(score)
        
        elif self.active_test.test_type == 'final':
            score = total_correct_count * 2.5
            level = self.calculate_placement_level(answers) 
        else:
            score = 0
            level = "N/A"

        # 3. Guardar resultados en el TestAttempt
        self.active_test.score_percentage = score
        self.active_test.assigned_level = level
        
        try:
            self.db_session.commit()
        except Exception as e:
            self.db_session.rollback()
            return {"error": f"Error al guardar resultados finales: {e}"}

        # 4. Limpiar estado y retornar
        results = {
            "score": score,
            "level": level,
            "correct": total_correct_count,
            "total": total_questions,
            "level_scores": level_scores
        }
        self.active_test = None
        self.question_list = []
        self.current_question_index = -1
        
        return results

    def _estimate_level_by_score(self, score: float) -> str:
        """
        Estima un nivel de ubicación basado puramente en el puntaje porcentual.
        Se usa solo para el simulador de práctica.
        """
        if score < 30: return "Beginner"
        if score < 50: return "Elementary"
        if score < 70: return "Pre-intermediate"
        if score < 85: return "Intermediate"
        if score < 95: return "Upper-intermediate"
        return "Advanced"

    def calculate_placement_level(self, answers: list[AttemptAnswer]) -> str:
        """
        Implementa la lógica de ubicación detallada
        basada en fallos por sección, según el Archivo 2.
        """
        failures = {
            "Beginner": 0,
            "Elementary": 0,
            "Pre-intermediate": 0,
            "Intermediate": 0,
            "Upper-intermediate": 0,
            "Advanced": 0
        }
        
        for ans in answers:
            if not ans.question:
                continue
                
            level = ans.question.level
            is_correct = (ans.selected_option and ans.selected_option.is_correct)
            
            if not is_correct:
                if level in failures:
                    failures[level] += 1
        
        # Aplicar las reglas de ubicación
        if failures["Beginner"] >= 2:
            return "Beginner"
        if failures["Elementary"] >= 3:
            return "Elementary"
        if failures["Pre-intermediate"] >= 3:
            return "Pre-intermediate"
        if failures["Intermediate"] >= 4:
            return "Intermediate"
        if failures["Upper-intermediate"] >= 2:
            return "Upper-intermediate"
        if failures["Advanced"] >= 1:
            return "Advanced"
        
        return "Advanced"

    # --- (FUNCIÓN DRÁSTICAMENTE ACTUALIZADA) ---
    def get_dashboard_data(self) -> dict:
        """
        (ACTUALIZADO) Recopila estadísticas detalladas de todos los intentos
        del usuario, separadas por tipo de examen y nivel de pregunta.
        """
        if not self.current_user:
            return {}
        
        # 1. Definir la estructura de datos que devolveremos
        all_levels = ["Beginner", "Elementary", "Pre-intermediate", "Intermediate", "Upper-intermediate", "Advanced"]
        level_template = {level: {"correct": 0, "total": 0} for level in all_levels}
        
        data = {
            "practice_stats": {
                "attempts_count": 0,
                "attempts_remaining": 5,
                "avg_score": 0.0,
                "high_score": 0.0,
                "scores_over_time": [],
                "performance_by_level": {level: {"correct": 0, "total": 0} for level in all_levels}
            },
            "final_stats": {
                "attempts_count": 0,
                "attempts_remaining": 2,
                "avg_score": 0.0,
                "high_score": 0.0,
                "last_level": "N/A",
                "scores_over_time": [],
                "performance_by_level": {level: {"correct": 0, "total": 0} for level in all_levels}
            }
        }

        # 2. Consultar todos los intentos y todas sus respuestas de una vez
        stmt = select(TestAttempt).options(
            selectinload(TestAttempt.answers).options(
                selectinload(AttemptAnswer.selected_option),
                selectinload(AttemptAnswer.question)
            )
        ).filter_by(
            user_id=self.current_user.id
        ).order_by(TestAttempt.start_time)
        
        all_attempts = self.db_session.execute(stmt).scalars().all()

        if not all_attempts:
            return data # Devuelve la plantilla vacía si no hay intentos

        # 3. Procesar los intentos
        practice_scores = []
        final_scores = []
        
        for attempt in all_attempts:
            # 3a. Separar por tipo de examen
            stats_key = ""
            if attempt.test_type == 'practice':
                stats_key = "practice_stats"
                if attempt.score_percentage is not None:
                    practice_scores.append(attempt.score_percentage)
                
            elif attempt.test_type == 'final':
                stats_key = "final_stats"
                if attempt.score_percentage is not None:
                    final_scores.append(attempt.score_percentage)
                if attempt.assigned_level:
                    data["final_stats"]["last_level"] = attempt.assigned_level

            if not stats_key:
                continue

            # 3b. Procesar las respuestas de CADA intento
            for ans in attempt.answers:
                if not ans.question:
                    continue
                
                level = ans.question.level
                if level in all_levels:
                    data[stats_key]["performance_by_level"][level]["total"] += 1
                    if ans.selected_option and ans.selected_option.is_correct:
                        data[stats_key]["performance_by_level"][level]["correct"] += 1

        # 4. Calcular estadísticas finales para Práctica
        if practice_scores:
            data["practice_stats"]["attempts_count"] = len(practice_scores)
            data["practice_stats"]["attempts_remaining"] = max(0, 5 - len(practice_scores))
            data["practice_stats"]["avg_score"] = sum(practice_scores) / len(practice_scores)
            data["practice_stats"]["high_score"] = max(practice_scores)
            data["practice_stats"]["scores_over_time"] = practice_scores

        # 5. Calcular estadísticas finales para Examen Final
        if final_scores:
            data["final_stats"]["attempts_count"] = len(final_scores)
            data["final_stats"]["attempts_remaining"] = max(0, 2 - len(final_scores))
            data["final_stats"]["avg_score"] = sum(final_scores) / len(final_scores)
            data["final_stats"]["high_score"] = max(final_scores)
            data["final_stats"]["scores_over_time"] = final_scores
            
        return data
    
    def get_admin_dashboard_data(self) -> dict:
        """
        Recopila estadísticas globales de TODOS los usuarios para el admin.
        """
        # 1. KPIs Globales
        total_users = self.db_session.execute(select(func.count(User.id)).where(User.username != 'admin')).scalar()
        total_practice = self.db_session.execute(select(func.count(TestAttempt.id)).where(TestAttempt.test_type == 'practice')).scalar()
        total_final = self.db_session.execute(select(func.count(TestAttempt.id)).where(TestAttempt.test_type == 'final')).scalar()
        
        avg_practice_score = self.db_session.execute(select(func.avg(TestAttempt.score_percentage)).where(TestAttempt.test_type == 'practice')).scalar() or 0.0
        avg_final_score = self.db_session.execute(select(func.avg(TestAttempt.score_percentage)).where(TestAttempt.test_type == 'final')).scalar() or 0.0

        # 2. Desempeño global por nivel de pregunta
        all_levels = ["Beginner", "Elementary", "Pre-intermediate", "Intermediate", "Upper-intermediate", "Advanced"]
        global_level_performance = {level: {"correct": 0, "total": 0} for level in all_levels}
        
        # Consultamos TODAS las respuestas de todos los intentos
        stmt_all_ans = select(AttemptAnswer).options(
            selectinload(AttemptAnswer.selected_option),
            selectinload(AttemptAnswer.question)
        )
        all_answers = self.db_session.execute(stmt_all_ans).scalars().all()
        
        for ans in all_answers:
            if not ans.question: continue
            level = ans.question.level
            if level in global_level_performance:
                global_level_performance[level]["total"] += 1
                if ans.selected_option and ans.selected_option.is_correct:
                    global_level_performance[level]["correct"] += 1

        # 3. Datos por usuario
        user_data = []
        # Obtenemos todos los usuarios (excepto el admin)
        all_users = self.db_session.execute(select(User).where(User.username != 'admin')).scalars().all()
        
        for user in all_users:
            user_practice = self.db_session.execute(select(TestAttempt).where(
                TestAttempt.user_id == user.id, TestAttempt.test_type == 'practice'
            )).scalars().all()
            
            user_final = self.db_session.execute(select(TestAttempt).where(
                TestAttempt.user_id == user.id, TestAttempt.test_type == 'final'
            )).scalars().all()

            practice_scores = [a.score_percentage for a in user_practice if a.score_percentage is not None]
            avg_practice = sum(practice_scores) / len(practice_scores) if practice_scores else 0.0
            
            last_level = "N/A"
            if user_final:
                # Ordenamos por fecha y tomamos el último
                user_final.sort(key=lambda x: x.start_time, reverse=True)
                if user_final[0].assigned_level:
                    last_level = user_final[0].assigned_level
            
            user_data.append({
                "username": user.username,
                "practice_attempts": len(user_practice),
                "final_attempts": len(user_final),
                "avg_practice_score": avg_practice,
                "last_final_level": last_level
            })

        # 4. Ensamblar el diccionario final
        admin_data = {
            "global_stats": {
                "total_users": total_users,
                "total_practice_attempts": total_practice,
                "total_final_attempts": total_final,
                "avg_practice_score": avg_practice_score,
                "avg_final_score": avg_final_score
            },
            "global_level_performance": global_level_performance,
            "user_details": user_data
        }
        
        return admin_data
    
    def get_user_detail_data(self, username: str) -> dict:
        """
        Recopila el historial de intentos COMPLETO de un solo usuario,
        incluyendo cada respuesta individual.
        """
        print(f"DEBUG: Buscando datos detallados para el usuario: {username}")
        
        # 1. Encontrar al usuario por su nombre
        user = self.db_session.execute(
            select(User).filter_by(username=username)
        ).scalar_one_or_none()
        
        if not user:
            return {"error": f"No se encontró al usuario {username}"}

        # 2. Cargar TODOS los intentos de ESE usuario, incluyendo
        #    respuestas, opciones seleccionadas y preguntas.
        stmt = select(TestAttempt).options(
            selectinload(TestAttempt.answers).options(
                selectinload(AttemptAnswer.selected_option),
                selectinload(AttemptAnswer.question)
            )
        ).filter_by(
            user_id=user.id
        ).order_by(TestAttempt.start_time.desc()) # El más reciente primero
        
        all_attempts = self.db_session.execute(stmt).scalars().all()
        
        # 3. Procesar los datos en un formato limpio para la vista
        processed_attempts = []
        for attempt in all_attempts:
            total_time = 0
            processed_answers = []
            
            for ans in attempt.answers:
                total_time += ans.time_taken_seconds
                
                # Manejar casos donde la pregunta o la opción fue eliminada
                q_text = "Pregunta eliminada"
                q_level = "N/A"
                if ans.question:
                    q_text = ans.question.text
                    q_level = ans.question.level
                
                opt_text = "N/A (sin respuesta)"
                is_correct = False
                if ans.selected_option:
                    opt_text = ans.selected_option.text
                    is_correct = ans.selected_option.is_correct

                processed_answers.append({
                    "question_text": q_text[:50] + "...", # Acortamos el texto
                    "question_level": q_level,
                    "selected_option": opt_text,
                    "is_correct": is_correct,
                    "time_taken": ans.time_taken_seconds
                })
            
            processed_attempts.append({
                "id": attempt.id,
                "type": "Práctica" if attempt.test_type == 'practice' else "Examen Final",
                "date": attempt.start_time.strftime("%Y-%m-%d %H:%M"),
                "score": attempt.score_percentage,
                "level": attempt.assigned_level,
                "total_time_seconds": total_time,
                "answers": processed_answers
            })

        return {
            "username": user.username,
            "attempts": processed_attempts
        }