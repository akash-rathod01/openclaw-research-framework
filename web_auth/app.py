"""
Flask Web Application with Authentication and Job Management
Provides user authentication, role-based access control, and job scheduling with Celery
"""
import os
from datetime import datetime
from functools import wraps

from flask import Flask, render_template, redirect, url_for, request, flash, jsonify, make_response
from flask_login import LoginManager, login_user, login_required, logout_user, UserMixin, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from markupsafe import escape

try:
    from web_auth.database import db
except ModuleNotFoundError:
    from database import db

# ============================================================================
# Flask App Initialization
# ============================================================================
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'replace-this-with-a-secure-key')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# API authentication token
API_TOKEN = os.environ.get('API_TOKEN', 'changeme')

# ============================================================================
# Database Models
# ============================================================================
class User(UserMixin, db.Model):
    """User model with role-based access control"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(50), default='user')  # admin, user, viewer

    def __repr__(self):
        return f'<User {self.username} ({self.role})>'

# ============================================================================
# Authentication and Authorization
# ============================================================================
@login_manager.user_loader
def load_user(user_id):
    """Load user by ID for Flask-Login"""
    return User.query.get(int(user_id))

def api_auth_required(f):
    """Decorator for API token authentication"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('X-API-Token')
        if not token or token != API_TOKEN:
            return make_response(jsonify({'error': 'Unauthorized'}), 401)
        return f(*args, **kwargs)
    return decorated

# ============================================================================
# Public Routes
# ============================================================================
@app.route('/')
def index():
    """Home page"""
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if request.method == 'POST':
        username = escape(request.form['username'])
        password = escape(request.form['password'])
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists')
            return redirect(url_for('register'))
        
        hashed_pw = generate_password_hash(password)
        new_user = User(username=username, password=hashed_pw)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful! Please log in.')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if request.method == 'POST':
        username = escape(request.form['username'])
        password = escape(request.form['password'])
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        
        flash('Invalid credentials')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    """User logout"""
    logout_user()
    return redirect(url_for('login'))

# ============================================================================
# Protected User Routes
# ============================================================================
@app.route('/dashboard')
@login_required
def dashboard():
    """User dashboard"""
    return render_template('dashboard.html', user=current_user)

@app.route('/skills')
@login_required
def skills():
    """Skills dashboard"""
    try:
        from web_auth.skill_loader import discover_skills
    except ModuleNotFoundError:
        from skill_loader import discover_skills
    skills_list = discover_skills()
    return render_template('skills.html', skills=skills_list, user=current_user)

# ============================================================================
# Job Management Routes
# ============================================================================
@app.route('/job_dashboard')
@login_required
def job_dashboard():
    """Job management dashboard"""
    try:
        from web_auth.job_model import Job
    except ModuleNotFoundError:
        from job_model import Job
    jobs = Job.query.order_by(Job.created_at.desc()).all()
    return render_template('job_dashboard.html', jobs=jobs, user=current_user)

@app.route('/start_job', methods=['POST'])
@login_required
def start_job():
    """Start a new scraping job (admin/user only)"""
    try:
        from web_auth.job_model import Job
        from web_auth.celery_worker import run_scraping_job
    except ModuleNotFoundError:
        from job_model import Job 
        from celery_worker import run_scraping_job
    
    if current_user.role not in ['admin', 'user']:
        flash('Access denied: Only admin/user can start jobs.')
        return redirect(url_for('job_dashboard'))
    
    url = escape(request.form['url'])
    job = Job(url=url, status='pending', owner_id=current_user.id)
    db.session.add(job)
    db.session.commit()
    
    # Schedule job with Celery
    run_scraping_job.delay(job.id, url)
    flash('Job scheduled and will run in the background!')
    return redirect(url_for('job_dashboard'))

@app.route('/view_log/<int:job_id>')
@login_required
def view_log(job_id):
    """View job log"""
    try:
        from web_auth.job_model import Job
    except ModuleNotFoundError:
        from job_model import Job
    job = Job.query.get(job_id)
    
    if not job or (job.owner_id != current_user.id and current_user.role != 'admin'):
        flash('Access denied or job not found.')
        return redirect(url_for('job_dashboard'))
    
    return render_template('view_log.html', job=job, user=current_user)

@app.route('/stop_job/<int:job_id>', methods=['POST'])
@login_required
def stop_job(job_id):
    """Stop a running job (admin/user only)"""
    try:
        from web_auth.job_model import Job
    except ModuleNotFoundError:
        from job_model import Job
    
    if current_user.role not in ['admin', 'user']:
        flash('Access denied: Only admin/user can stop jobs.')
        return redirect(url_for('job_dashboard'))
    
    job = Job.query.get(job_id)
    if job and job.status in ['pending', 'running']:
        job.status = 'stopped'
        job.updated_at = datetime.utcnow()
        db.session.commit()
        flash('Job stopped.')
    
    return redirect(url_for('job_dashboard'))

@app.route('/delete_job/<int:job_id>', methods=['POST'])
@login_required
def delete_job(job_id):
    """Delete a job (admin/user only)"""
    try:
        from web_auth.job_model import Job
    except ModuleNotFoundError:
        from job_model import Job
    
    if current_user.role not in ['admin', 'user']:
        flash('Access denied: Only admin/user can delete jobs.')
        return redirect(url_for('job_dashboard'))
    
    job = Job.query.get(job_id)
    if job:
        db.session.delete(job)
        db.session.commit()
        flash('Job deleted.')
    
    return redirect(url_for('job_dashboard'))

# ============================================================================
# Admin Routes
# ============================================================================
@app.route('/user_management')
@login_required
def user_management():
    """User management page (admin only)"""
    if current_user.role != 'admin':
        flash('Access denied: Admins only.')
        return redirect(url_for('dashboard'))
    
    users = User.query.all()
    return render_template('user_management.html', users=users)

@app.route('/change_role/<int:user_id>', methods=['POST'])
@login_required
def change_role(user_id):
    """Change user role (admin only)"""
    if current_user.role != 'admin':
        flash('Access denied: Admins only.')
        return redirect(url_for('dashboard'))
    
    user = User.query.get(user_id)
    if user:
        new_role = escape(request.form['role'])
        user.role = new_role
        db.session.commit()
        flash(f'Role updated for {user.username} to {new_role}')
    
    return redirect(url_for('user_management'))

# ============================================================================
# API Routes
# ============================================================================
@app.route('/api/jobs', methods=['GET'])
@api_auth_required
def api_list_jobs():
    """API: List all jobs"""
    try:
        from web_auth.job_model import Job
    except ModuleNotFoundError:
        from job_model import Job
    jobs = Job.query.order_by(Job.created_at.desc()).all()
    
    return jsonify([
        {
            'id': job.id,
            'url': job.url,
            'status': job.status,
            'owner_id': job.owner_id,
            'created_at': job.created_at.isoformat() if job.created_at else None,
            'updated_at': job.updated_at.isoformat() if job.updated_at else None,
            'result': job.result
        } for job in jobs
    ])

@app.route('/api/jobs', methods=['POST'])
@api_auth_required
def api_start_job():
    """API: Start a new job"""
    try:
        from web_auth.job_model import Job
        from web_auth.celery_worker import run_scraping_job
    except ModuleNotFoundError:
        from job_model import Job
        from celery_worker import run_scraping_job
    
    data = request.get_json()
    url = escape(data.get('url', ''))
    
    if not url:
        return make_response(jsonify({'error': 'Missing url'}), 400)
    
    job = Job(url=url, status='pending', owner_id=None)
    db.session.add(job)
    db.session.commit()
    
    run_scraping_job.delay(job.id, url)
    return jsonify({'message': 'Job scheduled', 'job_id': job.id}), 201

@app.route('/api/jobs/<int:job_id>', methods=['GET'])
@api_auth_required
def api_get_job(job_id):
    """API: Get job details"""
    try:
        from web_auth.job_model import Job
    except ModuleNotFoundError:
        from job_model import Job
    job = Job.query.get(job_id)
    
    if not job:
        return make_response(jsonify({'error': 'Job not found'}), 404)
    
    return jsonify({
        'id': job.id,
        'url': job.url,
        'status': job.status,
        'owner_id': job.owner_id,
        'created_at': job.created_at.isoformat() if job.created_at else None,
        'updated_at': job.updated_at.isoformat() if job.updated_at else None,
        'result': job.result,
        'log': getattr(job, 'log', None)
    })

@app.route('/api/skills', methods=['GET'])
@api_auth_required
def api_list_skills():
    """API: List available skills"""
    try:
        from web_auth.skill_loader import discover_skills
    except ModuleNotFoundError:
        from skill_loader import discover_skills
    skills_list = discover_skills()
    return jsonify([{'name': s['name']} for s in skills_list])

# ============================================================================
# Application Entry Point
# ============================================================================
if __name__ == '__main__':
    with app.app_context():
        if not os.path.exists('users.db'):
            db.create_all()
            print("Database created successfully!")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
