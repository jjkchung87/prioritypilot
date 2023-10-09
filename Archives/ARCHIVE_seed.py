from Archives.models import db, Golfer, Tournament, TournamentGolfer, User, League, Team
from app import app
import requests

db.session.rollback()

db.session.query(User).delete()
db.session.query(League).delete()
db.session.query(Team).delete()

db.session.commit()


user_1 = User.signup(username="arlo_chung",
            first_name="Arlo",
            last_name="Chung",
            email="arlo@dog.com",
            password="arlo123")

user_2 = User.signup(username="michael_scott",
            first_name="Michael",
            last_name="Scott",
            email="michael@office.com",
            password="michael123")

user_3 = User.signup(username="rory_mcilroy",
            first_name="Rory",
            last_name="Mcilroy",
            email="rory@golfer.com",
            password="rory123")


league_1 = League.create_new_league(league_name="Public Drafted League",
                                privacy="public",
                                start_date="2023-7-25",
                                end_date="2023-8-15",
                                max_teams=5,
                                golfer_count=10,
                                draft_completed=True,
                                league_manager_id=user_1.id
                                )

league_2 = League.create_new_league(league_name="Private Undrafted League",
                                privacy="private",
                                start_date="2023-8-5",
                                end_date="2023-8-15",
                                max_teams=5,
                                golfer_count=10,
                                draft_completed=False,
                                league_manager_id=user_1.id
                                )

user_2.leagues.append(league_1)

db.session.add_all([user_1, user_2,user_3, league_1, league_2])
db.session.commit()

team_1 = Team(team_name="The Chungs",
            user_id=1,
            league_id=1
            )

team_2 = Team(team_name="The Office",
            user_id=2,
            league_id=2
            )

golfer_1 = Golfer.query.get(1)
golfer_2 = Golfer.query.get(2)
team_1.add_golfer(golfer_1.id)
team_2.add_golfer(golfer_2.id)

db.session.add_all([golfer_1, golfer_2, team_1, team_2])
db.session.commit()


