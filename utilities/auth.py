import random
from datetime import datetime, timedelta
from functools import wraps

import dash_core_components as dcc
import dash_html_components as html
import shortuuid
from flask_login import current_user
from flask_sqlalchemy import SQLAlchemy
from mailjet_rest import Client
from sqlalchemy import Table
from sqlalchemy.sql import select, and_
from werkzeug.security import generate_password_hash

from application.message_logger import MessageLogger
from utilities.keys import *

db = SQLAlchemy()
Column, String, Integer, DateTime = db.Column, db.String, db.Integer, db.DateTime

ml = MessageLogger('auth')
logger = ml.get_logger()


class User(db.Model):
    id = Column(Integer, primary_key=True)
    first = Column(String(100))
    last = Column(String(100))
    email = Column(String(100), unique=True)
    password = Column(String(100))


def user_table():
    return Table('user', User.metadata)


def add_user(first, last, password, email, engine):
    table = user_table()
    hashed_password = generate_password_hash(password, method='sha256')

    values = dict(
        first=first,
        last=last,
        email=email,
        password=hashed_password
    )
    statement = table.insert().values(**values)

    try:
        conn = engine.connect()
        conn.execute(statement)
        conn.close()
        return True
    except:
        return False


def show_users(engine):
    table = user_table()
    statement = select([table.c.first, table.c.last, table.c.email])

    conn = engine.connect()
    rs = conn.execute(statement)

    for row in rs:
        logger.info(row)

    conn.close()


def del_user(email, engine):
    table = user_table()

    logger.info("User with email " + email + " deleted")

    try:
        delete = table.delete().where(table.c.email == email)
    except:
        return False

    conn = engine.connect()
    conn.execute(delete)
    conn.close()

    return True


def user_exists(email, engine):
    """
    checks if the user exists with email <email>
    returns
        True if user exists
        False if user exists
    """
    table = user_table()
    statement = table. \
        select(). \
        where(table.c.email == email)
    with engine.connect() as conn:
        resp = conn.execute(statement)
        ret = next(filter(lambda x: x.email == email, resp), False)
    return bool(ret)


def change_password(email, password, engine):
    if not user_exists(email, engine):
        return False

    table = user_table()
    hashed_password = generate_password_hash(password, method='sha256')
    values = dict(
        password=hashed_password
    )
    statement = table. \
        update(table). \
        where(table.c.email == email). \
        values(values)

    with engine.connect() as conn:
        conn.execute(statement)

    # success value
    return True


def change_user(first, last, email, engine):
    # if there is no user in the database with that email, return False
    if not user_exists(email, engine):
        return False

    # otherwise, that user exists; update that user's info
    table = user_table()
    values = dict(
        first=first,
        last=last,
    )
    statement = table. \
        update(table). \
        where(table.c.email == email). \
        values(values)
    with engine.connect() as conn:
        conn.execute(statement)
    # success value
    return True


class PasswordChange(db.Model):
    __tablename__ = 'password_change'
    id = Column(Integer, primary_key=True)
    email = Column(String(100))
    password_key = Column(String(6))
    timestamp = Column(DateTime())


def password_change_table():
    return Table('password_change', PasswordChange.metadata)


def send_mail(email, firstname, title, text, id):
    # send password key via email
    try:
        mailjet = Client(auth=(MAILJET_API_KEY, MAILJET_API_SECRET), version='v3.1')
        data = {
            'Messages': [
                {
                    "From": {
                        "Email": FROM_EMAIL,
                        "Name": "Influential Users"
                    },
                    "To": [
                        {
                            "Email": email,
                            "Name": firstname,
                        }
                    ],
                    "Subject": "Greetings from Influential Users App",
                    "TextPart": title,
                    "HTMLPart": text,
                    "CustomID": id
                }
            ]
        }
        result = mailjet.send.create(data=data)
        if result.status_code != 200:
            logger.warning('Request status for email sending: ' + str(result.status_code))
            logger.warning(str(result.json()))
            return False
        return True

    except Exception as e:
        logger.error("Send email error: " + str(e))
        return False


def send_password_key(email, firstname, engine):
    """
    ensure email exists
    create random 6-number password key
    send email containing that password key
    return True if that all worked
    return False if one step fails
    """

    # make sure email exists
    if not user_exists(email, engine):
        return False

    # generate password key
    key = ''.join([random.choice('1234567890') for x in range(6)])

    table = user_table()
    statement = select([table.c.first]).where(table.c.email == email)
    with engine.connect() as conn:
        resp = list(conn.execute(statement))
        if len(resp) == 0:
            return False
        else:
            first = resp[0].first

    # send email
    if not send_mail(email, first, "Password reset code",
                     "<p>Dear {},<p> <p>Your password reset code is: <strong>{}</strong>".format(firstname, key),
                     "AppResetPassword"):
        return False

    # store that key in the password_key table
    table = password_change_table()
    values = dict(
        email=email,
        password_key=key,
        timestamp=datetime.now()
    )
    statement = table.insert().values(**values)
    try:
        with engine.connect() as conn:
            conn.execute(statement)
        logger.info('Stored temporary reset password key')
    except:
        return False

    # change their current password to a random string
    # first, get first and last name
    random_password = ''.join([random.choice('1234567890') for x in range(15)])
    if change_password(email, random_password, engine):
        logger.info("Changed user " + firstname + " password")
    else:
        return False

    # finished successfully
    return True


def send_registration_confirmation(email, engine):
    """
    ensure email exists
    send confirmation email
    return True if that all worked
    return False if one step fails
    """

    # make sure email exists
    if not user_exists(email, engine):
        return False

    table = user_table()
    statement = select([table.c.first]).where(table.c.email == email)
    with engine.connect() as conn:
        resp = list(conn.execute(statement))
        if len(resp) == 0:
            return False
        else:
            first = resp[0].first

    # send email
    if not send_mail(email, first, "Registration Successful",
                     "<p>Dear {},<p> <p>Your account was successfully created".format(first),
                     "AppRegistration"):
        return False

    # finished successfully
    return True


def send_delete_confirmation(email, firstname):
    """
    send confirmation email
    return True if that all worked
    return False if one step fails
    """

    # send email
    if not send_mail(email, firstname, "Deleted Successful",
                     "<p>Dear {},<p> <p>Your account was deleted".format(firstname),
                     "AppAccountDelete"):
        return False

    # finished successfully
    return True


def send_finished_process_confirmation(email, firstname, keyword):
    """
    send finished process email
    return True if that all worked
    return False if one step fails
    """

    # send email
    if not send_mail(email, firstname, "Finished processing",
                     "<p>Dear {},<p> <p>Your processing for {} was finished".format(firstname, keyword),
                     "AppProcessing"):
        return False

    # finished successfully
    return True


def send_profile_change(email, firstname):
    """
    send profile update
    return True if that all worked
    return False if one step fails
    """

    # send email
    if not send_mail(email, firstname, "Profile updated",
                     "<p>Dear {},<p> <p>Your profile data has changed".format(firstname),
                     "AppProfileUpdate"):
        return False

    # finished successfully
    return True


def validate_password_key(email, key, engine):
    # email exists
    if not user_exists(email, engine):
        return False

    # there is entry matching key and email
    table = password_change_table()
    statement = select([table.c.email, table.c.password_key, table.c.timestamp]). \
        where(and_(table.c.email == email, table.c.password_key == key))
    with engine.connect() as conn:
        resp = list(conn.execute(statement))
        if len(resp) == 1:
            if (resp[0].timestamp - (datetime.now() - timedelta(1))).days < 1:
                logger.info('Password key is valid')
                return True
        return False


def layout_auth(mode):
    """
    if mode is 'require-authentication':
        if user is not authenticated, sends the user to login page instead of returning the output of the function
        i.e. the user needs to be logged in to see the page content (e.g. profile, home, etc.)

    if mode is 'require-nonauthentication':
        if user is authenticated, sends the user to login page instead of returning the output of the function
        i.e. the user needs to be logged out to see the page content (e.g. register, login, etc.)
    """

    def this_decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if mode == 'require-authentication':
                logger.info('User authenticated')
                if current_user.is_authenticated:
                    return f(*args, **kwargs)
                return html.Div(
                    dcc.Location(id=shortuuid.uuid(), refresh=True, pathname='/login')
                )
            else:  # mode=='require-nonauthentication':
                logger.info('User not authenticated')
                if not current_user.is_authenticated:
                    return f(*args, **kwargs)
                return html.Div(
                    dcc.Location(id=shortuuid.uuid(), refresh=True, pathname='/login')
                )

        return decorated_function

    return this_decorator
