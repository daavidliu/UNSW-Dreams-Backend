import src.tokenhandler
from src.data import data
from src.data import save_data
from src.error import InputError
from src.auth import  check_email, check_email_registered
from datetime import timezone, datetime

def user_profile(token, u_id):
    if src.tokenhandler.check_token(token) != {}:
        #if token is valid, return user details
        for user in data['users']:
            if user['user_id'] == u_id:
                return {'user' : {
                            'u_id' : user['user_id'],
                            'email' : user['email'],
                            'name_first' : user['name_first'],
                            'name_last' : user['name_last'],
                            'handle_str' : user['handle_str'],
                            'profile_img_url': user['profile_img_url'],
                            }
                        }
    
    return {}

def user_profile_setname(token, name_first, name_last):
    checked_token = src.tokenhandler.check_token(token)

    #first_name check
    if len(name_first) > 50 or len(name_first) < 1:
        raise InputError(description='Invalid first name!')

    #last_name_check
    if len(name_last) > 50 or len(name_last) < 1:
        raise InputError(description='Invalid second name!')

    if checked_token != {}:
        for user in data['users']:
            if user['user_id'] == checked_token['user_id']:
                user['name_first'] = name_first
                user['name_last'] = name_last
                save_data()
        #if token is valid, change name

    return {
    }

def user_profile_setemail(token, email):
    checked_token = src.tokenhandler.check_token(token)
    check_email_registered(email)
    check_email(email)
    if checked_token != {}:
        #if token is valid, return user details
        for user in data['users']:
            if user['user_id'] == checked_token['user_id']:
                user['email'] = email
                save_data()
    return {
    }

def user_profile_sethandle(token, handle_str):
    checked_token = src.tokenhandler.check_token(token)
    if len(handle_str) < 3:
        raise InputError(description='handle too short')
    elif len(handle_str) > 20:
        raise InputError(description='handle too short')

    #check if handle is already in use
    for user in data['users']:
        if user['handle_str'] == handle_str:
            raise InputError(description='string already used')
    if checked_token != {}:
        #if token is valid, return user details
        for user in data['users']:
            if user['user_id'] == checked_token['user_id']:
                user['handle_str'] = handle_str
                save_data()
    return {
    }

def user_profile_all(token):
    checked_token = src.tokenhandler.check_token(token)
    users_list = []
    if checked_token != {}:
        for user in data['users']:
            users_list.append(
                {
                    'u_id' : user['user_id'],
                    'email' : user['email'],
                    'name_first' : user['name_first'],
                    'name_last' : user['name_last'],
                    'handle_str' : user['handle_str'],
                    'profile_img_url' : user['profile_img_url'],
                }
            )

    return {'users' : users_list}

