try:
    import secrets
    DATABASE_URL = secrets.DATABASE_URL
    SECRET_KEY = secrets.SECRET_KEY
except:
    import os
    DATABASE_URL = os.environ["DATABASE_URL"]
    SECRET_KEY = os.environ["SECRET_KEY"]
