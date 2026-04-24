from cryptography.fernet import Fernet
import os

# Encryption key for sensitive data (should be stored securely in production)
FERNET_KEY = os.environ.get('FERNET_KEY', Fernet.generate_key())
fernet = Fernet(FERNET_KEY)

def encrypt_data(data):
    if data is None:
        return None
    return fernet.encrypt(data.encode()).decode()

def decrypt_data(token):
    if token is None:
        return None
    return fernet.decrypt(token.encode()).decode()

from datetime import datetime
try:
    from web_auth.database import db
except ModuleNotFoundError:
    from database import db

class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(500), nullable=False)
    status = db.Column(db.String(50), default='pending')  # pending, running, completed, failed
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    owner = db.relationship('User', backref='jobs')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    _result_path = db.Column('result_path', db.String(500))  # Encrypted
    _log = db.Column('log', db.Text)  # Encrypted

    @property
    def result_path(self):
        return decrypt_data(self._result_path) if self._result_path else None

    @result_path.setter
    def result_path(self, value):
        self._result_path = encrypt_data(value) if value else None

    @property
    def log(self):
        return decrypt_data(self._log) if self._log else None

    @log.setter
    def log(self, value):
        self._log = encrypt_data(value) if value else None

    def __repr__(self):
        return f'<Job {self.id} {self.url} {self.status}>'
