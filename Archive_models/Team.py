from . import db, EnumBase, Bcrypt, func, validates, event, datetime  # Import db from the models package



class Team (db.Model):
    """Team model"""

    __tablename__ = "teams"

    id = db.Column(db.Integer,
                   primary_key=True)
    
    name = db.Column(db.String,
                            nullable=False,
                            unique=True)
    
    created_at = db.Column(db.DateTime,
                           default=datetime.utcnow)
        

    @validates('name')
    def convert_to_lowercase(self, key, value):
        """first line of defence to convert team name to lowercase"""
        return value.lower()
    
    def __repr__(self):
        """Better representation of team model"""
        return f"<Team #{self.id} {self.name}>"
    
    def serialize(self):
        """Serialize team to Python object"""

        return {
            "id": self.id,
            "name": self.name,
            "users": [user.serialize() for user in self.users]
        }
    

    # @classmethod
    # def create_new_team(cls, team_name, start_date, end_date, privacy, max_teams, golfer_count, team_manager_id, draft_completed):
    #     """create a new team and create """

    #     def generate_entry_code():
    #         characters = string.digits + string.ascii_uppercase
    #         return ''.join(random.choices(characters, k=6))

    #     entry_code = generate_entry_code()

    #     team = team(team_name=team_name, 
    #                     entry_code=entry_code, 
    #                     privacy=privacy, 
    #                     max_teams=max_teams, 
    #                     golfer_count=golfer_count,
    #                     team_manager_id=team_manager_id,
    #                     draft_completed=draft_completed, 
    #                     start_date=start_date, 
    #                     end_date=end_date)
    #     user = User.query.get(team_manager_id)
    #     team.users.append(user)
    #     db.session.add(team)
    #     db.session.commit()
    #     return team
    
    # @classmethod
    # def authenticate(cls, team_name, entry_code):
    #     """authentication to see/join a private team"""

    #     team = team.query.filter(team.team_name == team_name, team.entry_code == entry_code).first()

    #     if team:
    #         return team
        
    #     else:
    #         return False

