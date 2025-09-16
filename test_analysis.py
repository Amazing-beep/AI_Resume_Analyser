#!/usr/bin/env python3
"""
Comprehensive test script for the AI Resume Analyzer
Tests all major functionality including authentication, analysis, and database integration
"""

import requests
import json
import os
from io import BytesIO

# Base URL for the API
BASE_URL = "http://localhost:5000/api"

def test_health_check():
    """Test the health check endpoint"""
    print("🔍 Testing health check...")
    response = requests.get(f"{BASE_URL}/health")
    assert response.status_code == 200
    data = response.json()
    assert data['status'] == 'healthy'
    print("✅ Health check passed")

def test_user_registration():
    """Test user registration"""
    print("🔍 Testing user registration...")
    user_data = {
        "username": "testuser2",
        "email": "test2@example.com", 
        "password": "password123"
    }
    response = requests.post(f"{BASE_URL}/auth/register", json=user_data)
    assert response.status_code == 201
    data = response.json()
    assert data['message'] == 'Registration successful'
    assert data['user']['username'] == 'testuser2'
    print("✅ User registration passed")
    return response.cookies

def test_user_login():
    """Test user login"""
    print("🔍 Testing user login...")
    login_data = {
        "username": "testuser2",
        "password": "password123"
    }
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    assert response.status_code == 200
    data = response.json()
    assert data['message'] == 'Login successful'
    print("✅ User login passed")
    return response.cookies

def test_profile_access(cookies):
    """Test authenticated profile access"""
    print("🔍 Testing profile access...")
    response = requests.get(f"{BASE_URL}/auth/profile", cookies=cookies)
    assert response.status_code == 200
    data = response.json()
    assert 'user' in data
    assert 'statistics' in data
    print("✅ Profile access passed")

def test_resume_analysis(cookies):
    """Test resume analysis with authentication"""
    print("🔍 Testing resume analysis...")
    
    # Create a sample resume file
    resume_content = """
John Doe
Senior Software Engineer
Email: john.doe@email.com
Phone: (555) 123-4567

PROFESSIONAL SUMMARY
Experienced software engineer with 7+ years of expertise in full-stack development, 
specializing in Python, JavaScript, React, and cloud technologies. Proven track record 
of building scalable web applications and leading development teams.

TECHNICAL SKILLS
Programming Languages: Python, JavaScript, TypeScript, Java, SQL
Web Technologies: React, Node.js, Express, HTML5, CSS3, Bootstrap
Databases: PostgreSQL, MySQL, MongoDB, Redis
Cloud Platforms: AWS (EC2, S3, Lambda), Docker, Kubernetes
Tools & Frameworks: Git, Jenkins, Django, Flask, REST APIs
Methodologies: Agile, Scrum, TDD, CI/CD

PROFESSIONAL EXPERIENCE
Senior Software Engineer | TechCorp Inc. | 2020 - Present
- Led development of microservices architecture using Python and Docker
- Built responsive web applications using React and TypeScript
- Implemented CI/CD pipelines using Jenkins and AWS
- Mentored junior developers and conducted code reviews

Software Engineer | StartupXYZ | 2018 - 2020
- Developed full-stack web applications using Django and React
- Designed and implemented RESTful APIs
- Worked with PostgreSQL and Redis for data storage
- Collaborated in Agile development environment
"""
    
    job_description = """
Senior Full Stack Developer Position

We are seeking a highly skilled Senior Full Stack Developer to join our dynamic team. 
The ideal candidate will have extensive experience in modern web development technologies 
and a passion for creating scalable, high-performance applications.

Required Skills:
- 5+ years of experience in full-stack development
- Proficiency in JavaScript, TypeScript, Python, and SQL
- Strong experience with React, Node.js, Express framework
- Database experience with PostgreSQL, MongoDB, and Redis
- Cloud platform experience, preferably AWS
- Experience with Docker, Kubernetes, and containerization
- Knowledge of CI/CD pipelines and DevOps practices
- Understanding of Agile/Scrum methodologies
- Strong problem-solving and communication skills

Preferred Qualifications:
- Experience with microservices architecture
- Knowledge of Jenkins, Git, and version control
- Experience mentoring junior developers
- Bachelor's degree in Computer Science or related field
"""
    
    # Prepare the multipart form data
    files = {
        'resume': ('test_resume.txt', BytesIO(resume_content.encode()), 'text/plain')
    }
    data = {
        'job_description': job_description
    }
    
    response = requests.post(f"{BASE_URL}/analyze", files=files, data=data, cookies=cookies)
    assert response.status_code == 200
    
    result = response.json()
    assert result['success'] == True
    assert 'analysis' in result
    assert result['saved'] == True  # Should be saved since user is authenticated
    
    analysis = result['analysis']
    assert 'composite_score' in analysis
    assert 'similarity_score' in analysis
    assert 'skill_match_score' in analysis
    assert 'recommendations' in analysis
    
    print(f"✅ Resume analysis passed")
    print(f"   📊 Overall Match: {analysis['composite_score']:.1f}%")
    print(f"   📊 Content Similarity: {analysis['similarity_score']:.1f}%") 
    print(f"   📊 Skill Match: {analysis['skill_match_score']:.1f}%")
    
    return result

def test_analysis_history(cookies):
    """Test getting analysis history"""
    print("🔍 Testing analysis history...")
    response = requests.get(f"{BASE_URL}/history", cookies=cookies)
    assert response.status_code == 200
    
    data = response.json()
    assert 'analyses' in data
    assert len(data['analyses']) > 0  # Should have at least one analysis from previous test
    
    print(f"✅ Analysis history passed - Found {len(data['analyses'])} analyses")

def test_user_resumes(cookies):
    """Test getting user resumes"""
    print("🔍 Testing user resumes...")
    response = requests.get(f"{BASE_URL}/resumes", cookies=cookies)
    assert response.status_code == 200
    
    data = response.json()
    assert data['success'] == True
    assert 'resumes' in data
    assert len(data['resumes']) > 0  # Should have at least one resume
    
    print(f"✅ User resumes passed - Found {len(data['resumes'])} resumes")

def run_all_tests():
    """Run all tests in sequence"""
    print("🚀 Starting comprehensive test suite for AI Resume Analyzer")
    print("=" * 60)
    
    try:
        # Test basic functionality
        test_health_check()
        
        # Test authentication
        registration_cookies = test_user_registration()
        login_cookies = test_user_login()
        test_profile_access(login_cookies)
        
        # Test core functionality
        analysis_result = test_resume_analysis(login_cookies)
        test_analysis_history(login_cookies)
        test_user_resumes(login_cookies)
        
        print("\n" + "=" * 60)
        print("🎉 ALL TESTS PASSED! The AI Resume Analyzer is fully functional!")
        print("=" * 60)
        
        print("\n📋 Test Summary:")
        print("✅ Health check endpoint")
        print("✅ User registration")
        print("✅ User login")
        print("✅ Authenticated profile access")
        print("✅ Resume analysis with database saving")
        print("✅ Analysis history retrieval")
        print("✅ User resume management")
        
        print(f"\n📊 Sample Analysis Results:")
        if 'analysis' in analysis_result:
            analysis = analysis_result['analysis']
            print(f"   • Overall Match: {analysis['composite_score']:.1f}%")
            print(f"   • Content Similarity: {analysis['similarity_score']:.1f}%")
            print(f"   • Skill Match: {analysis['skill_match_score']:.1f}%")
            print(f"   • Recommendations: {len(analysis['recommendations'])} suggestions")
        
        return True
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        return False
    except Exception as e:
        print(f"\n💥 UNEXPECTED ERROR: {e}")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)

