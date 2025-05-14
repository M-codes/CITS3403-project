import unittest
from datetime import datetime
from app import create_app, db
from app.models import User, DataPoint, SharedPlot, DataShare

class ModelTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app({
            'TESTING': True,
            'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
            'WTF_CSRF_ENABLED': False
        })
        print("Using DB:", self.app.config['SQLALCHEMY_DATABASE_URI'])
        self.client = self.app.test_client()

        with self.app.app_context():
            db.create_all()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_user_creation(self):
        with self.app.app_context():
            user = User(email='user@example.com', password_hash='hashed123')
            db.session.add(user)
            db.session.commit()
            self.assertEqual(User.query.count(), 1)
            self.assertEqual(User.query.first().email, 'user@example.com')

    def test_datapoint_creation(self):
        with self.app.app_context():
            user = User(email='dp@example.com', password_hash='123')
            db.session.add(user)
            db.session.commit()

            dp = DataPoint(region='Testland', date=datetime(2024, 5, 1).date(), value=42.5, user_id=user.id)
            db.session.add(dp)
            db.session.commit()

            self.assertEqual(DataPoint.query.count(), 1)
            self.assertEqual(DataPoint.query.first().region, 'Testland')

    def test_shared_plot(self):
        with self.app.app_context():
            user = User(email='plot@example.com', password_hash='pass')
            db.session.add(user)
            db.session.commit()

            plot = SharedPlot(
                plot_filename='plot1.png',
                comment='This is important',
                email='plot@example.com',
                user_id=user.id,
                title='Peak Cases'
            )
            db.session.add(plot)
            db.session.commit()

            self.assertEqual(SharedPlot.query.count(), 1)
            self.assertEqual(SharedPlot.query.first().title, 'Peak Cases')

    def test_data_share_relationship(self):
        with self.app.app_context():
            owner = User(email='owner@example.com', password_hash='pw')
            recipient = User(email='recipient@example.com', password_hash='pw')
            db.session.add_all([owner, recipient])
            db.session.commit()

            dp = DataPoint(region='SharedRegion', date=datetime.utcnow().date(), value=9.9, user_id=owner.id)
            db.session.add(dp)
            db.session.commit()

            share = DataShare(owner_id=owner.id, recipient_id=recipient.id, data_id=dp.id)
            db.session.add(share)
            db.session.commit()

            self.assertEqual(DataShare.query.count(), 1)
            self.assertEqual(DataShare.query.first().owner.email, 'owner@example.com')
            self.assertEqual(DataShare.query.first().recipient.email, 'recipient@example.com')
            self.assertEqual(DataShare.query.first().data_point.region, 'SharedRegion')
