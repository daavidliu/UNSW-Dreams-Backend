import src.channel 
import src.tokenhandler
import src.message
import src.channels
from src.data import data
from src.error import InputError
from src.error import AccessError
from datetime import datetime, timedelta
import time

####################################################### HELPER FUNCTON

def channel_id_checker(channel_id):
    '''
    Checks if the channle exists in the data 
    '''
    for chnl in data['channels']:
        if chnl['channel_id'] == channel_id:
            return True

    raise InputError(description='Not a valid channel id')

def auth_user_existance_check(token, channel_id):
    '''
    checks if the user exists in the channel
    '''
    auth_user_id = src.tokenhandler.check_token(token)['user_id']

    current_channel = src.channels.specific_channel(channel_id)
    if auth_user_id in current_channel['all_members']:
        return True

    raise AccessError(description='User is not in the channel')

##################################################### START ######################################
def standup_start_v1(token, channel_id, length):
    '''
    For the given channel_id the functions makes a standup condition under the auth_user_id for a
    specific duration of time. During this time all the messiges sent using standup_send will be sent
    to data['messages'], under the auth_user_id 
    Arguments:
        auth_user_id(TOKEN)  -  token of the authorised usuer 
        channel_id(int)       -  channel id for the channel the active standup is running 
        length(int)         -  time in seconds, for how long the function will run

    Exceptions:
        InputError - channel id is not valid 
                    - an  active standup is currenty running in the channel with channel_id
        AcessError - The auth user is not member of the channel

    Return Value
        { time_finish } in seconds

    '''
    src.tokenhandler.check_token(token)['user_id']

    #checks for valid channel id
    channel_id_checker(channel_id)

    #checks for authuser existance
    auth_user_existance_check(token, channel_id)
    
    current_channel = src.channels.specific_channel(channel_id)
    end_time = (datetime.now() + timedelta(0,length)).timestamp()

    if current_channel['standup_time'] < datetime.now().timestamp():
        #standup is currently inactive
        current_channel['standup_queue_id'] = src.message.message_sendlater_v1(token, channel_id, '', end_time)['message_id']
        current_channel['standup_time'] = end_time
    
        return{'time_finish': end_time}

    raise InputError(description='Active channel is currently running')
    

############################################################# ACTIVE ############################### 
def standup_active_v1(token, channel_id):
    '''
    Checks if an active standup is currently going on or not, if yes then it return the status of the channel
    and the time at which the standup will end   
    Arguments:
        auth_user_id(TOKEN)  -  token of the authorised usuer 
        channel_id(int)       -  channel id for the channel the active standup is running 

    Exceptions:
        InputError - channel id is not valid 

    Return Value
        { time_finish, standup_active } in boolian

    '''      

    src.tokenhandler.check_token(token)['user_id']

    #checks for valid channel id 
    channel_id_checker(channel_id)
    current_channel = src.channels.specific_channel(channel_id)
    auth_user_existance_check(token, channel_id)
    '''
    print(current_channel['standup_time'])
    print(datetime.now().timestamp())
    '''
    if current_channel['standup_time'] > datetime.now().timestamp(): 
        #standup is currently active
        #print('is active')
        return {
            'is_active': True, 
            'time_finish': current_channel['standup_time']
        }
    
    return {'is_active': False, 'time_finish': None}

############################################################# SEND ###########################
def standup_send_v1(token, channel_id, message):
    '''
    Takes all the messages sent by the members of the channel_id, then sends them to the data
    under the u_id of the user who started the standup   
    Arguments:
        auth_user_id(TOKEN)  -  token of the authorised usuer 
        channel_id(int)       -  channel id for the channel the active standup is running 
        message(strng)         -  content which the member wants to add in the standup queue

    Exceptions:
        InputError - channel id is not valid 
                    - message is longer than 1000 character
                    - an active standup is not currently running in the channel
        AcessError - The auth user is not member of the channel that the standup is active in  

    Return Value
        {} empty dictionary 

    '''

    #check token is valid
    auth_user_id = src.tokenhandler.check_token(token)['user_id']

    #checks for valid channel id 
    channel_id_checker(channel_id)
    auth_user_existance_check(token, channel_id)

    #finds the specific channel
    current_channel = src.channels.specific_channel(channel_id)

    #checks if there is an active standup
    if current_channel['standup_time'] < datetime.now().timestamp(): 
        raise InputError(description='An active standup is not currently running in this channel')
    
    #checks if message length exiceds 1000 characters or not
    if len(message) > 1000:
        raise InputError(description='message is too long')

    senders_name = src.user.user_profile(token, auth_user_id)['user']['handle_str']

    for msg in data['messages']:
        if msg['message_id'] == current_channel['standup_queue_id']:
            if msg['message'] == '':
                msg['message'] = senders_name + ': ' + message
            else:
                msg['message'] = msg['message'] + '\n' + senders_name + ': ' + message
    
    return {}