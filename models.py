from app import db
from datetime import datetime
from flask_login import UserMixin
import secrets
import hashlib


class Admin(UserMixin, db.Model):
    """Admin user model for dashboard access"""
    __tablename__ = 'admins'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Admin {self.username}>'


class CrewMember(db.Model):
    """Crew member model for registration and tracking"""
    __tablename__ = 'crew_members'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    rank = db.Column(db.String(64), nullable=False)
    passport = db.Column(db.String(32), unique=True, nullable=False)
    
    # Enhanced fields
    nationality = db.Column(db.String(64), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)
    years_experience = db.Column(db.Integer, nullable=False)
    last_vessel_type = db.Column(db.String(128))
    availability_date = db.Column(db.Date, nullable=False)
    mobile_number = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    
    # Emergency contact
    emergency_contact_name = db.Column(db.String(128))
    emergency_contact_phone = db.Column(db.String(20))
    emergency_contact_relationship = db.Column(db.String(64))
    
    # File upload fields - Core documents
    passport_file = db.Column(db.String(255))
    cdc_file = db.Column(db.String(255))  # CDC/Seaman Book
    resume_file = db.Column(db.String(255))
    photo_file = db.Column(db.String(255))
    medical_certificate_file = db.Column(db.String(255))
    
    # Additional required documents
    coc_cop_file = db.Column(db.String(255))  # Certificate of Competency/Proficiency
    stcw_certificates_file = db.Column(db.String(255))  # STCW Certificates
    gmdss_dce_file = db.Column(db.String(255))  # GMDSS or DCE (if applicable)
    yellow_fever_file = db.Column(db.String(255))  # Yellow Fever (optional)
    bank_details_file = db.Column(db.String(255))  # Bank details document
    aadhaar_pan_file = db.Column(db.String(255))  # Aadhaar/PAN for Indian nationals
    
    # Profile access token for secure private access
    profile_token = db.Column(db.String(128), unique=True)
    
    # Status and notes
    status = db.Column(db.Integer, default=0)  # 0=Registered, 1=Screening, 2=Documents Verified, 3=Approved, -1=Rejected, -2=Flagged
    admin_notes = db.Column(db.Text)
    screening_notes = db.Column(db.Text)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<CrewMember {self.name} ({self.passport})>'
    
    def get_status_name(self):
        """Get the human-readable status name"""
        status_names = {
            0: "Registered",
            1: "Screening",
            2: "Documents Verified", 
            3: "Approved",
            -1: "Rejected",
            -2: "Flagged"
        }
        return status_names.get(self.status, "Unknown")
    
    def get_status_class(self):
        """Get Bootstrap class for status"""
        status_classes = {
            0: "secondary",
            1: "warning",
            2: "info",
            3: "success",
            -1: "danger",
            -2: "dark"
        }
        return status_classes.get(self.status, "secondary")
    
    def generate_profile_token(self):
        """Generate a secure token for profile access"""
        if not self.profile_token:
            # Generate a secure random token
            random_bytes = secrets.token_bytes(32)
            # Create a hash that includes crew ID for uniqueness
            token_data = f"{self.id}_{self.passport}_{random_bytes.hex()}"
            self.profile_token = hashlib.sha256(token_data.encode()).hexdigest()
            db.session.commit()
        return self.profile_token
    
    def get_required_documents(self):
        """Get list of required documents with their status"""
        # Core documents (always required)
        documents = [
            {'field': 'passport_file', 'name': 'Passport', 'required': True},
            {'field': 'cdc_file', 'name': 'CDC (Seaman Book)', 'required': True},
            {'field': 'resume_file', 'name': 'Resume/CV', 'required': True},
            {'field': 'photo_file', 'name': 'Photo (Passport Size)', 'required': True},
            {'field': 'medical_certificate_file', 'name': 'Medical Certificate', 'required': True},
            {'field': 'coc_cop_file', 'name': 'COC/COP Certificate', 'required': True},
            {'field': 'stcw_certificates_file', 'name': 'STCW Certificates', 'required': True},
            {'field': 'bank_details_file', 'name': 'Bank Details Document', 'required': True},
            {'field': 'gmdss_dce_file', 'name': 'GMDSS/DCE Certificate', 'required': False},
            {'field': 'yellow_fever_file', 'name': 'Yellow Fever Certificate', 'required': False},
        ]
        
        # Add Aadhaar/PAN for Indian nationals
        if self.nationality and self.nationality.lower() in ['indian', 'india']:
            documents.append({
                'field': 'aadhaar_pan_file', 
                'name': 'Aadhaar/PAN Card', 
                'required': True
            })
        
        # Check status of each document
        for doc in documents:
            doc['uploaded'] = bool(getattr(self, doc['field']))
            doc['status'] = 'complete' if doc['uploaded'] else 'missing'
        
        return documents
    
    def get_profile_completion_percentage(self):
        """Calculate profile completion percentage"""
        documents = self.get_required_documents()
        required_docs = [doc for doc in documents if doc['required']]
        uploaded_docs = [doc for doc in required_docs if doc['uploaded']]
        
        if not required_docs:
            return 100
        
        return int((len(uploaded_docs) / len(required_docs)) * 100)
    
    def is_profile_complete(self):
        """Check if profile is 100% complete"""
        return self.get_profile_completion_percentage() == 100


class StaffMember(db.Model):
    """Staff member model for offshore/office staff registration"""
    __tablename__ = 'staff_members'
    
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(128), nullable=False)
    email_or_whatsapp = db.Column(db.String(128), nullable=False)
    position_applying = db.Column(db.String(128), nullable=False)
    department = db.Column(db.String(32), nullable=False)  # Ops, HR, Tech, Crewing
    years_experience = db.Column(db.Integer, nullable=False)
    current_employer = db.Column(db.String(128))
    location = db.Column(db.String(128), nullable=False)
    availability_date = db.Column(db.Date, nullable=False)
    mobile_number = db.Column(db.String(20), nullable=False)
    
    # Additional information
    education = db.Column(db.String(255))
    certifications = db.Column(db.Text)
    salary_expectation = db.Column(db.String(64))
    
    # File upload fields
    resume_file = db.Column(db.String(255))
    photo_file = db.Column(db.String(255))
    
    # Status and notes
    status = db.Column(db.Integer, default=1)  # 1=Screening, 3=Approved, -1=Rejected
    admin_notes = db.Column(db.Text)
    screening_notes = db.Column(db.Text)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<StaffMember {self.full_name} ({self.position_applying})>'
    
    def get_status_name(self):
        """Get the human-readable status name"""
        status_names = {
            1: "Screening",
            3: "Approved",
            -1: "Rejected"
        }
        return status_names.get(self.status, "Unknown")
    
    def get_status_class(self):
        """Get Bootstrap class for status"""
        status_classes = {
            1: "warning",
            3: "success",
            -1: "danger"
        }
        return status_classes.get(self.status, "warning")