from src.error import InputError
from src.error import AccessError
import pytest
import src.message
import src.auth
import src.channel
import src.channels
from src.data import data
import src.tokenhandler
import src.other
import src.dm

import time
from datetime import timezone, datetime, timedelta

@pytest.fixture
def setup():
    src.other.clear_v1()

    james_auth = src.auth.auth_register_v1('jamesj@gmail.com', 'password', 'James', 'Jules')
    first_channel = src.channels.channels_create_v1(james_auth['token'], 'James', True)
    Nat_auth = src.auth.auth_register_v1('natnot@gmail.com', 'password', 'Nat', 'Alie')
    first_dm = src.dm.dm_create_v1(james_auth['token'], [Nat_auth['auth_user_id']])
    dave_auth = src.auth.auth_register_v1('daveee@gmail.com', 'password', 'Dave', 'Sam')
    return [james_auth, first_channel, Nat_auth, first_dm, dave_auth]


#MESSAGE_SEND
def test_message_send_v1(setup):
    message1_id = src.message.message_send_v1(setup[0]['token'], setup[1]['channel_id'],"Test message")
    
    assert message1_id['message_id'] == 1
 
    src.other.clear_v1()
    
#Message is longer than 1000 words
def test_message_send_InputError(setup):
    with pytest.raises(InputError):
        src.message.message_send_v1(setup[0]['token'], setup[1]['channel_id'], 1002*"e")
    src.other.clear_v1()
    
 #User has not joined the channel
def test_message_send_AccessError(setup):
    with pytest.raises(AccessError):
        src.message.message_send_v1(setup[2]['token'], setup[1]['channel_id'], "Random other message")
    src.other.clear_v1()
    
#MESSAGE_EDIT
def test_message_edit_v1(setup):
 
    message1_id = src.message.message_send_v1(setup[0]['token'], setup[1]['channel_id'],"Test message")
    
    src.message.message_edit_v1(setup[0]['token'], message1_id['message_id'], "Message edit works")
        
    for message in data['messages']:
        if message['message_id'] == 1:
            assert message['message'] == "Message edit works"
            
    src.other.clear_v1()

#Message is longer than 1000 words
def test_message_edit_InputError(setup):

    message1_id = src.message.message_send_v1(setup[0]['token'], setup[1]['channel_id'],"Test message")
 
    with pytest.raises(InputError):
        src.message.message_edit_v1(setup[0]['token'], message1_id['message_id'], 1001*"e")
    src.other.clear_v1()
    

#edit message is a deleted message
def test_message_edit_deleted_message(setup):

   message1_id = src.message.message_send_v1(setup[0]['token'], setup[1]['channel_id'],"")
   src.message.message_remove_v1(setup[0]['token'], message1_id['message_id'] )

   with pytest.raises(InputError):
      src.message.message_edit_v1(setup[0]['token'], message1_id['message_id'], "add")
   src.other.clear_v1()

    
#User is not in the channel
def test_message_edit_AccessError(setup):

    message1_id = src.message.message_send_v1(setup[0]['token'], setup[1]['channel_id'],"Test message")
    


    with pytest.raises(AccessError):
        src.message.message_edit_v1(setup[4]['token'], message1_id['message_id'], "Random other message")
    src.other.clear_v1()
    
    
#MESSAGE_REMOVE
def test_message_remove_v1(setup):

    message1_id = src.message.message_send_v1(setup[0]['token'], setup[1]['channel_id'],"Test message")
    
    src.message.message_remove_v1(setup[0]['token'], message1_id['message_id'] )

    for message in data['messages']:
        if message['message_id'] == 0:
            assert message['message'] == ""
            break
    
    src.other.clear_v1()
    
    
#message no longer exists
def test_message_remove_nomessage(setup):

    message1_id = src.message.message_send_v1(setup[0]['token'], setup[1]['channel_id'],"Test message")
    
    src.message.message_remove_v1(setup[0]['token'], message1_id['message_id'] )
    
    with pytest.raises(InputError):
        src.message.message_remove_v1(setup[0]['token'], message1_id['message_id'])

    src.other.clear_v1()
    
    
def test_message_remove_AccessError(setup):

    message1_id = src.message.message_send_v1(setup[0]['token'], setup[1]['channel_id'],"Test message")
    
    with pytest.raises(AccessError):
        src.message.message_remove_v1(setup[4]['token'], message1_id['message_id'])

    src.other.clear_v1()
    
    
#MESSAGE_SHARE
#share to channel
def test_message_share_channel(setup):

    og_message1_id = src.message.message_send_v1(setup[0]['token'], setup[1]['channel_id'],"will share the message")

    shared1_message_id = src.message.message_share_v1(setup[0]['token'], og_message1_id['message_id'], "got it", setup[1]['channel_id'], '-1' )
    
    for message in data['messages']:
        if message['message_id'] == 1:
            assert message['message'] == "will share the message"
            break

    assert shared1_message_id['shared_message_id']== 2
    
    src.other.clear_v1()

#share to dm
def test_message_share_dm(setup):

    og_message1_id = src.message.message_senddm_v1(setup[0]['token'], setup[3]['dm_id'], "created the dm")

    shared1_message_id = src.message.message_share_v1(setup[0]['token'], og_message1_id['message_id'], "got it too", '-1', setup[3]['dm_id'] )
    
    for message in data['messages']:
        if message['message_id'] == 1:
            assert message['message'] == "created the dm"
            break

    assert shared1_message_id['shared_message_id'] == 2
    
    src.other.clear_v1()
    
#Member is not a part of the dm
def test_message_share_AccessError(setup):

    random_auth = src.auth.auth_register_v1('rantnot@gmail.com', 'password', 'No', 'one')
    
    with pytest.raises(AccessError):
        src.message.message_senddm_v1(random_auth['token'], setup[3]['dm_id'], "hello")

    src.other.clear_v1()

    
#MESSAGE_SENDDM
def test_message_senddm(setup):

    message3_id = src.message.message_senddm_v1(setup[0]['token'], setup[3]['dm_id'], "hello")

    #assert data['messages']['message'] == "hello"
    for message in data['messages']:
        if message['message_id'] == 1:
            assert message['message'] == "hello"
            break

    assert message3_id['message_id'] == 1

    src.other.clear_v1()
    
#Message longer than 1000 words
def test_message_senddm_InputError(setup):

    with pytest.raises(InputError):
        src.message.message_senddm_v1(setup[0]['token'], setup[3]['dm_id'], 1001*"n")

    src.other.clear_v1()
    
#Member is not a part of the dm
def test_message_senddm_AccessError(setup):

    random_auth = src.auth.auth_register_v1('rantnot@gmail.com', 'password', 'No', 'one')
    
    with pytest.raises(AccessError):
        src.message.message_senddm_v1(random_auth['token'], setup[3]['dm_id'], "hello")

    src.other.clear_v1()


#tests for the send later functions

def test_message_sendlater_v1(setup):
    curr_time = datetime.now()
    delayed_time = curr_time + timedelta(0,0.1)
    assert src.message.message_sendlater_v1(setup[0]['token'], setup[1]['channel_id'], 'delayed message', delayed_time.timestamp()) == {'message_id': 1}
    assert src.channel.channel_messages_v1(setup[0]['token'], setup[1]['channel_id'], 0)['messages'] == []

    time.sleep(0.2)
    assert src.channel.channel_messages_v1(setup[0]['token'], setup[1]['channel_id'], 0)['messages'][0]['message'] == 'delayed message'

def test_message_sendlater_v1_invalid_time(setup):
    curr_time = datetime.now()
    past_time = curr_time - timedelta(0,1)
    with pytest.raises(InputError):
        src.message.message_sendlater_v1(setup[0]['token'], setup[1]['channel_id'], 'delayed message', past_time.timestamp()) == {'message_id': 1}


def test_message_sendlaterdm_v1(setup):
    curr_time = datetime.now()
    delayed_time = curr_time + timedelta(0,0.1)
    assert src.message.message_sendlaterdm_v1(setup[0]['token'], setup[3]['dm_id'], 'delayed message', delayed_time.timestamp()) == {'message_id': 1}
    assert src.dm.dm_messages_v1(setup[0]['token'], setup[3]['dm_id'], 0)['messages'] == []

    time.sleep(0.2)
    assert src.dm.dm_messages_v1(setup[0]['token'], setup[3]['dm_id'], 0)['messages'][0]['message'] == 'delayed message'

def test_message_sendlaterdm_v1_invalid_time(setup):
    curr_time = datetime.now()
    past_time = curr_time - timedelta(0,1)
    with pytest.raises(InputError):
        src.message.message_sendlaterdm_v1(setup[0]['token'], setup[3]['dm_id'], 'delayed message', past_time.timestamp()) == {'message_id': 1}




def test_message_react_v1(setup):
    message_id = src.message.message_send_v1(setup[0]['token'], setup[1]['channel_id'],"Test message")
    assert src.message.message_react_v1(setup[0]['token'], message_id['message_id'], 1) == {}
    #user 1 checking the first message in the channel
    message = src.channel.channel_messages_v1(setup[0]['token'], setup[1]['channel_id'], 0)['messages'][0]
    assert message['reacts'] == [
        {
            'react_id': 1,
            'u_ids': [setup[0]['auth_user_id']],
            'is_this_user_reacted': True
        }
    ]

    #user 2 joins the channel
    src.channel.channel_join_v1(setup[2]['token'], setup[1]['channel_id'])
    #user 2 checking the first message in the channel
    message = src.channel.channel_messages_v1(setup[2]['token'], setup[1]['channel_id'], 0)['messages'][0]
    assert message['reacts'] == [
        {
            'react_id': 1,
            'u_ids': [setup[0]['auth_user_id']],
            'is_this_user_reacted': False
        }
    ]


def test_message_react_v1_invalid(setup):
    #user1 sends the message in the channel
    message1_id = src.message.message_send_v1(setup[0]['token'], setup[1]['channel_id'],"Test message")['message_id']

    #Input errors
    src.message.message_react_v1(setup[0]['token'], message1_id, 1)
    with pytest.raises(InputError): #message already reacted
        src.message.message_react_v1(setup[0]['token'], message1_id, 1)
    invalid_id = 24601
    with pytest.raises(InputError): #message_id invalid
        src.message.message_react_v1(setup[0]['token'], invalid_id, 1)
    with pytest.raises(InputError): #react_id invalid
        src.message.message_react_v1(setup[0]['token'], message1_id, invalid_id)

    #Access Errors
    with pytest.raises(AccessError): #user2 not a member of the channel or dm
        src.message.message_react_v1(setup[2]['token'], message1_id, 1)


def test_message_unreact_v1(setup):
    message = src.message.message_send_v1(setup[0]['token'], setup[1]['channel_id'],"Test message")
    src.message.message_react_v1(setup[0]['token'], message['message_id'], 1)
    assert src.message.message_unreact_v1(setup[0]['token'], message['message_id'], 1) == {}
    #checking the first message in the channel
    message = src.channel.channel_messages_v1(setup[0]['token'], setup[1]['channel_id'], 0)['messages'][0] 
    assert message['reacts'] == [
        {
            'react_id': 1,
            'u_ids': [],
            'is_this_user_reacted': False
        }
    ]

def test_message_unreact_v1_invalid(setup):
    #user1 sends the message in the channel
    message1_id = src.message.message_send_v1(setup[0]['token'], setup[1]['channel_id'],"Test message")['message_id']

    #Input errors
    
    with pytest.raises(InputError): #message already unreacted
        src.message.message_unreact_v1(setup[0]['token'], message1_id, 1)
    src.message.message_react_v1(setup[0]['token'], message1_id, 1)
    invalid_id = 24601
    with pytest.raises(InputError): #message_id invalid
        src.message.message_unreact_v1(setup[0]['token'], invalid_id, 1)
    with pytest.raises(InputError): #react_id invalid
        src.message.message_unreact_v1(setup[0]['token'], message1_id, invalid_id)

    #Access Errors
    with pytest.raises(AccessError): #user2 not a member of the channel or dm
        src.message.message_unreact_v1(setup[2]['token'], message1_id, 1)


def test_message_pin_v1(setup):
    message_id = src.message.message_send_v1(setup[0]['token'], setup[1]['channel_id'],"Test message")
    assert src.message.message_pin_v1(setup[0]['token'], message_id['message_id']) == {}
    #checking the first message in the channel
    message = src.channel.channel_messages_v1(setup[0]['token'], setup[1]['channel_id'], 0)['messages'][0] 
    assert message['is_pinned'] == True

def test_message_pin_v1_invalid(setup):
    #user1 sends the message in the channel
    message1_id = src.message.message_send_v1(setup[0]['token'], setup[1]['channel_id'],"Test message")['message_id']

    #Input errors
    src.message.message_pin_v1(setup[0]['token'], message1_id)
    with pytest.raises(InputError): #message already pinned
        src.message.message_pin_v1(setup[0]['token'], message1_id)
    invalid_id = 24601
    with pytest.raises(InputError): #message_id invalid
        src.message.message_pin_v1(setup[0]['token'], invalid_id)

    #Access Errors
    with pytest.raises(AccessError): #user2 not a member of the channel or dm
        src.message.message_pin_v1(setup[2]['token'], message1_id)
    
def test_message_unpin_v1(setup):
    #send message
    message1_id = src.message.message_send_v1(setup[0]['token'], setup[1]['channel_id'],"Test message")['message_id']
    #pin message
    src.message.message_pin_v1(setup[0]['token'], message1_id)
    #unpin message
    assert src.message.message_unpin_v1(setup[0]['token'], message1_id) == {}
    #checking the first message in the channel
    message = src.channel.channel_messages_v1(setup[0]['token'], setup[1]['channel_id'], 0)['messages'][0] 
    assert message['is_pinned'] == False

def test_message_unpin_v1_invalid(setup):
    message1_id = src.message.message_send_v1(setup[0]['token'], setup[1]['channel_id'],"Test message")['message_id']
    
    #Input errors
    with pytest.raises(InputError): #message not pinned
        src.message.message_unpin_v1(setup[0]['token'], message1_id) 
    invalid_id = 24601
    with pytest.raises(InputError): #message_id invalid
        src.message.message_unpin_v1(setup[0]['token'], invalid_id) 

    #Access Errors
    src.message.message_pin_v1(setup[0]['token'], message1_id)
    with pytest.raises(AccessError): #user2 not a member of the channel or dm
        src.message.message_unpin_v1(setup[2]['token'], message1_id)
    



    
