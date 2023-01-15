from src.data import data
from src.data import save_data
from src.error import InputError
from src.error import AccessError
from datetime import datetime
import src.tokenhandler



def channels_list_v1(token):
    '''
    Provide a list of all channels (and their associated details) that the authorised user is part of
    
    Arguments:
        auth_user_id(int)  - user id of the authorised user

    Exceptions:
        AcessError - If user id is not verified

    Return Value:
        It returns a dictionary which contains the channel and details of the channel that the user is part of

    '''
    checked_token = src.tokenhandler.check_token(token)

    # Created a list to store the values for 'name' and 'channel_id'
    user_channel_list = []

    for channel in data['channels']:
        if checked_token['user_id'] in channel['all_members']:
            user_channel_list.append({'channel_id': channel['channel_id'], 'name': channel['name']})
    ''''
    print('channel_list is')
    print(user_zchannel_list)
    '''
    return {
        'channels' : user_channel_list 
    }
        



def channels_listall_v1(token):
    '''
    Provide a list of all channels (and their associated details)    
    Arguments:
        auth_user_id(int)  - user id of the authorised user

    Exceptions:
        AcessError - If user id is not verified

    Return Value:
        It returns a dictionary which contains ALL the channels and their associated details

    '''
    src.tokenhandler.check_token(token)
    
    # Created a list to store the values for 'name' and 'channel_id'
    channel_list = []
    
    for channel in data['channels']:

        # Copying data to temporary dictionary 
        newDetails = {
            'channel_id': channel['channel_id'],
            'name' : channel['name']
        }

        # Data  added form newDetails to 'chanel_list'
        channel_list.append(newDetails)
    

    return {
        'channels': channel_list
    }    
    
    

def channels_create_v1(token, name, is_public):
    '''
    Creates a new channel with that name that is either a public or private channel    
    Arguments:
        auth_user_id(int)  -  user id of the authorised user
        name(string)       -  Name of the channel
        is_public(boolean) -  Shows if channel is public or private

    Exceptions:
        InputError - Name is more than 20 characters
        AcessError - To check if user is registered 

    Return Value:
        It returns a dictionary which contains the channel id of the channel created.

    '''

    checked_token = src.tokenhandler.check_token(token)

    # error if name is longer than 20 characters
    if len(name) > 20:
        raise InputError(description="Name cannot be longer than 20 characters!")

    # create new dictionaries with keys as attributes of the channel

    # generate a new & unique channel_id
    id = 1
    list = channels_listall_v1(token)
    for channel in list['channels']:
        id += 1

    channel = {
                'channel_id': id, 
                'name': name, 
                'is_public': is_public, 
                'owner_members': [checked_token['user_id']], 
                'all_members': [checked_token['user_id']], 
                'standup_queue_id': -1,
                'standup_time': -1
            }

    data['channels'].append(channel)
    data['dreams_stats']['channels_exist'].append({
        'num_channels_exist': len(data['channels']), 
        'time_stamp': datetime.now().timestamp()
    })

    stats = {}
    for search_user in data['users']:
        if search_user['user_id'] == checked_token['user_id']:
            stats = search_user['stats']
    num_channels_joined = stats['channels_joined'][-1]['num_channels_joined'] + 1
    stats['channels_joined'].append({
        'num_channels_joined': num_channels_joined, 
        'time_stamp': datetime.now().timestamp()
    })
    save_data()

    return {'channel_id': id}
    
def specific_channel(channelid):
    '''
    return the channel with the unique channel id, else returns InputError.
    '''
    for chnl in data['channels']:
        if chnl['channel_id'] == channelid:
            return chnl

    raise InputError('Channel ID is not a valid channel')
    
