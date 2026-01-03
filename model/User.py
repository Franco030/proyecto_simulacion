import datetime
from typing import List, Optional
from sqlalchemy import Column, Integer, String, Boolean, Float, DateTime, LargeBinary, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column
from model import Base

class User(Base):
    __tablename__ = 'users'
    __table_args__ = {'extend_existing':True}
    
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    password_hash: Mapped[bytes] = mapped_column(LargeBinary(200), nullable=False)
    
    # Relación: Si se borra un usuario, sus intentos NO se borran por defecto.
    # Esto es generalmente más seguro.
    attempts: Mapped[List["TestAttempt"]] = relationship(back_populates="user")

    def __repr__(self):
        return f"<User(username='{self.username}')>"