from . import db, validates, datetime, event, EnumBase, Enum, User

class Status(EnumBase):
    NOT_STARTED = 'Not Started'
    IN_PROGRESS = 'In Progress'
    COMPLETE = 'Complete'
    DELAYED = 'Delayed'


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

    start_date = db.Column(db.DateTime,
                           nullable=False)

    end_date = db.Column(db.DateTime,
                           nullable=False)
    
    status = db.Column(Enum(Status), nullable=False, default=Status.NOT_STARTED)
    

    user_id = db.Column(db.Integer, 
                        db.ForeignKey ('users.id'),
                        nullable=False)
    
    tasks = db.relationship("Task", backref="project", cascade="all, delete-orphan")

    # users = db.relationship("Users", secondary="users_projects", backref="projects")
    
    @validates('project_name')
    def convert_to_lowercase(self, key, value):
        """first line of defence to convert project name to lowercase"""
        return value.lower()


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
            "start_date": self.start_date,
            "end_date": self.end_date,
            "user_id": self.user_id,
            "status": self.status,
            "tasks": [task.serialize() for task in self.tasks],
            "users": [user.serialize() for user in self.users]
        }
    

    @classmethod
    def create_new_project(cls, project_name, description, start_date, end_date, user_id):
        """create a new project and create """

        project = Project(project_name=project_name,
                          description=description,
                          start_date=start_date, 
                          end_date=end_date,
                          user_id=user_id
                          )
        user = User.query.get(user_id)
        project.users.append(user)
        db.session.add(project)
        db.session.commit()
        return project
    

@event.listens_for(Project, 'before_insert')
def convert_project_name_to_lowercase(mapper, connection, target):
    """Second line of defence to convert project_name to lowercase"""
    target.project_name = target.project_name.lower()

