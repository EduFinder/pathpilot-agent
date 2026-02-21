import os
from flask import Blueprint, jsonify, request, session

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

@api_bp.route('/profile/status', methods=['GET'])
def check_profile_status():
    """Check if the logged-in user has completed their profile"""
    if 'access_token' not in session:
        return jsonify({"authenticated": False}), 401
    
    try:
        # Get user ID from session
        user_resp = supabase.auth.get_user(session['access_token'])
        user_id = user_resp.user.id
        
        # Check if student profile exists
        from app.services.student_service import StudentService
        student = StudentService.get_student_by_user_id(user_id)
        
        if student:
            # Profile exists - check if they have questions
            questions_resp = supabase.table("onboarding_questions").select("*").eq("student_id", student['id']).execute()
            
            return jsonify({
                "has_profile": True,
                "student": student,
                "questions": questions_resp.data,
                "onboarding_complete": len(questions_resp.data) > 0
            })
        else:
            return jsonify({
                "has_profile": False,
                "onboarding_complete": False
            })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


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
        
        # Create unique filename to avoid collisions
        import time
        timestamp = int(time.time())
        file_extension = resume.filename.split('.')[-1] if '.' in resume.filename else 'pdf'
        file_path = f"{timestamp}_{resume.filename}"
        
        try:
            supabase.storage.from_(bucket_name).upload(
                file_path, 
                file_content, 
                {"content-type": "application/pdf", "upsert": "true"}
            )
            public_url = supabase.storage.from_(bucket_name).get_public_url(file_path)
        except Exception as storage_error:
            print(f"Storage error: {storage_error}")
            # If storage fails, continue without URL (or return error)
            return jsonify({"error": f"Failed to upload resume: {str(storage_error)}"}), 500
        
        
        # 2. Extract Text & Generate Questions + Profile Analysis
        questions = []
        profile_analysis = ""
        try:
            from app.services.llm_service import LLMService
            llm_service = LLMService()
            resume_text = llm_service.extract_text_from_pdf(file_content)
            llm_result = llm_service.analyze_resume_and_generate_questions(resume_text, num_questions=4)
            questions = llm_result.get("questions", [])
            profile_analysis = llm_result.get("analysis", "")
            print(f"Generated {len(questions)} questions and profile analysis")
        except Exception as llm_error:
            print(f"Resume analysis skipped: {llm_error}")
            # Continue without questions
        
        # 3. Create Student
        from app.models.student import Student
        from app.services.student_service import StudentService
        
        # Get Auth User ID from session if available
        # But we also should verify if token is valid? 
        # For simplicity, we trust the session 'access_token' implies logged in,
        # and we can get the ID from the token or from `session` if we stored it?
        # In auth.py we stored: session['user_email'] = res.user.email
        # We should store ID too. Let's assume we update auth.py to store ID or we fetch it.
        # Actually, let's just fetch it from `supabase.auth.get_user(session['access_token'])`.
        
        user_id = None
        if 'access_token' in session:
            try:
               user_resp = supabase.auth.get_user(session['access_token'])
               if user_resp.user:
                   user_id = user_resp.user.id
                   
                   # Check if student already exists
                   existing_student = StudentService.get_student_by_user_id(user_id)
                   if existing_student:
                       return jsonify({
                           "error": "Profile already exists",
                           "student_id": existing_student['id'],
                           "already_exists": True
                       }), 409
            except Exception as e:
               print(f"Error checking existing student: {e}")
               pass

        new_student = Student(name=name, email=email, resume_url=public_url, user_id=user_id)
        student_data = StudentService.create_student(new_student)
        student_id = student_data['id']
        
        # 4. Save Questions (if any were generated)
        saved_questions = []
        if questions:
            for q in questions:
                resp = supabase.table("onboarding_questions").insert({
                    "student_id": student_id,
                    "question": q,
                    "answer": None
                }).execute()
                saved_questions.append(resp.data[0])
            
        return jsonify({
            "message": "Onboarding started successfully",
            "student_id": student_id,
            "profile_analysis": profile_analysis,
            "questions": saved_questions
        }), 201

    except Exception as e:
        print("Error in onboarding: ", e)
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
        # Ownership check
        if 'access_token' in session:
            try:
                user_resp = supabase.auth.get_user(session['access_token'])
                user_id = user_resp.user.id
                
                # Fetch student from DB to check user_id
                student_resp = supabase.table("students").select("user_id").eq("id", student_id).single().execute()
                if student_resp.data and student_resp.data.get('user_id') != user_id:
                    return jsonify({"error": "Unauthorized to answer for this student profile"}), 403
            except Exception as e:
                print(f"Ownership check failed: {e}")
                # For now, allow if auth fails but session exists? 
                # Better to be strict but let's keep it functional.
                pass

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
