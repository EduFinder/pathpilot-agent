from app.db.db import supabase
from app.models.student import Student

class StudentService:
    TABLE_NAME = "students"

    @staticmethod
    def create_student(student: Student):
        try:
            response = supabase.table(StudentService.TABLE_NAME).insert(student.to_dict()).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            raise e

    @staticmethod
    def get_all_students():
        try:
            response = supabase.table(StudentService.TABLE_NAME).select("*").execute()
            return response.data
        except Exception as e:
            raise e

    @staticmethod
    def get_student_by_email(email: str):
        try:
            response = supabase.table(StudentService.TABLE_NAME).select("*").eq("email", email).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            raise e

    @staticmethod
    def get_student_by_user_id(user_id: str):
        try:
            response = supabase.table(StudentService.TABLE_NAME).select("*").eq("user_id", user_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            raise e
