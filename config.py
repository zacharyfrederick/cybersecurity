import os
basedir = os.path.join(os.path.dirname(__file__))
upload_dir = os.path.join(basedir, 'uploads/images')

class Config(object):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = False
    PEPPER = 'TEST'
    SECRET_KEY = '123'
    UPLOAD_FOLDER = upload_dir
    ALLOWED_EXTENSIONS = ['png', 'jpg', 'jpeg']

