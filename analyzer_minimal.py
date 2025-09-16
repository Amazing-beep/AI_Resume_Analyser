from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from flask_login import current_user, login_required
import re
from collections import Counter
from src.models import db, User, Resume, Analysis, JobDescription

analyzer_bp = Blueprint('analyzer', __name__)

# Simple skill database for lightweight deployment
SIMPLE_SKILLS = {
    'programming_languages': [
        'python', 'javascript', 'java', 'c++', 'c#', 'php', 'ruby', 'go', 'rust', 'swift',
        'typescript', 'kotlin', 'scala', 'r', 'matlab', 'sql', 'html', 'css'
    ],
    'web_technologies': [
        'react', 'angular', 'vue', 'node.js', 'express', 'django', 'flask', 'spring',
        'bootstrap', 'jquery', 'webpack', 'babel', 'sass', 'less'
    ],
    'databases': [
        'mysql', 'postgresql', 'mongodb', 'redis', 'sqlite', 'oracle', 'cassandra',
        'elasticsearch', 'dynamodb', 'firebase'
    ],
    'cloud_platforms': [
        'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'jenkins', 'terraform',
        'ansible', 'chef', 'puppet'
    ],
    'tools_frameworks': [
        'git', 'github', 'gitlab', 'jira', 'confluence', 'slack', 'trello',
        'postman', 'swagger', 'junit', 'pytest', 'selenium'
    ]
}

def extract_text_from_file(file):
    """Extract text from uploaded file (text files only)"""
    try:
        # Only support text files for minimal deployment
        return file.read().decode('utf-8')
    except Exception as e:
        return f"Error extracting text: {str(e)}. Please upload a plain text file."

def preprocess_text(text):
    """Clean and preprocess text"""
    # Convert to lowercase
    text = text.lower()
    # Remove extra whitespace and newlines
    text = re.sub(r'\s+', ' ', text)
    # Remove special characters but keep alphanumeric and spaces
    text = re.sub(r'[^a-zA-Z0-9\s\.\+\#]', ' ', text)
    return text.strip()

def extract_skills_simple(text):
    """Extract skills from text using simple keyword matching"""
    text = preprocess_text(text)
    found_skills = {}
    
    for category, skills_list in SIMPLE_SKILLS.items():
        found_skills[category] = []
        for skill in skills_list:
            # Use word boundaries to avoid partial matches
            pattern = r'\b' + re.escape(skill.lower()) + r'\b'
            if re.search(pattern, text):
                found_skills[category].append(skill)
    
    return found_skills

def extract_keywords_simple(text, top_n=20):
    """Extract important keywords using simple frequency analysis"""
    text = preprocess_text(text)
    words = text.split()
    
    # Filter out common stop words
    stop_words = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with',
        'by', 'from', 'up', 'about', 'into', 'through', 'during', 'before', 'after',
        'above', 'below', 'between', 'among', 'is', 'are', 'was', 'were', 'be', 'been',
        'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
        'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those'
    }
    
    # Filter words
    filtered_words = [word for word in words if len(word) > 2 and word not in stop_words]
    
    # Count frequency and return top keywords
    word_freq = Counter(filtered_words)
    return [word for word, count in word_freq.most_common(top_n)]

def calculate_similarity_simple(resume_text, job_description):
    """Calculate simple similarity between resume and job description"""
    resume_words = set(preprocess_text(resume_text).split())
    job_words = set(preprocess_text(job_description).split())
    
    if not job_words:
        return 0.0
    
    intersection = resume_words.intersection(job_words)
    return len(intersection) / len(job_words)

def analyze_resume_job_match_simple(resume_text, job_description):
    """Main analysis function with simplified processing"""
    # Extract skills from both
    resume_skills = extract_skills_simple(resume_text)
    job_skills = extract_skills_simple(job_description)
    
    # Extract keywords
    resume_keywords = extract_keywords_simple(resume_text)
    job_keywords = extract_keywords_simple(job_description)
    
    # Calculate overall similarity
    similarity_score = calculate_similarity_simple(resume_text, job_description)
    
    # Find matching and missing skills
    matching_skills = {}
    missing_skills = {}
    skill_matches = 0
    total_job_skills = 0
    
    for category in job_skills.keys():
        resume_cat_skills = set(resume_skills.get(category, []))
        job_cat_skills = set(job_skills.get(category, []))
        
        matching_skills[category] = list(resume_cat_skills.intersection(job_cat_skills))
        missing_skills[category] = list(job_cat_skills - resume_cat_skills)
        
        skill_matches += len(matching_skills[category])
        total_job_skills += len(job_cat_skills)
    
    # Calculate skill match score
    skill_match_score = (skill_matches / total_job_skills * 100) if total_job_skills > 0 else 0
    
    # Find matching keywords
    matching_keywords = list(set(resume_keywords).intersection(set(job_keywords)))
    missing_keywords = list(set(job_keywords) - set(resume_keywords))
    
    # Calculate composite score (weighted average)
    composite_score = (similarity_score * 0.4 + (skill_match_score / 100) * 0.6) * 100
    
    # Generate recommendations
    recommendations = generate_recommendations_simple(missing_skills, missing_keywords, composite_score)
    
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

def generate_recommendations_simple(missing_skills, missing_keywords, composite_score):
    """Generate actionable recommendations"""
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
    
    # Skill-specific recommendations
    for category, skills in missing_skills.items():
        if skills:
            skills_subset = skills[:3]  # Top 3 missing skills
            category_name = category.replace('_', ' ').title()
            recommendations.append(f"Consider adding {category_name.lower()}: {', '.join(skills_subset)}")
    
    # Keyword recommendations
    if len(missing_keywords) > 3:
        recommendations.append(f"Include these important keywords: {', '.join(missing_keywords[:5])}")
    
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
        analysis_result = analyze_resume_job_match_simple(resume_text, job_description)
        
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

@analyzer_bp.route('/health', methods=['GET'])
@cross_origin()
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'message': 'Resume analyzer is running'})

