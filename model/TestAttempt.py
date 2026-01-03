import datetime
from typing import List, Optional
from sqlalchemy import Column, Integer, String, Boolean, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column
from model import Base

class TestAttempt(Base):
    __tablename__ = 'test_attempts'
    __table_args__ = {'extend_existing':True}
    
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)
    test_type: Mapped[str] = mapped_column(String(20), nullable=False, index=True) 
    start_time: Mapped[datetime.datetime] = mapped_column(default=datetime.datetime.utcnow)
    score_percentage: Mapped[Optional[float]] = mapped_column(nullable=True) 
    assigned_level: Mapped[Optional[str]] = mapped_column(String(50), nullable=True) 
    
    user: Mapped["User"] = relationship(back_populates="attempts")
    
    # Lógica Cascade: Si un Intento se borra, todas sus respuestas
    # individuales deben ser borradas también.
    answers: Mapped[List["AttemptAnswer"]] = relationship(
        back_populates="test_attempt", 
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<TestAttempt(id={self.id}, user_id={self.user_id}, type='{self.test_type}', score={self.score_percentage})>"