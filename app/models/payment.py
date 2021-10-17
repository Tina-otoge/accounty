import math
import sqlalchemy as sa
from sqlalchemy import orm

from app import db


class Payment(db.Base):
    MAX_MONTH_PRICE = 6

    id = sa.Column(sa.Integer, primary_key=True)
    paypal_transaction = sa.Column(sa.String, unique=True)
    consumer_name = sa.Column(sa.ForeignKey('consumers.name'), nullable=False)
    date = sa.Column(sa.Date)
    months_amount = sa.Column(sa.Integer, default=1)
    euros_amount = sa.Column(sa.Float)
    notes = sa.Column(sa.String)

    consumer = orm.relationship('Consumer', backref='payments')

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('months_amount', math.ceil(kwargs.get('euros_amount', 0) / self.MAX_MONTH_PRICE))
        super().__init__(*args, **kwargs)

    def __str__(self):
        return f'{self.__class__.__name__} of {self.euros_amount}€ for {self.months_amount} months on {self.date} (Notes: {self.notes}) (Transaction ID: {self.paypal_transaction})'

    @classmethod
    def get_total(cls):
        return sum(x.euros_amount for x in db.session.query(cls))

    @classmethod
    def get_start(cls):
        return db.session.query(cls).order_by(cls.date.asc()).first().date
