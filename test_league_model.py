import os
from unittest import TestCase
from sqlalchemy import exc
from models import db, User, League  # Import your models
from datetime import datetime


# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///golfantasy-test"

# Now we can import app

from app import app, CURR_USER_KEY  # Import the app instance

db.create_all()

class UserModelTestCase(TestCase):
    """Tests for Leagues model."""

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
    
    def test_duplicate_league(self):
        """Test creating a duplicate le"""
        league_name = "Full Pre-draft Public League"
        start_date = "2023-08-15"
        end_date = "2023-9-30"
        privacy = "private"
        max_teams = 1
        golfer_count = 3
        league_manager_id = self.test_user_1.id
        draft_completed = False

        with self.assertRaises(exc.IntegrityError):
            dup_league= League.create_new_league(league_name, start_date, end_date, privacy, max_teams, golfer_count, league_manager_id, draft_completed)
            db.session.commit()  # This line will not be reached if IntegrityError is raised

    def test_valid_authentication(self):
        """test valid league authentication"""

        l = League.authenticate(self.available_pre_draft_private_league.league_name, self.available_pre_draft_private_league.entry_code)

        self.assertIsNotNone(l)
        self.assertEqual(l.id, self.available_pre_draft_private_league.id)
    
    def test_invalid_authentication(self):
        """test valid league authentication"""

        invalid_entry_code = "INVALID KEY"
        self.assertFalse(League.authenticate(self.available_pre_draft_private_league.league_name, invalid_entry_code))

    def test_status(self):
        """test statuses of leagues"""
        self.assertEqual(self.available_pre_draft_private_league.status,"pre-draft")
        self.assertEqual(self.in_draft_league.status,"in-draft")
        self.assertEqual(self.in_play_league.status,"in-play")
        self.assertEqual(self.end_play_league.status,"end-play")

def test_get_available_public_leagues(self):
    """test getting available public leagues"""

    leagues = self.test_user_2.get_available_public_leagues()

    self.assertIn(self.available_pre_draft_public_league.id, [league[0] for league in leagues])

    def test_valid_join(self):
        """test joining of league"""

        # self.assertTrue(self.available_pre_draft_private_league.join_validation(self.test_user_2)['success'])
        self.assertEqual(self.full_pre_draft_public_league.join_validation(self.test_user_2)['msg'],'Maximum capacity reached in this league.')
        self.assertEqual(self.in_draft_league.join_validation(self.test_user_2)['msg'],'Too late to join league.')
        self.assertEqual(self.in_play_league.join_validation(self.test_user_2)['msg'],'Too late to join league.')
        self.assertEqual(self.end_play_league.join_validation(self.test_user_2)['msg'],'Too late to join league.')
        self.assertEqual(self.available_pre_draft_private_league.join_validation(self.test_user_1)['msg'],'You are already part of this league!')
