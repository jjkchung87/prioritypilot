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

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False

class UserViewTestCase(TestCase):
    """Test views for users."""

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
    
    def test_show_user_details(self):
        """Test user details view"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.test_user_1.id
            resp = c.get(f"/golfantasy/users/{self.test_user_1.id}")

            self.assertEqual(resp.status_code, 200)
            self.assertIn("arlo_chung", str(resp.data))

