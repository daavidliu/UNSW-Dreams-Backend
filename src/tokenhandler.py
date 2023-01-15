import jwt
from src.data import data
from src.error import InputError
#Token handler

#Create a token for a user

SECRET = 'blinker'

def encode_message(input):
    return jwt.encode(input, SECRET, algorithm="HS256")

def decode_message(input):
    return jwt.decode(input, SECRET, algorithms="HS256")

def generate_token(sessionID):
    #already validated user login, just generates a token
    token = encode_message(sessionID)
    return token

def check_token(token):
    '''
    Given an active token, decodes it and checks if a user has a valid session

    Arguments:
        token (str)         -   

    Return Value:
        returns user id and session id upon success
        returns an empty dictionary if it is not an active token

    '''
    try:
        decoded = decode_message(token)
        for idx, user in enumerate(data['users']):
            user['user_id'] = user['user_id'] + 1 - 1
            for session in data['users'][idx]['session_list']:
                if session == decoded['session_id']:
                    return {'user_id' : data['users'][idx]['user_id'], 'session_id': decoded['session_id']}
    except jwt.DecodeError as err:
        raise InputError(description='Token not valid!') from err

    return {}
