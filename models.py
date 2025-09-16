from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
import json

db = SQLAlchemy()

class User(UserMixin, db.Model):
    """User model for authentication and profile management"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    resumes = db.relationship('Resume', backref='user', lazy=True, cascade='all, delete-orphan')
    analyses = db.relationship('Analysis', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<User {self.username}>'

class Resume(db.Model):
    """Resume model to store user's resume files and content"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    file_type = db.Column(db.String(10), nullable=False)  # txt, pdf, docx
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    analyses = db.relationship('Analysis', backref='resume', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Resume {self.filename}>'

class JobDescription(db.Model):
    """Job description model to store job postings for analysis"""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    company = db.Column(db.String(200))
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    analyses = db.relationship('Analysis', backref='job_description', lazy=True)
    
    def __repr__(self):
        return f'<JobDescription {self.title}>'

class Analysis(db.Model):
    """Analysis model to store resume analysis results"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    resume_id = db.Column(db.Integer, db.ForeignKey('resume.id'), nullable=False)
    job_description_id = db.Column(db.Integer, db.ForeignKey('job_description.id'), nullable=True)
    
    # Analysis scores
    composite_score = db.Column(db.Float, nullable=False)
    similarity_score = db.Column(db.Float, nullable=False)
    skill_match_score = db.Column(db.Float, nullable=False)
    
    # Analysis results (stored as JSON)
    matching_keywords = db.Column(db.Text)  # JSON array
    missing_keywords = db.Column(db.Text)   # JSON array
    matching_skills = db.Column(db.Text)    # JSON object
    missing_skills = db.Column(db.Text)     # JSON object
    job_skills = db.Column(db.Text)         # JSON object
    recommendations = db.Column(db.Text)    # JSON array
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    analysis_version = db.Column(db.String(10), default='1.0')
    
    def __repr__(self):
        return f'<Analysis {self.id} - Score: {self.composite_score}%>'
    
    def get_matching_keywords(self):
        """Get matching keywords as Python list"""
        return json.loads(self.matching_keywords) if self.matching_keywords else []
    
    def set_matching_keywords(self, keywords):
        """Set matching keywords from Python list"""
        self.matching_keywords = json.dumps(keywords)
    
    def get_missing_keywords(self):
        """Get missing keywords as Python list"""
        return json.loads(self.missing_keywords) if self.missing_keywords else []
    
    def set_missing_keywords(self, keywords):
        """Set missing keywords from Python list"""
        self.missing_keywords = json.dumps(keywords)
    
    def get_matching_skills(self):
        """Get matching skills as Python dict"""
        return json.loads(self.matching_skills) if self.matching_skills else {}
    
    def set_matching_skills(self, skills):
        """Set matching skills from Python dict"""
        self.matching_skills = json.dumps(skills)
    
    def get_missing_skills(self):
        """Get missing skills as Python dict"""
        return json.loads(self.missing_skills) if self.missing_skills else {}
    
    def set_missing_skills(self, skills):
        """Set missing skills from Python dict"""
        self.missing_skills = json.dumps(skills)
    
    def get_job_skills(self):
        """Get job skills as Python dict"""
        return json.loads(self.job_skills) if self.job_skills else {}
    
    def set_job_skills(self, skills):
        """Set job skills from Python dict"""
        self.job_skills = json.dumps(skills)
    
    def get_recommendations(self):
        """Get recommendations as Python list"""
        return json.loads(self.recommendations) if self.recommendations else []
    
    def set_recommendations(self, recs):
        """Set recommendations from Python list"""
        self.recommendations = json.dumps(recs)
    
    def to_dict(self):
        """Convert analysis to dictionary for API responses"""
        return {
            'id': self.id,
            'composite_score': round(self.composite_score, 2),
            'similarity_score': round(self.similarity_score, 2),
            'skill_match_score': round(self.skill_match_score, 2),
            'matching_keywords': self.get_matching_keywords(),
            'missing_keywords': self.get_missing_keywords(),
            'matching_skills': self.get_matching_skills(),
            'missing_skills': self.get_missing_skills(),
            'job_skills': self.get_job_skills(),
            'recommendations': self.get_recommendations(),
            'created_at': self.created_at.isoformat(),
            'analysis_version': self.analysis_version
        }

class UserSession(db.Model):
    """User session model for tracking active sessions"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    session_token = db.Column(db.String(255), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    
    def __repr__(self):
        return f'<UserSession {self.user_id}>'

