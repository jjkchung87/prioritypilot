from . import User, Meeting, db, ForeignKey

class UserMeeting(db.Model):
    """User and Meeting Association"""

    __tablename__= "users_meetings"

    id = db.Column(db.Integer,
                primary_key=True)

    user_id = db.Column(db.Integer,
                        db.ForeignKey('users.id', ondelete='cascade'))
    
    meeting_id = db.Column(db.Integer,
                          db.ForeignKey('meetings.id', ondelete='cascade'))
    
    def __repr__(self):
        """Better representation of UserMeeting"""
        return f"<UserMeeting #{self.id} {self.user_id} {self.meeting_id}>"
    