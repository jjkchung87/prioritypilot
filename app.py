import os

from flask import Flask, render_template, request, flash, redirect, session, g, jsonify
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError
import requests
from models import db, connect_db, User, League, Team, Golfer, Tournament, UserGolfer, LeagueTeam, TeamGolfer, TournamentGolfer

app = Flask(__name__)

# Get DB_URI from environ variable (useful for production/testing) or,
# if not set there, use development local db.
app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ.get('DATABASE_URL', 'postgresql:///golf_fantasy'))

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['EXPLAIN_TEMPLATE_LOADING'] = True
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "it's a secret")
app.debug=True
toolbar = DebugToolbarExtension(app)
app.app_context().push()
connect_db(app)

CURR_USER_KEY = "curent user"

@app.before_request
def add_user_to_g():
    """If we're logged in, add curr user to Flask global "g". Used to manage user auth and access control throughout application"""

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])

    else:
        g.user = None


def do_login(user):
    """Log in user."""

    session[CURR_USER_KEY] = user.id


def do_logout():
    """Logout user."""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]




@app.route("/golfantasy")
def show_homepage():
    """Show homepage"""

    return render_template("home.html")

#*******************************************************************************************************************************
#API End-points:

@app.route("/golfantasy/api/users/signup", methods=["POST"])
def signup_endpoint():
    """Endpoint for new user sign up"""
    username = request.json["username"]
    first_name = request.json["first_name"]
    last_name = request.json["last_name"]
    email = request.json["email"]
    password = request.json["password"]
    profile_url = request.json.get("profile_url")

    user = User.signup(username=username, email=email, first_name=first_name, last_name=last_name, password=password, profile_url=profile_url)

    import pdb
    pdb.set_trace()

    do_login(user)

    return jsonify(user=user.serialize()), 201

@app.route("/golfantasy/api/users/login", methods=['POST'])
def login_endpoint():
    """Endpoint for user login"""
    username = request.json['username']
    password = request.json['password']

    user = User.authenticate(username, password)
    
    do_login(user)
    
    return jsonify(user=user.serialize()), 200

@app.route("/golfantasy/api/users/<int:user_id>", methods=["GET"])
def get_user(user_id):
    """Endpoint to get specified user"""

    user = User.query.get_or_404(user_id)

    return jsonify(user=user.serialize()), 200


@app.route("/golfantasy/api/users/<int:user_id>/leagues/create", methods=['POST'])
def create_league_endpoint(user_id):
    """Endpoint for new league creation"""
    user = User.query.get_or_404(user_id)
    league_name = request.json["league_name"]
    start_date = request.json["start_date"]
    end_date = request.json["end_date"]
    privacy = request.json["privacy"]
    golfer_count = request.json["golfer_count"]
 
    league = League.create_new_league(league_name=league_name,
                                      start_date=start_date,
                                      end_date=end_date,
                                      privacy=privacy,
                                      golfer_count=golfer_count)
    
    user.leagues.append(league)
    db.session.commit()

    return jsonify(user=user.serialize(), league=league.serialize()), 201

@app.route("/golfantasy/api/users/<int:user_id>/leagues/<league_id>", methods=["POST"])
def user_joins_league_endpoint(user_id, league_id):

    user = User.query.get_or_404(user_id)
    league = League.query.get_or_404(league_id)
    user.leagues.append(league)
    db.session.commit()

    return jsonify(user=user.serialize(), league=league.serialize()), 201

@app.route("/golfantasy/api/leagues/public", methods=['GET'])
def get_all_public_leagues_endpoint():
    """Endpoint to get all leagues"""

    leagues = League.query.filter_by(privacy="public")
    
    return jsonify(leagues = [league.serialize() for league in leagues]), 200

@app.route("/golfantasy/api/leagues/<int:league_id>", methods=['GET'])
def get_single_league_endpoint(league_id):
    """Endpoint to get specific league"""

    # Find the league by its ID
    league = League.query.get_or_404(league_id)

    # Check if the league is private or public
    if league.privacy == 'private':
        # If the league is private, check if the entry code is provided in the query parameters
        entry_code = request.args.get('entry_code')

        if not entry_code:
            # If no entry code is provided, return an error response
            return jsonify(message="Entry code is required to join this private league"), 403

        # Authenticate the entry code
        if not League.authenticate(league.league_name, entry_code):
            # If the entry code is invalid, return an error response
            return jsonify(message="Invalid entry code"), 403

    # Serialize the league data and return it as a response
    return jsonify(league.serialize()), 200

@app.route("/golfantasy/api/teams/create", methods=["POST"])
def create_team_endpoint():
    """Endpoint to create new team"""

    team_name = request.json["team_name"]
    league_id = request.json["league_id"]
    user_id = request.json["user_id"]

    team = Team(team_name=team_name,
                user_id=user_id,
                league_id=league_id)
    
    return jsonify(team = team.serialize()), 201

@app.route("/golfantasy/api/teams/<int:team_id>", methods=["GET"])
def get_single_team_endpoint(team_id):
    """Endpoint to see team"""

    team=Team.query.get_or_404(team_id=team_id)
    
    return jsonify(team = team.serialize()), 200

@app.route("/golfantasy/api/teams", methods=["GET"])
def get_all_teams_endpoint():
    """Endpoint to see all teams"""

    teams=Team.query.all()

    return jsonify(teams=[team.serialize() for team in teams]), 200

@app.route("/golfantasy/api/golfers", methods=["GET"])
def get_all_golfers_endpoint():
    """Endpoint to get all golfers"""

    golfers=Golfer.query.all()

    return jsonify(golfers=[golfer.serialize() for golfer in golfers]), 200

@app.route("/golfantasy/api/leagues/<int:league_id>/golfers/available", methods=["GET"])
def get_all_available_golfers_endpoint(league_id):
    """Endpoint to get all available golfers"""

    # Find the league by its ID
    league = League.query.get_or_404(league_id)

    # Get the list of all golfers
    all_golfers = Golfer.query.all()

    # Filter out golfers who are already in the league
    available_golfers = [golfer for golfer in all_golfers if golfer not in league.golfers]

    # Serialize the list of available golfers and return it as a response
    return jsonify([golfer.serialize() for golfer in available_golfers]), 200

@app.route("/golfantasy/api/golfers/<int:golfer_id>", methods=["GET"])
def get_golfer_endpoint(golfer_id):
    """Endpoint to get single golfer"""

    golfer = Golfer.query.get_or_404(golfer_id)

    return jsonify(golfer = golfer.serialize()), 200

@app.route("/golfantasy/api/tournaments", methods=["GET"])
def get_all_tournaments_endpoint():
    """Endpoint to get all tournaments"""

    tournaments = Tournament.query.all()

    return jsonify(tournaments=[tournament.serialize() for tournament in tournaments])

@app.route("/golfantasy/api/tournaments/<int:tournament_id>", methods=["GET"])
def get_single_tournament_endpoint(tournament_id):
    """Endpoint to get single tournament"""

    tournament = Tournament.query.get_or_404(tournament_id)

    return jsonify(tournament=tournament.serialize())

