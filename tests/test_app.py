import unittest
from app import db, User

class TestUserModel(unittest.TestCase):

    def setUp(self):
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_create_user(self):
        user = User(username="johndoe", password="password", history="search history")
        db.session.add(user)
        db.session.commit()

        assert user.id is not None
        assert user.username == "johndoe"
        assert user.password == "password"
        assert user.history == "search history"

    def test_duplicate_username(self):
        user1 = User(username="johndoe", password="password1", history="search history")
        db.session.add(user1)
        db.session.commit()

        user2 = User(username="johndoe", password="password2", history="search history")
        db.session.add(user2)
        with self.assertRaises(Exception):
            db.session.commit()

    def test_missing_username(self):
        with self.assertRaises(Exception):
            user = User(password="password", history="search history")
            db.session.add(user)
            db.session.commit()

    def test_missing_password(self):
        with self.assertRaises(Exception):
            user = User(username="johndoe", history="search history")
            db.session.add(user)
            db.session.commit()

if __name__ == '__main__':
    unittest.main()

