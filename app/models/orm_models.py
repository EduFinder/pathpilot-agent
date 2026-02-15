from sqlalchemy import Column, String, Text, ForeignKey, TIMESTAMP, UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.orm import Base
import uuid

class Student(Base):
    __tablename__ = "students"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    resume_url = Column(String, nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("auth.users.id"), nullable=True) # Linked to Supabase Auth
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    # Relationship to Q&A
    questions = relationship("OnboardingQuestion", back_populates="student")

class OnboardingQuestion(Base):
    __tablename__ = "onboarding_questions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_id = Column(UUID(as_uuid=True), ForeignKey("students.id"), nullable=False)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    student = relationship("Student", back_populates="questions")
