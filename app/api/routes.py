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
@api_bp.route("/submit", methods=["POST"])
def submit():
    name = request.form.get("name")
    email = request.form.get("email")
    resume = request.files.get("resume")

    # Basic validation
    if not name or not email or not resume:
        return jsonify({"error": "Missing required fields"}), 400

    # Save resume file
    # Upload to Supabase Storage
    try:
        bucket_name = "resumes"
        file_content = resume.read()
        file_path = f"{resume.filename}" # Path within bucket
        
        # Upload file
        # Note: Set upsert=True to overwrite existing files with the same name
        supabase.storage.from_(bucket_name).upload(
            file_path, 
            file_content, 
            {"upsert": "true"}
        )
        
        # Get public URL
        public_url = supabase.storage.from_(bucket_name).get_public_url(file_path)
        file_path = public_url
    except Exception as e:
        return jsonify({"error": f"Failed to upload to cloud: {str(e)}"}), 500

    return jsonify({
        "message": "Data received successfully",
        "name": name,
        "email": email,
        "resume_saved_at": file_path
    }), 200

