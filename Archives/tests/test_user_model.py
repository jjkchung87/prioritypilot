import os
from unittest import TestCase
from sqlalchemy import exc
from Archives.models import db, User, League  # Import your models


# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///golfantasy-test"

# Now we can import app

from app import app, CURR_USER_KEY  # Import the app instance

db.create_all()

class UserModelTestCase(TestCase):
    """Test models for users."""

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

     
    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res
    
    def test_user_model(self):
        """Does basic model work?"""

        u = User(
            email="test@test.com",
            username="testuser",
            first_name="test",
            last_name="test",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        # User should have no leagues or teams
        self.assertEqual(len(u.leagues), 0)
        self.assertEqual(len(u.teams), 0)

    def test_duplicate_username_signup(self):
        """Test duplicate username signup"""
        
        username = "arlo_chung"
        email = "arlo@dog.com"
        first_name = "Arlo"
        last_name = "Chung"
        password = "arlo123"

        with self.assertRaises(exc.IntegrityError):
            u = User.signup(username, email, first_name, last_name, password)
            db.session.commit()  # This line will not be reached if IntegrityError is raised


    def test_successful_authentication(self):
        """Test successful authentication"""
        
        password = "arlo123"

        u = User.authenticate(self.test_user_1.username, password)

        self.assertIsNotNone(u)
        self.assertEqual(u.id, self.test_user_1.id)
    
    def test_invalid_username(self):
        """Test invalid username"""
        self.assertFalse(User.authenticate("badusername", "password"))

    def test_wrong_password(self):
        """Test invalid password"""
        self.assertFalse(User.authenticate(self.test_user_1.username, "badpassword"))

    def test_convert_to_lowercase(self):
        """Test converting username to lowercase"""

        u = User(
            email="test@test.com",
            username="TestUseR",
            first_name="test",
            last_name="test",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        self.assertTrue(u.username == "testuser")

    def test_update_password(self):
        """Test updating a password"""

        self.test_user_1.update_password("arlo123","arlo789")
        db.session.commit()

        self.assertTrue(User.authenticate(self.test_user_1.username,"arlo789"))

    