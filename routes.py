import os
import csv
from io import StringIO
from datetime import datetime
from flask import render_template, request, redirect, url_for, flash, session, make_response, send_from_directory
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
from werkzeug.utils import secure_filename

from app import app, db
from models import Admin, CrewMember, StaffMember
from forms import CrewRegistrationForm, StaffRegistrationForm, TrackingForm, AdminLoginForm, CrewProfileDocumentForm
from utils import save_uploaded_file


@app.route('/')
def index():
    """Home page"""
    return render_template('index.html')


@app.route('/register/crew', methods=['GET', 'POST'])
def register_crew():
    """Crew member registration"""
    form = CrewRegistrationForm()
    
    if form.validate_on_submit():
        # Check if passport already exists
        existing_crew = CrewMember.query.filter_by(passport=form.passport.data.upper() if form.passport.data else '').first()
        if existing_crew:
            flash('A crew member with this passport number already exists.', 'error')
            return render_template('register_crew.html', form=form)
        
        # Create new crew member
        crew_member = CrewMember(
            name=form.name.data,
            nationality=form.nationality.data,
            date_of_birth=form.date_of_birth.data,
            mobile_number=form.mobile_number.data,
            email=form.email.data,
            rank=form.rank.data,
            passport=form.passport.data.upper() if form.passport.data else '',
            years_experience=form.years_experience.data,
            last_vessel_type=form.last_vessel_type.data,
            availability_date=form.availability_date.data,
            emergency_contact_name=form.emergency_contact_name.data,
            emergency_contact_phone=form.emergency_contact_phone.data,
            emergency_contact_relationship=form.emergency_contact_relationship.data
        )
        
        # Handle file uploads - Core documents only for registration
        file_fields = ['passport_file', 'cdc_file', 'resume_file', 'photo_file', 'medical_certificate_file']
        for field_name in file_fields:
            file_field = getattr(form, field_name)
            if file_field.data:
                filename = save_uploaded_file(file_field.data, 'crew')
                setattr(crew_member, field_name, filename)
        
        db.session.add(crew_member)
        db.session.commit()
        
        # Generate profile token for secure access
        crew_member.generate_profile_token()
        
        flash('Registration successful! Your application has been submitted. Our team will review your profile and contact you with the next steps.', 'success')
        return redirect(url_for('track_status', passport=crew_member.passport))
    
    return render_template('register_crew.html', form=form)


@app.route('/register/staff', methods=['GET', 'POST'])
def register_staff():
    """Staff member registration"""
    form = StaffRegistrationForm()
    
    if form.validate_on_submit():
        # Create new staff member
        staff_member = StaffMember(
            full_name=form.full_name.data,
            email_or_whatsapp=form.email_or_whatsapp.data,
            mobile_number=form.mobile_number.data,
            location=form.location.data,
            position_applying=form.position_applying.data,
            department=form.department.data,
            years_experience=form.years_experience.data,
            current_employer=form.current_employer.data,
            availability_date=form.availability_date.data,
            education=form.education.data,
            certifications=form.certifications.data,
            salary_expectation=form.salary_expectation.data
        )
        
        # Handle file uploads
        file_fields = ['resume_file', 'photo_file']
        for field_name in file_fields:
            file_field = getattr(form, field_name)
            if file_field.data:
                filename = save_uploaded_file(file_field.data, 'staff')
                setattr(staff_member, field_name, filename)
        
        db.session.add(staff_member)
        db.session.commit()
        
        flash('Registration successful! Your application has been submitted.', 'success')
        return redirect(url_for('index'))
    
    return render_template('register_staff.html', form=form)


@app.route('/track', methods=['GET', 'POST'])
def track_status():
    """Track application status"""
    form = TrackingForm()
    crew_member = None
    passport_param = request.args.get('passport')
    
    if passport_param:
        form.passport.data = passport_param
    
    if form.validate_on_submit() or passport_param:
        passport = form.passport.data or passport_param
        crew_member = CrewMember.query.filter_by(passport=passport.upper() if passport else '').first()
        if not crew_member:
            flash('No crew member found with this passport number.', 'error')
    
    return render_template('track_status.html', form=form, crew_member=crew_member)


@app.route('/my-profile/<int:crew_id>-<token>')
def crew_private_profile(crew_id, token):
    """Crew member private profile for document uploads"""
    crew_member = CrewMember.query.get_or_404(crew_id)
    
    # Verify token
    if not crew_member.profile_token or crew_member.profile_token != token:
        flash('Invalid or expired profile link.', 'error')
        return redirect(url_for('index'))
    
    # Initialize document form
    document_form = CrewProfileDocumentForm()
    
    # Handle document uploads
    if document_form.validate_on_submit():
        updated_docs = []
        
        # Handle all document fields
        document_fields = [
            'passport_file', 'cdc_file', 'resume_file', 'photo_file', 'medical_certificate_file',
            'coc_cop_file', 'stcw_certificates_file', 'gmdss_dce_file', 'yellow_fever_file',
            'bank_details_file', 'aadhaar_pan_file'
        ]
        
        for field_name in document_fields:
            file_field = getattr(document_form, field_name)
            if file_field.data:
                filename = save_uploaded_file(file_field.data, 'crew')
                setattr(crew_member, field_name, filename)
                updated_docs.append(field_name.replace('_file', '').replace('_', ' ').title())
        
        if updated_docs:
            crew_member.updated_at = datetime.utcnow()
            db.session.commit()
            flash(f'Successfully uploaded: {", ".join(updated_docs)}', 'success')
        else:
            flash('No files were selected for upload.', 'warning')
        
        return redirect(url_for('crew_private_profile', crew_id=crew_id, token=token))
    
    return render_template('crew_private_profile.html', 
                         crew_member=crew_member, 
                         document_form=document_form)


@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Admin login"""
    if current_user.is_authenticated:
        return redirect(url_for('admin_dashboard'))
    
    form = AdminLoginForm()
    
    if form.validate_on_submit():
        admin = Admin.query.filter_by(username=form.username.data).first()
        if admin and admin.password_hash and check_password_hash(admin.password_hash, form.password.data):
            login_user(admin)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('admin/login.html', form=form)


@app.route('/admin/logout')
@login_required
def admin_logout():
    """Admin logout"""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))


@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    """Admin dashboard"""
    # Get statistics
    total_crew = CrewMember.query.count()
    total_staff = StaffMember.query.count()
    crew_screening = CrewMember.query.filter_by(status=1).count()
    staff_screening = StaffMember.query.filter_by(status=1).count()
    crew_approved = CrewMember.query.filter_by(status=3).count()
    staff_approved = StaffMember.query.filter_by(status=3).count()
    
    # Get recent registrations
    recent_crew = CrewMember.query.order_by(CrewMember.created_at.desc()).limit(5).all()
    recent_staff = StaffMember.query.order_by(StaffMember.created_at.desc()).limit(5).all()
    
    return render_template('admin/dashboard.html',
                         total_crew=total_crew,
                         total_staff=total_staff,
                         crew_screening=crew_screening,
                         staff_screening=staff_screening,
                         crew_approved=crew_approved,
                         staff_approved=staff_approved,
                         recent_crew=recent_crew,
                         recent_staff=recent_staff)


@app.route('/admin/crew')
@login_required
def crew_list():
    """Crew member list"""
    status_filter = request.args.get('status')
    search = request.args.get('search', '')
    
    query = CrewMember.query
    
    if status_filter:
        query = query.filter(CrewMember.status == int(status_filter))
    
    if search:
        query = query.filter(
            db.or_(
                CrewMember.name.ilike(f'%{search}%'),
                CrewMember.passport.ilike(f'%{search}%'),
                CrewMember.rank.ilike(f'%{search}%')
            )
        )
    
    crew_members = query.order_by(CrewMember.created_at.desc()).all()
    
    return render_template('admin/crew_list.html', crew_members=crew_members, search=search, status_filter=status_filter)


@app.route('/admin/staff')
@login_required
def staff_list():
    """Staff member list"""
    status_filter = request.args.get('status')
    search = request.args.get('search', '')
    
    query = StaffMember.query
    
    if status_filter:
        query = query.filter(StaffMember.status == int(status_filter))
    
    if search:
        query = query.filter(
            db.or_(
                StaffMember.full_name.ilike(f'%{search}%'),
                StaffMember.position_applying.ilike(f'%{search}%'),
                StaffMember.department.ilike(f'%{search}%')
            )
        )
    
    staff_members = query.order_by(StaffMember.created_at.desc()).all()
    
    return render_template('admin/staff_list.html', staff_members=staff_members, search=search, status_filter=status_filter)


@app.route('/admin/crew/<int:crew_id>')
@login_required
def crew_profile(crew_id):
    """Crew member profile"""
    crew_member = CrewMember.query.get_or_404(crew_id)
    return render_template('admin/crew_profile.html', crew_member=crew_member)


@app.route('/admin/staff/<int:staff_id>')
@login_required
def staff_profile(staff_id):
    """Staff member profile"""
    staff_member = StaffMember.query.get_or_404(staff_id)
    return render_template('admin/staff_profile.html', staff_member=staff_member)


@app.route('/admin/crew/<int:crew_id>/update_status', methods=['POST'])
@login_required
def update_crew_status(crew_id):
    """Update crew member status"""
    crew_member = CrewMember.query.get_or_404(crew_id)
    action = request.form.get('action')
    notes = request.form.get('notes', '')
    
    if action == 'approve':
        crew_member.status = 3
        crew_member.admin_notes = notes
        flash('Crew member approved successfully.', 'success')
    elif action == 'reject':
        crew_member.status = -1
        crew_member.admin_notes = notes
        flash('Crew member rejected.', 'warning')
    elif action == 'flag':
        crew_member.status = -2
        crew_member.admin_notes = notes
        flash('Crew member flagged for review.', 'info')
    elif action == 'screening':
        crew_member.status = 1
        crew_member.screening_notes = notes
        flash('Crew member moved to screening.', 'info')
    elif action == 'verified':
        crew_member.status = 2
        crew_member.admin_notes = notes
        flash('Documents verified.', 'success')
    
    crew_member.updated_at = datetime.utcnow()
    db.session.commit()
    
    return redirect(url_for('crew_profile', crew_id=crew_id))


@app.route('/admin/staff/<int:staff_id>/update_status', methods=['POST'])
@login_required
def update_staff_status(staff_id):
    """Update staff member status"""
    staff_member = StaffMember.query.get_or_404(staff_id)
    action = request.form.get('action')
    notes = request.form.get('notes', '')
    
    if action == 'approve':
        staff_member.status = 3
        staff_member.admin_notes = notes
        flash('Staff member approved successfully.', 'success')
    elif action == 'reject':
        staff_member.status = -1
        staff_member.admin_notes = notes
        flash('Staff member rejected.', 'warning')
    elif action == 'screening':
        staff_member.status = 1
        staff_member.screening_notes = notes
        flash('Staff member moved to screening.', 'info')
    
    staff_member.updated_at = datetime.utcnow()
    db.session.commit()
    
    return redirect(url_for('staff_profile', staff_id=staff_id))


@app.route('/admin/crew/export')
@login_required
def export_crew_csv():
    """Export crew data to CSV"""
    crew_members = CrewMember.query.all()
    
    output = StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow([
        'ID', 'Name', 'Rank', 'Passport', 'Nationality', 'Date of Birth',
        'Years Experience', 'Mobile Number', 'Email', 'Status', 'Profile Completion',
        'Created At', 'Updated At'
    ])
    
    # Write data
    for crew in crew_members:
        writer.writerow([
            crew.id, crew.name, crew.rank, crew.passport, crew.nationality,
            crew.date_of_birth, crew.years_experience, crew.mobile_number,
            crew.email or '', crew.get_status_name(), 
            f"{crew.get_profile_completion_percentage()}%",
            crew.created_at, crew.updated_at
        ])
    
    response = make_response(output.getvalue())
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = f'attachment; filename=crew_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    
    return response


@app.route('/admin/staff/export')
@login_required
def export_staff_csv():
    """Export staff data to CSV"""
    staff_members = StaffMember.query.all()
    
    output = StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow([
        'ID', 'Full Name', 'Position Applying', 'Department', 'Location',
        'Years Experience', 'Email/WhatsApp', 'Mobile Number', 'Status',
        'Created At', 'Updated At'
    ])
    
    # Write data
    for staff in staff_members:
        writer.writerow([
            staff.id, staff.full_name, staff.position_applying, staff.department,
            staff.location, staff.years_experience, staff.email_or_whatsapp,
            staff.mobile_number, staff.get_status_name(),
            staff.created_at, staff.updated_at
        ])
    
    response = make_response(output.getvalue())
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = f'attachment; filename=staff_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    
    return response


# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('errors/500.html'), 500


@app.errorhandler(403)
def forbidden_error(error):
    return render_template('errors/403.html'), 403


# Template filters
@app.template_filter('moment')
def moment_filter():
    """Return current year for footer"""
    return datetime.now()

# Template global function
@app.template_global()
def moment():
    """Return current datetime for templates"""
    return datetime.now()


@app.template_filter('currency')
def currency_filter(amount):
    """Format currency"""
    if amount:
        return f"${amount:,.2f}"
    return "$0.00"


@app.template_filter('filesize')
def filesize_filter(bytes):
    """Format file size"""
    if bytes is None:
        return "0 B"
    
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes < 1024.0:
            return f"{bytes:.1f} {unit}"
        bytes /= 1024.0
    return f"{bytes:.1f} TB"


# Context processors
@app.context_processor
def utility_processor():
    """Add utility functions to template context"""
    return {
        'enumerate': enumerate,
        'len': len,
        'str': str,
        'int': int,
        'float': float,
        'round': round,
        'min': min,
        'max': max,
        'sum': sum,
        'abs': abs,
        'getattr': getattr,
        'hasattr': hasattr,
        'setattr': setattr
    }


# Static file handling for uploaded files
@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    """Serve uploaded files"""
    upload_folder = app.config.get('UPLOAD_FOLDER', 'static/uploads')
    return send_from_directory(upload_folder, filename)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
