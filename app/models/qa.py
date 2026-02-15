from dataclasses import dataclass
from typing import Optional

@dataclass
class OnboardingQA:
    student_id: str
    question: str
    answer: Optional[str] = None
    id: Optional[str] = None
    created_at: Optional[str] = None

    def to_dict(self):
        return {
            "student_id": self.student_id,
            "question": self.question,
            "answer": self.answer
        }
