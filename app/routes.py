from datetime import date
import requests
import textwrap
import time

from app import app, db

def pre(s: str):
    import html
    return '<pre>{}</pre>'.format(html.escape(s))

def count_months(start: date, end=None):
    end = end or date.today()
    years = end.year - start.year
    months = end.month - start.month
    months += years * 12
    return months

@app.route('/')
def index():
    from .models import Consumer, Payment
    consumers = db.session.query(Consumer).all()
    start = Payment.get_start()
    months = count_months(start)
    sep = '\n' + '=' * 10 + '\n'
    res = f'Grand total = {Payment.get_total()}€'
    res += sep
    res += f'Running since {start} ({months} months), spent {months * 22.79}€'
    res += sep
    res += '\n\n'.join(f'{x}\n{x.get_missing_string()}' for x in consumers)
    return pre(res)

def get_report(name):
    from .models import Consumer
    consumer = db.session.get(Consumer, name)
    res = str(consumer)
    res += '\n' + consumer.get_missing_string()
    res += '\n\n' + '\n'.join(map(str, reversed(consumer.payments)))
    return res

@app.route('/<name>')
def consumer(name):
    return pre(get_report(name))

def execute_webhook(url, content):
    return requests.post(url, json={
        'username': 'Laffey automated report',
        'avatar_url': 'https://laffey.tina.moe/laffey-chibi.png',
        'content': content,
    })

@app.route('/<name>/discord/')
def send_report(name, url=None):
    CHUNK_SIZE = 1900 # Discord max is 2000
    from .models import Consumer
    consumer = db.session.get(Consumer, name)
    url = url or consumer.webhook
    if not url:
        return 'No webhook URL for this user'
    report = get_report(name)
    results = []
    results.append(execute_webhook(
        url,
        'Commander... Laffey is here to bring you your report...'
        '\nIf you notice anything weird or out of order please report back to Tina... Zzz...'
        '\nYou can do so directly in this channel.'
    ))
    while report:
        chunk = report[:CHUNK_SIZE]
        results.append(execute_webhook(url, f'```\n{chunk}\n```'))
        report = report[CHUNK_SIZE:]
        if report:
            time.sleep(1)
    return pre('\n'.join(f'{x} {x.content.decode()}' for x in results))

@app.route('/<name>/discord/test')
def send_report_to_test_channel(name):
    import config
    return send_report(name, config.TEST_WEBHOOK)
