import os
import uuid
from werkzeug.utils import secure_filename
from flask import current_app


def save_uploaded_file(file, folder_type):
    """Save uploaded file and return filename"""
    if file and file.filename:
        # Generate unique filename
        filename = secure_filename(file.filename)
        name, ext = os.path.splitext(filename)
        unique_filename = f"{folder_type}_{uuid.uuid4().hex[:8]}_{name}{ext}"
        
        # Create upload directory if it doesn't exist
        upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], folder_type)
        os.makedirs(upload_path, exist_ok=True)
        
        # Save file
        file_path = os.path.join(upload_path, unique_filename)
        file.save(file_path)
        
        return f"{folder_type}/{unique_filename}"
    
    return None


def allowed_file(filename, allowed_extensions):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions