import src.user
import src.tokenhandler
from src.data import data
from src.data import save_data

from src.error import InputError
from src.error import AccessError

from src.user import user_profile

from datetime import timezone, datetime


#HELPER FUNCTIONS:
# To check if dm_id is valid
def valid_dm_id(dm_id):
    '''
    Check if the dm_id id valid, i.e is there in the data['dms'] list
    Tests the exceptions
    Arguments -
        dm_id  (int)  - the dm_id of the dm

    Return Value:
        InputError - returns InputError of dm_id is invalid 
    '''
    is_valid = False
    for dm in data['dms']:
        if dm['dm_id'] == dm_id:
            is_valid = True

    if is_valid == False:
        raise InputError(description="dm_id not valid")

#To check if user is part of dm
def check_if_user_is_memember(token, dm_id):
    '''
    Check if the user is member of the dm, i.e - if the dm_id is there in the dm_list_v1 
    Tests the exceptions
    Arguments -
        dm_id  (int)  - the dm_id of the dm
        token  (str)  - a unique strings

    Return Value:
        InputError - returns AccessError of dif user is not present.
    '''
    
    auth_id = src.tokenhandler.check_token(token)['user_id']
    
    is_in_list = False
    for dm in data['dms']: 
        if dm['dm_id'] == dm_id and auth_id in dm['members']:
            is_in_list = True
    if is_in_list == False:
        raise AccessError(description="Auth User not in dm")




#DM FUNCTIONS
def dm_details_v1(token, dm_id):
    '''
    Users that are part of this direct message can view basic information about the DM
    Arguments -
        dm_id  (int)  - the dm_id of the dm
        token  (str)  - a unique strings
    
    Exceptions -
        InputError  -   dm_id is not a valid DM
        AccessError -   Authorised user is not a member of this DM with dm_id

    Return Value:
        Returns a dictionary with the basic details { name, members }
    '''
    dm_id = int(dm_id)
    #check token is valid
    src.tokenhandler.check_token(token)['user_id']

    #check if dm_id is valid
    valid_dm_id(dm_id)

    #if user is not memeber of dm
    check_if_user_is_memember(token,dm_id) 

    name = ''
    members = []

    #Find the dm in data and return name and members
    for dm in data['dms']:
        if dm.get('dm_id') == dm_id:
            name = dm.get('name')
            for member in dm['members']:
                members.append(user_profile(token, member)['user'])

            break
    
    return {
        'name': name, 
        'members': members
    }


def dm_list_v1(token):
    '''
    Returns the list of DMs that the user is a member of
    Arguments -
        dm_id  (int)  - the dm_id of the dm
        token  (str)  - a unique string
    
    Exceptions - none

    Return Value:
        Returns a dictionary with the basic details of the dm that the user is part of { dms }

    '''
    checked_token = src.tokenhandler.check_token(token)

    #create a list to store details 'name' and 'dm_id' for the user
    user_dm_list = []

    #Find user in members and add the dm_id and name of dm to the user_dm_list
    for dm in data['dms']:
        if checked_token['user_id'] in dm['members']:
            user_dm_list.append({'dm_id' : dm['dm_id'], 'name' : dm['name']})

    return {'dms': user_dm_list}


def dm_create_v1(token, u_ids):
    '''
    Create a new dm with the user_id of the token as the owner and add the list of users (with given u_ids)
    u_ids contains the user(s) that this DM is directed to, and will not include the creator. 
    The creator is the owner of the DM. 
    The key 'name' should be automatically generated based on the user(s) that is in this dm.
    The name should be an alphabetically-sorted, comma-separated list of user handles, e.g. 'handle1, handle2, handle3'.
    
    Arguments -
        u_ids  (list)  - a list of user(s) that this DM is directed to (wants to be added) and doesnt include creator
        token  (str)   - a unique string - (is the creator/owner)

    Exceptions - 
        InputError  -   if any of the u_id in u_ids list is not registered

    Return Value:
        Returns a dictionary with name of dm and dm_id of the created dm { dm_id, dm_name }
        
    '''
    #check token is valid
    checked_token = src.tokenhandler.check_token(token)


    #check if u_id is valid
    for u_id in u_ids:
        is_verified = False
        for user in data['users']:
            if u_id == user['user_id']:
                is_verified = True

        if is_verified == False:
            raise InputError(description="u_id is not registered")
  

    #create a dm_id
    curr_users = data['dms']
    curr_id = (len(curr_users) + 1)

    #create a dm_name
    owner_id = checked_token['user_id']
    u_ids.append(owner_id)

    all_members = [] 
    for u_id in u_ids:
        all_members.append(int(u_id))


    dm_name = []
    for uid in all_members:
        for user in data['users']:
            if user['user_id'] == uid:
                name = user.get('handle_str')
                dm_name.append(name)
                dm_name = sorted(dm_name)
    dm_name = ",".join(dm_name)
       
    
           
   
    #create a new dictionary 'dm' with keys as the attributes of the dm
    dm = {'dm_id' : curr_id,
        'name': dm_name,
        'messages' : {},
        'owner' : owner_id,
        'members' : all_members
        }

    data['dms'].append(dm)
    save_data()

    #code for notifications
    handle = ''

    for user in data['users']:
        if checked_token['user_id'] == user['user_id']:
            handle = user['handle_str']

    for user in data['users']:
        if user['user_id'] in u_ids:
            user['notifications'].append(
                {
                    'channel_id': -1,
                    'dm_id': curr_id,
                    'notification_message': handle + ' added you to ' + dm_name,
                    'time_created': datetime.now().timestamp()
                }
            )

    data['dreams_stats']['dms_exist'].append({
        'num_dms_exist': len(data['dms']), 
        'time_stamp': datetime.now().timestamp()
    })


    for user in data['users']:
        stats = {}
        if user['user_id'] in u_ids:
            stats = user['stats']
            num_dms_joined = stats['dms_joined'][-1]['num_dms_joined'] + 1
            stats['dms_joined'].append({
                    'num_dms_joined': num_dms_joined, 
                    'time_stamp': datetime.now().timestamp()
                })

    save_data()

    return {'dm_id' : curr_id, 'dm_name' : dm_name}


def dm_remove_v1(token, dm_id):
    '''
    Remove an existing DM. This can only be done by the original creator of the DM.
    Arguments -
        dm_id  (int)  - the dm_id of the dm
        token  (str)  - a unique string
    
    Exceptions -
        InputError  -   dm_id does not refer to a valid DM
        AccessError -   the user is not the original DM creator
    Return Value:
        Returns an empty dictionary {}
    '''
    #check token is valid
    checked_token = src.tokenhandler.check_token(token)

    #check for valid dm_id
    valid_dm_id(dm_id)

    #check if its owner
    is_verified = False
    for dm in data['dms']:
        if dm['owner'] == checked_token['user_id'] :
            is_verified = True
    if is_verified == False:
        raise AccessError(description='You are not the DM creator!')

    #remove existing dm   
    u_ids = [] 
    for dm in data['dms']:
        if dm['dm_id'] == dm_id:
            u_ids = dm['members'].copy()
            data['dms'].remove(dm)

    data['dreams_stats']['dms_exist'].append({
        'num_dms_exist': len(data['dms']), 
        'time_stamp': datetime.now().timestamp()
    })

    for user in data['users']:
        stats = {}
        if user['user_id'] in u_ids:
            stats = user['stats']
            num_dms_joined = stats['dms_joined'][-1]['num_dms_joined'] - 1
            stats['dms_joined'].append({
                    'num_dms_joined': num_dms_joined, 
                    'time_stamp': datetime.now().timestamp()
                })

    save_data()

    return {}


def dm_invite_v1(token, dm_id, u_id):
    '''
    Inviting a user to an existing dm
    ASSUMPTIONS are made 
    Arguments -
        dm_id  (int)  - the dm_id of the dm
        token  (str)  - a unique string
        u_id   (int)  - the user_id of the user invited
    
    Exceptions -
        InputError  -   dm_id does not refer to a valid DM
                        u_id does not refer to a valid user (not registered)
        AccessError -   the authorised user is not already a member of the DM
    Return Value:
        Returns an empty dictionary {}

    '''
    #check dm_id refers to a valid dm
    valid_dm_id(dm_id)

    #check token is valid
    u_id_2 = src.tokenhandler.check_token(token)['user_id']

    #check user_id is valid
    is_verified = False 
    for user in data['users']:
        if u_id == user['user_id']:
            is_verified = True

    if is_verified == False: 
        raise InputError(description='Invalid user id!')

    #check auth_user is a part of the dm
    check_if_user_is_memember(token,dm_id) 

    #check if invited user is already a member
    is_in_list = False
    dms = data['dms']
    dm_name = ''
    for dm in dms: 
        if dm['dm_id'] == dm_id:
            for user in dm['members']:
                if user == u_id:
                    is_in_list = True
            if not is_in_list:
                dm['members'].append(u_id)
                dm_name = dm['name']
                break
    
    #code for notifications
    handle_2 = ''

    for user in data['users']:
        if u_id_2 == user['user_id']:
            handle_2 = user['handle_str']

    for user in data['users']:
        if u_id == user['user_id']:
            user['notifications'].append(
                {
                    'channel_id': -1,
                    'dm_id': dm_id,
                    'notification_message': handle_2 + ' added you to ' + dm_name,
                    'time_created': datetime.now().timestamp()
                }
            )

    stats = {}
    for search_user in data['users']:
        if search_user['user_id'] == u_id:
            stats = search_user['stats']
    num_dms_joined = stats['dms_joined'][-1]['num_dms_joined'] - 1
    stats['dms_joined'].append({
        'num_dms_joined': num_dms_joined, 
        'time_stamp': datetime.now().timestamp()
    })

    return {}

def dm_leave_v1(token, dm_id):
    '''
    Given a DM ID, the user is removed as a member of this DM
    ASSUMPTIONS are made 
    Arguments -
        dm_id  (int)  - the dm_id of the dm
        token  (str)  - a unique string - the user to be removed 
    
    Exceptions -
        InputError  -   dm_id does not refer to a valid DM
        AccessError -   Authorised user is not a member of DM with dm_id
    Return Value:
        Returns an empty dictionary {}
    '''
    #check dm_id refers to a valid dm
    valid_dm_id(dm_id)

    #check token is valid
    checked_token = src.tokenhandler.check_token(token)

    #check auth_user is a part of the dm
    check_if_user_is_memember(token,dm_id)  

    #remove the user from the dms
    #ASSUMPTION - If a user leaves the name of the group remains same and if owner is removed then owner is empty

    dms = data['dms']
    for dm in dms: 
        if dm['dm_id'] == dm_id:
            for user in dm['members']:
                if user == checked_token['user_id']:
                   dm['members'].remove(checked_token['user_id']) 

    stats = {}
    for search_user in data['users']:
        if search_user['user_id'] == checked_token['user_id']:
            stats = search_user['stats']
    num_dms_joined = stats['dms_joined'][-1]['num_dms_joined'] - 1
    stats['dms_joined'].append({
        'num_dms_joined': num_dms_joined, 
        'time_stamp': datetime.now().timestamp()
    })

    return {}

def dm_messages_v1(token, dm_id, start):
    '''
    Given a DM with ID dm_id that the authorised user is part of, return up to 50 messages between index "start" and "start + 50". 
    Message with index 0 is the most recent message in the DM. This function returns a new index "end" which is the value of "start + 50", 
    or, if this function has returned the least recent messages in the DM, returns -1 in "end" to indicate there are no more messages to 
    load after this return.

    Arguments -
        dm_id  (int)  - the dm_id of the dm
        token  (str)  - a unique string - the user to be removed 
        start  (int)  - integer to indicate start of messages
    
    Exceptions:
        InputError  - occurs when either dm_id or u_id are not valid, or if start is greater than the total number of messages in the dm.
        AccessError - occurs when the auth_user is not already part of the dm

    Return Value:
        Returns {messages, start, end} on successful addition of user
    '''
    
    messages = []

    start = int(start)

    #check token is valid
    auth_user_id = src.tokenhandler.check_token(token)['user_id']

    #check if the dm_id is valid
    valid_dm_id(dm_id)

    #check if the user is a part of that dm
    check_if_user_is_memember(token,dm_id) 

    for message in src.data.data['messages']:
        if message['dm_id'] == dm_id and message['time_created'] < datetime.now().timestamp():
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

    dm_messages_v1 = {
        'messages': [],
        'start': start,
        'end': -1
    }

    counter = 0
    x = total - 1 - start

    while counter < 50 and x >= 0:
        dm_messages_v1['messages'].append(messages[x])
        counter += 1
        x -= 1

    if counter == 50:
        dm_messages_v1['end'] = start + 50
    
    return dm_messages_v1




