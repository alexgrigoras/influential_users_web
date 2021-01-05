from utilities.auth import (
    User,
    PasswordChange,
    UserSearches,
    add_user,
    show_users,
    user_exists
)
from utilities.config import engine


# engine is open to sqlite///users.db

def create_table(model, engine):
    model.metadata.create_all(engine)


# create the tables
create_table(User, engine)
create_table(PasswordChange, engine)
create_table(UserSearches, engine)

# add a test user to the database
first = 'test'
last = 'test'
email = 'test@test.com'
password = 'test'
add_user(first, last, password, email, engine)

# show that the users exists
show_users(engine)

# confirm that user exists
print(user_exists(email, engine))
