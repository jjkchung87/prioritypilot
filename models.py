from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_bcrypt import Bcrypt
from sqlalchemy import ForeignKey, ForeignKeyConstraint
import random
import string

db = SQLAlchemy()
def connect_db(app):
    db.app = app
    db.init_app(app)

bcrypt = Bcrypt()

DEFAULT_URL = 'https://hips.hearstapps.com/hmg-prod/images/gettyimages-1226623221.jpg'


class User(db.Model):
    """User model"""

    __tablename__ = "users"

    id = db.Column(db.Integer,
                   primary_key=True)
    
    username = db.Column(db.String(15),
                         unique=True,
                         nullable=False)
    
    email = db.Column(db.Text,
                      unique=True,
                      nullable=False)
    
    first_name = db.Column(db.Text,
                           nullable=False)

    last_name = db.Column(db.Text,
                           nullable=False)
    
    password = db.Column(db.Text,
                         nullable=False)
    
    date_joined = db.Column(db.DateTime,
                            default=datetime.utcnow)

    profile_url = db.Column(db.Text,
                            default=DEFAULT_URL)
    
    teams = db.relationship('Team', backref="users")

    leagues = db.relationship('League', secondary="user_leagues", backref="users")
    # golfers = db.relationship('Golfer', secondary="user_golfers", backref="users")
    
    def __repr__(self):
        """better representation of obect"""
        return f"<User #{self.id} {self.username}>"
    
    def serialize(self):
        """Serialize user to Python object"""

        return {
            "id": self.id,
            "username": self.username,
            "leagues": [league.serialize() for league in self.leagues],
            "teams": [team.serialize() for team in self.teams]
        }
    
    @classmethod
    def signup(cls, username, email, first_name, last_name, password, profile_url=DEFAULT_URL):
        """Sign up a new user with password hashing"""

        hashed = bcrypt.generate_password_hash(password)
        hashed_utf8 = hashed.decode("utf8")

        user = User(username=username, 
            email=email,
            password=hashed_utf8,
            first_name=first_name,
            last_name=last_name,
            profile_url=profile_url)
        
        db.session.add(user)
        db.session.commit()
        return user

    @classmethod
    def authenticate(cls, username, password):
        """Authenticate user against hashed password"""

        user = User.query.filter_by(username=username).first()
        if user and bcrypt.check_password_hash(user.password, password):
            return user
        else:
            return False
    

class League (db.Model):
    """League model"""

    __tablename__ = "leagues"

    id = db.Column(db.Integer,
                   primary_key=True)
    
    league_name = db.Column(db.String(30),
                            nullable=False,
                            unique=True)
    
    entry_code = db.Column(db.Text,
                           nullable=False)
    
    privacy = db.Column(db.Text,nullable=False)

    max_teams = db.Column(db.Integer)

    golfer_count = db.Column(db.Integer)  
    
    created_at = db.Column(db.DateTime,
                           default=datetime.utcnow)
    
    start_date = db.Column(db.DateTime,
                           nullable=False)

    end_date = db.Column(db.DateTime,
                           nullable=False)
    
    league_manager_id = db.Column(db.Integer, nullable=False)
    
    draft_completed = db.Column(db.Boolean,
                                nullable=False,
                                default=False)
    
    teams = db.relationship("Team", backref="leagues")

    golfers = db.relationship("Golfer", secondary="league_golfers", backref="leagues")
    
    @property
    def status(self):
        """Property to get status of league"""
        return self.get_status()

    def __repr__(self):
        """Better representation of League model"""
        return f"<League #{self.id} {self.league_name}>"
    
    
    def get_status(self):
        """Get status of league"""

        current_date = datetime.utcnow()

        if self.draft_completed:
            if current_date <= self.end_date:
                return "in-play"
            
            if current_date > self.end_date:
                return "end-play"

        if current_date < self.start_date:
            return "pre-draft"
    
        if self.start_date <= current_date <= self.end_date:
            if self.draft_completed:
                return "in-play"
            else:
                return "in-draft"

        if current_date > self.end_date:
            return "end-play"

    def serialize(self):
        """Serialize league to Python object"""

        return {
            "id": self.id,
            "league_name": self.league_name,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "privacy": self.privacy,
            "max_teams": self.max_teams,
            "golfer_count": self.golfer_count,
            "teams": [team.serialize() for team in self.teams],
            "golfers": [golfer.serialize() for golfer in self.golfers]
        }
    
    @classmethod
    def create_new_league(cls, league_name, start_date, end_date, privacy, max_teams, golfer_count, league_manager_id, draft_completed):
        """create a new league and create """

        def generate_entry_code():
            characters = string.digits + string.ascii_uppercase
            return ''.join(random.choices(characters, k=6))

        entry_code = generate_entry_code()

        league = League(league_name=league_name, 
                        entry_code=entry_code, 
                        privacy=privacy, 
                        max_teams=max_teams, 
                        golfer_count=golfer_count,
                        league_manager_id=league_manager_id,
                        draft_completed=draft_completed, 
                        start_date=start_date, 
                        end_date=end_date)
        user = User.query.get(league_manager_id)
        league.users.append(user)
        db.session.add(league)
        db.session.commit()
        return league
    
    @classmethod
    def authenticate(cls, league_name, entry_code):
        """authentication to see/join a private league"""

        league = League.query.filter(League.league_name == league_name, League.entry_code == entry_code).first()

        if league:
            return league
        
        else:
            return False

class Team (db.Model):
    """Team model"""

    __tablename__ = "teams"

    id = db.Column(db.Integer,
                   primary_key=True)
    
    team_name = db.Column(db.Text,
                            nullable=False,
                            unique=True)
    
    user_id = db.Column(db.Integer,
                        db.ForeignKey('users.id', ondelete="cascade"))
    
    league_id = db.Column(db.Integer,
                          db.ForeignKey('leagues.id', ondelete="cascade"))
    
    created_at = db.Column(db.DateTime,
                           default=datetime.utcnow)
    
    golfers = db.relationship('Golfer',secondary="team_golfers", backref="teams")

    
    def __repr__(self):
        """Better representation of Team model"""
        return f"<Team #{self.id} {self.team_name} {self.user_id}>"
    
    def serialize(self):
        """Serialize team to Python object"""

        return {
            "id": self.id,
            "team_name": self.team_name,
            "user_id": self.user_id,
            "league_id": self.league_id,            
            "golfers": [golfer.serialize() for golfer in self.golfers]
        }
    
    def add_golfer(self, golfer_id):
        """Add golfer on the team and related league"""

        golfer = Golfer.query.get(golfer_id)
        league = League.query.get(self.league_id)
        
        self.golfers.append(golfer)
        league.golfers.append(golfer)
        
        db.session.commit()

    def remove_golfer(self, golfer_id):
        """Remove a golfer on the team and related league"""

        golfer = Golfer.query.get(golfer_id)
        league = League.query.get(self.league_id)        
        
        self.golfers.remove(golfer)
        league.golfers.remove(golfer)
        
        db.session.commit()


class Golfer (db.Model):
    """Golfer model"""

    __tablename__ = "golfers"

    id = db.Column(db.Integer,
                   primary_key=True)
    
    dg_id = db.Column(db.Integer,
                       unique=True,
                       nullable=False)
    
    first_name = db.Column(db.Text,
                           nullable=False)
    
    last_name = db.Column(db.Text,
                           nullable=False)
    
    __table_args__ = (db.UniqueConstraint("id", "dg_id", name="uq_golfer_id_dg_id"),)
    
    tournaments = db.relationship("Tournament",
                                  secondary="tournament_golfers",
                                  backref="golfers",
                                  primaryjoin="and_(Golfer.id == TournamentGolfer.golfer_id, Golfer.dg_id == TournamentGolfer.golfer_dg_id)",
                                  secondaryjoin="Tournament.id == TournamentGolfer.tournament_id")

    def __repr__(self):
        """Better representation of golfer"""
        return f"<Golfer #{self.id} dg_id:{self.dg_id} {self.first_name} {self.last_name}>"
    
    def serialize(self):
        """Serialize golfer to Python object"""

        return {
            "id": self.id,
            "dg_id": self.dg_id,
            "first_name": self.first_name,
            "last_name": self.last_name
        }
    
class Tournament (db.Model):
    """Tournament model"""

    __tablename__ = "tournaments"

    id = db.Column(db.Integer,
                   primary_key=True)
    
    dg_id = db.Column(db.Integer, nullable=False)
    
    tournament_name = db.Column(db.Text,
                           nullable=False)
    
    calendar_year = db.Column(db.Integer)
    
    date = db.Column(db.DateTime,
                           nullable=False)
    tour = db.Column(db.Text)

    __table_args__ = (
        db.UniqueConstraint("tournament_name","calendar_year","dg_id", name="uq_tournament_name_calendar_year_dg_id"),
    )

    def __repr__(self):
        """Better representation of tournaments"""
        return f"<Tournament #{self.id} dg_id:{self.dg_id} {self.tournament_name} {self.calendar_year} {self.date} {self.tour}>"
    
    def serialize(self):
        """Serialize tournament to Python object"""
        return {
            "id": self.id,
            "tournament_name": self.tournament_name,
            "calendar_year": self.calendar_year,
            "date": self.date,
            "tour": self.tour
        }    
    

class UserLeague(db.Model):
    """User and League Association"""

    __tablename__= "user_leagues"

    id = db.Column(db.Integer,
                primary_key=True)

    user_id = db.Column(db.Integer,
                        db.ForeignKey('users.id', ondelete='cascade'))
    
    league_id = db.Column(db.Integer,
                          db.ForeignKey('leagues.id', ondelete='cascade'))
    
    def __repr__(self):
        """Better representation of UserGolfer"""
        return f"<UserLeague #{self.id} {self.user_id} {self.league_id}>"
    

class UserGolfer(db.Model):
    """User and Golfer associationn"""

    __tablename__= "user_golfers"

    id = db.Column(db.Integer,
                primary_key=True)

    user_id = db.Column(db.Integer,
                        db.ForeignKey('users.id', ondelete='cascade'))
    
    golfer_id = db.Column(db.Integer,
                          db.ForeignKey('golfers.id', ondelete='cascade'))
    
    def __repr__(self):
        """Better representation of UserGolfer"""
        return f"<UserGolfer #{self.id} {self.user_id} {self.golfer_id}>"
    


# class LeagueTeam(db.Model):
#     """League and Team association"""

#     __tablename__  = "league_teams"

#     id = db.Column(db.Integer,
#                 primary_key=True)

#     league_id = db.Column(db.Integer,
#                         db.ForeignKey('leagues.id', ondelete='cascade'))
        
#     team_id = db.Column(db.Integer,
#                         db.ForeignKey('teams.id', ondelete='cascade'))
    
#     team_score = db.Column(db.Integer)

#     user_id = db.Column(db.Integer,
#                         db.ForeignKey('users.id', ondelete='cascade'))

#     def __repr__(self):
#         """Better representation of LeagueTeam"""
#         return f"<LeagueTeam #{self.id} {self.league_id} {self.team_id} {self.team_score}>"
        
    
class TeamGolfer(db.Model):
    """Team and Golfer association"""

    __tablename__  = "team_golfers"

    id = db.Column(db.Integer,
                primary_key=True)

    team_id = db.Column(db.Integer,
                        db.ForeignKey('teams.id', ondelete='cascade'))
    
    golfer_id = db.Column(db.Integer,
                        db.ForeignKey('golfers.id', ondelete='cascade'))
    
    golfer_score = db.Column(db.Integer)

    def __repr__(self):
        """Better representation of TeamGolfer"""
        return f"<TeamGolfer #{self.id} {self.team_id} {self.golfer_id} {self.golfer_score}>"

class LeagueGolfer(db.Model):
    """League and Golfer association"""

    __tablename__  = "league_golfers"

    id = db.Column(db.Integer,
                primary_key=True)

    league_id = db.Column(db.Integer,
                        db.ForeignKey('leagues.id', ondelete='cascade'))
    
    golfer_id = db.Column(db.Integer,
                        db.ForeignKey('golfers.id', ondelete='cascade'))
    
    golfer_score = db.Column(db.Integer)

    def __repr__(self):
        """Better representation of LeagueGolfer"""
        return f"<LeagueGolfer #{self.id} {self.league_id} {self.golfer_id} {self.golfer_score}>"
    

class TournamentGolfer(db.Model):
    """Tournament and Golfer association model"""

    __tablename__ = "tournament_golfers"

    id = db.Column(db.Integer, primary_key=True)

    # Define the local IDs as foreign keys with ondelete='CASCADE'
    tournament_id = db.Column(db.Integer, ForeignKey('tournaments.id', ondelete='CASCADE'))
    golfer_id = db.Column(db.Integer, ForeignKey('golfers.id', ondelete='CASCADE'))

    # Define the external IDs as foreign keys with ondelete='CASCADE'
    tournament_name = db.Column(db.Text)
    calendar_year = db.Column(db.Integer)
    tournament_dg_id = db.Column(db.Integer)


    # Add other fields for the association as needed
    round = db.Column(db.Integer)
    course_par = db.Column(db.Integer)
    score_vs_par = db.Column(db.Integer)
    golfer_score = db.Column(db.Integer)

    # Add the golfer_dg_id as well
    golfer_dg_id = db.Column(db.Integer, ForeignKey('golfers.dg_id', ondelete='CASCADE'))

    # Define a unique constraint to ensure golfer_id and golfer_dg_id always match
    __table_args__ = (
        # db.UniqueConstraint("golfer_id", "golfer_dg_id", name="uq_tournament_golfer_golfer_id_dg_id"),
        db.ForeignKeyConstraint(["tournament_name","calendar_year","tournament_dg_id"], ["tournaments.tournament_name","tournaments.calendar_year","tournaments.dg_id"], ondelete="CASCADE"),
    )

    def __repr__(self):
        """Better representation of TournamentGolfer"""
        return f"<TournamentGolfer #{self.id} {self.tournament_id} {self.tournament_name} {self.calendar_year} {self.tournament_dg_id} {self.golfer_id} {self.golfer_dg_id} {self.golfer_score}>"
