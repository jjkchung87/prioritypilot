from . import User, Task, db, ForeignKey

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
    