import datetime
from typing import List, Optional
from sqlalchemy import Column, Integer, String, Boolean, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column
from model import Base

class Question(Base):
    __tablename__ = 'questions'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    text: Mapped[str] = mapped_column(String(1000), nullable=False)
    level: Mapped[str] = mapped_column(String(50), nullable=False, index=True) 
    image_path: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # Lógica Cascade: Si una Pregunta se borra, todas sus Opciones hijas
    # deben ser borradas automáticamente.
    options: Mapped[List["Option"]] = relationship(
        back_populates="question", 
        cascade="all, delete-orphan"
    )
    
    attempt_answers: Mapped[List["AttemptAnswer"]] = relationship(back_populates="question")