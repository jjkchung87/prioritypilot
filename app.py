import os

from flask import Flask, render_template, request, flash, redirect, session, g, jsonify, url_for
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func, and_
import requests
from models import db, connect_db, User, League, Team, Golfer, Tournament, UserGolfer, TeamGolfer, TournamentGolfer, UserLeague, LeagueGolfer
from forms import SignUpForm, LoginForm, CreateLeagueForm, JoinPrivateLeagueForm, JoinPublicLeagueForm, CreateTeamForm, UserUpdateForm
from datetime import datetime, timedelta
from flask_socketio import SocketIO, emit

app = Flask(__name__)
socketio = SocketIO(app)

# Get DB_URI from environ variable (useful for production/testing) or,
# if not set there, use development local db.
app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ.get('DATABASE_URL', 'postgresql:///golfantasy'))

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['EXPLAIN_TEMPLATE_LOADING'] = True
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "it's a secret")
app.debug=True
toolbar = DebugToolbarExtension(app)
app.app_context().push()
connect_db(app)

CURR_USER_KEY = "curr_user"

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


@app.route("/")
def root_route():
    """re-direct to homepage"""
    return redirect (url_for("show_homepage"))


@app.route("/golfantasy")
def show_homepage():
    """Show homepage"""

    if not g.user:
        return render_template("anon-home.html")
    
   # Calculate the date ranges for the last 30 days and prior 30 days
    last_30_days_end = datetime.utcnow()
    last_30_days_start = last_30_days_end - timedelta(days=30)
    prior_30_days_end = last_30_days_start - timedelta(days=1)
    prior_30_days_start = prior_30_days_end - timedelta(days=30)

    # Subquery to get the average score versus par for the last 30 days
    subquery_last_30_days = (db.session.query(TournamentGolfer.golfer_id,
                                            func.avg(TournamentGolfer.score_vs_par).label('avg_score_vs_par_last_30_days'))
                            .join(Tournament, and_(TournamentGolfer.tournament_name == Tournament.tournament_name,
                                                    TournamentGolfer.calendar_year == Tournament.calendar_year,
                                                    TournamentGolfer.tournament_dg_id == Tournament.dg_id))
                            .filter(and_(Tournament.date >= last_30_days_start,
                                        Tournament.date <= last_30_days_end))
                            .group_by(TournamentGolfer.golfer_id)
                            .subquery())

    # Subquery to get the average score versus par for the prior 30 days
    subquery_prior_30_days = (db.session.query(TournamentGolfer.golfer_id,
                                            func.avg(TournamentGolfer.score_vs_par).label('avg_score_vs_par_prior_30_days'))
                            .filter(and_(Tournament.date >= prior_30_days_start,
                                        Tournament.date <= prior_30_days_end))
                            .group_by(TournamentGolfer.golfer_id)
                            .subquery())

    # Main query to get the final table
    query = (db.session.query(subquery_last_30_days.c.golfer_id,
                            subquery_last_30_days.c.avg_score_vs_par_last_30_days,
                            subquery_prior_30_days.c.avg_score_vs_par_prior_30_days)
            .join(subquery_prior_30_days, subquery_last_30_days.c.golfer_id == subquery_prior_30_days.c.golfer_id)
            .order_by(subquery_last_30_days.c.avg_score_vs_par_last_30_days.asc())
            .all())

    # Output the results

    results = []
    for golfer_id, avg_score_vs_par_last_30_days, avg_score_vs_par_prior_30_days in query:
        golfer = Golfer.query.get(golfer_id)
        results.append({"id":golfer.id,
                        "first_name":golfer.first_name,
                        "last_name":golfer.last_name,
                        "avg_score_vs_par_last_30": int(avg_score_vs_par_last_30_days),
                        "avg_score_vs_par_prior_30": int(avg_score_vs_par_prior_30_days)})

    return render_template("home.html", results=results)

#*******************************************************************************************************************************
#User Sign-up / Login / Logout

@app.route("/golfantasy/signup", methods=["GET", "POST"])
def handle_signup_page():
    """Handle signup page"""

    form = SignUpForm()

    if form.validate_on_submit():
        username = form.username.data
        first_name = form.first_name.data
        last_name = form.last_name.data
        email = form.email.data
        password = form.password.data
        profile_url = form.profile_url.data
    
        user = User.signup(username=username, email=email, first_name=first_name, last_name=last_name, password=password, profile_url=profile_url)

        do_login(user)

        return redirect(url_for("show_homepage"))
    
    return render_template("signup.html", form=form)


@app.route("/golfantasy/login", methods=["GET", "POST"])
def handle_login_page():
    """Handle Login Page"""

    if g.user:
        return redirect(url_for("show_homepage"))

    form = LoginForm()


    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = User.authenticate(username=username, password=password)

        do_login(user)


        return redirect(url_for("show_homepage"))
    
    return render_template("login.html", form=form)

@app.route("/golfantasy/update", methods = ["GET, POST"])
def update_user_details():
    """Handle user profile update page"""

    form = UserUpdateForm(obj = g.user)

    if not g.user:
        flash("Need to be signed in")
        return redirect (url_for("show_homepage"))
    
    if form.validate_on_submit():
        if not User.authenticate(g.user.username, form.password.data):
            flash("Username and password do not match.", "danger")

        


@app.route("/golfantasy/logout", methods=["POST"])
def logout():
    """Log user out"""

    do_logout()

    return redirect(url_for("show_homepage"))


@app.route("/golfantasy/users/<int:user_id>")
def show_user(user_id):
    """Show user page"""

    if not g.user:
        return redirect(url_for("show_homepage"))
    
    user = User.query.get_or_404(user_id)

    return render_template("user.html",user=user)

#*******************************************************************************************************************************
#League Creation / Selection:

@app.route("/golfantasy/leagues", methods=["GET"])
def show_leagues_first_page():
    """Show and leagues first page"""

    if not g.user:
        return redirect(url_for("show_homepage"))
    
    return render_template("league-create-or-join.html")


@app.route("/golfantasy/leagues/create", methods=["GET", "POST"])
def handle_league_creation():
    """Handle league creation"""

    if not g.user:
        return redirect(url_for("show_homepage"))
    
    form = CreateLeagueForm()

    if form.validate_on_submit():
        league_name = form.league_name.data
        start_date = form.start_date.data
        end_date = form.end_date.data
        privacy = form.privacy.data
        max_teams = form.max_teams.data
        golfer_count = form.golfer_count.data
        league_manager_id = g.user.id

        league = League.create_new_league(league_name=league_name,
                                      start_date=start_date,
                                      end_date = end_date,
                                      privacy = privacy,
                                      max_teams=max_teams,
                                      golfer_count = golfer_count,
                                      league_manager_id = league_manager_id,
                                      draft_completed = False
                                      )

        user = User.query.get(g.user.id)


        return redirect(f"/golfantasy/leagues/{league.id}/teams")
    
    return render_template('league-create.html', form=form, user=g.user)

@app.route("/golfantasy/leagues/join", methods=["GET", "POST"])
def handle_join_league_page():
    """Handle join league page"""

    if not g.user:
        return redirect(url_for("show_homepage"))

    private_form = JoinPrivateLeagueForm()    
    public_form = JoinPublicLeagueForm()

    public_leagues = db.session.query(League.id, League.league_name).filter_by(privacy="public").all()
    public_form.set_choices(public_leagues)

    user = User.query.get(g.user.id)


    if request.method == "POST":
        if private_form.validate_on_submit():
            league_name = private_form.league_name.data
            entry_code = private_form.entry_code.data
            league = League.authenticate(league_name=league_name, entry_code=entry_code)
            
            if league.status in ('in-play', 'end-play', 'in-draft'):
                flash('Too late to join league')
                return redirect('/golfantasy/leagues/join')

            if league.max_teams <= len(league.teams):
                flash('Maximum capacity reached in this league.')
                return redirect('/golfantasy/leagues/join')

            if league in user.leagues:
                flash('You are already part of this league!')
                return redirect('/golfantasy/leagues/join')
      
            user.leagues.append(league)
            db.session.commit()
            return redirect(f"/golfantasy/leagues/{league.id}/teams")
        
        if public_form.validate_on_submit():
            league_id = public_form.league_name.data
            league = League.query.filter_by(id=league_id).first()
            
            if league.status in ('in-play', 'end-play', 'in-draft'):
                flash('Too late to join league')
                return redirect('/golfantasy/leagues/join')

            if league.max_teams <= len(league.teams):
                flash('Maximum capacity reached in this league.')
                return redirect('/golfantasy/leagues/join')

            if league in user.leagues:
                flash('You are already part of this league!')
                return redirect('/golfantasy/leagues/join')
            user.leagues.append(league)
            db.session.commit()
            return redirect(f"/golfantasy/leagues/{league.id}/teams")
        
  
    return render_template("league-join.html", private_form=private_form, public_form=public_form)



#*******************************************************************************************************************************
#Team Creation:

@app.route("/golfantasy/leagues/<int:league_id>/teams", methods=["POST", "GET"])
def create_team(league_id):
    """Create a team"""

    if not g.user:
        return redirect(url_for(show_homepage))
    
    league = League.query.get_or_404(league_id)
    user = User.query.get(g.user.id)

    for team in user.teams:
        if team in league.teams:
            return redirect(f'/golfantasy/leagues/{league.id}/lobby')
        
    
    form = CreateTeamForm()

    if form.validate_on_submit():
        team_name = form.team_name.data
        team = Team(team_name=team_name,
                    user_id=user.id,
                    league_id=league.id)
        
        db.session.add(team)
        db.session.commit()
        return redirect(f"/golfantasy/leagues/{league.id}")
    
    return render_template("team-create.html", form=form, league=league, user=user)

#*******************************************************************************************************************************
#League Routes:

@app.route("/golfantasy/leagues/<int:league_id>")
def direct_to_correct_league_page(league_id):
    """Direct to the correct league page depending on league status"""

    if not g.user:
        return redirect(url_for(show_homepage))
    
    league = League.query.get_or_404(league_id)
    team = None
    for t in g.user.teams:
        if t.league_id == league.id:
            team = t
            break

    if league.status == "end-play" or league.status == "in-play":
        if team is None:
            return redirect(f"/golfantasy/users/{g.user.id}")
        else:
            return render_template("league-dash.html", league=league, team=team)
        
    if league.status == "in-draft":
        if team is None:
            return redirect(f"/golfantasy/leagues/{league.id}/teams")
        
        else:
            return render_template("league-draft.html", league=league, team=team)
        
    if league.status == "pre-draft":
        if team is None:
            return redirect(f"/golfantasy/leagues/{league.id}/teams")
        else:
            return render_template("league-lobby.html", league=league, team=team)

@app.route("/golfantasy/leagues/<int:league_id>/draft", methods=["POST"])
def manual_start_draft(league_id):
    """Manually start leeague draft"""

    if not g.user:
        return redirect(url_for(show_homepage))
    
    league = League.query.get_or_404(league_id)
    
    if league.league_manager_id != g.user.id:
        flash("Only the league manager can start the draft")
        return redirect(f"/golfantasy/leagues/{league_id}")
    
    now = datetime.utcnow()

    league.start_date = now
    db.session.commit()

    return redirect(f"/golfantasy/leagues/{league_id}")




# @app.route("/golfantasy/leagues/<int:league_id>/lobby")
# def show_league_lobby(league_id):
#     """Show league pre-draft lobby"""

#     if not g.user:
#         return redirect(url_for(show_homepage))
        
#     league = League.query.get_or_404(league_id)
    
#     if league.status == "in-draft":
#         return redirect(f"/golfantasy/leagues/{league.id}/draft")
    
#     if league.status == "in-play" or "end-play":
#         return redirect(f"/golfantasy/leagues/{league.id}/dash")
    
#     else:
#         team = ""
#         for t in g.user.teams:
#             if t.league_id == league.id:
#                 team = t
#                 break
#         if team is None:
#             return redirect(f'/golfantasy/leagues/{league.id}/teams')
        
#         return render_template("league-lobby.html", league=league, team=team)


# @app.route("/golfantasy/leagues/<int:league_id>/draft")
# def show_draft(league_id):
#     """Show draft"""

#     if not g.user:
#             return redirect(url_for(show_homepage))
        
#     league = League.query.get_or_404(league_id)
    
#     if league.status == "pre-draft":
#             return redirect(f"/golfantasy/leagues/{league.id}/lobby")
    
#     if league.status == "in-play" or "end-play":
#         return redirect(f"/golfantasy/leagues/{league.id}/dash")

#     else:
#         team = ""
#         for t in g.user.teams:
#             if t.league_id == league.id:
#                 team = t
#                 break
#         if team is None:
#             return redirect(f'/golfantasy/leagues/{league.id}/teams')
        
#         return render_template("league-draft.html", league=league, team=team)


#*******************************************************************************************************************************
#Dashboards

# @app.route("/golfantasy/leagues/<int:league_id>/dash")
# def show_league_dash(league_id):
#     """Show league dash"""

#     if not g.user:
#         return redirect(url_for("show_homepage"))

#     league = League.query.get_or_404(league_id)

#     if league.status == "pre-draft":
#         return redirect(f"/golfantasy/leagues/{league.id}/lobby")
    
#     elif league.status == "in-draft":
#         return redirect(f"/golfantasy/leagues/{league.id}/draft")

#     # Check if the user has a team associated with the current league
#     else:
#         team = None
#         for t in g.user.teams:
#             if t.league_id == league.id:
#                 team = t
#                 break

#         if team is None:
#             return redirect(f'/golfantasy/leagues/{league.id}/teams')

#         return render_template("league-dash.html", league=league, team=team)

@app.route("/golfantasy/teams/<team_id>")
def show_team_dash(team_id):
    """Show team dash"""

    if not g.user:
            return redirect(url_for(show_homepage))

    team = Team.query.get_or_404(team_id)
    user = User.query.get(g.user.id)

    return render_template("team-dash.html", team=team, user=user)

@app.route("/golfantasy/golfers/<int:golfer_id>")
def show_golfer(golfer_id):
    """Show golfer details"""

    if not g.user:
            return redirect(url_for(show_homepage))
    
    golfer = Golfer.query.get_or_404(golfer_id)
    user = User.query.get(g.user.id)

    return render_template("golfer.html", golfer=golfer, user=user)

@app.route("/golfantasy/golfers")
def show_golfers():
    """Show golfers """

    if not g.user:
            return redirect(url_for(show_homepage))
    
    golfers = Golfer.query.all()
    user = User.query.get(g.user.id)

    return render_template("golfers.html", golfers=golfers, user=user)



#*******************************************************************************************************************************
#API End-points:

@app.route("/golfantasy/api/users/signup", methods=["POST"])
def signup_endpoint():
    """Endpoint for new user sign up"""
    form = SignUpForm(request.form)

    if form.validate():
        # Extract form data
        username = form.username.data
        first_name = form.first_name.data
        last_name = form.last_name.data
        email = form.email.data
        password = form.password.data
        profile_url = form.profile_url.data

        # Call User.signup class method to create a new user
        user = User.signup(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            password=password,
            profile_url=profile_url,
        )

        # Return the serialized user data along with a success response
        return jsonify({"user": user.serialize(), "message": "User signup successful!"}), 201
    else:
        # Return error response if form validation fails
        errors = {field.name: field.errors for field in form}
        return jsonify({"errors": errors}), 400

    # username = request.json["username"]
    # first_name = request.json["first_name"]
    # last_name = request.json["last_name"]
    # email = request.json["email"]
    # password = request.json["password"]
    # profile_url = request.json.get("profile_url")

    # user = User.signup(username=username, email=email, first_name=first_name, last_name=last_name, password=password, profile_url=profile_url)

    # do_login(user)

    # return jsonify(user=user.serialize()), 201



@app.route("/golfantasy/api/users/authenticate", methods=['POST'])
def authentication_endpoint():
    """Endpoint for user authentication"""
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


# @app.route("/golfantasy/api/users/<int:user_id>/leagues/create", methods=['POST'])
# def create_league_endpoint(user_id):
#     """Endpoint for new league creation"""
#     user = User.query.get_or_404(user_id)
#     league_name = request.json["league_name"]
#     start_date = request.json["start_date"]
#     end_date = request.json["end_date"]
#     privacy = request.json["privacy"]
#     golfer_count = request.json["golfer_count"]
 
#     league = League.create_new_league(league_name=league_name,
#                                       start_date=start_date,
#                                       end_date=end_date,
#                                       privacy=privacy,
#                                       golfer_count=golfer_count)
    
#     db.session.commit()

#     return jsonify(user=user.serialize(), league=league.serialize()), 201

# @app.route("/golfantasy/api/users/<int:user_id>/leagues/<league_id>", methods=["POST"])
# def user_joins_league_endpoint(user_id, league_id):

#     user = User.query.get_or_404(user_id)
#     league = League.query.get_or_404(league_id)
#     user.leagues.append(league)
#     db.session.commit()

#     return jsonify(user=user.serialize(), league=league.serialize()), 201

# @app.route("/golfantasy/api/leagues/public", methods=['GET'])
# def get_all_public_leagues_endpoint():
#     """Endpoint to get all leagues"""

#     leagues = League.query.filter_by(privacy="public")
    
#     return jsonify(leagues = [league.serialize() for league in leagues]), 200

@app.route("/golfantasy/api/leagues/<int:league_id>", methods=['GET'])
def get_single_league_endpoint(league_id):
    """Endpoint to get specific league"""

    # Find the league by its ID
    league = League.query.get_or_404(league_id)

    # # Check if the league is private or public
    # if league.privacy == 'private':
    #     # If the league is private, check if the entry code is provided in the query parameters
    #     entry_code = request.args.get('entry_code')

    #     if not entry_code:
    #         # If no entry code is provided, return an error response
    #         return jsonify(message="Entry code is required to join this private league"), 403

    #     # Authenticate the entry code
    #     if not League.authenticate(league.league_name, entry_code):
    #         # If the entry code is invalid, return an error response
    #         return jsonify(message="Invalid entry code"), 403

    # Serialize the league data and return it as a response
    return jsonify(league.serialize()), 200

# @app.route("/golfantasy/api/teams/create", methods=["POST"])
# def create_team_endpoint():
#     """Endpoint to create new team"""
    
#     # user can only create one team within a league

#     team_name = request.json["team_name"]
#     league_id = request.json["league_id"]
#     user_id = request.json["user_id"]

#     team = Team(team_name=team_name,
#                 user_id=user_id,
#                 league_id=league_id)
    
#     db.session.add(team)
#     db.session.commit()
    
#     return jsonify(team = team.serialize()), 201

@app.route("/golfantasy/api/teams/<int:team_id>", methods=["GET"])
def get_single_team_endpoint(team_id):
    """Endpoint to see team"""

    team=Team.query.get_or_404(team_id)
    
    return jsonify(team = team.serialize()), 200

# @app.route("/golfantasy/api/teams", methods=["GET"])
# def get_all_teams_endpoint():
#     """Endpoint to see all teams"""

#     teams=Team.query.all()

#     return jsonify(teams=[team.serialize() for team in teams]), 200

# @app.route("/golfantasy/api/golfers", methods=["GET"])
# def get_all_golfers_endpoint():
#     """Endpoint to get all golfers"""

#     golfers=Golfer.query.all()

#     return jsonify(golfers=[golfer.serialize() for golfer in golfers]), 200

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
    return jsonify(golfers = [golfer.serialize() for golfer in available_golfers]), 200

@app.route("/golfantasy/api/teams/<int:team_id>/golfers/<int:golfer_id>", methods=["POST", "DELETE"])
def add_or_remove_golfer_to_team(team_id, golfer_id):
    """Endpoint to add or remove a golfer from a team"""

    team = Team.query.get_or_404(team_id)
    golfer = Golfer.query.get_or_404(golfer_id)

    if request.method == "POST":
        team.add_golfer(golfer.id)

    if request.method == "DELETE":
        team.remove_golfer(golfer.id)

    db.session.commit()
    return jsonify(golfer=golfer.serialize())


@app.route("/golfantasy/api/leagues/<int:league_id>/teams", methods=["GET"])
def get_teams_in_league(league_id):
    """Endpoint to get teams in a league"""

    league = League.query.get_or_404(league_id)
    teams = league.teams

    teams = [team.serialize() for team in teams]
 
    return jsonify(teams=teams), 200

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

