from . import db, EnumBase, Enum, validates, datetime, event, User, Project  # Import db from the models package


class Priority(EnumBase):
    LOW = 'Low'
    MODERATE = 'Moderate'
    HIGH = 'High'

class Status(EnumBase):
    NOT_STARTED = 'Not Started'
    IN_PROGRESS = 'In Progress'
    COMPLETE = 'Complete'
    DELAYED = 'Delayed'

class Type(EnumBase):
    TASK = 'Task'
    MEETING = 'Meeting'

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
    
    type = db.Column(Enum(Type), nullable=False)
    
    priority = db.Column(Enum(Priority), nullable=False, default=Priority.MODERATE)
    
    status = db.Column(Enum(Status), nullable=False, default=Status.NOT_STARTED)
    
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
    
    user_id = db.Column(db.Integer, 
                        db.ForeignKey ('users.id'),
                        nullable=False)

    project_id = db.Column(db.Integer, 
                        db.ForeignKey ('projects.id'),
                        nullable=False)    

    # users = db.relationship("Users", secondary="users_tasks", backref="tasks")


    @validates('task_name')
    def convert_to_lowercase(self, key, value):
        """first line of defence to convert task name to lowercase"""
        return value.lower()


    def __repr__(self):
        """Better representation of task model"""
        return f"<Task #{self.id} {self.task_name}>"
    
    def serialize(self):
        """Serialize task to Python object"""

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
            "start_date": self.start_date,
            "end_date": self.end_date,
            "user_id": self.user_id,
            "project_id": self.project_id,
            "users": [user.serialize() for user in self.users]
        }
    

    @classmethod
    def create_new_task(cls, task_name, description, notes, type, priority, status, start_date, end_date, user_id, project_id):
        """create a new task and create """

        task = Task(task_name=task_name,
                          description=description,
                          notes=notes,
                          type=type,
                          priority=priority,
                          status=status,
                          start_date=start_date, 
                          end_date=end_date,
                          user_id=user_id,
                          project_id=project_id
                          )
        user = User.query.get(user_id)
        task.users.append(user)
        db.session.add(task)
        db.session.commit()
        return task
    

@event.listens_for(Task, 'before_insert')
def convert_task_name_to_lowercase(mapper, connection, target):
    """Second line of defence to convert task_name to lowercase"""
    target.task_name = target.task_name.lower()

