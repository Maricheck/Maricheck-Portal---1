from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, SelectField, IntegerField, DateField, TextAreaField, SubmitField, PasswordField
from wtforms.validators import DataRequired, Email, Length, Optional, NumberRange


class CrewRegistrationForm(FlaskForm):
    # Personal Information
    name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=128)])
    nationality = StringField('Nationality', validators=[DataRequired(), Length(max=64)])
    date_of_birth = DateField('Date of Birth', validators=[DataRequired()])
    mobile_number = StringField('Mobile Number', validators=[DataRequired(), Length(max=20)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=120)])
    
    # Professional Information
    rank = SelectField('Rank/Position', choices=[
        ('', 'Select Rank'),
        ('Captain', 'Captain'),
        ('Chief Officer', 'Chief Officer'),
        ('Second Officer', 'Second Officer'),
        ('Third Officer', 'Third Officer'),
        ('Chief Engineer', 'Chief Engineer'),
        ('First Engineer', 'First Engineer'),
        ('Second Engineer', 'Second Engineer'),
        ('Third Engineer', 'Third Engineer'),
        ('Bosun', 'Bosun'),
        ('AB Seaman', 'AB Seaman'),
        ('Ordinary Seaman', 'Ordinary Seaman'),
        ('Cook', 'Cook'),
        ('Steward', 'Steward'),
        ('Oiler', 'Oiler'),
        ('Wiper', 'Wiper'),
        ('Other', 'Other')
    ], validators=[DataRequired()])
    
    passport = StringField('Passport Number', validators=[DataRequired(), Length(min=6, max=32)])
    years_experience = IntegerField('Years of Experience', validators=[DataRequired(), NumberRange(min=0, max=50)])
    last_vessel_type = StringField('Last Vessel Type', validators=[Optional(), Length(max=128)])
    availability_date = DateField('Availability Date', validators=[DataRequired()])
    
    # Emergency Contact
    emergency_contact_name = StringField('Emergency Contact Name', validators=[Optional(), Length(max=128)])
    emergency_contact_phone = StringField('Emergency Contact Phone', validators=[Optional(), Length(max=20)])
    emergency_contact_relationship = StringField('Relationship', validators=[Optional(), Length(max=64)])
    
    # File Uploads - Core Documents
    passport_file = FileField('Passport Copy', validators=[Optional(), FileAllowed(['pdf', 'jpg', 'jpeg', 'png'], 'PDF and image files only!')])
    cdc_file = FileField('CDC Certificate', validators=[Optional(), FileAllowed(['pdf', 'jpg', 'jpeg', 'png'], 'PDF and image files only!')])
    resume_file = FileField('Resume/CV', validators=[Optional(), FileAllowed(['pdf', 'doc', 'docx'], 'PDF and Word documents only!')])
    photo_file = FileField('Photo', validators=[Optional(), FileAllowed(['jpg', 'jpeg', 'png'], 'Image files only!')])
    medical_certificate_file = FileField('Medical Certificate', validators=[Optional(), FileAllowed(['pdf', 'jpg', 'jpeg', 'png'], 'PDF and image files only!')])
    
    submit = SubmitField('Register')


class StaffRegistrationForm(FlaskForm):
    # Personal Information
    full_name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=128)])
    email_or_whatsapp = StringField('Email or WhatsApp', validators=[DataRequired(), Length(max=128)])
    mobile_number = StringField('Mobile Number', validators=[DataRequired(), Length(max=20)])
    location = StringField('Current Location', validators=[DataRequired(), Length(max=128)])
    
    # Professional Information
    position_applying = StringField('Position Applying For', validators=[DataRequired(), Length(max=128)])
    department = SelectField('Department', choices=[
        ('', 'Select Department'),
        ('Ops', 'Operations'),
        ('HR', 'Human Resources'),
        ('Tech', 'Technical'),
        ('Crewing', 'Crewing')
    ], validators=[DataRequired()])
    
    years_experience = IntegerField('Years of Experience', validators=[DataRequired(), NumberRange(min=0, max=50)])
    current_employer = StringField('Current Employer', validators=[Optional(), Length(max=128)])
    availability_date = DateField('Availability Date', validators=[DataRequired()])
    
    # Additional Information
    education = StringField('Education', validators=[Optional(), Length(max=255)])
    certifications = TextAreaField('Certifications', validators=[Optional()])
    salary_expectation = StringField('Salary Expectation', validators=[Optional(), Length(max=64)])
    
    # File Uploads
    resume_file = FileField('Resume/CV', validators=[Optional(), FileAllowed(['pdf', 'doc', 'docx'], 'PDF and Word documents only!')])
    photo_file = FileField('Photo', validators=[Optional(), FileAllowed(['jpg', 'jpeg', 'png'], 'Image files only!')])
    
    submit = SubmitField('Register')


class TrackingForm(FlaskForm):
    passport = StringField('Passport Number', validators=[DataRequired(), Length(min=6, max=32)])
    submit = SubmitField('Track Status')


class CrewProfileDocumentForm(FlaskForm):
    """Form for crew members to upload missing documents on their profile page"""
    # Core Documents
    passport_file = FileField('Passport Copy', validators=[Optional(), FileAllowed(['pdf', 'jpg', 'jpeg', 'png'], 'PDF and image files only!')])
    cdc_file = FileField('CDC (Seaman Book)', validators=[Optional(), FileAllowed(['pdf', 'jpg', 'jpeg', 'png'], 'PDF and image files only!')])
    resume_file = FileField('Resume/CV', validators=[Optional(), FileAllowed(['pdf', 'doc', 'docx'], 'PDF and Word documents only!')])
    photo_file = FileField('Photo (Passport Size)', validators=[Optional(), FileAllowed(['jpg', 'jpeg', 'png'], 'Image files only!')])
    medical_certificate_file = FileField('Medical Certificate', validators=[Optional(), FileAllowed(['pdf', 'jpg', 'jpeg', 'png'], 'PDF and image files only!')])
    
    # Additional Documents
    coc_cop_file = FileField('COC/COP Certificate', validators=[Optional(), FileAllowed(['pdf', 'jpg', 'jpeg', 'png'], 'PDF and image files only!')])
    stcw_certificates_file = FileField('STCW Certificates', validators=[Optional(), FileAllowed(['pdf', 'jpg', 'jpeg', 'png'], 'PDF and image files only!')])
    gmdss_dce_file = FileField('GMDSS/DCE Certificate', validators=[Optional(), FileAllowed(['pdf', 'jpg', 'jpeg', 'png'], 'PDF and image files only!')])
    yellow_fever_file = FileField('Yellow Fever Certificate', validators=[Optional(), FileAllowed(['pdf', 'jpg', 'jpeg', 'png'], 'PDF and image files only!')])
    bank_details_file = FileField('Bank Details Document', validators=[Optional(), FileAllowed(['pdf', 'jpg', 'jpeg', 'png'], 'PDF and image files only!')])
    aadhaar_pan_file = FileField('Aadhaar/PAN Card', validators=[Optional(), FileAllowed(['pdf', 'jpg', 'jpeg', 'png'], 'PDF and image files only!')])
    
    submit = SubmitField('Upload Documents')


class AdminLoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=64)])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')