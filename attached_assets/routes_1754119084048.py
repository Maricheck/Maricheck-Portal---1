import os
import csv
from io import StringIO
from datetime import datetime
from flask import render_template, request, redirect, url_for, flash, session, make_response
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
        existing_crew = CrewMember.query.filter_by(passport=form.passport.data.upper()).first()
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
            passport=form.passport.data.upper(),
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
        
        # Create profile access URL
        profile_url = url_for('crew_private_profile', 
                            crew_id=crew_member.id, 
                            token=crew_member.profile_token, 
                            _external=True)
        
        flash(f'Registration successful! Your application has been submitted. Save this link to access your private profile: {profile_url}', 'success')
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
        crew_member = CrewMember.query.filter_by(passport=passport.upper()).first()
        if not crew_member:
            flash('No crew member found with this passport number.', 'error')
    
    return render_template('track_status.html', form=form, crew_member=crew_member)


@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Admin login"""
    if current_user.is_authenticated:
        return redirect(url_for('admin_dashboard'))
    
    form = AdminLoginForm()
    
    if form.validate_on_submit():
        admin = Admin.query.filter_by(username=form.username.data).first()
        if admin and check_password_hash(admin.password_hash, form.password.data):
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
        'Years Experience', 'Mobile Number', 'Email', 'Status', 'Created At'
    ])
    
    # Write data
    for crew in crew_members:
        writer.writerow([
            crew.id, crew.name, crew.rank, crew.passport, crew.nationality,
            crew.date_of_birth, crew.years_experience, crew.mobile_number,
            crew.email or '', crew.get_status_name(), crew.created_at
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
        'ID', 'Full Name', 'Position', 'Department', 'Years Experience',
        'Mobile Number', 'Email/WhatsApp', 'Location', 'Status', 'Created At'
    ])
    
    # Write data
    for staff in staff_members:
        writer.writerow([
            staff.id, staff.full_name, staff.position_applying, staff.department,
            staff.years_experience, staff.mobile_number, staff.email_or_whatsapp,
            staff.location, staff.get_status_name(), staff.created_at
        ])
    
    response = make_response(output.getvalue())
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = f'attachment; filename=staff_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    
    return response


@app.route('/my-profile/<int:crew_id>-<token>', methods=['GET', 'POST'])
def crew_private_profile(crew_id, token):
    """Secure crew member private profile page with token-based access"""
    # Find crew member and verify token
    crew_member = CrewMember.query.get_or_404(crew_id)
    
    if not crew_member.profile_token or crew_member.profile_token != token:
        flash('Invalid access link. Please check your URL.', 'error')
        return redirect(url_for('index'))
    
    form = CrewProfileDocumentForm()
    
    if form.validate_on_submit():
        # Handle file uploads for missing documents only
        documents_uploaded = []
        required_docs = crew_member.get_required_documents()
        
        for doc in required_docs:
            field_name = doc['field']
            file_field = getattr(form, field_name)
            
            # Only upload if document is missing and file is provided
            if not doc['uploaded'] and file_field.data:
                filename = save_uploaded_file(file_field.data, 'crew')
                setattr(crew_member, field_name, filename)
                documents_uploaded.append(doc['name'])
        
        if documents_uploaded:
            db.session.commit()
            flash(f'Successfully uploaded: {", ".join(documents_uploaded)}', 'success')
            return redirect(url_for('crew_private_profile', crew_id=crew_id, token=token))
        else:
            flash('No new documents were uploaded.', 'info')
    
    # Get document status and completion data
    documents = crew_member.get_required_documents()
    completion_percentage = crew_member.get_profile_completion_percentage()
    is_complete = crew_member.is_profile_complete()
    
    return render_template('crew_profile.html', 
                         crew_member=crew_member,
                         documents=documents,
                         completion_percentage=completion_percentage,
                         is_complete=is_complete,
                         form=form)
