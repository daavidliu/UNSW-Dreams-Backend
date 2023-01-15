from src.data import data
import src.auth
from src.data import save_data
from src.error import InputError
from src.error import AccessError
from src.channels import channels_list_v1
from datetime import datetime

#function resets the stuctures inside the data dictionary to empty
def clear_v1():
    '''
    Resets the internal data of the application to it's initial state
    
    Arguments:
        ()

    Exceptions:
        N/A

    Return Value:
        {}

    '''

    data['users'] = []
    data['channels'] = []
    data['dms'] = []
    data['messages'] = []
    data['dreams_stats'] = {
            'channels_exist': [
                {
                    'num_channels_exist': 0, 
                    'time_stamp': datetime.now().timestamp()
                }
            ],
            'dms_exist': [
                {
                    'num_dms_exist': 0, 
                    'time_stamp': datetime.now().timestamp()
                }
            ], 
            'messages_exist': [
                {
                    'num_messages_exist': 0, 
                    'time_stamp': datetime.now().timestamp()
                }
            ], 
            'utilization_rate': 1 
        }
    src.auth.reset_session_number()
    save_data()
    return {}



def search_v2(token, query_str):
    '''
    Given a query string, return a collection of messages in all of the channels/DMs 
    that the user has joined that match the query

    Arguments:
        auth_user_id(int)  -  user id of the authorised user
        query_str(string)       -  string which is to be serched in the channles/dms

    Exceptions:
        InputError - string is larger than 1000 caharaters 

    Return Value:
        list of all the messeges which query_str was part of 

    '''
    auth_user_id = src.tokenhandler.check_token(token)['user_id']
    #check if tocken is valid
    try:
        checked_token = src.tokenhandler.check_token(token)
        if checked_token == {}:
            raise AccessError(description="User id not verified!")
    except InputError as err:
        raise AccessError(description="User id not verified!") from err
    
    # checking inputerror
    if len(query_str) > 1000:
        raise InputError(description='Too long!')

    msg_list = []
    for msg in data['messages']:
        if auth_user_id == msg['u_id']:
            if query_str in msg['message']: #msg['message'].find(query_str) >=0
                msg_list.append(msg)
                break
        break

    return{
        'messages': msg_list
    }
    