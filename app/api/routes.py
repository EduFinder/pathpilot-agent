import os
from flask import Blueprint, jsonify, request

# Create a blueprint for API routes
api_bp = Blueprint('api', __name__, url_prefix='/api')
from app.db.db import supabase

# UPLOAD_FOLDER no longer needed
# UPLOAD_FOLDER='C:\\Work\\EduFinder\\pathpilot-agent\\uploads'

@api_bp.route('/', methods=['GET'])
def test():
    """Test endpoint"""
    return jsonify({
        'status': 'success',
        'message': 'Test route working!'
    }), 200

@api_bp.route('/studentInfo', methods=['GET'])
def db_check():
    try:
        response = supabase.table("students").select("*").execute()
        return jsonify({"status": "connected", "data": response.data})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@api_bp.route("/onboarding", methods=["POST"])
def onboarding_start():
    name = request.form.get("name")
    email = request.form.get("email")
    resume = request.files.get("resume")

    if not name or not email or not resume:
        return jsonify({"error": "Missing required fields"}), 400

    try:
        # 1. Upload Resume
        bucket_name = "UserResume"
        # We need to read content twice: once for upload, once for parsing
        file_content = resume.read()
        file_path = f"{resume.filename}" 
        
        supabase.storage.from_(bucket_name).upload(
            file_path, 
            file_content, 
            {"upsert": "true"}
        )
        public_url = supabase.storage.from_(bucket_name).get_public_url(file_path)
        
        # 2. Extract Text & Generate Questions
        from app.services.llm_service import LLMService
        llm_service = LLMService()
        resume_text = llm_service.extract_text_from_pdf(file_content)
        questions = llm_service.generate_personalized_questions(resume_text, num_questions=3)
        
        # 3. Create Student
        from app.models.student import Student
        from app.services.student_service import StudentService
        
        new_student = Student(name=name, email=email, resume_url=public_url)
        student_data = StudentService.create_student(new_student)
        student_id = student_data['id']
        
        # 4. Save Questions
        from app.services.qa_service import QAService
        # Insert questions linked to the student
        # We assume supabase returns list of inserted objects
        saved_questions = []
        for q in questions:
            # We insert one by one or batch if needed, here simple loop for clarity
            resp = supabase.table("onboarding_questions").insert({
                "student_id": student_id,
                "question": q,
                "answer": None
            }).execute()
            saved_questions.append(resp.data[0])
            
        return jsonify({
            "message": "Onboarding started successfully",
            "student_id": student_id,
            "questions": saved_questions
        }), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api_bp.route("/onboarding/answers", methods=["POST"])
def save_answers():
    """
    Expects JSON:
    {
        "student_id": "uuid",
        "answers": [
            {"question_id": 1, "answer": "text"},
            {"question_id": 2, "answer": "text"}
        ]
    }
    """
    data = request.json
    student_id = data.get("student_id")
    answers_list = data.get("answers")
    
    if not student_id or not answers_list:
        return jsonify({"error": "Missing student_id or answers"}), 400

    try:
        results = []
        for item in answers_list:
            q_id = item.get("question_id")
            ans = item.get("answer")
            
            resp = supabase.table("onboarding_questions")\
                .update({"answer": ans})\
                .eq("id", q_id)\
                .eq("student_id", student_id)\
                .execute()
            results.append(resp.data)
            
        return jsonify({
            "message": "Answers saved successfully",
            "updates": results
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@api_bp.route("/students", methods=["GET"])
def get_students():
    try:
        from app.services.student_service import StudentService
        students = StudentService.get_all_students()
        return jsonify(students), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
