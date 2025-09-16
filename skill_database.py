"""
Comprehensive skill database for resume analysis
"""

# Extended skill categories with more comprehensive lists
SKILL_DATABASE = {
    'programming_languages': {
        'keywords': ['python', 'java', 'javascript', 'c++', 'c#', 'php', 'ruby', 'go', 'rust', 'swift', 
                    'kotlin', 'typescript', 'scala', 'r', 'matlab', 'perl', 'shell', 'bash', 'powershell',
                    'objective-c', 'dart', 'elixir', 'haskell', 'clojure', 'f#', 'vb.net', 'cobol', 'fortran'],
        'weight': 1.5  # Higher weight for programming languages
    },
    
    'web_technologies': {
        'keywords': ['html', 'css', 'react', 'angular', 'vue', 'node.js', 'express', 'django', 'flask',
                    'spring', 'bootstrap', 'jquery', 'sass', 'less', 'webpack', 'babel', 'next.js',
                    'nuxt.js', 'svelte', 'ember.js', 'backbone.js', 'meteor', 'gatsby', 'strapi',
                    'fastapi', 'laravel', 'symfony', 'codeigniter', 'rails', 'sinatra'],
        'weight': 1.3
    },
    
    'databases': {
        'keywords': ['mysql', 'postgresql', 'mongodb', 'redis', 'sqlite', 'oracle', 'sql server',
                    'cassandra', 'elasticsearch', 'dynamodb', 'couchdb', 'neo4j', 'influxdb',
                    'mariadb', 'firestore', 'cosmos db', 'aurora', 'bigquery', 'snowflake'],
        'weight': 1.4
    },
    
    'cloud_platforms': {
        'keywords': ['aws', 'azure', 'google cloud', 'gcp', 'docker', 'kubernetes', 'terraform',
                    'jenkins', 'gitlab ci', 'github actions', 'circleci', 'travis ci', 'ansible',
                    'puppet', 'chef', 'vagrant', 'helm', 'istio', 'prometheus', 'grafana',
                    'cloudformation', 'pulumi', 'serverless', 'lambda', 'cloud functions'],
        'weight': 1.4
    },
    
    'data_science': {
        'keywords': ['machine learning', 'deep learning', 'tensorflow', 'pytorch', 'pandas', 'numpy',
                    'scikit-learn', 'tableau', 'power bi', 'jupyter', 'anaconda', 'spark', 'hadoop',
                    'kafka', 'airflow', 'mlflow', 'kubeflow', 'dask', 'plotly', 'seaborn',
                    'matplotlib', 'opencv', 'nltk', 'spacy', 'transformers', 'bert', 'gpt'],
        'weight': 1.5
    },
    
    'mobile_development': {
        'keywords': ['ios', 'android', 'react native', 'flutter', 'xamarin', 'ionic', 'cordova',
                    'swift', 'kotlin', 'objective-c', 'java', 'dart', 'unity', 'unreal engine'],
        'weight': 1.3
    },
    
    'testing': {
        'keywords': ['unit testing', 'integration testing', 'selenium', 'cypress', 'jest', 'mocha',
                    'pytest', 'junit', 'testng', 'cucumber', 'postman', 'newman', 'k6', 'jmeter',
                    'appium', 'detox', 'enzyme', 'testing library'],
        'weight': 1.2
    },
    
    'version_control': {
        'keywords': ['git', 'github', 'gitlab', 'bitbucket', 'svn', 'mercurial', 'perforce',
                    'git flow', 'github flow', 'pull request', 'merge request', 'code review'],
        'weight': 1.1
    },
    
    'soft_skills': {
        'keywords': ['leadership', 'communication', 'teamwork', 'problem solving', 'project management',
                    'agile', 'scrum', 'kanban', 'mentoring', 'collaboration', 'analytical thinking',
                    'creativity', 'adaptability', 'time management', 'critical thinking', 'innovation'],
        'weight': 1.0
    },
    
    'methodologies': {
        'keywords': ['agile', 'scrum', 'kanban', 'waterfall', 'lean', 'devops', 'ci/cd', 'tdd',
                    'bdd', 'ddd', 'microservices', 'monolith', 'event-driven', 'rest', 'graphql',
                    'soap', 'grpc', 'oauth', 'jwt', 'saml'],
        'weight': 1.2
    },
    
    'security': {
        'keywords': ['cybersecurity', 'penetration testing', 'vulnerability assessment', 'owasp',
                    'ssl', 'tls', 'encryption', 'authentication', 'authorization', 'firewall',
                    'vpn', 'ids', 'ips', 'siem', 'compliance', 'gdpr', 'hipaa', 'sox'],
        'weight': 1.4
    }
}

# Industry-specific skill mappings
INDUSTRY_SKILLS = {
    'software_engineering': ['programming_languages', 'web_technologies', 'databases', 'version_control', 'testing'],
    'data_science': ['data_science', 'programming_languages', 'databases', 'cloud_platforms'],
    'devops': ['cloud_platforms', 'version_control', 'methodologies', 'security'],
    'mobile_development': ['mobile_development', 'programming_languages', 'version_control'],
    'cybersecurity': ['security', 'programming_languages', 'cloud_platforms', 'methodologies'],
    'web_development': ['web_technologies', 'programming_languages', 'databases', 'version_control']
}

# Common job titles and their associated skill categories
JOB_TITLE_SKILLS = {
    'software engineer': 'software_engineering',
    'full stack developer': 'web_development',
    'frontend developer': 'web_development',
    'backend developer': 'software_engineering',
    'data scientist': 'data_science',
    'data analyst': 'data_science',
    'machine learning engineer': 'data_science',
    'devops engineer': 'devops',
    'cloud engineer': 'devops',
    'mobile developer': 'mobile_development',
    'ios developer': 'mobile_development',
    'android developer': 'mobile_development',
    'security engineer': 'cybersecurity',
    'cybersecurity analyst': 'cybersecurity'
}

def get_relevant_skills_for_job(job_description):
    """
    Determine which skill categories are most relevant for a given job description
    """
    job_desc_lower = job_description.lower()
    relevant_categories = set()
    
    # Check for job titles
    for title, category in JOB_TITLE_SKILLS.items():
        if title in job_desc_lower:
            if category in INDUSTRY_SKILLS:
                relevant_categories.update(INDUSTRY_SKILLS[category])
    
    # If no specific job title found, include all categories but with different weights
    if not relevant_categories:
        relevant_categories = set(SKILL_DATABASE.keys())
    
    return list(relevant_categories)

def get_skill_weight(category):
    """Get the weight for a skill category"""
    return SKILL_DATABASE.get(category, {}).get('weight', 1.0)

def get_all_skills_flat():
    """Get all skills as a flat list for general matching"""
    all_skills = []
    for category_data in SKILL_DATABASE.values():
        all_skills.extend(category_data['keywords'])
    return all_skills

