from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity, verify_jwt_in_request
from flask_jwt_extended.exceptions import NoAuthorizationError
from app import db
from app.models import FloodReport, User
from app.utils import save_file, parse_filters
from datetime import datetime

bp = Blueprint('api', __name__, url_prefix='/api')

@bp.route('/floods', methods=['GET'])
def get_floods():
    """Get all flood reports with optional filtering"""
    try:
        filters = parse_filters(request.args)
        query = FloodReport.query

        # Apply filters
        if 'severity' in filters:
            query = query.filter_by(severity=filters['severity'])

        if 'status' in filters:
            query = query.filter_by(status=filters['status'])

        if 'start_date' in filters:
            start = datetime.fromisoformat(filters['start_date'])
            query = query.filter(FloodReport.created_at >= start)

        if 'end_date' in filters:
            end = datetime.fromisoformat(filters['end_date'])
            query = query.filter(FloodReport.created_at <= end)

        reports = query.order_by(FloodReport.created_at.desc()).all()

        return jsonify([report.to_dict() for report in reports]), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/floods/<int:id>', methods=['GET'])
def get_flood(id):
    """Get single flood report by ID"""
    try:
        report = FloodReport.query.get_or_404(id)
        return jsonify(report.to_dict()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 404

@bp.route('/floods', methods=['POST'])
@jwt_required()
def create_flood():
    """Create new flood report (requires authentication)"""
    try:
        current_user_id = int(get_jwt_identity())  # Convert string back to int
        data = request.get_json()

        # Validate required fields
        required_fields = ['latitude', 'longitude', 'severity']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400

        # Validate severity
        valid_severities = ['Low', 'Medium', 'High', 'Critical']
        if data['severity'] not in valid_severities:
            return jsonify({'error': 'Invalid severity level'}), 400

        # Create new report with user association
        report = FloodReport(
            user_id=current_user_id,
            latitude=data['latitude'],
            longitude=data['longitude'],
            address=data.get('address'),
            severity=data['severity'],
            description=data.get('description'),
            photo_url=data.get('photo_url')
        )

        db.session.add(report)
        db.session.commit()

        return jsonify(report.to_dict()), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/upload', methods=['POST'])
def upload_file():
    """Upload photo file"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400

        file = request.files['file']

        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        # Check file size
        file.seek(0, 2)  # Seek to end
        size = file.tell()
        file.seek(0)  # Reset to beginning

        if size > current_app.config['MAX_UPLOAD_SIZE']:
            return jsonify({'error': 'File too large'}), 400

        filename = save_file(file)

        if filename:
            return jsonify({'filename': filename, 'url': f'/uploads/{filename}'}), 200
        else:
            return jsonify({'error': 'Invalid file type'}), 400

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/floods/<int:id>', methods=['PUT'])
def update_flood(id):
    """Update flood report"""
    try:
        report = FloodReport.query.get_or_404(id)
        data = request.get_json()

        # Update allowed fields
        if 'address' in data:
            report.address = data['address']
        if 'severity' in data:
            report.severity = data['severity']
        if 'description' in data:
            report.description = data['description']
        if 'status' in data:
            report.status = data['status']

        report.updated_at = datetime.utcnow()
        db.session.commit()

        return jsonify(report.to_dict()), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/floods/<int:id>', methods=['DELETE'])
def delete_flood(id):
    """Delete flood report"""
    try:
        report = FloodReport.query.get_or_404(id)
        db.session.delete(report)
        db.session.commit()

        return jsonify({'message': 'Report deleted successfully'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/stats', methods=['GET'])
def get_stats():
    """Get statistics about flood reports"""
    try:
        total = FloodReport.query.filter_by(status='Active').count()
        by_severity = db.session.query(
            FloodReport.severity,
            db.func.count(FloodReport.id)
        ).filter_by(status='Active').group_by(FloodReport.severity).all()

        stats = {
            'total_active': total,
            'by_severity': {severity: count for severity, count in by_severity}
        }

        return jsonify(stats), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
