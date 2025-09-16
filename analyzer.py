from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from flask_login import current_user, login_required
import spacy
import re
from collections import Counter
import PyPDF2
import docx
import io
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
from src.utils.skill_database import SKILL_DATABASE, get_relevant_skills_for_job, get_skill_weight
from src.models import db, User, Resume, Analysis, JobDescription

analyzer_bp = Blueprint('analyzer', __name__)

# Load spaCy model
nlp = spacy.load('en_core_web_sm')

def extract_text_from_file(file):
    """Extract text from uploaded file (PDF or DOCX)"""
    try:
        if file.filename.lower().endswith('.pdf'):
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(file.read()))
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
            return text
        elif file.filename.lower().endswith('.docx'):
            doc = docx.Document(io.BytesIO(file.read()))
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text
        else:
            # Assume it's a text file
            return file.read().decode('utf-8')
    except Exception as e:
        return f"Error extracting text: {str(e)}"

def preprocess_text(text):
    """Clean and preprocess text"""
    # Convert to lowercase
    text = text.lower()
    # Remove extra whitespace and newlines
    text = re.sub(r'\s+', ' ', text)
    # Remove special characters but keep alphanumeric and spaces
    text = re.sub(r'[^a-zA-Z0-9\s\.\+\#]', ' ', text)
    return text.strip()

def extract_skills(text, job_description=None):
    """Extract skills from text using comprehensive skill database"""
    text = preprocess_text(text)
    found_skills = {}
    
    # Get relevant skill categories based on job description
    if job_description:
        relevant_categories = get_relevant_skills_for_job(job_description)
    else:
        relevant_categories = list(SKILL_DATABASE.keys())
    
    for category in relevant_categories:
        if category in SKILL_DATABASE:
            found_skills[category] = []
            skills_list = SKILL_DATABASE[category]['keywords']
            
            for skill in skills_list:
                # Use word boundaries to avoid partial matches
                pattern = r'\b' + re.escape(skill.lower()) + r'\b'
                if re.search(pattern, text):
                    found_skills[category].append(skill)
    
    return found_skills

def extract_keywords_nlp(text, top_n=20):
    """Extract important keywords using NLP"""
    doc = nlp(text)
    
    # Extract entities and important tokens
    keywords = []
    
    # Named entities
    for ent in doc.ents:
        if ent.label_ in ['ORG', 'PRODUCT', 'WORK_OF_ART', 'EVENT']:
            keywords.append(ent.text.lower())
    
    # Important tokens (nouns, adjectives)
    for token in doc:
        if (token.pos_ in ['NOUN', 'ADJ'] and 
            not token.is_stop and 
            not token.is_punct and 
            len(token.text) > 2):
            keywords.append(token.lemma_.lower())
    
    # Count frequency and return top keywords
    keyword_freq = Counter(keywords)
    return [word for word, count in keyword_freq.most_common(top_n)]

def calculate_similarity(resume_text, job_description):
    """Calculate similarity between resume and job description"""
    vectorizer = TfidfVectorizer(stop_words='english', max_features=1000)
    
    try:
        tfidf_matrix = vectorizer.fit_transform([resume_text, job_description])
        similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        return similarity
    except:
        return 0.0

def analyze_resume_job_match(resume_text, job_description):
    """Main analysis function with improved scoring"""
    # Preprocess texts
    resume_clean = preprocess_text(resume_text)
    job_clean = preprocess_text(job_description)
    
    # Extract skills from both (pass job description for context-aware extraction)
    resume_skills = extract_skills(resume_text, job_description)
    job_skills = extract_skills(job_description)
    
    # Extract keywords
    resume_keywords = extract_keywords_nlp(resume_text)
    job_keywords = extract_keywords_nlp(job_description)
    
    # Calculate overall similarity
    similarity_score = calculate_similarity(resume_clean, job_clean)
    
    # Find matching and missing skills with weighted scoring
    matching_skills = {}
    missing_skills = {}
    skill_match_score = 0
    total_job_skills = 0
    
    for category in job_skills.keys():
        resume_cat_skills = set(resume_skills.get(category, []))
        job_cat_skills = set(job_skills.get(category, []))
        
        matching_skills[category] = list(resume_cat_skills.intersection(job_cat_skills))
        missing_skills[category] = list(job_cat_skills - resume_cat_skills)
        
        # Calculate weighted skill match score
        category_weight = get_skill_weight(category)
        matched_count = len(matching_skills[category])
        total_count = len(job_cat_skills)
        
        if total_count > 0:
            skill_match_score += (matched_count / total_count) * category_weight
            total_job_skills += category_weight
    
    # Normalize skill match score
    if total_job_skills > 0:
        skill_match_score = (skill_match_score / total_job_skills) * 100
    else:
        skill_match_score = 0
    
    # Find matching keywords
    matching_keywords = list(set(resume_keywords).intersection(set(job_keywords)))
    missing_keywords = list(set(job_keywords) - set(resume_keywords))
    
    # Calculate composite score (weighted average)
    composite_score = (similarity_score * 0.4 + (skill_match_score / 100) * 0.6) * 100
    
    # Generate recommendations
    recommendations = generate_recommendations(missing_skills, missing_keywords, composite_score, skill_match_score)
    
    return {
        'similarity_score': round(similarity_score * 100, 2),
        'skill_match_score': round(skill_match_score, 2),
        'composite_score': round(composite_score, 2),
        'resume_skills': resume_skills,
        'job_skills': job_skills,
        'matching_skills': matching_skills,
        'missing_skills': missing_skills,
        'resume_keywords': resume_keywords,
        'job_keywords': job_keywords,
        'matching_keywords': matching_keywords,
        'missing_keywords': missing_keywords[:10],  # Limit to top 10
        'recommendations': recommendations
    }

def generate_recommendations(missing_skills, missing_keywords, composite_score, skill_match_score):
    """Generate actionable recommendations with improved scoring"""
    recommendations = []
    
    # Overall score assessment
    if composite_score < 30:
        recommendations.append("Your resume has low alignment with this job. Consider significant tailoring to match the requirements.")
    elif composite_score < 50:
        recommendations.append("Your resume shows moderate alignment. Focus on highlighting relevant experience and skills.")
    elif composite_score < 70:
        recommendations.append("Good alignment! Consider minor adjustments to strengthen your application.")
    else:
        recommendations.append("Excellent match! Your resume aligns very well with the job requirements.")
    
    # Skill-specific recommendations (prioritize by category weight)
    priority_categories = ['programming_languages', 'data_science', 'cloud_platforms', 'databases']
    
    for category in priority_categories:
        if category in missing_skills and missing_skills[category]:
            skills = missing_skills[category][:3]  # Top 3 missing skills
            category_name = category.replace('_', ' ').title()
            recommendations.append(f"Consider adding {category_name.lower()}: {', '.join(skills)}")
    
    # Handle other categories
    for category, skills in missing_skills.items():
        if category not in priority_categories and skills:
            skills_subset = skills[:2]  # Top 2 for other categories
            category_name = category.replace('_', ' ').title()
            recommendations.append(f"Include {category_name.lower()}: {', '.join(skills_subset)}")
    
    # Keyword recommendations
    if len(missing_keywords) > 3:
        recommendations.append(f"Include these important keywords: {', '.join(missing_keywords[:5])}")
    
    # Skill match specific advice
    if skill_match_score < 40:
        recommendations.append("Focus on developing the key technical skills mentioned in the job description.")
    elif skill_match_score > 80:
        recommendations.append("Strong technical skill match! Ensure your experience examples demonstrate these skills.")
    
    return recommendations[:8]  # Limit to 8 recommendations

@analyzer_bp.route('/analyze', methods=['POST'])
@cross_origin()
def analyze_resume():
    """Main endpoint for resume analysis"""
    try:
        # Check if file is uploaded
        if 'resume' not in request.files:
            return jsonify({'error': 'No resume file uploaded'}), 400
        
        resume_file = request.files['resume']
        job_description = request.form.get('job_description', '')
        
        if not job_description:
            return jsonify({'error': 'Job description is required'}), 400
        
        # Extract text from resume
        resume_text = extract_text_from_file(resume_file)
        
        if resume_text.startswith('Error'):
            return jsonify({'error': resume_text}), 400
        
        # Perform analysis
        analysis_result = analyze_resume_job_match(resume_text, job_description)
        
        # Save to database if user is authenticated
        if current_user.is_authenticated:
            try:
                # Save or update resume
                resume = Resume.query.filter_by(
                    user_id=current_user.id,
                    filename=resume_file.filename
                ).first()
                
                if not resume:
                    resume = Resume(
                        user_id=current_user.id,
                        filename=resume_file.filename,
                        content=resume_text,
                        file_type=resume_file.filename.split('.')[-1].lower()
                    )
                    db.session.add(resume)
                    db.session.flush()  # Get the ID
                
                # Create job description entry
                job_desc = JobDescription(
                    title="Analyzed Position",
                    content=job_description
                )
                db.session.add(job_desc)
                db.session.flush()  # Get the ID
                
                # Save analysis
                analysis = Analysis(
                    user_id=current_user.id,
                    resume_id=resume.id,
                    job_description_id=job_desc.id,
                    composite_score=analysis_result['composite_score'],
                    similarity_score=analysis_result['similarity_score'],
                    skill_match_score=analysis_result['skill_match_score']
                )
                
                # Set JSON fields
                analysis.set_matching_keywords(analysis_result['matching_keywords'])
                analysis.set_missing_keywords(analysis_result['missing_keywords'])
                analysis.set_matching_skills(analysis_result['matching_skills'])
                analysis.set_missing_skills(analysis_result['missing_skills'])
                analysis.set_job_skills(analysis_result['job_skills'])
                analysis.set_recommendations(analysis_result['recommendations'])
                
                db.session.add(analysis)
                db.session.commit()
                
                # Add analysis ID to result
                analysis_result['analysis_id'] = analysis.id
                
            except Exception as e:
                db.session.rollback()
                print(f"Database error: {e}")
                # Continue without saving to database
        
        return jsonify({
            'success': True,
            'analysis': analysis_result,
            'saved': current_user.is_authenticated
        })
        
    except Exception as e:
        return jsonify({'error': f'Analysis failed: {str(e)}'}), 500

@analyzer_bp.route('/history', methods=['GET'])
@login_required
@cross_origin()
def get_analysis_history():
    """Get user's analysis history"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        analyses = Analysis.query.filter_by(user_id=current_user.id)\
            .order_by(Analysis.created_at.desc())\
            .paginate(page=page, per_page=per_page, error_out=False)
        
        result = {
            'analyses': [analysis.to_dict() for analysis in analyses.items],
            'total': analyses.total,
            'pages': analyses.pages,
            'current_page': page,
            'per_page': per_page
        }
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': f'Failed to get history: {str(e)}'}), 500

@analyzer_bp.route('/analysis/<int:analysis_id>', methods=['GET'])
@login_required
@cross_origin()
def get_analysis(analysis_id):
    """Get specific analysis by ID"""
    try:
        analysis = Analysis.query.filter_by(
            id=analysis_id,
            user_id=current_user.id
        ).first()
        
        if not analysis:
            return jsonify({'error': 'Analysis not found'}), 404
        
        return jsonify({
            'success': True,
            'analysis': analysis.to_dict()
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to get analysis: {str(e)}'}), 500

@analyzer_bp.route('/resumes', methods=['GET'])
@login_required
@cross_origin()
def get_user_resumes():
    """Get user's saved resumes"""
    try:
        resumes = Resume.query.filter_by(
            user_id=current_user.id,
            is_active=True
        ).order_by(Resume.uploaded_at.desc()).all()
        
        result = []
        for resume in resumes:
            result.append({
                'id': resume.id,
                'filename': resume.filename,
                'file_type': resume.file_type,
                'uploaded_at': resume.uploaded_at.isoformat(),
                'analysis_count': len(resume.analyses)
            })
        
        return jsonify({
            'success': True,
            'resumes': result
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to get resumes: {str(e)}'}), 500

@analyzer_bp.route('/health', methods=['GET'])
@cross_origin()
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'message': 'Resume analyzer is running'})

