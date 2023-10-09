from .. import db, EnumBase, Enum, validates, datetime, event, json, User  # Import db from the models package


class Type(EnumBase):
    NEW_PROJECT = 'New Project'
    ASSISTANCE = 'Assistance'

class Conversation(db.Model):
    """Conversation model"""

    __tablename__ = "conversations"

    id = db.Column(db.Integer,
                   primary_key=True)
    
    user_id = db.Column(db.Integer, 
                        db.ForeignKey ('users.id'),
                        nullable=False)

    type = db.Column(Enum(Type), nullable=False)
    
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
    

    @classmethod
    def create_new_conversation(cls, 
                                user_id,
                                type,
                                task_id,
                                project_id
                                ):
        """create a new conversation """

        conversation = Conversation(user_id=user_id,
                                    type=type,
                                    task_id=task_id,
                                    project_id=project_id,
                                    )
        user = User.query.get(user_id)
        conversation.users.append(user)
        db.session.add(conversation)
        db.session.commit()
        return conversation
    
