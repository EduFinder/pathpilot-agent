from app.db.db import supabase
from app.models.qa import OnboardingQA

class QAService:
    TABLE_NAME = "onboarding_questions"

    @staticmethod
    def create_questions(student_id: str, questions: list[str]):
        """Saves a batch of questions for a student"""
        try:
            data = [{"student_id": student_id, "question": q} for q in questions]
            response = supabase.table(QAService.TABLE_NAME).insert(data).execute()
            return response.data
        except Exception as e:
            raise e

    @staticmethod
    def save_answers(student_id: str, answers: dict[str, str]):
        """
        Updates answers for specific questions.
        Expects a dict where key is the Question ID (or question text if we query by that) 
        but let's assume we pass question_id in the frontend flow.
        For simplicity in this MVP, we might re-insert or update. 
        Let's assume the frontend sends {question_id: answer_text}
        """
        try:
            results = []
            for qa_id, answer_text in answers.items():
                resp = supabase.table(QAService.TABLE_NAME)\
                    .update({"answer": answer_text})\
                    .eq("id", qa_id)\
                    .execute()
                results.append(resp.data)
            return results
        except Exception as e:
            raise e
            
    @staticmethod
    def get_questions_for_student(student_id: str):
        try:
            response = supabase.table(QAService.TABLE_NAME).select("*").eq("student_id", student_id).execute()
            return response.data
        except Exception as e:
            raise e
