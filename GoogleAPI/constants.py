# API key

API_KEY_CREDENTIALS_PATH = 'resources/api_key.txt'

# OAuth 2.0

SCOPES = [
    'https://www.googleapis.com/auth/contacts',
    'https://www.googleapis.com/auth/contacts.readonly',
    'https://www.googleapis.com/auth/plus.login',
    'https://www.googleapis.com/auth/user.addresses.read',
    'https://www.googleapis.com/auth/user.birthday.read',
    'https://www.googleapis.com/auth/user.emails.read',
    'https://www.googleapis.com/auth/user.phonenumbers.read',
    'email',
    'https://www.googleapis.com/auth/plus.profile.emails.read',
    'profile',
]
CLIENT_SECRET_PATH = 'resources/client_secret.json'
APPLICATION_NAME = 'People API Parser'
OAUTH_2_CREDENTIALS_PATH = 'resources/people-and-plus.googleapis.com-credentials.json'

# Credentials types
API_KEY_CREDENTIALS_TYPE = 'API key'
OAUTH_2_CREDENTIALS_TYPE = 'OAuth 2.0'

# Others
EMPTY_BINARY_STRING = b''
