#!/usr/bin/env python3
"""
Test script for the resume analyzer functionality
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from src.routes.analyzer import (
    preprocess_text, 
    extract_skills, 
    extract_keywords_nlp, 
    calculate_similarity,
    analyze_resume_job_match
)

def test_basic_functionality():
    """Test basic NLP functions"""
    print("=== Testing Basic NLP Functionality ===")
    
    # Sample resume text
    sample_resume = """
    John Doe
    Software Engineer
    
    Experience:
    - 3 years of Python development
    - Built web applications using React and Node.js
    - Worked with MySQL and PostgreSQL databases
    - Experience with AWS cloud services
    - Led a team of 5 developers
    
    Skills: Python, JavaScript, React, Node.js, MySQL, PostgreSQL, AWS, Docker, Git
    """
    
    # Sample job description
    sample_job = """
    We are looking for a Senior Software Engineer with:
    - 5+ years of Python experience
    - Strong React and JavaScript skills
    - Experience with PostgreSQL and MongoDB
    - AWS cloud platform experience
    - Leadership and team management skills
    - Knowledge of Docker and Kubernetes
    """
    
    print("1. Testing text preprocessing...")
    clean_resume = preprocess_text(sample_resume)
    print(f"Original length: {len(sample_resume)}, Clean length: {len(clean_resume)}")
    
    print("\n2. Testing skill extraction...")
    resume_skills = extract_skills(sample_resume)
    job_skills = extract_skills(sample_job)
    
    print("Resume skills found:")
    for category, skills in resume_skills.items():
        if skills:
            print(f"  {category}: {skills}")
    
    print("\nJob skills found:")
    for category, skills in job_skills.items():
        if skills:
            print(f"  {category}: {skills}")
    
    print("\n3. Testing keyword extraction...")
    resume_keywords = extract_keywords_nlp(sample_resume)
    job_keywords = extract_keywords_nlp(sample_job)
    
    print(f"Resume keywords: {resume_keywords[:10]}")
    print(f"Job keywords: {job_keywords[:10]}")
    
    print("\n4. Testing similarity calculation...")
    similarity = calculate_similarity(sample_resume, sample_job)
    print(f"Similarity score: {similarity:.3f}")
    
    print("\n5. Testing full analysis...")
    analysis = analyze_resume_job_match(sample_resume, sample_job)
    
    print(f"Overall similarity: {analysis['similarity_score']}%")
    print(f"Matching keywords: {len(analysis['matching_keywords'])}")
    print(f"Missing keywords: {len(analysis['missing_keywords'])}")
    print("Recommendations:")
    for rec in analysis['recommendations']:
        print(f"  - {rec}")
    
    return True

def test_edge_cases():
    """Test edge cases and error handling"""
    print("\n=== Testing Edge Cases ===")
    
    # Empty texts
    print("1. Testing empty texts...")
    try:
        result = analyze_resume_job_match("", "")
        print("Empty text handling: OK")
    except Exception as e:
        print(f"Empty text error: {e}")
    
    # Very short texts
    print("2. Testing short texts...")
    try:
        result = analyze_resume_job_match("Python developer", "Need Python skills")
        print(f"Short text similarity: {result['similarity_score']}%")
    except Exception as e:
        print(f"Short text error: {e}")
    
    return True

if __name__ == "__main__":
    print("Starting Resume Analyzer Tests...")
    
    try:
        test_basic_functionality()
        test_edge_cases()
        print("\n=== All Tests Completed Successfully! ===")
    except Exception as e:
        print(f"\n=== Test Failed: {e} ===")
        import traceback
        traceback.print_exc()

