from . import db, EnumBase, Bcrypt, func, validates, event, datetime  # Import db from the models package

# from flask_sqlalchemy import SQLAlchemy
# from datetime import datetime
# from flask_bcrypt import Bcrypt
# from sqlalchemy import ForeignKey, ForeignKeyConstraint, event, func
# from sqlalchemy.orm import validates
# import random
# import string


bcrypt = Bcrypt()

DEFAULT_URL = 'https://hips.hearstapps.com/hmg-prod/images/gettyimages-1226623221.jpg'


class User(db.Model):
    """User model"""

    __tablename__ = "users"

    id = db.Column(db.Integer,
                   primary_key=True)
    
    email = db.Column(db.Text,
                      unique=True,
                      nullable=False)
    
    first_name = db.Column(db.Text,
                           nullable=False)

    last_name = db.Column(db.Text,
                           nullable=False)
    
    team_id = db.Column(db.Integer, 
                        db.ForeignKey ('teams.id'),
                        nullable=False)
    
    role = db.Column(db.Text,
                           nullable=False)
    
    password = db.Column(db.Text,
                         nullable=False)
    
    date_joined = db.Column(db.DateTime,
                            default=datetime.utcnow)

    profile_img = db.Column(db.Text,
                            default=DEFAULT_URL)
    
    team = db.relationship('Team', backref="users")
    
    projects = db.relationship('Project', secondary="users_projects", backref="users")
    
    tasks = db.relationship('Task', secondary="users_tasks", backref="users")

    conversations = db.relationship('Conversation', backref="users")

    meetings = db.relationship("Meeting", secondary="users_meetings", backref="users")


    def __repr__(self):
        """better representation of obect"""
        return f"<User #{self.id} {self.first_name} {self.last_name} {self.role} {self.team}>"
    
    def serialize(self):
        """Serialize user to Python object"""

        return {
            "id": self.id,
            "email": self.email,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "team_id": self.team_id,
            "role": self.role,
            "projects": [project.serialize() for project in self.projects],
            "tasks": [task.serialize() for task in self.tasks]
        }
    
    def update_password(self, old_password, new_password):
        """update to new password"""

        if self.authenticate(self.username, old_password):
            hashed_new_pw = bcrypt.generate_password_hash(new_password)
            hashed_new_pw_utf8 = hashed_new_pw.decode("utf8")
            self.password = hashed_new_pw_utf8
            db.session.commit()
        
        return False

    
    @classmethod
    def signup(cls, email, first_name, last_name, team_id, role, password, profile_img=DEFAULT_URL):
        """Sign up a new user with password hashing"""

        hashed = bcrypt.generate_password_hash(password)
        hashed_utf8 = hashed.decode("utf8")

        user = User( 
            email=email,
            password=hashed_utf8,
            first_name=first_name,
            last_name=last_name,
            team_id=team_id,
            role=role,
            profile_img=profile_img)
        
        db.session.add(user)
        db.session.commit()
        return user

    @classmethod
    def authenticate(cls, email, password):
        """Authenticate user against hashed password"""

        user = User.query.filter_by(email=email).first()
        if user and bcrypt.check_password_hash(user.password, password):
            return user
        else:
            return False
         
