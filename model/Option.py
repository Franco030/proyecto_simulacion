import datetime
from typing import List, Optional
from sqlalchemy import Column, Integer, String, Boolean, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column
from model import Base

class Option(Base):
    __tablename__ = 'options'
    __table_args__ = {'extend_existing':True}
    
    id: Mapped[int] = mapped_column(primary_key=True)
    question_id: Mapped[int] = mapped_column(ForeignKey('questions.id'), nullable=False)
    text: Mapped[str] = mapped_column(String(500), nullable=False)
    is_correct: Mapped[bool] = mapped_column(default=False, nullable=False)
    
    question: Mapped["Question"] = relationship(back_populates="options")
    
    attempt_answers: Mapped[List["AttemptAnswer"]] = relationship(back_populates="selected_option")

    def __repr__(self):
        return f"<Option(text='{self.text[:20]}...', is_correct={self.is_correct})>"