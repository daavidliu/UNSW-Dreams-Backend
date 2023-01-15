import re
import src.tokenhandler
from src.data import data
from src.data import save_data
from src.error import InputError
from src.error import AccessError

from datetime import datetime

from flask import request

session_number = 0

def auth_login_v1(email, password):
    '''
    Given a registered users' email and password and returns their `auth_user_id` value
    Arguments:
        email (string)         -   Email Address of the user to be registered
        password(string)       -   Desired password

    Exceptions:
        InputError  - occurs when email id is not valid 
                      occurs when email id is already registered or is being used by another user 
                      Password is incorrect

    Return Value:
        Returns {auth_user_id} after sucessful login
    
    '''
    global session_number
    '''
    print("\n \n \n \n \n")
    print(data)
    print("\n \n \n \n \n")
    '''
    check_email(email)
    #checking if email is registered 
    is_verified = False
    for user in data['users']:
        if user['email'] == email:
            is_verified = True

    if not is_verified:
        raise InputError(description='Email not registered!')

    #generate new session number, and its respective token
    session_number += 1
    token = src.tokenhandler.generate_token({'session_id': session_number})
        
    for user in data['users']:
        if user['email'] == email and user['password']== password:
            #add session to user
            user['session_list'].append(session_number)
            save_data()
            return {
                'token' : token,
                'auth_user_id': user['user_id']
            }

    raise InputError(description='Wrong password!')

def auth_register_v1(email, password, name_first, name_last):
    '''
    Given a user's first and last name, email address, and password, create a new account for them. 
    This is done by creating a new user id called auth_user_id
    
    Arguments:
        email (string)         -   Email Address of the user to be registered
        password(string)       -   Desired password  
        name_first(string)     -   First name of the user 
        name_last(string)      -   Last name of the user

    Exceptions:
        InputError  - occurs when email id is not valid 
                      occurs when email id is already registered or is being used by another user 
                      Password is less than 6 characters
                      First name and Last name has more than 50 characters

    Return Value:
        Returns {auth_user_id} on successful addition of user 

    '''
    global session_number
    check_email(email)
    check_email_registered(email)

    #pass check
    if len(password) < 6:
        raise InputError (description="Password too short!")

    #first_name check
    if len(name_first) > 50 or len(name_first) < 1:
        raise InputError (description="First name invalid!")

    #last_name_check
    if len(name_last) > 50 or len(name_last) < 1:
        raise InputError (description="Last name invalid!")

    #creates a new dictonary for the user with the following keys
    user = dict.fromkeys(['user_id','handle_str', 'session_list', 'name_first', 'name_last', 'email', 'password'])


    
    #add session number to user's session list
    data['users']
    user['name_first'] = name_first
    user['name_last'] = name_last
    user['email'] = email
    user['password'] = password
    user['handle_str'] = generate_handle(name_first,name_last)
    user['session_list'] = []
    user['notifications'] = []
    user['stats'] = {
            'channels_joined': [
                {
                    'num_channels_joined': 0, 
                    'time_stamp': datetime.now().timestamp()
                }
            ],
            'dms_joined': [
                {
                    'num_dms_joined': 0, 
                    'time_stamp': datetime.now().timestamp()
                }
            ], 
            'messages_sent': [
                {
                    'num_messages_sent': 0, 
                    'time_stamp': datetime.now().timestamp()
                }
            ], 
            'involvement_rate': 0 
    }
    user['profile_img_url'] = ''
    
    try:
        #set image path
        current_path = request.url_root
        user['profile_img_url'] = current_path + 'imgurl/default.jpg'
    except:
        pass
    
    
    #list of current users 
    curr_users = data['users']
    
    current_id = (len(curr_users) + 1)
    
    #assigning user_id
    user['user_id'] = current_id

    if current_id == 1:
        user['permission_id'] = 1
    else:
        user['permission_id'] = 2

    #adding the details to data file
    data['users'].append(user)
        
    #generate new session number, and its respective token
    session_number += 1
    token = src.tokenhandler.generate_token({'session_id': session_number})
    #add session to user
    user['session_list'].append(session_number)
    save_data()
    return {
        'token' : token,
        'auth_user_id' : current_id,
    }    



def check_email(email):
    '''
    Check if given email is valid
    Arguments:
        email (string)         -   Email Address to be checked

    Exceptions:
        InputError  - occurs when email id is not valid 

    '''
    regex = '^[a-zA-Z0-9]+[\\._]?[a-zA-Z0-9]+[@]\\w+[.]\\w{2,3}$'
    if not re.search(regex,email):  
        raise InputError(description='Invalid email format!')



def check_email_registered(email):
    '''
    Check if given email has already been registered 
    Arguments:
        email (string)         -   Email Address to be checked

    Exceptions:
        InputError  - occurs when email has already been registered

    '''   
    for user in data['users']:
        if user['email'] == email:
            raise InputError (description="Email already used!")



def generate_handle(name_first, name_last):
    '''
    Generates user's handle

    Arguments:
        name_first (str)         -   users first name
        name_last (str)         -   users last name

    Return Value:
        returns the handle automatically generaemailted

    '''
    name_first = name_first.replace(' ', '')
    name_first = name_first.replace('@', '')
    name_last = name_last.replace(' ', '')
    name_last = name_last.replace('@', '')

    concatentation = name_first.lower() + name_last.lower()
    orig_handle_str = concatentation[:20]

    handle_str = orig_handle_str

    x = 0
    new_number = 0

    while x < len(data['users']):
        if handle_str == data['users'][x]['handle_str']:
            handle_str = orig_handle_str + str(new_number)
            new_number += 1
            x = -1
        x += 1
    
    return handle_str

def logout_v1(token):
    '''
    Given an active token, invalidates the token to log the user out. 
    If a valid token is given, and the user is successfully logged out, 
    it returns true, otherwise false.

    Arguments:
        token (str)         -   

    Return Value:
        returns {is_success}

    '''
    try: 
        checked_token = src.tokenhandler.check_token(token)
        if checked_token != {}:
            #token is valid, remove token from user
            for user in data['users']:
                if user['user_id'] == checked_token['user_id']:
                    user['session_list'].remove(checked_token['session_id'])
                    save_data()
                    return {'is_success': True}
    except:
        return {'is_success': False}

def reset_session_number():
    global session_number
    session_number = 0
    return None

def passwordreset_request_v1(email):
    '''
    Given an email address, if the user is a registered user, sends them an email 
    containing a specific secret code, that when entered in auth_passwordreset_reset, 
    shows that the user trying to reset the password is the one who got sent this email.

    Arguments:
        email (str)         -   email of the user.

    Return Value:
        {}

    '''
    pass

def passwordreset_rest_v1(reset_code, new_password):
    '''
    Given a reset code for a user, set that user's new password to the password provided.

    Arguments:
        reset_code (str)         -   email of the user.
        new_password (str)       -   New password for login.

    Exceptions:
        InputError  - reset code invalid, or password is less than 6 characters long.
    
    Return Value:
        {}

    '''
    pass

