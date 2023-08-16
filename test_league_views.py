import os
from unittest import TestCase
from sqlalchemy import exc
from models import db, User, League, Team  # Import your models
from datetime import datetime
from urllib.parse import urlencode


# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///golfantasy-test"

# Now we can import app

from app import app, CURR_USER_KEY  # Import the app instance


# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False

class LeagueViewsTestCase(TestCase):
    """Tests for Leagues views."""

    def setUp(self):
        """Create test client, add sample data."""
        
        db.drop_all()
        db.create_all()

        self.client = app.test_client()

        # Add test users
        username_1 = "arlo_chung"
        email_1 = "arlo@dog.com"
        first_name_1 = "Arlo"
        last_name_1 = "Chung"
        password_1 = "arlo123"

        test_user_1 = User.signup(username_1, email_1, first_name_1, last_name_1, password_1)
        test_user_1.id=1

        self.test_user_1 = test_user_1
        self.test_user_1_id = test_user_1.id

        username_2 = "harper_chung"
        email_2 = "harper@human.com"
        first_name_2 = "Harper"
        last_name_2 = "Chung"
        password_2 = "harper123"

        test_user_2 = User.signup(username_2, email_2, first_name_2, last_name_2, password_2)
        test_user_2.id=2

        self.test_user_2 = test_user_2
        self.test_user_2_id = test_user_2.id

        db.session.commit()

        # Set up Leagues


        league_name = "Available Pre-draft Private League"
        start_date = "2023-08-31"
        end_date = "2023-9-30"
        privacy = "private"
        max_teams = 2
        golfer_count = 3
        league_manager_id = test_user_1.id
        draft_completed = False
        available_pre_draft_private_league = League.create_new_league(league_name, start_date, end_date, privacy, max_teams, golfer_count, league_manager_id, draft_completed)
        entry_code = "ABC123"
        available_pre_draft_private_league.entry_code = entry_code
        self.available_pre_draft_private_league = available_pre_draft_private_league

        league_name = "Available Pre-draft Public League"
        start_date = "2023-08-31"
        end_date = "2023-9-30"
        privacy = "public"
        max_teams = 2
        golfer_count = 3
        league_manager_id = test_user_1.id
        draft_completed = False
        available_pre_draft_public_league = League.create_new_league(league_name, start_date, end_date, privacy, max_teams, golfer_count, league_manager_id, draft_completed)
        entry_code = "ABC123"
        available_pre_draft_public_league.entry_code = entry_code
        self.available_pre_draft_public_league = available_pre_draft_public_league

        league_name = "Full Pre-draft Public League"
        start_date = "2023-08-31"
        end_date = "2023-9-30"
        privacy = "public"
        max_teams = 1
        golfer_count = 3
        league_manager_id = test_user_1.id
        draft_completed = False
        full_pre_draft_public_league = League.create_new_league(league_name, start_date, end_date, privacy, max_teams, golfer_count, league_manager_id, draft_completed)
        entry_code = "ABC123"
        full_pre_draft_public_league.entry_code = entry_code
        self.full_pre_draft_public_league = full_pre_draft_public_league

        league_name = "In-draft League"
        start_date = datetime.utcnow()
        end_date = "2023-9-30"
        privacy = "public"
        max_teams = 2
        golfer_count = 5
        league_manager_id = test_user_1.id
        draft_completed = False
        in_draft_league = League.create_new_league(league_name, start_date, end_date, privacy, max_teams, golfer_count, league_manager_id, draft_completed)
        self.in_draft_league = in_draft_league

        league_name = "In-play League"
        start_date = "2023-07-01"
        end_date = "2023-8-31"
        privacy = "public"
        max_teams = 4
        golfer_count = 3
        league_manager_id = test_user_1.id
        draft_completed = True
        in_play_league = League.create_new_league(league_name, start_date, end_date, privacy, max_teams, golfer_count, league_manager_id, draft_completed)
        self.in_play_league = in_play_league

        league_name = "End-play League"
        start_date = "2023-06-15"
        end_date = "2023-8-05"
        privacy = "public"
        max_teams = 4
        golfer_count = 4
        league_manager_id = test_user_1.id
        draft_completed = True
        end_play_league = League.create_new_league(league_name, start_date, end_date, privacy, max_teams, golfer_count, league_manager_id, draft_completed)
        self.end_play_league = end_play_league

    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res
    
    def test_leagues_first_page(self):
        """Test seeing first page of Leagues"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.test_user_1.id
            resp = c.get(f"/golfantasy/leagues")

            self.assertEqual(resp.status_code, 200)
            self.assertIn("<h3>Create or Join a League!</h3>", str(resp.data))
    
    def test_leagues_first_page_unauthorized(self):
        """Test seeing first page of Leagues"""

        with self.client as c:
            resp = c.get(f"/golfantasy/leagues", follow_redirects=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("<h2>Get <em>ready</em> to join the ultimate <br> <em>golf fantasy league</em></h2>", str(resp.data))


    def test_league_creation_success(self):
        """Test successful creation of league"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.test_user_1.id
            data = {
                "league_name": "New league",
                "start_date": "2023-09-01",
                "end_date": "2023-10-31",
                "privacy": "public",
                "max_teams": 2,
                "golfer_count": 3,
                "league_manager_id": self.test_user_1.id  # Make sure you pass the ID here
            }
            resp = c.post("/golfantasy/leagues/create", data=urlencode(data), content_type='application/x-www-form-urlencoded', follow_redirects=True)

        self.assertEqual(resp.status_code, 200)
        self.assertIn("Create a Team!", str(resp.data))

    # def test_private_league_join_success(self):
    #     """Test successful join of league"""

    #     with self.client as c:
    #         with c.session_transaction() as sess:
    #             sess[CURR_USER_KEY] = self.test_user_1.id
    #         data = {
    #             "league_name" : self.available_pre_draft_private_league.league_name,
    #             "entry_code" : self.available_pre_draft_private_league.entry_code
    #         }
    #         resp = c.post("/golfantasy/leagues/join", data=urlencode(data), content_type='application/x-www-form-urlencoded', follow_redirects=True)

    #     self.assertEqual(resp.status_code, 200)
    #     self.assertIn("Create a Team!", str(resp.data))
 
    # def test_private_league_join_unsuccessful(self):
    #     """Test unsuccessful join of league"""

    #     with self.client as c:
    #         with c.session_transaction() as sess:
    #             sess[CURR_USER_KEY] = self.test_user_1.id
    #         data = {
    #             "league_name" : self.available_pre_draft_private_league.league_name,
    #             "entry_code" : "WRONG ENTRY CODE"
    #         }
    #         resp = c.post("/golfantasy/leagues/join", data=urlencode(data), content_type='application/x-www-form-urlencoded', follow_redirects=True)

    #     self.assertEqual(resp.status_code, 200)
    #     self.assertIn("Invalid league name / entry code. Please try again.", str(resp.data))

    def create_team(self, league):
        """Create team for test user 1 in a given league"""

        team = Team(team_name="Test User 1 Team",
                    user_id=self.test_user_1.id,
                    league_id=league.id)

        db.session.add(team)
        db.session.commit()
    
    def test_going_to_league_lobby(self):
        """Test going to league lobby"""

        testing_league = self.available_pre_draft_private_league

        self.create_team(testing_league)

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.test_user_1.id
            
            resp = c.get(f"/golfantasy/leagues/{testing_league.id}")
        
        self.assertEqual(resp.status_code, 200)
        self.assertIn("Lobby",str(resp.data))

        
    def test_going_to_league_draft(self):
        """Test going to league draft"""

        testing_league = self.in_draft_league

        self.create_team(testing_league)

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.test_user_1.id
            
            resp = c.get(f"/golfantasy/leagues/{testing_league.id}")
        
        self.assertEqual(resp.status_code, 200)
        self.assertIn("<h4>Draft Order</h4>",str(resp.data))

        
    def test_going_to_league_dash(self):
        """Test going to league dash"""

        testing_league = self.in_play_league

        self.create_team(testing_league)

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.test_user_1.id
            
            resp = c.get(f"/golfantasy/leagues/{testing_league.id}")
        
        self.assertEqual(resp.status_code, 200)
        self.assertIn("<h4>League Leaderboard</h4>",str(resp.data))

        