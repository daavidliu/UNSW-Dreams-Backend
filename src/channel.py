import src.user
import src.channels
import src.tokenhandler
from src.data import data
from src.data import save_data
from src.error import InputError
from src.error import AccessError
from src.user import user_profile

from datetime import timezone, datetime

def channel_invite_v1(token, channel_id, u_id):
    '''
    adds given user to a given channel, by another user already in that channel

    Arguments:
        token (str)             - token for the user already in the channel 
        channel_id (int)        - ID number for channel user will be added too
        u_id (int)              - ID number for the user going to be added

    Exceptions:
        InputError  - occurs when either channel_id or u_id are not valid
        AccessError - occurs when the inviting user is not already part of the channel

    Return Value:
        Returns {} on successful addition of user

    '''
    #check channel_id refers to a valid channel

    is_valid_channel = False
    for channel in data['channels']:
        if channel['channel_id'] == channel_id:
            is_valid_channel = True

    if is_valid_channel == False:
        raise InputError (description="Channel_id invalid!")

    #check token is valid
    u_id_2 = src.tokenhandler.check_token(token)['user_id']

    

    #check user_id is valid

    is_verified = False 
    for user in data['users']:
        if u_id == user['user_id']:
            is_verified = True

    if is_verified == False: 
        raise InputError (description='U_id invalid!')

    channel_name = ''

    #check auth_user is a part of the channel
    is_in_list = False
    channelList = src.channels.channels_list_v1(token)
    for channel in channelList['channels']: 
        if channel['channel_id'] == channel_id:
            is_in_list = True
            channel_name = channel['name']
    if is_in_list == False:
        raise AccessError (description="User not in channel!") 
        
    if u_id_2 == u_id:
        return {}
    #check invited user is NOT a part of the channel
    is_in_list = False
    channels = data['channels']
    for channel in channels: 
        if channel['channel_id'] == channel_id:
            for user in channel['all_members']:
                if user == u_id:
                    is_in_list = True
            if not is_in_list:
                channel['all_members'].append(u_id)
                save_data()
                break
    
    '''
    #retrieve user data
    for user in data['users']:
        if user.get('user_id') == u_id:
            user_name_first = user.get('name_first') 
            user_name_last = user.get('name_last')
            break
    '''

    handle_2 = ''

    for user in data['users']:
        if u_id_2 == user['user_id']:
            handle_2 = user['handle_str']

    stats = {}
    for user in data['users']:
        if u_id == user['user_id']:
            stats = user['stats']
            user['notifications'].append(
                {
                    'channel_id': channel_id,
                    'dm_id': -1,
                    'notification_message': handle_2 + ' added you to ' + channel_name,
                    'time_created': datetime.now().timestamp()
                }
            )
    
    num_channels_joined = stats['channels_joined'][-1]['num_channels_joined'] + 1
    stats['channels_joined'].append({
        'num_channels_joined': num_channels_joined, 
        'time_stamp': datetime.now().timestamp()
    })
    save_data()

    return {}

def channel_details_v1(token, channel_id):
    '''
    adds given user to a given channel, by another user already in that channel

    Arguments:
        auth_user_id (int)      - ID number for authorised user in channel 
        channel_id (int)        - ID number for channel details are requested from

    Exceptions:
        InputError  - occurs when either channel_id is not valid
        AccessError - occurs when the auth_user is not part of the channel

    Return Value:
        Returns {name, owner_members, all members} on successful confirmation of channel and user validity

    '''   
    #check token is valid
    u_id = src.tokenhandler.check_token(token)['user_id']

    #check channel id is valid
    is_in_list = False
    for channel in data['channels']: 
        if channel['channel_id'] == channel_id:
            is_in_list = True
            if u_id not in channel['all_members']:
                raise AccessError(description='User not part of the channel!')
            
            #passed above checks, return the details of the required channel
            name = channel.get('name')
            
            owner_members = []
            for member in channel['owner_members']:
                owner_members.append(user_profile(token, member)['user'])
            
            all_members = []
            for member in channel['all_members']:
                all_members.append(user_profile(token, member)['user'])
            return {'name': name, 'is_public': channel['is_public'], 'owner_members': owner_members, 'all_members': all_members}
    
    if not is_in_list:
        raise InputError(description='(channel/details/v2) Channel_id is invalid!')



def channel_messages_v1(token, channel_id, start):
    '''
    Given a Channel with ID channel_id that the authorised user is part of, return up to 50 messages between index "start" and "start + 50". 
    Message with index 0 is the most recent message in the channel. This function returns a new index "end" which is the value of "start + 50", 
    or, if this function has returned the least recent messages in the channel, returns -1 in "end" to indicate there are no more messages to 
    load after this return.

    Arguments:
        auth_user_id (int)      - ID number for authorised user already in channel, 
        channel_id (int)        - ID number for channel user will be added too
        start (int)             - integer to indicate start of messages

    Exceptions:
        InputError  - occurs when either channel_id or u_id are not valid, or if start is greater than the total number of messages in the channel.
        AccessError - occurs when the auth_user is not already part of the channel

    Return Value:
        Returns {messages, start, end} on successful addition of user

    '''

    messages = []

    start = int(start)

    #check token is valid
    auth_user_id = src.tokenhandler.check_token(token)['user_id']

    #check if the channel_id is valid
    is_in_list = False
    channelList = src.channels.channels_listall_v1(token)
    for channel in src.data.data['channels']: 
        if channel['channel_id'] == channel_id:
            is_in_list = True
    if is_in_list == False:
        raise InputError(description='Channel_id invalid!')

    #check if the user is a part of that channel
    is_in_list = False
    channelList = src.channels.channels_list_v1(token)
    for channel in channelList['channels']: 
        if channel['channel_id'] == channel_id:
            is_in_list = True
    if is_in_list == False:
        raise AccessError(description='User is not part of the channel!')

    

    for message in src.data.data['messages']:
        
        if message['channel_id'] == channel_id and message['time_created'] < datetime.now().timestamp():
            message_dict = {
                'message_id': message['message_id'],
                'u_id': message['u_id'],
                'message': message['message'],
                'time_created': message['time_created'],
                'reacts': [
                    {
                        'react_id': 1,
                        'u_ids': message['reacts'][0]['u_ids'],
                        'is_this_user_reacted': False
                    }
                ],
                'is_pinned': message['is_pinned']
            }
            for react in message_dict['reacts']:
                if auth_user_id in react['u_ids']:
                    react['is_this_user_reacted'] = True

            messages.append(message_dict)
    
    total = len(messages)
        

    if total < start :
        raise InputError(description='Invalid start!')

    channel_messages_v1 = {
        'messages': [],
        'start': start,
        'end': -1
    }

    counter = 0
    x = total - 1 - start

    while counter < 50 and x >= 0:
        channel_messages_v1['messages'].append(messages[x])
        counter += 1
        x -= 1

    if counter == 50:
        channel_messages_v1['end'] = start + 50
    
    return channel_messages_v1


def channel_join_v1(token, channel_id):

    '''
    Given a channel_id of a channel that the authorised user can join, add them to that channel

    Arguments:
        auth_user_id (int)      - ID number for authorised user joining the channel, 
        channel_id (int)        - ID number for the channel

    Exceptions:
        InputError  - occurs when either channel_id or u_id are not valid
        AccessError - occurs when the channel_id refers to a private channel

    Return Value:
        Returns {} on successful addition of user

    '''
    #check token is valid
    auth_user_id = src.tokenhandler.check_token(token)['user_id']

    #check for input error
    is_found_channel = False

    is_admin = False
    for user in data['users']:
        if auth_user_id == user['user_id'] and user['permission_id'] == 1:
            is_admin = True

    for channel in data['channels']:
        if channel['channel_id'] == channel_id:
            is_found_channel = True
            
            if channel['is_public'] == False and not is_admin:
                raise AccessError(description='Private channel!')

    if not is_found_channel:
        raise InputError(description='Channel_id invalid!')

    #no error, add user to list of members
    for channel in data['channels']:
        if channel['channel_id'] == channel_id:
            if auth_user_id not in channel['all_members']:
                channel['all_members'].append(auth_user_id)

    stats = {}
    for search_user in data['users']:
        if search_user['user_id'] == auth_user_id:
            stats = search_user['stats']
    num_channels_joined = stats['channels_joined'][-1]['num_channels_joined'] + 1
    stats['channels_joined'].append({
        'num_channels_joined': num_channels_joined, 
        'time_stamp': datetime.now().timestamp()
    })
    save_data()

    return {}


#functions not required fopr iteration 1

def channel_leave_v1(token, channel_id):
    '''
    given a channel  which removers the given auth_user_id for the channel with the given channel_id
    
    Arguments:
        (token)auth_user_id (int)      - ID number for authorised user leaving the channel, 
        channel_id (int)        - ID number for the channel

    Exceptions:
        InputError  - occurs when either channel_id or token are not valid
        AccessError - occurs when the  auth user is not a member of the channel

    Return Value:
        Returns {} when the user suceesfully leaves the channel


    '''
    #check token is valid
    auth_user_id = src.tokenhandler.check_token(token)['user_id']
    
    # checking for input error
    valid_channel = False
    for channel in data['channels']:
        if channel_id == channel['channel_id']:
            valid_channel = True

    if not valid_channel:
        raise InputError(description='Channel_id invalid!')

    #checking for access error
    user_not_part = False
    for channel in data["channels"]:
        if channel_id == channel['channel_id']:
            if auth_user_id in channel['owner_members'] or auth_user_id in channel['all_members']:
                user_not_part = True

    if not user_not_part:
        raise AccessError(description='User not part of the channel!')

    #Required function performing it's job
    for channel in data['channels']:
        if channel_id == channel['channel_id']:
            channel['all_members'].remove(auth_user_id)

    stats = {}
    for search_user in data['users']:
        if search_user['user_id'] == auth_user_id:
            stats = search_user['stats']
    num_channels_joined = stats['channels_joined'][-1]['num_channels_joined'] - 1
    stats['channels_joined'].append({
        'num_channels_joined': num_channels_joined, 
        'time_stamp': datetime.now().timestamp()
    })
    save_data()

    return {}

def channel_addowner_v1(token, channel_id, u_id):
    """
    given a channel  which adds the user with u_id to the channel with the given channel_id
    
    Arguments:
        (token)auth_user_id (int)      - ID number for authorised user who calls the function to add u_id, 
        channel_id (int)               - ID number for the channel
        u_id (int)                     - ID number for the user which is to be added 

    Exceptions:
        InputError  - occurs when either channel_id or u_id are not valid
                    -when the user with u_id is already an owner of the channel

        AccessError - occurs when the  auth user is not owner of "Dream"  or an owner of the channel

    Return Value:
        Returns {} when the user suceesfully leaves the channel

    """
    #check token is valid
    auth_user_id = src.tokenhandler.check_token(token)['user_id']
    
    valid_channel = False

    # checking for input error
    for channel in data['channels']:
        if channel_id == channel['channel_id']:
            valid_channel = True
            if u_id in channel['owner_members']:
                raise InputError(description='User is already an owner!')
            if auth_user_id not in channel['owner_members']:
                raise AccessError(description='You are not an owner of this channel!')
            channel['owner_members'].append(u_id)

    if not valid_channel:
        raise InputError(description='Channel_id not valid!')

    return {}

def channel_removeowner_v1(token, channel_id, u_id):
    """
    given a channel which removes the user with u_id to the channel with the given channel_id
    
    Arguments:
        (token)auth_user_id (int)      - ID number for authorised user who calls the function to add u_id, 
        channel_id (int)               - ID number for the channel
        u_id (int)                     - ID number for the user which is to be removed 

    Exceptions:
        InputError  - occurs when either channel_id or u_id are not valid
                    -when the user whith u_id is not an owner of the channel
                    -when the user is currently the only owner of the channel
                    
        AccessError - occurs when the  auth user is not owner of "Dream"  or an owner of the channel

    Return Value:
        Returns {} when the user suceesfully leaves the channel

    """
    #check token is valid
    auth_user_id = src.tokenhandler.check_token(token)['user_id']

    valid_channel = False
    for channel in data['channels']:
        if channel_id == channel['channel_id']:
            if len(channel['owner_members']) == 1:
                raise InputError(description='Cannot remove last owner!')
            if u_id not in channel['owner_members'] or auth_user_id not in channel['owner_members']:
                raise InputError(description='User is not an owner!')
            channel['owner_members'].remove(u_id)
            valid_channel = True
    
    if not valid_channel:
        raise InputError(description='Invalid Channel_id!')
        
    return {}

