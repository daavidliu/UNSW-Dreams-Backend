from src.data import data, save_data
from src.error import InputError
from src.error import AccessError

import src.tokenhandler
from src import channel, dm, message, auth

def admin_user_remove(token, u_id):
    '''
    Given a User by their user ID, remove the user from the Dreams. Dreams owners can remove other 
    **Dreams** owners (including the original first owner). Once users are removed from **Dreams**, 
    the contents of the messages they sent will be replaced by 'Removed user'. Their profile must 
    still be retrievable with user/profile/v2, with their name replaced by 'Removed user'.

    Arguments:
        token (str)             - token for the user with owner permission
        u_id (int)              - ID number for the user being removed

    Exception:
        InputError - u_id does not refer to a valid user, the user is currently the only owner
        AcessError - The authorised user is not an owner

    Return Value:
        returns {}

    '''

    #check token is valid
    auth_id = src.tokenhandler.check_token(token)['user_id']

    #check that the auth user is an owner
    num_owners = 0
    for user in data['users']:
        if user['permission_id'] == 1 and user['handle_str'] != 'removeduser':
            num_owners += 1
        if user['user_id'] == auth_id and user['permission_id'] != 1:
            raise AccessError(description='User is not an owner!')

    #if the user is currently the only owner
    if num_owners == 1 and auth_id == u_id:
        raise InputError(description='Cannot remove the only owner!')

    #login as the user
    user = {}
    is_verified = False 
    for search_user in data['users']:
        if u_id == search_user['user_id']:
            is_verified = True 
            user = search_user
            break
    if is_verified == False: 
        raise InputError(description='U_id invalid!')
    user_token = src.auth.auth_login_v1(user['email'], user['password'])['token']
    
    #modifying messages sent by the removed user
    for message in data['messages']:
        if message['u_id'] == u_id:
            message['message'] = 'Removed user'

    #user leaves channels & dms
    channels_list = src.channels.channels_list_v1(user_token)['channels']
    for channel in data['channels']:
        if channel['channel_id'] in channels_list:
            src.channel.channel_leave_v1(user_token, channel['channel_id'])
    dms_list = src.dm.dm_list_v1(user_token)['dms']
    for dm in data['dms']:
        if dm['dm_id'] in dms_list:
            src.dm.dm_leave_v1(user_token, dm['dm_id'])

    #find user, and set user details to removed user
    user['name_first'] = 'Removed'
    user['name_last'] = 'user'
    user['email'] = 'removed@user.com'
    user['handle_str'] = 'removeduser'
    user['session_list'] = []

    save_data()

    return {}


def admin_permission_change(token, u_id, permission_id):
    '''
    Given a User by their user ID, set their permissions 
    to new permissions described by permission_id.

    Arguments:
        token (str)             - token for the user with owner permission
        u_id (int)              - ID number for the user being removed
        permission_id (int)     - 1 is owner, 2 is user

    Exception:
        InputError - u_id does not refer to a valid user, permission_id does not refer to a value permission
        AcessError - The authorised user is not an owner

    Return Value:
        returns {}

    '''

    if permission_id != 1 and permission_id != 2:
        raise InputError(description='Permission_id invalid!')

    #check token is valid
    auth_id = src.tokenhandler.check_token(token)['user_id']

    #check that the auth user is an owner
    for user in data['users']:
        if user['user_id'] == auth_id and user['permission_id'] != 1:
            raise AccessError(description='User is not an owner!')

    #find user, and set user details to removed user
    is_verified = False 
    for user in data['users']:
        if u_id == user['user_id']:
            is_verified = True
            user['permission_id'] = permission_id

    if is_verified == False: 
        raise InputError(description='U_id invalid!')

    return {}