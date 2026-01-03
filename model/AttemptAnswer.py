import datetime
from typing import List, Optional
from sqlalchemy import Column, Integer, String, Boolean, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column
from model import Base

class AttemptAnswer(Base):
    __tablename__ = 'attempt_answers'
    __table_args__ = {'extend_existing':True}
    
    id: Mapped[int] = mapped_column(primary_key=True)
    test_attempt_id: Mapped[int] = mapped_column(ForeignKey('test_attempts.id'), nullable=False)
    
    # Lógica Cascade (ondelete): Si se borra una Pregunta o una Opción,
    # no queremos borrar todo el intento. Simplemente ponemos la FK a NULL.
    # Esto preserva el historial del intento, aunque la pregunta ya no exista.
    question_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey('questions.id', ondelete="SET NULL"), 
        nullable=True
    )
    selected_option_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey('options.id', ondelete="SET NULL"), 
        nullable=True
    )
    
    time_taken_seconds: Mapped[int] = mapped_column(default=0) 
    
    test_attempt: Mapped["TestAttempt"] = relationship(back_populates="answers")
    
    question: Mapped[Optional["Question"]] = relationship(back_populates="attempt_answers")
    
    selected_option: Mapped[Optional["Option"]] = relationship(back_populates="attempt_answers")