from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_bcrypt import Bcrypt
from sqlalchemy import ForeignKey, ForeignKeyConstraint

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

    leagues = db.relationship('League', secondary="league_teams", backref="users")
    golfers = db.relationship('Golfer', secondary="user_golfers", backref="users")
    
    def __repr__(self):
        """better representation of obect"""
        return f"<User #{self.id} {self.username}"
    
    @classmethod
    def signup(cls, username, email, first_name, last_name, password, profile_url):
        """Sign up a new user with password hashing"""

        hashed = bcrypt.generate_password_hash(password)
        hashed_utf8 = hashed.decode("utf8")

        return cls(username=username, 
                   email=email,
                   password=hashed_utf8,
                   first_name=first_name,
                   last_name=last_name,
                   profile_url=profile_url)

    def authenticate(cls, username, password):
        """Authenticate user against hashed password"""

        user = cls.query.filter_by(username=username).first()
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
    
    created_at = db.Column(db.DateTime,
                           default=datetime.utcnow)
    
    start_date = db.Column(db.DateTime,
                           nullable=False)

    end_date = db.Column(db.DateTime,
                           nullable=False)
    
    teams = db.relationship("Team", secondary="league_teams", backref="leagues")
    
    def __repr__(self):
        """Better representation of League model"""
        return f"<League #{self.id} {self.league_name}"
    

class Team (db.Model):
    """Team model"""

    __tablename__ = "teams"

    id = db.Column(db.Integer,
                   primary_key=True)
    
    team_name = db.Column(db.String(30),
                            nullable=False,
                            unique=True)
    
    user_id = db.Column(db.Integer,
                        db.ForeignKey('users.id', ondelete='cascade'))
    
    created_at = db.Column(db.DateTime,
                           default=datetime.utcnow)
    
    golfers = db.relationship('Golfer',secondary="team_golfers", backref="teams")
    
    def __repr__(self):
        """Better representation of Team model"""
        return f"<League #{self.id} {self.team_name} {self.user_id}"
    
    

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
        return f"<Golfer #{self.id} {self.first_name} {self.last_name}"
    
    
    
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
        db.UniqueConstraint("tournament_name","calendar_year","date", name="uq_tournament_name_calendar_year_date"),
    )


    
    def __repr__(self):
        """Better representation of tournaments"""
        return f"<Tournament #{self.id} {self.first_name} {self.last_name}"
    
    
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
        return f"<UserGolfer #{self.id} {self.user_id} {self.golfer_id}"

class LeagueTeam(db.Model):
    """League and Team association"""

    __tablename__  = "league_teams"

    id = db.Column(db.Integer,
                primary_key=True)

    league_id = db.Column(db.Integer,
                        db.ForeignKey('leagues.id', ondelete='cascade'))
        
    team_id = db.Column(db.Integer,
                        db.ForeignKey('teams.id', ondelete='cascade'))
    
    team_score = db.Column(db.Integer)

    user_id = db.Column(db.Integer,
                        db.ForeignKey('users.id', ondelete='cascade'))

    def __repr__(self):
        """Better representation of LeagueTeam"""
        return f"<LeagueTeam #{self.id} {self.league_id} {self.team_id} {self.team_score}"
        
    
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
        return f"<TeamGolfer #{self.id} {self.team_id} {self.golfer_id} {self.golfer_score}"
    

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
    date = db.Column(db.DateTime)


    # Add other fields for the association as needed
    round = db.Column(db.Integer)
    golfer_score = db.Column(db.Integer)

    # Add the golfer_dg_id as well
    golfer_dg_id = db.Column(db.Integer, ForeignKey('golfers.dg_id', ondelete='CASCADE'))

    # Define a unique constraint to ensure golfer_id and golfer_dg_id always match
    __table_args__ = (
        db.UniqueConstraint("golfer_id", "golfer_dg_id", name="uq_tournament_golfer_golfer_id_dg_id"),
        db.ForeignKeyConstraint(["tournament_name","calendar_year","date"], ["tournaments.tournament_name","tournaments.calendar_year","tournaments.date"], ondelete="CASCADE"),
    )

    def __repr__(self):
        """Better representation of TournamentGolfer"""
        return f"<TournamentGolfer #{self.id} {self.tournament_id} {self.tournament_name} {self.calendar_year} {self.date} {self.golfer_id} {self.golfer_dg_id} {self.golfer_score}"
