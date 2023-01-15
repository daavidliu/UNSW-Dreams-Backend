from src.data import data, save_data
from src.error import InputError
from src.error import AccessError
import src.tokenhandler
import src.channels
import src.message
import src.auth
import src.channel
import src.user
import src.dm
import src.other
import src.standup

from datetime import datetime



def message_send_v1(token, channel_id, message):
    """
    Send a message from authorised_user to the channel specified by channel_id.

    Arguments:
        token (string)  - Valid token session for the authorised_user
        dm_id (integer)  - ID of the direct message
        message (string)  - Message being sent to the specific channel ID

    Exceptions:
        InputError  - Occurs when message is more than 1000 characters
        AccessError - Occurs when the authorised user has not joined the channel they are trying to post to

    Return Value:
        Returns message_id
        
    """

    content = message

    #check token is valid
    token_check = src.tokenhandler.check_token(token)['user_id']
    
    #check if channel has valid channel ID
    channel_name = ''
    is_valid_channel = False
    for channel in data['channels']:
        if channel['channel_id'] == channel_id:
            is_valid_channel = True
            channel_name = channel['name']
            if token_check not in channel['all_members']:
                raise AccessError(description="Auth User not in channel")

    if is_valid_channel == False:
        raise InputError(description="not a valid channel")
    
    #input error
    if (len(message) > 1000):
        raise InputError(description="message too long")
    
    #defining dm_id
    dm_id = -1
     
    #defining message_id
    message_id = 1 + len(data['messages'])
            
    new_message = {
        'message_id' : message_id,
        'channel_id' : channel_id,
        'dm_id' : dm_id,
        'u_id' : token_check,
        'message' : content,
        'time_created': datetime.now().timestamp(),
        'reacts': [
            {
                'react_id': 1,
                'u_ids': [],
                'is_this_user_reacted': False
            }
        ],
        'is_pinned': False
        }

    data['messages'].append(new_message)

    #code for notifications
    message_notification(token_check, channel_name, content, channel_id, dm_id, datetime.now().timestamp())

    data['dreams_stats']['messages_exist'].append({
        'num_messages_exist': len(data['messages']), 
        'time_stamp': datetime.now().timestamp()
    })

    stats = {}
    for search_user in data['users']:
        if search_user['user_id'] == token_check:
            stats = search_user['stats']
    num_messages_sent = stats['messages_sent'][-1]['num_messages_sent'] + 1
    stats['messages_sent'].append({
        'num_messages_sent': num_messages_sent, 
        'time_stamp': datetime.now().timestamp()
    })
    save_data()

    return {'message_id' : message_id}
    
def message_edit_v1(token, message_id, message):
    """
    Given a message, update its text with new text.

    Arguments:
        token (string)  - Valid token session for the authorised_user
        message_id (integer)  - ID of the message
        message (string)  - Message being edited

    Exceptions:
        InputError  - Occurs when message is more than 1000 characters
                    - message_id refers to a deleted message
                    
        AccessError - when none of the following are true:
            Message with message_id was sent by the authorised user making this request
            The authorised user is an owner of this channel (if it was sent to a channel) or the **Dreams**

    Return Value:
        Returns {}
        
    """
    content = message
    if content == '':
        message_remove_v1(token, message_id)

    #check token is valid
    token_check = src.tokenhandler.check_token(token)['user_id']
    
    #variable that determines whether the user has access to edit the message.
    access = False

    #check if the user is an owner of dreams
    for user in data['users']:
        if user['user_id'] == token_check and user['permission_id'] == 1:
            access = True

    #check the length of the message
    if (len(message) > 1000):
        raise InputError(description='Message is too long!')
    
    #check if the message exists
    channel_name = ''
    is_in_list = False
    for msg in data['messages']:
        if msg['message_id'] == message_id:
            is_in_list = True
            #give access to the user if original sender
            if msg['u_id'] == token_check:
                access = True
            
            #check channel ownership
            for channel in data['channels']:
                if msg['channel_id'] == channel['channel_id'] and token_check in channel['all_members']:
                    channel_name = channel['name']
                    access = True
            if not access:
                raise AccessError(description='User does not have persmission to edit the message!')
            
            for dm in data['dms']:
                if dm['dm_id'] == msg['dm_id']:
                    channel_name = dm['name']

            #change content of the message
            msg['message'] = content
            message_notification(token_check, channel_name, content, msg['channel_id'], msg['dm_id'], datetime.now().timestamp())

    if is_in_list == False:
        raise InputError(description="Message does not exist!")

    return {}


def message_remove_v1(token, message_id):
    """
    Given a message_id for a message, this message is removed from the channel/DM

    Arguments:
        token (string)  - Valid token session for the authorised_user
        message_id (integer)  - ID of the message

    Exceptions:
        InputError  - Message no longer exists
        
        AccessError - when none of the following are true:
            Message with message_id was sent by the authorised user making this request
            The authorised user is an owner of this channel (if it was sent to a channel) or the owner of **Dreams**

    Return Value:
        Returns {}
        
    """
    #check token is valid
    token_check = src.tokenhandler.check_token(token)['user_id']
    
    #variable that determines whether the user has access to edit the message.
    access = False

    #check if the user is an owner of dreams
    for user in data['users']:
        if user['user_id'] == token_check and user['permission_id'] == 1:
            access = True

    #check if the message exists
    is_in_list = False
    for msg in data['messages']:
        if msg['message_id'] == message_id:
            is_in_list = True
            #give access to the user if original sender
            if msg['u_id'] == token_check:
                access = True
            #check channel ownership
            for channel in data['channels']:
                if msg['channel_id'] == channel['channel_id'] and token_check in channel['all_members']:
                    access = True
            if not access:
                raise AccessError(description='User does not have persmission to edit the message!')
            #delete the message
            data['messages'].remove(msg)

    if is_in_list == False:
        raise InputError(description="Message does not exist!")

    stats = {}
    for search_user in data['users']:
        if search_user['user_id'] == token_check:
            stats = search_user['stats']
    num_messages_sent = stats['messages_sent'][-1]['num_messages_sent'] - 1
    stats['messages_sent'].append({
        'num_messages_sent': num_messages_sent, 
        'time_stamp': datetime.now().timestamp()
    })
    save_data()

    return {}


def message_share_v1(token, og_message_id, message, channel_id, dm_id):
    """
    Given a og_message_id for a message, this message gets shared in channels or DMs

    Arguments:
        token (string)  - Valid token session for the authorised_user
        og_message_id(integer) - Original message shared
        message(string)  - Message being shared
        channel_id(integer) - Channel ID
        dm_id(integer) _ DM ID
        
    Exceptions:
        
        AccessError - Occurs when the authorised user has not joined the channel they are trying to post to

    Return Value:
        Returns {shared_message_id}
        
    """

    content = message
    #check token is valid
    token_check = src.tokenhandler.check_token(token)['user_id']

    name = ''
    #check auth_user is a part of the channel or dm
    is_in_list = False
    
    for channel in data['channels']:
        if channel['channel_id'] == channel_id and token_check in channel['all_members']:
            is_in_list = True
            name = channel['name']
    
    if is_in_list == False:
        for dm in data['dms']:
            if dm['dm_id'] == dm_id and token_check in dm['members']:
                is_in_list = True
                name = dm['name']
    
    if is_in_list == False:
        raise AccessError (description="Auth User not in dm/channel")

    sender = ''
    og_content = ''
    valid_message = False
    for msg in data['messages']:
        if msg['message_id'] == og_message_id:
            valid_message = True
            og_content = msg['message']
            sender = src.user.user_profile(token, msg['u_id'])['user']['handle_str']

    new_message = '------' + '\n' + sender + ' sent "' + og_content + '" in ' + name + '\n' + '------' + '\n' + content

    if not valid_message:
        raise InputError(description='Invalid message_id!')
    

    shared_msg = {
        'message_id': len(data['messages']) + 1,
        'channel_id': channel_id,
        'dm_id': dm_id,
        'u_id': token_check,
        'message': new_message,
        'time_created': datetime.now().timestamp(),
        'reacts': [
            {
                'react_id': 1,
                'u_ids': [],
                'is_this_user_reacted': False
            }
        ],
        'is_pinned': False
    }

    data['messages'].append(shared_msg)

    #code for notifications
    message_notification(token_check, name, content, channel_id, dm_id, datetime.now().timestamp())

    stats = {}
    for search_user in data['users']:
        if search_user['user_id'] == token_check:
            stats = search_user['stats']
    num_messages_sent = stats['messages_sent'][-1]['num_messages_sent'] + 1
    stats['messages_sent'].append({
        'num_messages_sent': num_messages_sent, 
        'time_stamp': datetime.now().timestamp()
    })
    save_data()

    return {'shared_message_id': shared_msg['message_id']}

        
def message_senddm_v1(token, dm_id, message):
    """
   Send a message from authorised_user to the DM specified by dm_id.

    Arguments:
        token (string)  - Valid token session for the authorised_user
        message(string)  - Message being shared
        dm_id(integer) _ DM ID
        
    Exceptions:
    
        InputError  - Occurs when message is more than 1000 characters
        
        AccessError - Occurs when the authorised user is not a member of the dm

    Return Value:
        Returns {message_id}
        
    """

    content = message

    #check token is valid
    token_check = src.tokenhandler.check_token(token)['user_id']
    
    #check if DM has valid DM ID
    dm_name = ''
    is_valid_dm = False
    for dm in data['dms']:
        if dm['dm_id'] == dm_id:
            is_valid_dm = True
            dm_name = dm['name']
            if token_check not in dm['members']:
                raise AccessError(description="Auth User not in dm")

    if is_valid_dm == False:
        raise InputError(description="not a valid dm")
    
    #input error
    if (len(message) > 1000):
        raise InputError(description="message too long")
    
    #defining channel_id
    channel_id = -1
     
    #defining message_id
    message_id = 1 + len(data['messages'])
            
    new_message = {
        'message_id' : message_id,
        'channel_id' : channel_id,
        'dm_id' : dm_id,
        'u_id' : token_check,
        'message' : content,
        'time_created': datetime.now().timestamp(),
        'reacts': [
            {
                'react_id': 1,
                'u_ids': [],
                'is_this_user_reacted': False
            }
        ],
        'is_pinned': False
        }

    data['messages'].append(new_message)

    #code for notifications
    message_notification(token_check, dm_name, content, channel_id, dm_id, datetime.now().timestamp())

    stats = {}
    for search_user in data['users']:
        if search_user['user_id'] == token_check:
            stats = search_user['stats']
    num_messages_sent = stats['messages_sent'][-1]['num_messages_sent'] + 1
    stats['messages_sent'].append({
        'num_messages_sent': num_messages_sent, 
        'time_stamp': datetime.now().timestamp()
    })
    save_data()

    return {'message_id' : message_id}

def message_notification(u_id, name, message, channel_id, dm_id, time_created):
    #code for notifications
    handle = ''
    for user in data['users']:
        if u_id == user['user_id']:
            handle = user['handle_str']

    for user in data['users']:
        if ('@' + user['handle_str']) in message:
            user['notifications'].append(
                {
                    'channel_id': channel_id,
                    'dm_id': dm_id,
                    'notification_message': handle + ' tagged you in ' + name + ': ' + message[:20],
                    'time_created': time_created

                }
            )

def message_sendlater_v1(token, channel_id, message, time_sent):
    '''
    Send a message from authorised_user to the channel specified by channel_id 
    automatically at a specified time in the future.

    Arguments:
        token (string)  - Valid token session for the authorised_user
        channel_id (int) - id for the channel where the message is sent.
        message (string)  - Message being shared
        time_semt(integer) - Unix time for when the message will be sent
        
    Exceptions:
    
        InputError  - Invalid Channel_id, len(message) > 1000, time sent is in the past.
        
        AccessError - the authorised user has not joined the channel they are trying to post to

    Return Value:
        Returns {message_id}
        
    '''

    content = message

    #check token is valid
    token_check = src.tokenhandler.check_token(token)['user_id']

    #check time sent is not in the past
    if time_sent < datetime.now().timestamp():
        raise InputError(description='Cannot send message in the past!')
    
    #check if channel has valid channel ID
    channel_name = ''
    is_valid_channel = False
    for channel in data['channels']:
        if channel['channel_id'] == channel_id:
            is_valid_channel = True
            channel_name = channel['name']
            if token_check not in channel['all_members']:
                raise AccessError(description="Auth User not in channel")

    if is_valid_channel == False:
        raise InputError(description="not a valid channel")
    
    #input error
    if (len(message) > 1000):
        raise InputError(description="message too long")
    
    #defining dm_id
    dm_id = -1
     
    #defining message_id
    message_id = 1 + len(data['messages'])
            
    new_message = {
        'message_id' : message_id,
        'channel_id' : channel_id,
        'dm_id' : dm_id,
        'u_id' : token_check,
        'message' : content,
        'time_created': time_sent,
        'reacts': [
            {
                'react_id': 1,
                'u_ids': [],
                'is_this_user_reacted': False
            }
        ],
        'is_pinned': False
        }

    data['messages'].append(new_message)

    #code for notifications
    message_notification(token_check, channel_name, content, channel_id, dm_id, time_sent)

    stats = {}
    for search_user in data['users']:
        if search_user['user_id'] == token_check:
            stats = search_user['stats']
    num_messages_sent = stats['messages_sent'][-1]['num_messages_sent'] + 1
    stats['messages_sent'].append({
        'num_messages_sent': num_messages_sent, 
        'time_stamp': datetime.now().timestamp()
    })
    save_data()

    return {'message_id' : message_id}
    

def message_sendlaterdm_v1(token, dm_id, message, time_sent):
    '''
    Send a message from authorised_user to the channel specified by channel_id 
    automatically at a specified time in the future.

    Arguments:
        token (string)  - Valid token session for the authorised_user
        dm_id (int) - id for the dm where the message is sent.
        message (string)  - Message being shared
        time_semt(integer) - Unix time for when the message will be sent
        
    Exceptions:
    
        InputError  - Invalid DM_id, len(message) > 1000, time sent is in the past.
        
        AccessError - the authorised user has not joined the DM they are trying to post to

    Return Value:
        Returns {message_id}
        
    '''
    
    content = message

    #check token is valid
    token_check = src.tokenhandler.check_token(token)['user_id']

    #check time sent is not in the past
    if time_sent < datetime.now().timestamp():
        raise InputError(description='Cannot send message in the past!')
    
    #check if DM has valid DM ID
    dm_name = ''
    is_valid_dm = False
    for dm in data['dms']:
        if dm['dm_id'] == dm_id:
            is_valid_dm = True
            dm_name = dm['name']
            if token_check not in dm['members']:
                raise AccessError(description="Auth User not in dm")

    if is_valid_dm == False:
        raise InputError(description="not a valid dm")
    
    #input error
    if (len(message) > 1000):
        raise InputError(description="message too long")
    
    #defining channel_id
    channel_id = -1
     
    #defining message_id
    message_id = 1 + len(data['messages'])
    
    new_message = {
        'message_id' : message_id,
        'channel_id' : channel_id,
        'dm_id' : dm_id,
        'u_id' : token_check,
        'message' : content,
        'time_created': time_sent,
        'reacts': [
            {
                'react_id': 1,
                'u_ids': [],
                'is_this_user_reacted': False
            }
        ],
        'is_pinned': False
        }

    data['messages'].append(new_message)

    #code for notifications
    message_notification(token_check, dm_name, content, channel_id, dm_id, time_sent)

    stats = {}
    for search_user in data['users']:
        if search_user['user_id'] == token_check:
            stats = search_user['stats']
    num_messages_sent = stats['messages_sent'][-1]['num_messages_sent'] + 1
    stats['messages_sent'].append({
        'num_messages_sent': num_messages_sent, 
        'time_stamp': datetime.now().timestamp()
    })
    save_data()

    return {'message_id' : message_id}

def message_react_v1(token, message_id, react_id):
    '''
    Given a message within a channel or DM the authorised user is part of, 
    add a "react" to that particular message

    Arguments:
        token (string)  - Valid token session for the authorised_user
        message_id (int) - id for the message to be reacted.
        react_id (int) - The only valid react ID the frontend has is 1

        
    Exceptions:
    
        InputError  - message not within a channel/DM that the authorised user has joined
                    - react_id is not a valid
                    - Message already contains an active React from the authorised user
        
        AccessError - Auth user not within the channel or DM that the message is within

    Return Value:
        Returns {}
        
    '''
    auth_user_id = src.tokenhandler.check_token(token)['user_id']

    if react_id != 1:
        raise InputError(description='React is invalid!')

    is_valid_message = False
    user_is_member = False
    u_id = -1
    channel_id = -1
    dm_id = -1
    name = ''
    for message in data['messages']:
        if message_id == message['message_id']:
            is_valid_message = True
            u_id = message['u_id']
            channel_id = message['channel_id']
            dm_id = message['dm_id']

            #Check if the user is a part of the channel/DM
            for channel in data['channels']:
                if message['channel_id'] == channel['channel_id'] and auth_user_id in channel['all_members']:
                    user_is_member = True
                    name = channel['name']
            for dm in data['dms']:
                if message['dm_id'] == dm['dm_id'] and auth_user_id in dm['members']:
                    user_is_member = True
                    name = dm['name']
            #raise error if user is not a member of the channel/DM
            if not user_is_member:
                raise AccessError(description='User is not a member of the channel/DM!')
            #check if message is already reacted by user
            if auth_user_id in message['reacts'][0]['u_ids']:
                raise InputError(description='message already reacted by you!')
            #Add reaction to the message
            message['reacts'][0]['u_ids'].append(auth_user_id)

            break
    
    if not is_valid_message:
        raise InputError(description='Invalid message!')

    #code for notifications
    handle = ''
    for user in data['users']:
        if auth_user_id == user['user_id']:
            handle = user['handle_str']

    for user in data['users']:
        if user["user_id"] == u_id:
            user['notifications'].append(
                {
                    'channel_id': channel_id,
                    'dm_id': dm_id,
                    'notification_message': handle + ' reacted to your message in ' + name,
                    'time_created': datetime.now().timestamp()
                }
            )

    return {}


def message_unreact_v1(token, message_id, react_id):
    '''
    Given a message within a channel or DM the authorised user is part of, 
    remove a "react" to that particular message

    Arguments:
        token (string)  - Valid token session for the authorised_user
        message_id (int) - id for the message to be reacted.
        react_id (int) - The only valid react ID the frontend has is 1

        
    Exceptions:
    
        InputError  - message not within a channel/DM that the authorised user has joined
                    - react_id is not a valid
                    - Message doesn't contain an active React from the authorised user
        
        AccessError - Auth user not within the channel or DM that the message is within

    Return Value:
        Returns {}
        
    '''

    auth_user_id = src.tokenhandler.check_token(token)['user_id']

    if react_id != 1:
        raise InputError(description='React is invalid!')

    is_valid_message = False
    user_is_member = False
    for message in data['messages']:
        if message_id == message['message_id']:
            is_valid_message = True
            #Check if the user is a part of the channel/DM
            for channel in data['channels']:
                if message['channel_id'] == channel['channel_id'] and auth_user_id in channel['all_members']:
                    user_is_member = True
            for dm in data['dms']:
                if message['dm_id'] == dm['dm_id'] and auth_user_id in dm['members']:
                    user_is_member = True
            #raise error if user is not a member of the channel/DM
            if not user_is_member:
                raise AccessError(description='User is not a member of the channel/DM!')
            #check if message is already unreacted by user
            if auth_user_id not in message['reacts'][0]['u_ids']:
                raise InputError(description='message already unreacted by you!')
            #Remove reaction to the message
            message['reacts'][0]['u_ids'].remove(auth_user_id)

            return {}
    
    if not is_valid_message:
        raise InputError(description='Invalid message!')

def message_pin_v1(token, message_id):
    '''
    Given a message within a channel or DM, 
    mark it as "pinned" to be given special display treatment by the frontend

    Arguments:
        token (string)  - Valid token session for the authorised_user
        message_id (int) - id for the message to be reacted.


        
    Exceptions:
    
        InputError  - message_id invalid
                    - message is already pinned
 
        AccessError - Auth user not within the channel or DM that the message is within
                    - The authorised user is not an owner of the channel or DM

    Return Value:
        Returns {}
        
    '''
    auth_user_id = src.tokenhandler.check_token(token)['user_id']

    is_valid_message = False
    user_is_member = False
    for message in data['messages']:
        if message_id == message['message_id']:
            is_valid_message = True
            #Check if the user is a part of the channel/DM
            for channel in data['channels']:
                if message['channel_id'] == channel['channel_id'] and auth_user_id in channel['owner_members']:
                    user_is_member = True
            for dm in data['dms']:
                if message['dm_id'] == dm['dm_id'] and auth_user_id == dm['owner']:
                    user_is_member = True
            #raise error if user is not a member of the channel/DM
            if not user_is_member:
                raise AccessError(description='User is not an owner of the channel/DM!')
            
            #check if message is already pinned
            if message['is_pinned']:
                raise InputError(description='message already pinned!')
            #Remove reaction to the message
            message['is_pinned'] = True

            return {}
    
    if not is_valid_message:
        raise InputError(description='Invalid message!')

def message_unpin_v1(token, message_id):
    '''
    Given a message within a channel or DM, remove it's mark as unpinned

    Arguments:
        token (string)  - Valid token session for the authorised_user
        message_id (int) - id for the message to be reacted.


        
    Exceptions:
    
        InputError  - message_id invalid
                    - message is already unpinned
 
        AccessError - Auth user not within the channel or DM that the message is within
                    - The authorised user is not an owner of the channel or DM

    Return Value:
        Returns {}
        
    '''
    auth_user_id = src.tokenhandler.check_token(token)['user_id']

    is_valid_message = False
    user_is_member = False
    for message in data['messages']:
        if message_id == message['message_id']:
            is_valid_message = True
            #Check if the user is a part of the channel/DM
            for channel in data['channels']:
                if message['channel_id'] == channel['channel_id'] and auth_user_id in channel['owner_members']:
                    user_is_member = True
            for dm in data['dms']:
                if message['dm_id'] == dm['dm_id'] and auth_user_id == dm['owner']:
                    user_is_member = True
            #raise error if user is not a member of the channel/DM
            if not user_is_member:
                raise AccessError(description='User is not a member of the channel/DM!')
            
            #check if message is already unpinned
            if not message['is_pinned']:
                raise InputError(description='message already unpinned!')
            #Remove reaction to the message
            message['is_pinned'] = False

            return {}
    
    if not is_valid_message:
        raise InputError(description='Invalid message!')
