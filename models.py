from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
def connect_db(app):
    db.app = app
    db.init_app(app)



class User(db.Model):
    """user class"""

    
