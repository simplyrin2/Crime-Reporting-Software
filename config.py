import os

config = {
    'SECRET_KEY': os.environ.get('SECRET'),
    'DATABASE_URI': 'sqlite:///database.db',
    'ADMIN_USERNAME': 'police123',
    'ADMIN_PASSWORD': 'police123@#$'
}