"""User View tests."""

import os
from unittest import TestCase

from models import db, connect_db, User, Message, FollowersFollowee

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"

from app import app, CURR_USER_KEY

db.create_all()

app.config['WTF_CSRF_ENABLED'] = False

class UserViewTestCase(TestCase):
    """Test User routes."""

    def setUp(self):
        """Create est client, add sample data."""

        User.query.delete()
        Message.query.delete()
        FollowersFollowee.query.delete()

        db.session.commit()

        self.client = app.test_client()

    def test_list_users(self):
        """Test that /user route correctly shows searched users"""

        edward = User(
            id=1,
            email="ed@test.com",
            username="edward",
            password="HASHED_PASSWORD"
        )

        juan = User(
            id=2,
            email="juanton@test.com",
            username="juan",
            password="HASHED_PASSWORD"
        )

        db.session.add(edward)
        db.session.add(juan)
        db.session.commit()

        # SHOULD WE REMOVE THIS SINCE THIS IS TESTING THE USER MODEL
        # AND DATABASE MORE THAN THE VIEW FUNCTION?
        user_edward = User.query.get(1)
        user_juan = User.query.get(2)

        self.assertIsInstance(user_edward, User)
        self.assertIsInstance(user_juan, User)

        with self.client as c:
            resp = c.get('/users')
            
            self.assertEqual(resp.status_code, 200)
            self.assertIn(b'@edward', resp.data)
            self.assertIn(b'@juan', resp.data)

            resp = c.get('/users?q=ed')
            self.assertEqual(resp.status_code, 200)
            self.assertIn(b'@edward', resp.data)
            self.assertNotIn(b'@juan', resp.data)


    def test_users_show(self):
        """Test that /user/user_id shows that users profile"""

        edward = User(
            id=1,
            email="ed@test.com",
            username="edward",
            password="HASHED_PASSWORD",
            location="Oakland"
        )

        juan = User(
            id=2,
            email="juanton@test.com",
            username="juan",
            password="HASHED_PASSWORD",
            location="New York"
        )

        db.session.add(edward)
        db.session.add(juan)
        db.session.commit()

        # LETS SEE IF EDWARD FOLLOWS JUAN THAT FOLLOW/UNFOLLOW
        # BUTTON IS RIGHT
        edward.following.append(juan)
        db.session.commit()   

        with self.client as c:

            # Let's make sure our session knows we are test user "edward"
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = 1

            # Get edward's user detail page as edward
            resp = c.get('/users/1')
            
            self.assertEqual(resp.status_code, 200)
            self.assertIn(b'@edward', resp.data)
            self.assertIn(b'Oakland', resp.data)
            self.assertIn(b'Edit Profile</a>', resp.data)
            self.assertNotIn(b'@juan', resp.data)
            self.assertNotIn(b'New York', resp.data)

            # Get juan's user detail page as edward
            resp = c.get('/users/2')
            
            self.assertEqual(resp.status_code, 200)
            self.assertIn(b'@juan', resp.data)
            self.assertIn(b'New York', resp.data)
            self.assertIn(b'Unfollow</button>', resp.data)
            self.assertNotIn(b'@edward', resp.data)
            self.assertNotIn(b'Oakland', resp.data)


    def test_show_following(self):
        """Test /users/user_id/following route shows who user is following"""

        edward = User(
            id=1,
            email="ed@test.com",
            username="edward",
            password="HASHED_PASSWORD",
            location="Oakland"
        )

        juan = User(
            id=2,
            email="juanton@test.com",
            username="juan",
            password="HASHED_PASSWORD",
            location="New York"
        )

        timmy = User(
            id=3,
            email="tim@test.com",
            username="timmy",
            password="HASHED_PASSWORD",
            location="Antarctica"
        )        

        db.session.add(edward)
        db.session.add(juan)
        db.session.add(timmy)
        db.session.commit()

        # LETS SEE IF EDWARD FOLLOWS JUAN THAT FOLLOW/UNFOLLOW
        # BUTTON IS RIGHT
        edward.following.append(juan)
        db.session.commit()

        with self.client as c:

            # Let's make sure our session knows we are test user "edward"
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = 1

            # View who edward is following
            resp = c.get('/users/1/following')
            
            self.assertEqual(resp.status_code, 200)

            # test username under profile pic on left but not a
            # following card
            self.assertIn(b'@edward</h4>', resp.data)
            self.assertNotIn(b'@edward</a>', resp.data)

            #test follower cards
            self.assertIn(b'@juan', resp.data)
            self.assertNotIn(b'@timmy</a>', resp.data)  
            self.assertIn(b'Unfollow</button>', resp.data)

    def test_users_followers(self):
        """Test /users/user_id/followers route show who is following user"""

        edward = User(
            id=1,
            email="ed@test.com",
            username="edward",
            password="HASHED_PASSWORD",
            location="Oakland"
        )

        juan = User(
            id=2,
            email="juanton@test.com",
            username="juan",
            password="HASHED_PASSWORD",
            location="New York"
        )

        timmy = User(
            id=3,
            email="tim@test.com",
            username="timmy",
            password="HASHED_PASSWORD",
            location="Antarctica"
        )        

        db.session.add(edward)
        db.session.add(juan)
        db.session.add(timmy)
        db.session.commit()

        timmy.following.append(edward)
        db.session.commit()

        with self.client as c:

            # Let's make sure our session knows we are test user "edward"
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = 1

            # View edwards followers
            resp = c.get('/users/1/followers')
            
            self.assertEqual(resp.status_code, 200)

            # test username under profile pic on left but not a
            # following card
            self.assertIn(b'@edward</h4>', resp.data)
            self.assertNotIn(b'@edward</a>', resp.data)

            #test cards of followers
            self.assertNotIn(b'@juan', resp.data)
            self.assertIn(b'@timmy', resp.data)

    def test_users_likes(self):
        """Test the /users/user_id/likes page"""

        edward = User(
            id=1,
            email="ed@test.com",
            username="edward",
            password="HASHED_PASSWORD",
            location="Oakland"
        )

        juan = User(
            id=2,
            email="juanton@test.com",
            username="juan",
            password="HASHED_PASSWORD",
            location="New York"
        )

        timmy = User(
            id=3,
            email="tim@test.com",
            username="timmy",
            password="HASHED_PASSWORD",
            location="Antarctica"
        )

        db.session.add(edward)
        db.session.add(juan)
        db.session.add(timmy)
        db.session.commit()

        # POSTED BY EDWARD
        edwards_message = Message(
            id=1,
            text="test message 1",
            user_id=1
        )

        # POSTED BY TIMMY
        timmys_message = Message(
            id=2,
            text="test message 2",
            user_id=3
        )

        db.session.add(edwards_message)
        db.session.add(timmys_message)
        db.session.commit()

        # LETS LIKE SOME THINGS
        # EDWARD LIKES TIMMYS POST
        edward.messages_liked.append(Message.query.get(2))

        # JUAN LIKES EDWARDS POST
        juan.messages_liked.append(Message.query.get(1))

        db.session.commit()

        with self.client as c:

            # Let's make sure our session knows we are test user "edward"
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = 1

            # View edwards followers
            resp = c.get('/users/1/likes')
            
            self.assertEqual(resp.status_code, 200)

            #test list group items of liked posts on page
            self.assertNotIn(b'@juan', resp.data)
            self.assertIn(b'@timmy', resp.data)

            # check that only solid stars
            self.assertIn(b'class="fas fa-star', resp.data)
            self.assertNotIn(b'class="far fa-star', resp.data)

    def test_add_follow(self):
        """Test the /users/follow/user_id page"""

        edward = User(
            id=1,
            email="ed@test.com",
            username="edward",
            password="HASHED_PASSWORD",
            location="Oakland"
        )

        juan = User(
            id=2,
            email="juanton@test.com",
            username="juan",
            password="HASHED_PASSWORD",
            location="New York"
        )

        timmy = User(
            id=3,
            email="tim@test.com",
            username="timmy",
            password="HASHED_PASSWORD",
            location="Antarctica"
        )

        db.session.add(edward)
        db.session.add(juan)
        db.session.add(timmy)
        db.session.commit()

        # Edward is following Juan
        # Set Juan's user id to followee_id
        followee_id = 2

        db.session.commit()

        with self.client as c:

            # Let's make sure our session knows we are test user "edward"
            # Edward is the current logged in user
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = 1

            # Tell server to have Edward follow Juan
            resp = c.post('/users/follow/2', data={"text": "Hello"})


            # Why do we need to redefine juan and edward from the database?
            # this will not work outside the with block
            juan = User.query.get(2)
            edward = User.query.get(1)

            # Make sure it redirects
            self.assertEqual(resp.status_code, 302)
            # import pdb; pdb.set_trace()
            # Make sure Edward is a follower of Juan
            # Assert that Edwars is IN Juan's followers
            self.assertIn(edward, juan.followers)



    def test_stop_following(self):
        pass

    def test_profile(self):
        pass

    def test_delete_user(self):
        pass

    # def test_signup(self):
    #     pass

    # def test_login(self):
    #     pass

    # def test_logout(self):
    #     pass

    