from . import db, EnumBase, datetime, User


class Meeting (db.Model):
    """Meeting model"""

    __tablename__ = "meetings"

    id = db.Column(db.Integer,
                   primary_key=True,
                   unique=True)
    
    task_id = db.Column(db.Integer, 
                        db.ForeignKey ('tasks.id'),
                        nullable=False)    
    
    project_id = db.Column(db.Integer, 
                        db.ForeignKey ('projects.id'),
                        nullable=False)    

    subject = db.Column(db.String,
                            nullable=True,
                            unique=False)

    notes = db.Column(db.String,
                            nullable=True,
                            unique=False)
        
    created_at = db.Column(db.DateTime,
                           default=datetime.utcnow)
    
    modified_at = db.Column(db.DateTime,
                            default=datetime.utcnow)
    
    start_date_time = db.Column(db.DateTime,
                           nullable=False)

    end_date_time = db.Column(db.DateTime,
                           nullable=False)
    
    user_id = db.Column(db.Integer, nullable=False)


 

    def __repr__(self):
        """Better representation of meeting model"""
        return f"<Meeting #{self.id} {self.subject}>"
    
    def serialize(self):
        """Serialize meeting to Python object"""

        return {
            "id": self.id,
            "task_id": self.task_id,
            "project_id": self.project_id,
            "subject": self.subject,
            "notes": self.notes,
            "created_at": self.created_at,
            "modified_at": self.modified_at,
            "start_date_time": self.start_date_time,
            "end_date_time": self.end_date_time,
            "user_id": self.user_id,
            "users": [user.serialize() for user in self.users]
        }
    

    @classmethod
    def create_new_meeting(cls, 
                           task_id, 
                           project_id, 
                           subject, 
                           notes, 
                           created_at, 
                           modified_at, 
                           start_date_time, 
                           end_date_time, 
                           user_id, 
                           invited_user_ids):
        """create a new meeting """

        meeting = Meeting(task_id=task_id,
                          project_id=project_id,
                          subject=subject,
                          notes=notes,
                          created_at=created_at,
                          modified_at=modified_at,
                          start_date_time=start_date_time, 
                          end_date_time=end_date_time,
                          user_id=user_id
                          )
        
        user = User.query.get(user_id)
        meeting.users.append(user)
        
        for invited_user_id in invited_user_ids:
            u = User.query.get(invited_user_id)
            meeting.users.append(u)

        db.session.add(meeting)
        db.session.commit()
        return meeting
    