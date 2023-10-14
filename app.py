import os

from flask import Flask, render_template, request, flash, redirect, session, g, jsonify, url_for
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError, PendingRollbackError
from sqlalchemy import func, and_, case
import requests
from models import db, connect_db, User, Team, Project, Task, Conversation, UserProject
from datetime import datetime, timedelta
from controller import generate_ai_tasks, generate_ai_tips
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, get_jwt_identity, jwt_required


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ.get('DATABASE_URL', 'postgresql:///prioritypilot'))

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['EXPLAIN_TEMPLATE_LOADING'] = True
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "it's a secret")
app.config['JWT_SECRET_KEY'] = 'SECRET KEY FOR JWT'  # Replace with your own secret key

app.debug=True
if app.config['ENV'] == 'development':
    toolbar = DebugToolbarExtension(app)
app.app_context().push()
connect_db(app)
CORS(app)
jwt = JWTManager(app)


# #*******************************************************************************************************************************
# ENDPOINTS

# #*******************************************************************************************************************************
# SIGNUP

@app.route("/prioritypilot/api/users/signup", methods=["POST"])
def signup_endpoint():
    """Endpoint for new user sign up"""

    email = request.json.get('email')
    first_name = request.json.get('first_name')
    last_name = request.json.get('last_name')
    password = request.json.get('password')
    role = request.json.get('role')
    team_name = request.json.get('team')
    profile_img = request.json.get('profile_img_url')

    # Check if a user with the provided email already exists
    existing_user = User.query.filter_by(email=email).first()

    if existing_user:
        # Return an error response if the user already exists
        return jsonify({"message": "User with this email already exists."}), 409

    # Call User.signup class method to create a new user
    user = User.signup(
        email=email,
        first_name=first_name,
        last_name=last_name,
        password=password,
        team_name=team_name,
        role=role,
        profile_img=profile_img
    )

    # Create a JWT access token for the newly registered user
    access_token = create_access_token(identity=email)  # You can customize the token payload

    # Return the serialized user data along with the token in the response
    return jsonify({"user": user.serialize(), "access_token": access_token, "message": "User signup successful!"}), 201
    
# #*******************************************************************************************************************************
# LOGIN

@app.route("/prioritypilot/api/users/login", methods=["POST"])
def login_endpoint():
    """Endpoint for user login"""

    email = request.json.get('email')
    password = request.json.get('password')

    if not email or not password:
        # Check for missing email or password
        return jsonify({"message": "Email and password are required."}), 400

    user = User.authenticate(email, password)

    # Create a JWT access token for the newly registered user
    access_token = create_access_token(identity=email)  # You can customize the token payload

    if not user:
        # Check for incorrect email/password
        return jsonify({"message": "Incorrect email or password."}), 401

    # Return the serialized user data along with a success response
    return jsonify({"user": user.serialize(), "access_token": access_token, "message": "User login successful!"}), 200

# #*******************************************************************************************************************************
# GET USER

@app.route("/prioritypilot/api/users/<int:user_id>", methods=["GET"])
def get_single_user(user_id):
    """Endpoint to get single user"""

    user = User.query.get_or_404(user_id)

    # Return the serialized user data along with a success response
    return jsonify({"user": user.serialize(), "message": "Retrieved user!"}), 200


# #*******************************************************************************************************************************
# NEW PROJECT

@app.route("/prioritypilot/api/projects", methods=['POST'], endpoint="create_new_project")
@jwt_required()
def create_new_project():
    """Create a new project"""

    email = get_jwt_identity()

    project_name = request.json.get('project_name')
    description = request.json.get('description')
    # prompt = request.json.get('prompt')
    # start_date = request.json.get('start_date')
    end_date = request.json.get('end_date')
    user_id = request.json.get('user_id')
    ai = request.json.get('ai_recommendation')

    user = User.query.filter_by(email=email).one()

    if user.id != user_id:
        return jsonify({"message": "Not authorized."}), 401


    project = Project.create_new_project(project_name=project_name,
                                         description=description,
                                        #  start_date=start_date,
                                         end_date=end_date,
                                         user_id=user_id)
    
    if ai:
    
        prompt = f'I am a {user.role}. I am working on a project titled {project_name}. The deadline is {end_date}. Here is a description: {description}'
        messages = generate_ai_tasks(project.id, user.id, prompt)        
        conversation = Conversation(user_id=user_id,
                                    project_id=project.id)
        
        db.session.add(conversation)
        db.session.commit()
        
        conversation.set_messages(messages)


    return jsonify(project = project.serialize()), 200
    
    # return jsonify(project = project.serialize()), 200
    


# #*******************************************************************************************************************************
# NEW TASK

@app.route("/prioritypilot/api/projects/<int:project_id>/task", methods=["POST"], endpoint="create_new_task")
@jwt_required()
def create_new_task(project_id):
    """Endpoint to create a new task"""

    email = get_jwt_identity()

    task_name= request.json.get('title')
    description= request.json.get('description')
    priority= request.json.get('priority')
    end_date= request.json.get('deadline')
    project_id= project_id
    user_id= request.json.get('user_id')
    notes=""
    
    user = User.query.filter_by(email=email).one()

    if user.id != user_id:
        return jsonify({"message": "Not authorized."}), 401

    else:
        t = Task(task_name=task_name,
                description=description,
                priority=priority,
                end_date=end_date,
                project_id=project_id,
                user_id=user_id,
                notes=notes
                )
    
        db.session.add(t)
        db.session.commit()

        return jsonify({"task": t.serialize(), "message": "Task created!"}), 200


# #*******************************************************************************************************************************
# EDIT TASK
@app.route("/prioritypilot/api/projects/<int:project_id>/task/<int:task_id>", methods=["PATCH"], endpoint="edit_task")
@jwt_required()
def edit_task(project_id, task_id):
    """Endpoint to edit a task"""

    email = get_jwt_identity()

    task_name = request.json.get('title')
    description = request.json.get('description')
    priority = request.json.get('priority')
    end_date = request.json.get('deadline')
    status = request.json.get('status')
    user_id = request.json.get('user_id')
    modified_at = datetime.utcnow()

    user = User.query.filter_by(email=email).one()

    if user.id != user_id:
        return jsonify({"message": "Not authorized."}), 401

    task = Task.query.get_or_404(task_id)

    # Update the task's information
    task.task_name = task_name
    task.description = description
    task.priority = priority
    task.end_date = end_date
    task.status = status
    task.modified_at = modified_at

    db.session.commit()

    return jsonify({"task": task.serialize(), "message": "Task updated!"}), 200

# #*******************************************************************************************************************************
# GET AI TIPS FOR SINGLE TASK

@app.route("/prioritypilot/api/projects/<int:project_id>/task/<int:task_id>", methods=['POST'], endpoint="get_ai_tips")
@jwt_required()
def get_ai_tips_endpoint(project_id, task_id):
    """AI tips for single task"""

    email = get_jwt_identity()
    user = User.query.filter_by(email=email).one()
    user_id = request.json.get('user_id')
    
    if user.id != user_id:
        return jsonify({"message": "Not authorized."}), 401

    project_id=project_id
    task_id = task_id

    tips = generate_ai_tips(project_id, task_id)


    return jsonify({"tips":tips, "message":"Tips generated!"}), 200
    
    # return jsonify(project = project.serialize()), 200
    

# #*******************************************************************************************************************************
# #CURRENT USER AND SESSION MANAGEMENT

# CURR_USER_KEY = "curr_user"

# @app.before_request
# def add_user_to_g():
#     """If we're logged in, add curr user to Flask global "g". Used to manage user auth and access control throughout application"""

#     if CURR_USER_KEY in session:
#         g.user = User.query.get(session[CURR_USER_KEY])

#     else:
#         g.user = None


# def do_login(user):
#     """Log in user."""

#     session[CURR_USER_KEY] = user.id


# def do_logout():
#     """Logout user."""

#     if CURR_USER_KEY in session:
#         del session[CURR_USER_KEY]

# #*******************************************************************************************************************************
# #HOMEPAGE

# @app.route("/")
# def root_route():
#     """re-direct to homepage"""
#     return redirect (url_for("show_homepage"))


# @app.route("/golfantasy")
# def show_homepage():
#     """Show homepage"""

#     if not g.user:
#         return render_template("/home/anon-home.html")
    
#     latest_tournament = get_latest_tournament()
#     latest_tournament_results = get_latest_tournament_results(latest_tournament)


#     return render_template("/home/home.html", tournament = latest_tournament, results=latest_tournament_results)

# #*******************************************************************************************************************************
# #SIGN-UP / LOGIN / LOGOUT

# @app.route("/golfantasy/signup", methods=["GET", "POST"])
# def handle_signup_page():
#     """Handle signup page"""

#     form = SignUpForm()

#     if request.method == "POST":
    
#         if form.validate_on_submit():
#             username = form.username.data
#             first_name = form.first_name.data
#             last_name = form.last_name.data
#             email = form.email.data
#             password = form.password.data
#             if form.profile_url.data == "":
#                 profile_url = DEFAULT_URL
#             else:
#                 profile_url = form.profile_url.data
        
#             user = User.signup(username=username, 
#                                email=email, 
#                                first_name=first_name, 
#                                last_name=last_name, 
#                                password=password, 
#                                profile_url=profile_url)
#             do_login(user)
          
#             return jsonify({"success": True, "user": user.serialize()}), 200
        
#         else:
#             # Return error response if form validation fails
#             errors = {field.name: field.errors for field in form}
#             return jsonify({"errors": errors}), 400
    
#     return render_template("/user/signup.html", form=form)


# @app.route("/golfantasy/login", methods=["GET", "POST"])
# def handle_login_page():
#     """Handle Login Page"""

#     if g.user:
#         return redirect(url_for("show_homepage"))

#     form = LoginForm()


#     if form.validate_on_submit():
#         username = form.username.data
#         password = form.password.data

#         user = User.authenticate(username=username, password=password)

#         if user:
#             do_login(user)
#             flash(f"Welcome back, {user.username}!", "success")
#             return redirect(url_for("show_homepage"))
        
#         else:
#             flash("Invalid login credentials. Please try again.", "danger")
    
#     return render_template("/user/login.html", form=form)


# @app.route("/golfantasy/users/<int:user_id>", methods = ["GET", "POST"])
# def update_user_details(user_id):
#     """Handle user profile update page"""

#     form = UserUpdateForm(obj = g.user)

#     if not g.user:
#         flash("Need to be signed in")
#         return redirect (url_for("show_homepage"))
    
#     if form.validate_on_submit():
#         if not User.authenticate(g.user.username, form.old_password.data):
#             flash("Username and password do not match.", "danger")
#             return redirect(request.referrer)
        
#         try:
#             g.user.first_name = form.first_name.data
#             g.user.last_name = form.last_name.data
#             g.user.username = form.username.data
#             g.user.email = form.email.data
#             if form.profile_url.data == "":
#                 g.user.profile_url = DEFAULT_URL
#             else:
#                 g.user.profile_url = form.profile_url.data
#             db.session.commit()

#             if form.new_password.data:
#                 g.user.update_password(form.old_password.data, form.new_password.data)             

#             flash("Profile updated!","success")
#             return redirect(request.referrer)
        
#         except IntegrityError:
#             form.username.errors.append("Username is taken. Please try a different name.")
#             db.session.rollback()

#     return render_template("/user/user.html", form=form)

# @app.route("/golfantasy/logout", methods=["POST"])
# def logout():
#     """Log user out"""

#     do_logout()

#     return redirect(url_for("show_homepage"))


# # @app.route("/golfantasy/users/<int:user_id>")
# # def show_user(user_id):
# #     """Show user page"""

# #     if not g.user:
# #         return redirect(url_for("show_homepage"))
    
# #     user = User.query.get_or_404(user_id)

# #     return render_template("/user/user.html",user=user)

# #*******************************************************************************************************************************
# #LEAGUE CREATION / JOINING

# @app.route("/golfantasy/leagues", methods=["GET"])
# def show_leagues_first_page():
#     """Show and leagues first page"""

#     if not g.user:
#         return redirect(url_for("show_homepage"))
    
#     return render_template("/league/league-create-or-join.html")


# @app.route("/golfantasy/leagues/create", methods=["GET", "POST"])
# def handle_league_creation():
#     """Handle league creation"""

#     if not g.user:
#         return redirect(url_for("show_homepage"))
    
#     form = CreateLeagueForm()

#     if form.validate_on_submit():
#         league_name = form.league_name.data
#         start_date = form.start_date.data
#         end_date = form.end_date.data
#         privacy = form.privacy.data
#         max_teams = form.max_teams.data
#         golfer_count = form.golfer_count.data
#         league_manager_id = g.user.id
        
#         try:
#             league = League.create_new_league(league_name=league_name,
#                                           start_date=start_date,
#                                           end_date=end_date,
#                                           privacy=privacy,
#                                           max_teams=max_teams,
#                                           golfer_count=golfer_count,
#                                           league_manager_id=league_manager_id,
#                                           draft_completed=False
#                                           )

#             user = User.query.get(g.user.id)

#             return redirect(f"/golfantasy/leagues/{league.id}/teams")
        
#         except IntegrityError:
#             form.league_name.errors.append("A league with this name already exists. Please try a different name.")
#             db.session.rollback()

    
#     return render_template('/league/league-create.html', form=form, user=g.user)

# @app.route("/golfantasy/leagues/join", methods=["GET", "POST"])
# def handle_join_league_page():
#     """Handle join league page"""

#     if not g.user:
#         return redirect(url_for("show_homepage"))

#     private_form = JoinPrivateLeagueForm()    
#     public_form = JoinPublicLeagueForm()

#     public_leagues = g.user.get_available_public_leagues()
    
#     public_form.set_choices(public_leagues)

#     user = User.query.get(g.user.id)


#     if request.method == "POST":
#         if private_form.validate_on_submit():
#             league_name = private_form.league_name.data
#             entry_code = private_form.entry_code.data
            
#             league = League.authenticate(league_name=league_name, entry_code=entry_code)

#             if not league:
#                 flash('Invalid league name / entry code. Please try again.','danger')
#                 return redirect(request.referrer)
            
#             else:
#                 join = league.join_validation(user)
                
#                 if join['success'] == False:
#                     flash(join['msg'],'danger')
#                     return redirect(request.referrer)
                
#                 else:
#                     flash(join['msg'],'success')
#                     return redirect(f"/golfantasy/leagues/{league.id}/teams")
        
#         if public_form.validate_on_submit():
#             league_id = public_form.league_name.data
#             league = League.query.filter_by(id=league_id).first()
            
#             join = league.join_validation(user)
                
#             if join['success'] == False:
#                 flash(join['msg'],'danger')
#                 return redirect(request.referrer)
            
#             else:
#                 flash(join['msg'],'success')
#                 return redirect(f"/golfantasy/leagues/{league.id}/teams")

          
#     return render_template("/league/league-join.html", private_form=private_form, public_form=public_form)



# #*******************************************************************************************************************************
# #TEAM CREATION

# @app.route("/golfantasy/leagues/<int:league_id>/teams", methods=["POST", "GET"])
# def create_team(league_id):
#     """Create a team"""

#     if not g.user:
#         return redirect(url_for(show_homepage))
    
#     league = League.query.get_or_404(league_id)
#     user = User.query.get(g.user.id)

#     for team in user.teams:
#         if team in league.teams:
#             return redirect(f'/golfantasy/leagues/{league.id}')
        
    
#     form = CreateTeamForm()

#     if form.validate_on_submit():
#         try:
#             team_name = form.team_name.data
#             team = Team(team_name=team_name,
#                         user_id=user.id,
#                         league_id=league.id)
            
#             db.session.add(team)
#             db.session.commit()
#             return redirect(f"/golfantasy/leagues/{league.id}")
        
#         except IntegrityError:
#             form.team_name.errors.append("A team with this name already exists. Please try a different name.")
#             db.session.rollback()
    
#     return render_template("/team/team-create.html", form=form, league=league, user=user)

# #*******************************************************************************************************************************
# #LEAGUE PAGE ROUTES

# @app.route("/golfantasy/leagues/<int:league_id>")
# def direct_to_correct_league_page(league_id):
#     """Direct to the correct league page depending on league status"""

#     if not g.user:
#         return redirect(url_for(show_homepage))
    
#     league = League.query.get_or_404(league_id)
#     team = None
#     for t in g.user.teams:
#         if t.league_id == league.id:
#             team = t
#             break

#     if league.status == "end-play" or league.status == "in-play": #League dashboard
#         if team is None:
#             return redirect(f"/golfantasy/users/{g.user.id}")
        
#         else:
#             league_results = get_league_results(league)
#             top_golfers_in_league = get_top_golfers_in_league(league)
#             league_leader=""
#             if league_results:
#                 league_leader = league_results[0].team_name

#             return render_template("/league/league-dash.html", 
#                                    league=league, 
#                                    team=team, 
#                                    results=league_results, 
#                                    golfer_results = top_golfers_in_league,
#                                    league_leader=league_leader)
        
#     if league.status == "in-draft": #League draft
#         if team is None:
#             return redirect(f"/golfantasy/leagues/{league.id}/teams")
                
#         else:
#             all_golfers = Golfer.query.all()
#             available_golfers = [golfer for golfer in all_golfers if golfer not in league.golfers]
#             drafted_golfers = [golfer for golfer in league.golfers]
#             draft_order = [team.id for team in league.teams]
#             max_draft_picks = len(league.teams)*league.golfer_count
#             return render_template("/league/league-draft.html", 
#                                    league=league, team=team, 
#                                    available_golfers=available_golfers, 
#                                    drafted_golfers=drafted_golfers, 
#                                    draft_order=draft_order, 
#                                    max_draft_picks=max_draft_picks)
        
#     if league.status == "pre-draft": #League pre-draft lobby
#         if team is None:
#             return redirect(f"/golfantasy/leagues/{league.id}/teams")
#         else:
#             countdown_date = league.start_date
#             return render_template("/league/league-lobby.html", 
#                                    league=league, 
#                                    team=team)



# #*******************************************************************************************************************************
# #LEAGUE DRAFT - SOCKET
# @socketio.on("connect")
# def connect():

#     print('connected!')

# @socketio.on('make_draft_pick')
# def on_make_draft_pick(data):
    
#     team = Team.query.get(data['team_id'])
#     league = League.query.get(data['league_id'])
#     golfer = Golfer.query.get(data['golfer_id'])
#     team.add_golfer(golfer.id)
#     all_golfers = Golfer.query.all()
#     # available_golfers = [golfer.serialize() for golfer in all_golfers if golfer not in league.golfers]
#     drafted_golfers = [golfer.serialize() for golfer in league.golfers]
#     team_golfers = []
#     max_draft_picks = len(league.teams)*league.golfer_count


#     for team in league.teams:
#         team_dict ={
#             'team_name': team.team_name,
#             'golfers': [golfer.serialize() for golfer in team.golfers]
#         }
#         team_golfers.append(team_dict)
    
#     if league.draft_pick_index >= len(league.teams)-1:
#         league.draft_pick_index = 0
    
#     else: 
#         league.draft_pick_index += 1
    
#     league.draft_pick_count += 1
 
#     if league.draft_pick_count >= len(league.teams) * league.golfer_count:
#         league.draft_completed = True

#     db.session.commit()

#     emit('golfer_drafted', {
#                             'picked_golfer': golfer.serialize(),
#                             # 'available_golfers': available_golfers,
#                             'drafted_golfers': drafted_golfers,
#                             'team_golfers': team_golfers,
#                             'draft_pick_count': league.draft_pick_count,
#                             'max_draft_picks': max_draft_picks,
#                             'draft_pick_index': league.draft_pick_index,
#                             'draft_completed': league.draft_completed
#                             }, broadcast=True)
                            
  
# @app.route("/golfantasy/leagues/<int:league_id>/draft", methods=["POST"])
# def manual_start_draft(league_id):
#     """Manually start leeague draft"""

#     if not g.user:
#         return redirect(url_for(show_homepage))
    
#     league = League.query.get_or_404(league_id)
    
#     if league.league_manager_id != g.user.id:
#         flash("Only the league manager can start the draft","danger")
#         return redirect(f"/golfantasy/leagues/{league_id}")
    
#     now = datetime.utcnow()

#     league.start_date = now
#     db.session.commit()

#     return redirect(f"/golfantasy/leagues/{league_id}")


# #*******************************************************************************************************************************
# #TEAM VIEWS

# @app.route("/golfantasy/teams/<team_id>")
# def show_team_dash(team_id):
#     """Show team dash"""

#     if not g.user:
#             return redirect(url_for(show_homepage))

#     team = Team.query.get_or_404(team_id)
#     league = League.query.get(team.league_id)

#     team_results = get_team_results(league, team)

#     return render_template("/team/team-dash.html", team=team, results=team_results)


# #*******************************************************************************************************************************
# #API End-points for client-side to access:



# @app.route("/golfantasy/api/users/authenticate", methods=['POST'])
# def authenticate_user():
#     """Authenticates user to store on client-side at login"""

#     username = request.json.get('username')
#     password = request.json.get('password')

#     if not username or not password:
#         return jsonify(error="Username and password are required"), 400
        
#     user = User.authenticate(username, password)
        
#     if not user:
#         return jsonify(error="Invalid credentials"), 401
    
#     return jsonify(user=user.serialize()), 200

# @app.route("/golfantasy/api/users/<int:user_id>", methods=["GET"])
# def get_user(user_id):
#     """Endpoint to store currently signed in user on client-side"""

#     user = User.query.get_or_404(user_id)

#     return jsonify(user=user.serialize()), 200


# @app.route("/golfantasy/api/leagues/<int:league_id>", methods=['GET'])
# def get_single_league_endpoint(league_id):
#     """Endpoint to get specific league"""


#     league = League.query.get_or_404(league_id)

#     return jsonify(league.serialize()), 200

# @app.route("/golfantasy/api/teams/<int:team_id>", methods=["GET"])
# def get_single_team_endpoint(team_id):
#     """Endpoint to see specified team"""

#     team=Team.query.get_or_404(team_id)
    
#     return jsonify(team = team.serialize()), 200


    




# #*******************************************************************************************************************************
# # UNUSED API ROUTES

# # @app.route("/golfantasy/api/users/signup", methods=["POST"])
# # def signup_endpoint():
# #     """Endpoint for new user sign up"""
# #     form = SignUpForm(request.form)

# #     if form.validate():
# #         # Extract form data
# #         username = form.username.data
# #         first_name = form.first_name.data
# #         last_name = form.last_name.data
# #         email = form.email.data
# #         password = form.password.data
# #         profile_url = form.profile_url.data

# #         # Call User.signup class method to create a new user
# #         user = User.signup(
# #             username=username,
# #             email=email,
# #             first_name=first_name,
# #             last_name=last_name,
# #             password=password,
# #             profile_url=profile_url,
# #         )

# #         # Return the serialized user data along with a success response
# #         return jsonify({"user": user.serialize(), "message": "User signup successful!"}), 201
# #     else:
# #         # Return error response if form validation fails
# #         errors = {field.name: field.errors for field in form}
# #         return jsonify({"errors": errors}), 400

# #     # username = request.json["username"]
# #     # first_name = request.json["first_name"]
# #     # last_name = request.json["last_name"]
# #     # email = request.json["email"]
# #     # password = request.json["password"]
# #     # profile_url = request.json.get("profile_url")

# #     # user = User.signup(username=username, email=email, first_name=first_name, last_name=last_name, password=password, profile_url=profile_url)

# #     # do_login(user)

# #     # return jsonify(user=user.serialize()), 201


# # @app.route("/golfantasy/api/leagues/<int:league_id>/golfers/available", methods=["GET"])
# # def get_all_available_golfers_endpoint(league_id):
# #     """Endpoint to get all available golfers"""

# #     # Find the league by its ID
# #     league = League.query.get_or_404(league_id)

# #     # Get the list of all golfers
# #     all_golfers = Golfer.query.all()

# #     # Filter out golfers who are already in the league
# #     available_golfers = [golfer for golfer in all_golfers if golfer not in league.golfers]

# #     # Serialize the list of available golfers and return it as a response
# #     return jsonify(golfers = [golfer.serialize() for golfer in available_golfers]), 200

# # @app.route("/golfantasy/api/teams/<int:team_id>/golfers/<int:golfer_id>", methods=["POST", "DELETE"])
# # def add_or_remove_golfer_to_team(team_id, golfer_id):
# #     """Endpoint to add or remove a golfer from a team"""

# #     team = Team.query.get_or_404(team_id)
# #     golfer = Golfer.query.get_or_404(golfer_id)

# #     if request.method == "POST":
# #         team.add_golfer(golfer.id)

# #     if request.method == "DELETE":
# #         team.remove_golfer(golfer.id)

# #     db.session.commit()
# #     return jsonify(golfer=golfer.serialize())


# # @app.route("/golfantasy/api/leagues/<int:league_id>/teams", methods=["GET"])
# # def get_teams_in_league(league_id):
# #     """Endpoint to get teams in a league"""

# #     league = League.query.get_or_404(league_id)
# #     teams = league.teams

# #     teams = [team.serialize() for team in teams]
 
# #     return jsonify(teams=teams), 200

# # @app.route("/golfantasy/api/golfers/<int:golfer_id>", methods=["GET"])
# # def get_golfer_endpoint(golfer_id):
# #     """Endpoint to get single golfer"""

# #     golfer = Golfer.query.get_or_404(golfer_id)

# #     return jsonify(golfer = golfer.serialize()), 200

# # @app.route("/golfantasy/api/tournaments", methods=["GET"])
# # def get_all_tournaments_endpoint():
# #     """Endpoint to get all tournaments"""

# #     tournaments = Tournament.query.all()

# #     return jsonify(tournaments=[tournament.serialize() for tournament in tournaments])

# # @app.route("/golfantasy/api/tournaments/<int:tournament_id>", methods=["GET"])
# # def get_single_tournament_endpoint(tournament_id):
# #     """Endpoint to get single tournament"""

# #     tournament = Tournament.query.get_or_404(tournament_id)

# #     return jsonify(tournament=tournament.serialize())



# # *******************************************************************************************************************************
# #GOLFER VIEWS
# #These views are not utilized

# # @app.route("/golfantasy/golfers/<int:golfer_id>")
# # def show_golfer(golfer_id):
# #     """Show golfer details"""

# #     if not g.user:
# #             return redirect(url_for(show_homepage))
    
# #     golfer = Golfer.query.get_or_404(golfer_id)
# #     user = User.query.get(g.user.id)

# #     return render_template("/golfer/golfer.html", golfer=golfer, user=user)

# # @app.route("/golfantasy/golfers")
# # def show_golfers():
# #     """Show golfers """

# #     if not g.user:
# #             return redirect(url_for(show_homepage))
    
# #     golfers = Golfer.query.all()
# #     user = User.query.get(g.user.id)

# #     return render_template("/golfer/golfers.html", golfers=golfers, user=user)


