from flask_sqlalchemy import SQLAlchemy
from enum import Enum as EnumBase
from sqlalchemy import Enum
from datetime import datetime
from sqlalchemy import ForeignKey, ForeignKeyConstraint, event, func
from sqlalchemy.orm import validates
from flask_bcrypt import Bcrypt
import random
import string
import json

db = SQLAlchemy()

def connect_db(app):
    db.app = app
    db.init_app(app)

bcrypt = Bcrypt()

#*****************************************************************************************************************************************************************************************************************************************************************************
# USER

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
    
    department_id = db.Column(db.Integer, 
                        db.ForeignKey ('departments.id'),
                        nullable=False)
    
    role = db.Column(db.Text,
                           nullable=False)
    
    password = db.Column(db.Text,
                         nullable=False)
    
    date_joined = db.Column(db.DateTime,
                            default=datetime.utcnow)

    profile_img = db.Column(db.Text,
                            default=DEFAULT_URL)
    
    manager_id = db.Column(db.Integer, ForeignKey('users.id'))
    
    department = db.relationship('Department', backref="users")
    
    projects = db.relationship('Project', secondary="users_projects", backref="users")
    
    tasks = db.relationship('Task', secondary="users_tasks", backref="users")

    conversations = db.relationship('Conversation', backref="users")
    
    subordinates = db.relationship('User', backref=db.backref('manager', remote_side=[id]))

    # meetings = db.relationship("Meeting", secondary="users_meetings", backref="users")

    @property
    def subordinate_ids(self):
        """Return a list of user IDs for subordinates"""
        if self.subordinates:
            return [subordinate.id for subordinate in self.subordinates]
        else:
            return []
        
    def __repr__(self):
        """better representation of obect"""
        return f"<User #{self.id} {self.first_name} {self.last_name} {self.role} {self.department}>"
    
    def serialize(self):
        """Serialize user to Python object"""

        return {
            "id": self.id,
            "email": self.email,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "department_id": self.department_id,
            "role": self.role,
            "profile_img": self.profile_img,
            "subordinate_ids": self.subordinate_ids,
            "projects": [project.serialize() for project in self.projects]
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
    def signup(cls, email, first_name, last_name, department_name, role, password, profile_img=DEFAULT_URL, manager_id=None):
        """Sign up a new user with password hashing"""

        hashed = bcrypt.generate_password_hash(password)
        hashed_utf8 = hashed.decode("utf8")
        department = Department.query.filter_by(name=department_name).first()

        if not department:
            department = Department(name=department_name)
            db.session.add(department)
            db.session.commit()

        user = User( 
            email=email,
            password=hashed_utf8,
            first_name=first_name,
            last_name=last_name,
            department_id=department.id,
            role=role,
            profile_img=profile_img,
            manager_id=manager_id)
        
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

    

#*****************************************************************************************************************************************************************************************************************************************************************************
# Department

class Department (db.Model):
    """Department model"""

    __tablename__ = "departments"

    id = db.Column(db.Integer,
                   primary_key=True)
    
    name = db.Column(db.String,
                            nullable=False,
                            unique=True)
    
    created_at = db.Column(db.DateTime,
                           default=datetime.utcnow)
        

    # @validates('name')
    # def convert_to_lowercase(self, key, value):
    #     """first line of defence to convert department name to lowercase"""
    #     return value.lower()
    
    def __repr__(self):
        """Better representation of department model"""
        return f"<Department #{self.id} {self.name}>"
    
    def serialize(self):
        """Serialize department to Python object"""

        return {
            "id": self.id,
            "name": self.name,
            "users": [user.serialize() for user in self.users]
        }
    
#*****************************************************************************************************************************************************************************************************************************************************************************
# PROJECT


# class Status(EnumBase):
#     NOT_STARTED = 'Not Started'
#     IN_PROGRESS = 'In Progress'
#     COMPLETE = 'Complete'
#     DELAYED = 'Delayed'


class Project (db.Model):
    """Project model"""

    __tablename__ = "projects"

    id = db.Column(db.Integer,
                   primary_key=True)
    
    project_name = db.Column(db.String,
                            nullable=False,
                            unique=True)

    description = db.Column(db.String,
                            nullable=True,
                            unique=False)
    
    created_at = db.Column(db.DateTime,
                           nullable=False,
                           default=datetime.utcnow)
    
    modified_at = db.Column(db.DateTime,
                            nullable=False,
                            default=datetime.utcnow)

    # start_date = db.Column(db.DateTime,
    #                        nullable=False)

    end_date = db.Column(db.DateTime,
                           nullable=False)
    
    _valid_statuses = {'Not Started', 'In Progress', 'Complete', 'Delayed'}

    status = db.Column(db.String, nullable=False, default='Not Started')

    user_id = db.Column(db.Integer, 
                        db.ForeignKey ('users.id'),
                        nullable=False)
    
    tasks = db.relationship("Task", backref="project", cascade="all, delete-orphan")

    conversations = db.relationship("Conversation", backref="project", cascade="all, delete-orphan")

    

    @validates('status')
    def validate_status(self, key, value):
        if value not in self._valid_statuses:
            raise ValueError(f"Invalid status: {value}. Valid options are: {', '.join(self._valid_statuses)}")
        return value

    @property
    def user_ids(self):
        """Return a list of user IDs for users on project"""
        if self.users:
            return [user.id for user in self.users]
        else:
            return []

    def __repr__(self):
        """Better representation of project model"""
        return f"<Project #{self.id} {self.project_name}>"
    
    def serialize(self):
        """Serialize project to Python object"""

        return {
            "id": self.id,
            "project_name": self.project_name,
            "description": self.description,
            "created_at": self.created_at,
            "end_date": self.end_date,
            "user_id": self.user_id,
            "status": self.status,
            "user_ids": self.user_ids,
            "tasks": [task.serialize() for task in self.tasks]
        }
    

    @classmethod
    def create_new_project(cls, project_name, description, end_date, user_id):
        """create a new project and create """

        project = Project(project_name=project_name,
                          description=description,
                        #   start_date=start_date, 
                          end_date=end_date,
                          user_id=user_id
                          )
        user = User.query.get(user_id)
        project.users.append(user)
        db.session.add(project)
        db.session.commit()
        return project
    

# @event.listens_for(Project, 'before_insert')
# def convert_project_name_to_lowercase(mapper, connection, target):
#     """Second line of defence to convert project_name to lowercase"""
#     target.project_name = target.project_name.lower()

#*****************************************************************************************************************************************************************************************************************************************************************************
# TASK

class Task (db.Model):
    """Task model"""

    __tablename__ = "tasks"

    id = db.Column(db.Integer,
                   primary_key=True)
    
    task_name = db.Column(db.String,
                            nullable=False,
                            unique=False)

    description = db.Column(db.String,
                            nullable=True,
                            unique=False)

    notes = db.Column(db.String,
                            nullable=True,
                            unique=False)
    
    _valid_types = {'task','meeting'}

    type = db.Column(db.String, nullable=False, default='task')
    
    _valid_statuses = {'Not Started', 'In Progress', 'Complete', 'Delayed'}

    status = db.Column(db.String, nullable=False, default='Not Started')

    _valid_priorities = {'Low','Medium','High'}

    priority = db.Column(db.String, nullable=False, default='Medium')
    
    created_at = db.Column(db.DateTime,
                           nullable=False,
                           default=datetime.utcnow)
    
    modified_at = db.Column(db.DateTime,
                            nullable=False,
                            default=datetime.utcnow)
    
    end_date = db.Column(db.DateTime,
                           nullable=False)
    
    user_id = db.Column(db.Integer, 
                        db.ForeignKey ('users.id'),
                        nullable=False)
    
    meeting_user_id = db.Column(db.Integer, #if type is "Meeting", this indicates who the meeting is with.
                        db.ForeignKey ('users.id'),
                        nullable=True)

    project_id = db.Column(db.Integer, 
                        db.ForeignKey ('projects.id'),
                        nullable=False)    

    # users = db.relationship("Users", secondary="users_tasks", backref="tasks")

    @property
    def user_ids(self):
        """Return a list of user IDs for users on task"""
        if self.users:
            return [user.id for user in self.users]
        else:
            return []

    @validates('type')
    def validate_type(self, key, value):
        if value not in self._valid_types:
            raise ValueError(f"Invalid type: {value}. Valid options are: {', '.join(self._valid_types)}")
        return value
    
    @validates('status')
    def validate_status(self, key, value):
        if value not in self._valid_statuses:
            raise ValueError(f"Invalid status: {value}. Valid options are: {', '.join(self._valid_statuses)}")
        return value

    @validates('priority')
    def validate_priority(self, key, value):
        if value not in self._valid_priorities:
            raise ValueError(f"Invalid priority: {value}. Valid options are: {', '.join(self._valid_priorities)}")
        return value

    def __repr__(self):
        """Better representation of task model"""
        return f"<Task #{self.id} {self.task_name}>"
    
    def serialize(self):
        """Serialize task to Python object"""

        project = Project.query.get(self.project_id)
        project_name = project.project_name

        return {
            "id": self.id,
            "task_name": self.task_name,
            "description": self.description,
            "notes": self.notes,
            "type": self.type,
            "priority": self.priority,
            "status": self.status,
            "created_at": self.created_at,
            "modified_at": self.modified_at,
            "end_date": self.end_date,
            "user_id": self.user_id,
            "meeting_user_id": self.meeting_user_id,
            "project_id": self.project_id,
            "project_name": project_name,
            "user_ids": self.user_ids
        }
    

    @classmethod
    def create_new_task(cls, 
                        task_name, 
                        description, 
                        notes, 
                        type, 
                        priority, 
                        status, 
                        end_date, 
                        user_id, 
                        meeting_user_id, 
                        project_id, 
                        users=[]):
        """create a new task and create """

        task = Task(task_name=task_name,
                          description=description,
                          notes=notes,
                          type=type,
                          priority=priority,
                          status=status,
                          end_date=end_date,
                          user_id=user_id,
                          meeting_user_id=meeting_user_id,
                          project_id=project_id,
                          )
        user = User.query.get(user_id)
        task.users.append(user)
        task.users.extend(users)
        project = Project.query.get(project_id)
        project.users.append(user)
        project.users.extend(users)
        db.session.add(task)
        db.session.commit()
        return task
    

    
#*****************************************************************************************************************************************************************************************************************************************************************************
# CONVERSATION


class Conversation(db.Model):
    """Conversation model"""

    __tablename__ = "conversations"

    id = db.Column(db.Integer,
                   primary_key=True)
    
    user_id = db.Column(db.Integer, 
                        db.ForeignKey ('users.id'),
                        nullable=False)

    _valid_conversation_types = {'New Project','Assistance'}

    conversation_type = db.Column(db.String, nullable=False, default='New Project')
    
    task_id = db.Column(db.Integer, 
                        db.ForeignKey ('tasks.id'),
                        nullable=True)

    project_id = db.Column(db.Integer, 
                        db.ForeignKey ('projects.id'),
                        nullable=False)

    messages = db.Column(db.JSON, nullable=True)

    created_at = db.Column(db.DateTime,
                           default=datetime.utcnow)
    
    modified_at = db.Column(db.DateTime,
                            default=datetime.utcnow)
    
    def __repr__(self):
        """Better representation of Conversation model"""
        return f"<Conversation #{self.id} {self.messages}>"
    
    def set_messages(self, messages):
        """Serialize and store messages"""
        
        if self.messages:
            current_messages = json.loads(self.messages)
            current_messages.append(messages)
            self.messages = json.dumps(current_messages)

        else:
            self.messages = json.dumps(messages)

        db.session.commit()

    def get_messages(self):
        """Retrieve messages and turn into Python list of objects"""

        if self.messages:
            return json.loads(self.messages)
        return []



    # def serialize(self):
    #     """Serialize conversation to Python object"""

    #     return {
    #         "id": self.id,
    #         "user_id": self.user_id,
    #         "type": self.type,
    #         "task_id": self.task_id,
    #         "project_id": self.project_id,
    #         "messsages": self.messages,
    #         "created_at": self.created_at,
    #         "modified_at": self.modified_at
    #     }
    
    @validates('conversation_type')
    def validate_conversation_type(self, key, value):
        if value not in self._valid_conversation_types:
            raise ValueError(f"Invalid conversation_type: {value}. Valid options are: {', '.join(self._valid_conversation_types)}")
        return value


    @classmethod
    def create_new_conversation(cls, 
                                user_id,
                                conversation_type,
                                task_id,
                                project_id
                                ):
        """create a new conversation """

        conversation = Conversation(user_id=user_id,
                                    conversation_type=conversation_type,
                                    task_id=task_id,
                                    project_id=project_id,
                                    )
        user = User.query.get(user_id)
        conversation.users.append(user)
        db.session.add(conversation)
        db.session.commit()
        return conversation
    
#*****************************************************************************************************************************************************************************************************************************************************************************
# USERPROJECT

class UserProject(db.Model):
    """User and Project Association"""

    __tablename__= "users_projects"

    id = db.Column(db.Integer,
                primary_key=True)

    user_id = db.Column(db.Integer,
                        db.ForeignKey('users.id', ondelete='cascade'))
    
    project_id = db.Column(db.Integer,
                          db.ForeignKey('projects.id', ondelete='cascade'))
    
    def __repr__(self):
        """Better representation of UserProject"""
        return f"<UserProject #{self.id} {self.user_id} {self.project_id}>"

#*****************************************************************************************************************************************************************************************************************************************************************************
# USERTASK

class UserTask(db.Model):
    """User and Task Association"""

    __tablename__= "users_tasks"

    id = db.Column(db.Integer,
                primary_key=True)

    user_id = db.Column(db.Integer,
                        db.ForeignKey('users.id', ondelete='cascade'))
    
    task_id = db.Column(db.Integer,
                          db.ForeignKey('tasks.id', ondelete='cascade'))
    
    def __repr__(self):
        """Better representation of UserTask"""
        return f"<UserTask #{self.id} {self.user_id} {self.task_id}>"

#*****************************************************************************************************************************************************************************************************************************************************************************
# MEETING


# class Meeting (db.Model):
#     """Meeting model"""

#     __tablename__ = "meetings"

#     id = db.Column(db.Integer,
#                    primary_key=True,
#                    unique=True)
    
#     task_id = db.Column(db.Integer, 
#                         db.ForeignKey ('tasks.id'),
#                         nullable=False)    
    
#     project_id = db.Column(db.Integer, 
#                         db.ForeignKey ('projects.id'),
#                         nullable=False)    

#     subject = db.Column(db.String,
#                             nullable=True,
#                             unique=False)

#     notes = db.Column(db.String,
#                             nullable=True,
#                             unique=False)
        
#     created_at = db.Column(db.DateTime,
#                            default=datetime.utcnow)
    
#     modified_at = db.Column(db.DateTime,
#                             default=datetime.utcnow)
    
#     start_date_time = db.Column(db.DateTime,
#                            nullable=False)

#     end_date_time = db.Column(db.DateTime,
#                            nullable=False)
    
#     user_id = db.Column(db.Integer, nullable=False)


 

#     def __repr__(self):
#         """Better representation of meeting model"""
#         return f"<Meeting #{self.id} {self.subject}>"
    
#     def serialize(self):
#         """Serialize meeting to Python object"""

#         return {
#             "id": self.id,
#             "task_id": self.task_id,
#             "project_id": self.project_id,
#             "subject": self.subject,
#             "notes": self.notes,
#             "created_at": self.created_at,
#             "modified_at": self.modified_at,
#             "start_date_time": self.start_date_time,
#             "end_date_time": self.end_date_time,
#             "user_id": self.user_id,
#         }
    

#     @classmethod
#     def create_new_meeting(cls, 
#                            task_id, 
#                            project_id, 
#                            subject, 
#                            notes, 
#                            created_at, 
#                            modified_at, 
#                            start_date_time, 
#                            end_date_time, 
#                            user_id, 
#                            invited_user_ids):
#         """create a new meeting """

#         meeting = Meeting(task_id=task_id,
#                           project_id=project_id,
#                           subject=subject,
#                           notes=notes,
#                           created_at=created_at,
#                           modified_at=modified_at,
#                           start_date_time=start_date_time, 
#                           end_date_time=end_date_time,
#                           user_id=user_id
#                           )
        
#         user = User.query.get(user_id)
#         meeting.users.append(user)
        
#         for invited_user_id in invited_user_ids:
#             u = User.query.get(invited_user_id)
#             meeting.users.append(u)

#         db.session.add(meeting)
#         db.session.commit()
#         return meeting



#*****************************************************************************************************************************************************************************************************************************************************************************
# # USERMEETING

# class UserMeeting(db.Model):
#     """User and Meeting Association"""

#     __tablename__= "users_meetings"

#     id = db.Column(db.Integer,
#                 primary_key=True)

#     user_id = db.Column(db.Integer,
#                         db.ForeignKey('users.id', ondelete='cascade'))
    
#     meeting_id = db.Column(db.Integer,
#                           db.ForeignKey('meetings.id', ondelete='cascade'))
    
#     def __repr__(self):
#         """Better representation of UserMeeting"""
#         return f"<UserMeeting #{self.id} {self.user_id} {self.meeting_id}>"
    