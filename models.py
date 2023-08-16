from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_bcrypt import Bcrypt
from sqlalchemy import ForeignKey, ForeignKeyConstraint, event, func
from sqlalchemy.orm import validates
import random
import string

db = SQLAlchemy()
def connect_db(app):
    db.app = app
    db.init_app(app)

bcrypt = Bcrypt()

DEFAULT_URL = 'https://hips.hearstapps.com/hmg-prod/images/gettyimages-1226623221.jpg'
DEFAULT_GOLFER_URL = "https://png.pngtree.com/png-clipart/20210915/ourmid/pngtree-user-avatar-placeholder-black-png-image_3918427.jpg"


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
    
    @validates('username')
    def convert_to_lowercase(self, key, value):
        """first line of defence to convert usernamename to lowercase"""
        return value.lower()
   
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
    
    def update_password(self, old_password, new_password):
        """update to new password"""

        if self.authenticate(self.username, old_password):
            hashed_new_pw = bcrypt.generate_password_hash(new_password)
            hashed_new_pw_utf8 = hashed_new_pw.decode("utf8")
            self.password = hashed_new_pw_utf8
            db.session.commit()
        
        return False

    def get_available_public_leagues(self):
        """Returns a list of available public leagues for this user"""

        user_league_ids = [league.id for league in self.leagues]

        return (
            db.session.query(League.id, League.league_name)
            .join(League.users)  # Join with users to get available leagues
            .group_by(League.id, League.league_name)
            .having(func.count(User.id) < League.max_teams)
            .filter(League.privacy == "public")
            .filter(League.draft_completed == False)
            .filter(~League.id.in_(user_league_ids))  # Filter out leagues where user is already a part
            .all()
        )

    
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


        lower_username = username.lower()
        user = User.query.filter_by(username=username).first()
        if user and bcrypt.check_password_hash(user.password, password):
            return user
        else:
            return False
        
@event.listens_for(User, 'before_insert')
def convert_username_to_lowercase(mapper, connection, target):
    target.username = target.username.lower()    

class League (db.Model):
    """League model"""

    __tablename__ = "leagues"

    id = db.Column(db.Integer,
                   primary_key=True)
    
    league_name = db.Column(db.String,
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
    
    draft_pick_index = db.Column(db.Integer, default=0)

    draft_pick_count = db.Column(db.Integer, default=0)
    
    teams = db.relationship("Team", backref="leagues")

    golfers = db.relationship("Golfer", secondary="league_golfers", backref="leagues")
    
    @validates('league_name')
    def convert_to_lowercase(self, key, value):
        """first line of defence to convert league name to lowercase"""
        return value.lower()


    @property
    def status(self):
        """Property to get status of league"""
        return self.get_status()
    
    @property
    def draft_order(self):
        """Property to get the draft order of the league"""
        return self.get_draft_order()
    

    def __repr__(self):
        """Better representation of League model"""
        return f"<League #{self.id} {self.league_name}>"
    
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
            "draft_completed": self.draft_completed,
            "draft_pick_index": self.draft_pick_index,
            "draft_pick_count": self.draft_pick_count,
            "teams": [team.serialize() for team in self.teams],
            "golfers": [golfer.serialize() for golfer in self.golfers],
            "draft_order": self.draft_order
        }
    
    
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

    def get_draft_order(self):
        """Get draft order of league"""
        return [team.id for team in self.teams]
    
    def join_validation(self,user):
        """validation to join league"""

        if self.status in ('in-play', 'end-play', 'in-draft'):
            success = False
            msg = 'Too late to join league.'
            return {'success':success, 'msg':msg}

        if self.max_teams <= len(self.users):
            success = False
            msg = 'Maximum capacity reached in this league.'
            return {'success':success, 'msg':msg}

        if self in user.leagues:
            success = False
            msg = 'You are already part of this league!'
            return {'success':success, 'msg':msg}
        
        else:
            success = True
            user.leagues.append(self)
            db.session.commit()
            msg = f"Welcome to {self.league_name}"
            return {'success':success, 'msg':msg}


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

@event.listens_for(League, 'before_insert')
def convert_league_name_to_lowercase(mapper, connection, target):
    """Second line of defence to convert league_name to lowercase"""
    target.league_name = target.league_name.lower()



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

    @validates('team_name')
    def convert_to_lowercase(self, key, value):
        """first line of defence to convert team name to lowercase"""
        return value.lower()
    
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
        """Add golfer to the team and related league"""
  
        golfer = Golfer.query.get(golfer_id)
        league = League.query.get(self.league_id)

        if golfer in self.golfers:
            # Scenario 1: Golfer is already on the team
            raise ValueError("Golfer is already on this team")
        
        if golfer in league.golfers:
            # Scenario 2: Golfer is already on another team in the same league
            raise ValueError("Golfer is already on another team in the same league")

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

@event.listens_for(Team, 'before_insert')
def convert_team_name_to_lowercase(mapper, connection, target):
    target.team_name = target.team_name.lower()    


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
    
    owgr = db.Column(db.Integer)
    
    golfer_image_url = db.Column(db.Text,
                                 nullable=False,
                                 default=DEFAULT_GOLFER_URL)
    
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
            "last_name": self.last_name,
            "owgr": self.owgr,
            "golfer_image_url": self.golfer_image_url
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
        """Better representation of UserLeague"""
        return f"<UserLeague #{self.id} {self.user_id} {self.league_id}>"
    


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
