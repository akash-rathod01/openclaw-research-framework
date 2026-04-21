from celery import Celery
import os

# Celery configuration
celery_app = Celery(
    'agentic_rnd_tool',
    broker=os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/0'),
    backend=os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')
)

@celery_app.task
def run_scraping_job(job_id, url):
    # Import here to avoid circular import
    from web_auth.app import db
    from web_auth.job_model import Job
    from datetime import datetime
    import subprocess
    job = Job.query.get(job_id)
    if not job:
        return 'Job not found'
    job.status = 'running'
    db.session.commit()
    try:
        result = subprocess.run([
            'python',
            os.path.abspath(os.path.join(os.path.dirname(__file__), '../orchestrator.py')),
            url,
            '--max-sources', '10'
        ], capture_output=True, text=True, timeout=600)
        job.log = (result.stdout or '') + '\n' + (result.stderr or '')
        reports_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../reports'))
        report_files = [f for f in os.listdir(reports_dir) if f.startswith('report_') and f.endswith('.html')]
        if report_files:
            latest_report = max(report_files, key=lambda f: os.path.getctime(os.path.join(reports_dir, f)))
            job.result_path = f'/reports/{latest_report}'
        job.status = 'completed' if result.returncode == 0 else 'failed'
    except Exception as e:
        job.status = 'failed'
        job.result_path = None
        job.log = str(e)
    job.updated_at = datetime.utcnow()
    db.session.commit()
    return job.status
