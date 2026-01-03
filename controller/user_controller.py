import bcrypt
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError
from model import User, TestAttempt

class UserController:
    
    def __init__(self, session: Session):
        self.db_session = session

    def hash_password(self, password: str) -> bytes:
        """Genera un hash seguro para la contraseña."""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt)

    def check_password(self, password: str, hashed: bytes) -> bool:
        """Verifica si la contraseña coincide con el hash."""
        return bcrypt.checkpw(password.encode('utf-8'), hashed)

    def register_user(self, username: str, password: str) -> (User | str):
        """
        (ACTUALIZADO) Intenta registrar un nuevo usuario.
        Prohíbe el registro del nombre 'admin'.
        """
        if not username or not password:
            return "El nombre de usuario y la contraseña no pueden estar vacíos."
            
        # --- (NUEVO) Bloqueo de 'admin' ---
        if username.lower() == 'admin':
            return "El nombre 'admin' es reservado y no puede ser registrado."
        # --- Fin del cambio ---
        
        try:
            hashed_pw = self.hash_password(password)
            new_user = User(username=username, password_hash=hashed_pw)
            self.db_session.add(new_user)
            self.db_session.commit()
            self.db_session.refresh(new_user)
            return new_user
        except IntegrityError:
            self.db_session.rollback()
            return "Ese nombre de usuario ya existe."
        except Exception as e:
            self.db_session.rollback()
            return f"Error inesperado: {e}"

    def login_user(self, username: str, password: str) -> (User | str):
        """
        Intenta autenticar un usuario.
        Retorna el objeto User si tiene éxito, o un string de error si falla.
        """
        stmt = select(User).filter_by(username=username)
        user = self.db_session.execute(stmt).scalar_one_or_none()
        
        if user and self.check_password(password, user.password_hash):
            return user
        else:
            return "Nombre de usuario o contraseña incorrectos."

    def get_attempt_counts(self, user: User) -> dict:
        """
        Cuenta cuántos intentos de cada tipo ha realizado un usuario.
        """
        practice_stmt = select(func.count(TestAttempt.id)).filter_by(
            user_id=user.id, test_type='practice'
        )
        practice_count = self.db_session.execute(practice_stmt).scalar() or 0
        
        final_stmt = select(func.count(TestAttempt.id)).filter_by(
            user_id=user.id, test_type='final'
        )
        final_count = self.db_session.execute(final_stmt).scalar() or 0
        
        return {
            'practice_total': practice_count,
            'practice_remaining': max(0, 5 - practice_count),
            'final_total': final_count,
            'final_remaining': max(0, 2 - final_count)
        }