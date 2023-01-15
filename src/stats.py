import src.tokenhandler
from src.data import data, save_data
from src.error import InputError, AccessError
from src import dm, channel, channels, message, auth

from datetime import datetime


def user_stat_v1(token):
    '''
    Provides a list of all the required statics about the Dreams user
    
    Arguments:
        token (str)- token for the user in UNSW Dreams

    Exceptions:
        InputError - Invalid token

    Return Value:
        list of all the channels, DM's and messages the user is part of along with the utilization_rate

    '''
    auth_user_id = src.tokenhandler.check_token(token)['user_id']

    stats = {}
    for user in data['users']:
        if user['user_id'] == auth_user_id:
            stats = user['stats']

    num_channels_joined = stats['channels_joined'][-1]['num_channels_joined']
    num_dms_joined = stats['dms_joined'][-1]['num_dms_joined']
    num_messages_sent = stats['messages_sent'][-1]['num_messages_sent']

    num_dreams_channels = len(data['channels'])
    num_dreams_dms = len(data['dms'])
    num_dreams_msgs = len(data['messages'])

    involvement_top = (num_channels_joined + num_dms_joined + num_messages_sent)
    involvement_bot = (num_dreams_channels + num_dreams_dms + num_dreams_msgs)

    stats['involvement_rate'] = 1

    if involvement_bot != 0:
        stats['involvement_rate'] = involvement_top/involvement_bot
    
    return {'user_stats': stats}

def users_stats_v1(token):
    '''
    Provide a list of all channels, dms, messages that exist in UNSW Dreams
    
    Arguments:
        token (str)- token for the aut_user_id who has requested the use of this function 

    Exceptions:
        InputError - Invalid token

    Return Value:
        list of all the channels, DM's and messages that exists in UNSW Dreams along with the utilization_rate

    '''
    src.tokenhandler.check_token(token)

    num_users_who_have_joined_at_least_one_channel_or_dm = 0
    
    for user in data['users']:
        user_token = src.auth.auth_login_v1(user['email'], user['password'])['token']
        if len(src.channels.channels_list_v1(user_token)['channels']) != 0 or len(src.dm.dm_list_v1(user_token)['dms']) != 0:
            num_users_who_have_joined_at_least_one_channel_or_dm += 1

        src.auth.logout_v1(user_token)

    total_num_users = len(data['users'])
    
    utilization_rate = num_users_who_have_joined_at_least_one_channel_or_dm / total_num_users

    num_channels_exist = len(data['channels'])
    num_dms_exist = len(data['dms'])
    num_messages_exist = len(data['messages'])

    return{'dreams_stats': {
            'channels_exist': [num_channels_exist, datetime.now().timestamp()], 
            'dms_exist': [num_dms_exist, datetime.now().timestamp()], 
            'messages_exist': [num_messages_exist, datetime.now().timestamp()], 
            'utilization_rate': utilization_rate
        }
    }

