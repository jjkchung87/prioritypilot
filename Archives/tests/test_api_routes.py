import os
from unittest import TestCase
from sqlalchemy import exc
from Archives.models import db, User, League, Team  # Import your models
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

DEFAULT_URL = 'https://hips.hearstapps.com/hmg-prod/images/gettyimages-1226623221.jpg'


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
        profile_url = DEFAULT_URL

        test_user_1 = User.signup(username_1, email_1, first_name_1, last_name_1, password_1, profile_url)
        test_user_1.id=1

        self.test_user_1 = test_user_1
        self.test_user_1_id = test_user_1.id


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

        db.session.commit()

    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res
    
    def create_team(self, league):
        """Create team for test user 1 in a given league"""

        team = Team(team_name="Test User 1 Team",
                    user_id=self.test_user_1.id,
                    league_id=league.id)
        
        team.id = 1
        
        self.team_1 = team

        db.session.add(team)
        db.session.commit()
    
    def test_authentication_success(self):
        """test successful authentication"""

        with self.client as c:
            data = {"username": "arlo_chung",
                    "password": "arlo123"}

            resp = c.post("/golfantasy/api/users/authenticate", json=data)

            self.assertEqual(resp.status_code, 200)

            self.assertEqual(resp.json['user']['username'],'arlo_chung')

    def test_invalid_credentials(self):
        """test invalid credentials"""

        with self.client as c:
            data = {'username': "arlo_chung",
                    'password': 'WRONG PASSWORD'}

            resp = c.post("/golfantasy/api/users/authenticate", json = data)

            self.assertEqual(resp.status_code, 401)
            self.assertEqual(resp.json, {
                "error": "Invalid credentials"
            })

    def test_get_user_successful(self):
        """test successfully getting a user"""

        with self.client as c:
            resp = c.get(f"/golfantasy/api/users/{self.test_user_1.id}")

            self.assertTrue(resp.status_code, 200)
            self.assertEqual(resp.json['user']['username'],'arlo_chung')

    def test_get_nonexistent_user(self):
        """test getting non-existent user"""
        
        with self.client as c:
            resp = c.get("/golfantasy/api/user/999999")

            self.assertTrue(resp.status_code, 404)
    
    def test_get_league_successful(self):
        """test successfully getting a league"""

        with self.client as c:
            resp = c.get(f"/golfantasy/api/leagues/{self.available_pre_draft_private_league.id}")

            self.assertTrue(resp.status_code, 200)
            self.assertEqual(self.available_pre_draft_private_league.league_name,resp.json['league_name'])

    def test_get_nonexistent_league(self):
        """test getting a league that doesn't exist"""

        with self.client as c:
            resp = c.get("/golfantasy/api/leagues/99999999")

            self.assertTrue(resp.status_code, 404)

    def test_get_team_successful(self):
        """test successfully getting a team"""

        self.create_team(self.available_pre_draft_private_league)
        
        with self.client as c:
            resp = c.get(f"/golfantasy/api/teams/{self.team_1.id}")

            self.assertTrue(resp.status_code, 200)
            self.assertEqual(self.team_1.team_name,resp.json['team']['team_name'])

    def test_get_nonexistent_team(self):
        """test getting a team that doesn't exist"""
        
        with self.client as c:
            resp = c.get("/golfantasy/api/teams/999999999")

            self.assertTrue(resp.status_code, 404)





