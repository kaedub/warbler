"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase

from models import db, User, Message, FollowersFollowee

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()


class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        FollowersFollowee.query.delete()

        #########################################
        # What is the app test client needed for?
        # self.client = app.test_client()

    def tearDown(self):
        User.query.delete()
        Message.query.delete()
        FollowersFollowee.query.delete()
    
    def test_user_model(self):
        """Does basic model work?"""

        u = User(
            id=1,
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD",
            image_url="https://www.dictionary.com/e/wp-content/uploads/2018/03/bird-is-the-word.jpg",
            header_image_url="https://uproxx.files.wordpress.com/2015/06/family-guy-chicken.png",
            bio="I'm a bird and it's always the word!",
            location="The Chicken Coop, SF"
        )

        db.session.add(u)
        db.session.commit()

        # User should have no messages & no followers
        self.assertEqual(u.messages.count(), 0)
        self.assertEqual(u.followers.count(), 0)

        self.assertEqual(u.email, "test@test.com")
        self.assertEqual(u.username, "testuser")
        self.assertEqual(u.password, "HASHED_PASSWORD")

        # testing optional fields
        self.assertEqual(u.image_url, "https://www.dictionary.com/e/wp-content/uploads/2018/03/bird-is-the-word.jpg")
        self.assertEqual(u.header_image_url, "https://uproxx.files.wordpress.com/2015/06/family-guy-chicken.png")
        self.assertEqual(u.bio, "I'm a bird and it's always the word!")
        self.assertEqual(u.location, "The Chicken Coop, SF")

    def test_is_followed_by(self):
        """Test User followed_by method"""

        user1 = User(
            id=1,
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        user2 = User(
            id=2,
            email="test2@test.com",
            username="testuser2",
            password="HASHED_PASSWORD"
        )

        db.session.add(user1)
        db.session.add(user2)
        db.session.commit()

        user1.following.append(user2)
        db.session.commit()       

        self.assertFalse(user1.is_followed_by(user2))
        self.assertTrue(user2.is_followed_by(user1))


    def test_is_following(self):
        """Test User is_following method"""

        user1 = User(
            id=1,
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        user2 = User(
            id=2,
            email="test2@test.com",
            username="testuser2",
            password="HASHED_PASSWORD"
        )

        db.session.add(user1)
        db.session.add(user2)
        db.session.commit()

        user1.following.append(user2)
        user2.following.append(user1)
        db.session.commit()

        self.assertTrue(user1.is_following(user2))
        self.assertTrue(user2.is_following(user1))
        

    def test_get_number_of_likes(self):
        """Test the get_number_of_likes User method"""
        
        user1 = User(
            id=1,
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        user2 = User(
            id=2,
            email="test2@test.com",
            username="testuser2",
            password="HASHED_PASSWORD"
        )

        msg = Message(
            id=1,
            text="testuser message here",
            user_id=1
        )

        db.session.add(user1)
        db.session.add(user2)
        db.session.add(msg)
        db.session.commit()

        user2.messages_liked.append(msg)

        db.session.commit()

        self.assertEqual(user2.get_number_of_likes(), 1)
        self.assertEqual(user1.get_number_of_likes(), 0)


    def test_signup(self):
        """Test User signup method"""
        
        new_user = User.signup(
            username="newbuser", 
            email="newbie@nb.com", 
            password="noobstyle"
        )

        # db.session.commit()

        self.assertIsInstance(new_user, User)

        # self.assertEqual(new_user, User.query.get(3))

        self.assertEqual(new_user.username, "newbuser")
        self.assertEqual(new_user.email, "newbie@nb.com")
        self.assertNotEqual(new_user.password, "noobstyle")
    
    def test_verify_password(self):
        """Test User verify_password method"""

        new_user = User.signup(
            username="newbuser", 
            email="newbie@nb.com", 
            password="noobstyle"
        )

        db.session.add(new_user)
        db.session.commit()

        self.assertTrue(new_user.verify_password("noobstyle"))

    def test_authenticate(self):
        """Test User authenticate method"""

        new_user = User.signup(
            username="newbuser", 
            email="newbie@nb.com", 
            password="noobstyle"
        )

        db.session.add(new_user)
        db.session.commit()

        auth_user = new_user.authenticate(username="newbuser", password="noobstyle")

        self.assertIsInstance(auth_user, User)
        self.assertEqual(auth_user.username, "newbuser")
