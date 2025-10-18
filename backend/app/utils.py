import os
import uuid
from werkzeug.utils import secure_filename
from flask import current_app

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

def save_file(file):
    """Save uploaded file with unique filename"""
    if file and allowed_file(file.filename):
        # Create unique filename
        ext = file.filename.rsplit('.', 1)[1].lower()
        filename = f"{uuid.uuid4().hex}.{ext}"

        # Ensure upload folder exists
        upload_folder = current_app.config['UPLOAD_FOLDER']
        os.makedirs(upload_folder, exist_ok=True)

        # Save file
        filepath = os.path.join(upload_folder, filename)
        file.save(filepath)

        return filename
    return None

def parse_filters(args):
    """Parse query parameters for filtering"""
    filters = {}

    if 'severity' in args:
        filters['severity'] = args.get('severity')

    if 'start_date' in args:
        filters['start_date'] = args.get('start_date')

    if 'end_date' in args:
        filters['end_date'] = args.get('end_date')

    if 'status' in args:
        filters['status'] = args.get('status')
    else:
        filters['status'] = 'Active'  # Default to active reports

    return filters
