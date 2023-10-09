from . import User, Project, db, ForeignKey

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
    