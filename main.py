import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS
from flask_login import LoginManager
from flask_migrate import Migrate
from datetime import timedelta

# Import our models and routes
from src.models import db, User
from src.routes.analyzer import analyzer_bp
from src.routes.auth import auth_bp

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))

# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'asdf#FGSgvasgf$5$WGT')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'resume_analyzer.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)

# Initialize extensions
db.init_app(app)
migrate = Migrate(app, db)

# Setup CORS with credentials support
CORS(app, supports_credentials=True, origins=['http://localhost:5173', 'http://127.0.0.1:5173'])

# Setup Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Please log in to access this page.'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Register blueprints
app.register_blueprint(analyzer_bp, url_prefix='/api')
app.register_blueprint(auth_bp, url_prefix='/api/auth')

# Create database directory if it doesn't exist
os.makedirs(os.path.join(os.path.dirname(__file__), 'database'), exist_ok=True)

# Create database tables
with app.app_context():
    db.create_all()

# Health check endpoint
@app.route('/api/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'message': 'Resume Analyzer API is running',
        'version': '1.0.0'
    })

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
        return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "index.html not found", 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

