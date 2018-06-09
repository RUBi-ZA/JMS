import os

ENVIRONMENT = "development"

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ALLOWED_HOSTS = ['*']

TIME_ZONE = 'Africa/Johannesburg'

SECRET_KEY = '4ibn4o6g2r(9y8)tk52uc3-$g26a_jf2vc)gzqb)l^kaz&p8&g'

DB_USER = os.environ.get("DB_USER", "jms")
DB_PASS = os.environ.get("DB_PASS", "JMS>Galaxy")
DB_HOST = os.environ.get("DB_HOST", "dbserver")

ADMINS = (
    ('Your Name', 'your_email@example.com'),
)

SHARED_DIRECTORY = os.environ.get("SHARED_DIRECTORY", "/jabba/JMS/")

EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.live.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER", 'jms.rubi@outlook.com')
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD", 'JMS>Galaxy')
 
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
