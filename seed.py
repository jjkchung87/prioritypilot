import random
import string
from faker import Faker
from datetime import datetime, timedelta
from app import app
from models import db, Golfer, Tournament, TournamentGolfer, User, League, Team
from seed_dg import golfers_list


db.session.rollback()

db.session.query(User).delete()
db.session.query(League).delete()
db.session.query(Team).delete()

db.session.commit()

# Initialize Faker
fake = Faker()

# Create a list to store the fake users
fake_users = []

# Add test user
username = "arlo_chung"
email = "arlo@dog.com"
first_name = "Arlo"
last_name = "Chung"
password = "arlo123"

test_user = User.signup(username, email, first_name, last_name, password)

# Add test leagues

test_leagues = []

league_name = "In-draft League"
start_date = datetime.utcnow()
end_date = "2023-9-30"
privacy = "public"
max_teams = 4
golfer_count = 3
league_manager_id = test_user.id
draft_completed = False
in_draft_league = League.create_new_league(league_name, start_date, end_date, privacy, max_teams, golfer_count, league_manager_id, draft_completed)

league_name = "In-play League"
start_date = "2023-08-01"
end_date = "2023-9-30"
privacy = "public"
max_teams = 4
golfer_count = 3
league_manager_id = test_user.id
draft_completed = True
in_play_league = League.create_new_league(league_name, start_date, end_date, privacy, max_teams, golfer_count, league_manager_id, draft_completed)

db.session.add_all([in_draft_league,in_play_league])
db.session.commit()

test_leagues.append(in_draft_league)
test_leagues.append(in_play_league)

# Create 20 fake users
for i in range(2,22):
    username = f"user_{i}"
    first_name = fake.first_name()
    last_name = fake.last_name()
    email = f"{username}@example.com"
    password = f"password{i}"
    profile_url = fake.url()

    user = User.signup(username, email, first_name, last_name, password, profile_url)
    fake_users.append(user)


in_draft_league_users = fake_users[:in_draft_league.max_teams-1]
for user in in_draft_league_users:
    user.leagues.append(in_draft_league)

in_play_league_users = fake_users[in_draft_league.max_teams:in_draft_league.max_teams + in_play_league.max_teams-1]
for user in in_play_league_users:
    user.leagues.append(in_play_league)

db.session.commit()




# # Create a list to store the fake leagues
# fake_leagues = []

# # Create 10 fake leagues
# for i in range(10):
#     league_name = f"League {i}"
#     start_date = datetime.utcnow() + timedelta(days=random.randint(1, 30))
#     end_date = start_date + timedelta(days=random.randint(1, 30))
#     privacy = random.choice(["public", "private"])
#     max_teams = random.randint(4, 8)
#     golfer_count = random.randint(5, 10)
#     draft_completed = random.choice([True, False])

#     # Get a random user from the fake_users list as the league manager
#     league_manager = random.choice(fake_users)

#     # Create the league and associate the manager
#     league = League.create_new_league(league_name, start_date, end_date, privacy, max_teams, golfer_count, league_manager.id, draft_completed)
#     fake_leagues.append(league)

#     # If the league is currently either "in-draft", "in-play", or "end-play",
#     # ensure that the league manager has a team in this league
#     if league.status in ["in-draft", "in-play", "end-play"]:
#         team_name = f"{league_manager.username}'s Team (League: {league.id})"
#         team = Team(team_name=team_name, user_id=league_manager.id, league_id=league.id)
#         db.session.add(team)
#         db.session.commit()



# # Add users to each league
# user_ids = [user.id for user in User.query.all()]
# for league in fake_leagues:
#     random.shuffle(user_ids)
#     league_user_ids = user_ids[:league.max_teams]
#     for league_user_id in league_user_ids:
#         if league_user_id != league.league_manager_id:
#             user = User.query.get(league_user_id)
#             league.users.append(user)
#             db.session.commit()

# Create fake teams for each user in leagues with "in-draft," "in-play," or "end-play" status
for league in test_leagues:
    if league.status in ["in-draft", "in-play", "end-play"]:
        for user in league.users:
            team = Team(
                team_name=f"{user.username}'s Team (League: {league.league_name})",
                user_id=user.id,
                league_id=league.id
            )
            db.session.add(team)

# Create fake teams for some users in leagues with "pre-draft" status
for league in test_leagues:
    if league.status == "pre-draft":
        for user in league.users:
            if random.random() < 0.9:  # Randomly decide if the user should have a team
                team = Team(
                    team_name=f"{user.username}'s Team (League: {league.league_name})",
                    user_id=user.id,
                    league_id=league.id
                )
                db.session.add(team)

# Assuming you have already created 300 Golfer objects with their attributes from a 3rd party API.
# If you have them in a list named "golfers_list", you can directly use it here.

# Get all the leagues that are currently either "in-play" or "end-play"
play_leagues = [league for league in test_leagues if league.status in ["in-play", "end-play"]]

# Retrieve ids for existing golfers from the database

golfer_ids = [golfer.id for golfer in Golfer.query.all()]

# Assign golfers to teams in each of the "in-play" or "end-play" leagues
for league in play_leagues:
    teams = league.teams
    golfer_count = league.golfer_count

    # Randomly shuffle the list of golfers to assign to teams randomly
    random.shuffle(golfer_ids)

    # Loop through each team and assign golfers until the specified golfer_count is reached
    for team in teams:
        # Get a slice of the shuffled golfer ids list for this team
        team_golfers = golfer_ids[:golfer_count]

        # Remove the assigned golfer ids from the main list
        golfer_ids = golfer_ids[golfer_count:]

        # Add the golfers to the team and associated league
        for golfer_id in team_golfers:
            team.add_golfer(golfer_id)



# Commit the changes to the database
db.session.commit()
