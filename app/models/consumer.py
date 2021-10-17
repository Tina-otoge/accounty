from datetime import date
import sqlalchemy as sa

from app import db

class Consumer(db.Base):
    name = sa.Column(sa.String, primary_key=True)
    paypal_email = sa.Column(sa.String, unique=True)
    stop_date = sa.Column(sa.Date)
    actual_start = sa.Column(sa.Date)
    webhook = sa.Column(sa.String)

    def __str__(self):
        start = self.start_date
        end = self.end_date
        nb_payments = len(self.payments)
        euros = self.total_euros
        months = self.total_months
        return f'{self.name}: From {start} to {end} | {nb_payments} payments ({months} months) | {euros}€ | Terminated: {self.stop_date is not None}'

    @property
    def start_date(self):
        if self.actual_start:
            return self.actual_start
        from app.models import Payment
        first_payment = (
            db.session.query(Payment)
            .filter_by(consumer_name=self.name)
            .order_by(Payment.date.asc())
            .first()
        )
        if not first_payment:
            return None
        return first_payment.date

    @property
    def total_euros(self):
        return sum(x.euros_amount for x in self.payments)

    @property
    def total_months(self):
        return sum(x.months_amount for x in self.payments)

    @property
    def end_date(self):
        if not self.start_date:
            return None
        months = self.start_date.month + self.total_months
        years = self.start_date.year + ((months - 1) // 12)
        months = (months - 1) % 12 + 1
        days = self.start_date.day
        return date(years, months, days)

    def get_missing_string(self):
        if not self.end_date:
            return None
        today = self.stop_date or date.today()
        years = today.year - self.end_date.year
        months = today.month - self.end_date.month
        if months < 0:
            years -= 1
            months += 12
        return f'Missing {years} years and {months} months to cover until {today}'

    def get_payments_desc(self):
        from .payment import Payment
        return db.session.query(Payment).filter_by(consumer=self).order_by(Payment.date.desc()).all()
