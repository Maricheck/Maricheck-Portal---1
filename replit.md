# Maricheck - Maritime Crew Management System

## Overview

Maricheck is a Flask-based web application designed for managing maritime crew member registrations and staff recruitment. The system provides a dual-interface design with public-facing registration forms for crew and staff members, and a protected admin dashboard for managing applications, tracking statuses, and exporting data. The platform serves the maritime industry by streamlining the recruitment process for shipping companies and providing a professional portal for maritime professionals to register and track their applications.

## Recent Changes (August 2, 2025)

- **Privacy Enhancement**: Updated crew registration flow to NOT display private upload/profile links to crew members after registration
- **Admin Control**: Private profile links are now exclusively shown in the admin panel (crew table + profile view) for better privacy and admin control
- **Mobile Optimization**: Enhanced responsive design for admin crew list table with mobile-friendly column hiding and copy functionality
- **User Experience**: Improved registration success message to focus on team review rather than providing direct access links

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Template Engine**: Jinja2 templating with Flask for dynamic content rendering
- **UI Framework**: Bootstrap 5 with custom maritime theme using navy blue, sea green, and gold color scheme
- **Icons**: Font Awesome 6.4.0 for consistent iconography throughout the application
- **Typography**: Google Fonts (Inter) for professional, readable typography
- **Responsive Design**: Mobile-first approach using Bootstrap grid system with custom CSS optimizations
- **Interactive Elements**: International telephone input with country code detection, file upload previews, and form validation feedback
- **JavaScript**: Custom maricheck.js for enhanced user interactions, auto-hiding alerts, and form loading states

### Backend Architecture
- **Framework**: Flask (Python web framework) with modular route organization
- **Database**: SQLAlchemy ORM with SQLite default configuration (production-ready for PostgreSQL)
- **Authentication**: Flask-Login for session-based admin authentication with simple username/password system
- **Forms**: Flask-WTF with WTForms for comprehensive form handling, validation, and CSRF protection
- **Security**: Werkzeug password hashing for admin credentials, secure file uploads with unique naming
- **File Management**: Organized upload system with categorized storage (passport, CDC, resume, photo, medical certificates)
- **Configuration**: Environment-based configuration for database URL and session secrets

### Database Schema Design
- **Admin Model**: Simple authentication table with username and password hash
- **CrewMember Model**: Comprehensive crew registration with personal info, professional details, emergency contacts, and file upload references
- **StaffMember Model**: Shore-based staff registration with position and department tracking
- **Status Tracking**: Built-in status enumeration system (Registered, Screening, Documents Verified, Approved, Rejected, Flagged)
- **File References**: Database stores file paths rather than binary data for better performance

### Key Architectural Decisions
- **Dual Interface Separation**: Public registration portal and protected admin dashboard serve different user needs
- **Session-Based Authentication**: Simple admin login without complex role-based access control
- **File Upload Strategy**: Secure filename generation using UUID prefixes and organized folder structure
- **Database Agnostic Design**: SQLite for development with easy PostgreSQL migration for production
- **Status Management**: Centralized status tracking with visual indicators and filtering capabilities
- **Export Functionality**: CSV export capabilities for data portability and reporting

## External Dependencies

### Core Framework Dependencies
- **Flask**: Web framework for Python applications
- **SQLAlchemy**: Database ORM for data persistence and queries
- **Flask-Login**: User session management for admin authentication
- **Flask-WTF**: Form handling and CSRF protection
- **WTForms**: Form validation and rendering
- **Werkzeug**: Security utilities for password hashing and file handling

### Frontend Dependencies
- **Bootstrap 5**: CSS framework for responsive design and UI components
- **Font Awesome 6.4.0**: Icon library for consistent visual elements
- **Google Fonts (Inter)**: Typography for professional appearance
- **International Telephone Input**: Enhanced phone number input with country code detection

### Database Configuration
- **SQLite**: Default database for development and simple deployments
- **PostgreSQL**: Production database option (requires DATABASE_URL environment variable)
- **Database migrations**: Handled through SQLAlchemy create_all() method

### File Storage
- **Local File System**: Upload storage in static/uploads directory with organized subfolder structure
- **File Type Validation**: Support for PDF, image (JPG, PNG), and document (DOC, DOCX) formats
- **Security**: Secure filename generation and file type validation to prevent malicious uploads

### Environment Configuration
- **SESSION_SECRET**: Flask session encryption key
- **DATABASE_URL**: Database connection string for production PostgreSQL setup
- **UPLOAD_FOLDER**: File upload directory configuration
- **MAX_CONTENT_LENGTH**: File size limit configuration (16MB default)