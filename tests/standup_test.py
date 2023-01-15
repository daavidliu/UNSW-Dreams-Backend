import src.standup
import src.data
import src.channel
from src.error import InputError
from src.error import AccessError
import pytest
import src.tokenhandler
from datetime import datetime, timedelta
import time
import src.auth
import src.channels
import src.other
@pytest.fixture
def setup():
    src.other.clear_v1()
    user1 = src.auth.auth_register_v1('example1@email.com', 'password', 'john', 'one')
    user2 = src.auth.auth_register_v1('example2@gmail.com', 'password2', 'martha', 'two')
    new_channel = src.channels.channels_create_v1(user1['token'], 'testchannel', True)
    user3 = src.auth.auth_register_v1('example3@gmail.com', 'password3', 'nick', 'three')
    user4 = src.auth.auth_register_v1('example4@gmail.com', 'password2', 'david', 'four')

    src.channel.channel_join_v1(user2['token'], new_channel['channel_id'])
    src.channel.channel_join_v1(user3['token'], new_channel['channel_id'])
    return [
        {'token': user1['token'], 'id': user1['auth_user_id']},
        {'token': user2['token'], 'id': user2['auth_user_id']},
        {'channel_id': new_channel['channel_id']},
        {'token': user4['token'], 'id': user4['auth_user_id']},
        {'token': user3['token'], 'id': user3['auth_user_id']},
    ]

# checks inputerror for standup start/active/send
def test_channel_id_not_valid(setup): ############## DONE
    invalid_channel_id = 459786235
    length = 3
    tempo_msg = 'standup test check'
    with pytest.raises(InputError):
        src.standup.standup_start_v1(setup[0]['token'], invalid_channel_id, length)
    with pytest.raises(InputError):
        src.standup.standup_send_v1(setup[0]['token'], invalid_channel_id, tempo_msg)

    src.other.clear_v1()

#checks inputerror standup start ############ DONE
def test_active_standup_currently_runnig(setup):
    src.standup.standup_start_v1(setup[0]['token'], setup[2]['channel_id'], 0.1)
    assert src.standup.standup_active_v1(setup[1]['token'], setup[2]['channel_id'])['is_active'] == True
    with pytest.raises(InputError):
        src.standup.standup_start_v1(setup[1]['token'], setup[2]['channel_id'], 1)
    
    time.sleep(0.2)

    assert src.standup.standup_active_v1(setup[1]['token'], setup[2]['channel_id'])['is_active'] == False
    src.other.clear_v1()

#checks inputerror standup send 
def test_active_channel_not_currently_running(setup):########### DONE
    with pytest.raises(InputError):
        length = 3
        src.standup.standup_send_v1(setup[0]['token'], setup[2]['channel_id'], length) 
    src.other.clear_v1()

#checks inputerror for standup send 
def test_message_longer_than_1kchar(setup): ############# DONE
    src.standup.standup_start_v1(setup[0]['token'], setup[2]['channel_id'], 0.1)
    invalid_message = 'h'*1001
    with pytest.raises(InputError):
        src.standup.standup_send_v1(setup[0]['token'], setup[2]['channel_id'], invalid_message) 

    src.other.clear_v1()

#checks for input error for standup start
def test_accesError_auth_user_not_member_of_channel(setup): ########### DONE
    length = 4
    tempo_msg = 'checking if the member is in the messages for standup send'
    with pytest.raises(AccessError):
        src.standup.standup_start_v1(setup[3]['token'], setup[2]['channel_id'], length)
    
    src.standup.standup_start_v1(setup[0]['token'], setup[2]['channel_id'], length)
    with pytest.raises(AccessError):
        src.standup.standup_send_v1(setup[3]['token'], setup[2]['channel_id'], tempo_msg)

    src.other.clear_v1()


# checks if the rquired functions work as they should
def test_standup_start_andSend(setup):
    src.standup.standup_start_v1(setup[0]['token'], setup[2]['channel_id'], 0.1)

    src.standup.standup_send_v1(setup[0]['token'], setup[2]['channel_id'], 'message1')
    src.standup.standup_send_v1(setup[1]['token'], setup[2]['channel_id'], 'message2')
    src.standup.standup_send_v1(setup[4]['token'], setup[2]['channel_id'], 'message3')

    assert src.channel.channel_messages_v1(setup[0]['token'], setup[2]['channel_id'], 0)['messages'] == []
    
    time.sleep(0.2)
    print(src.channel.channel_messages_v1(setup[0]['token'], setup[2]['channel_id'], 0))
    assert src.channel.channel_messages_v1(setup[0]['token'], setup[2]['channel_id'], 0)['messages'][0]['message'] == 'johnone: message1\nmarthatwo: message2\nnickthree: message3'

    src.other.clear_v1()



def test_standup_active(setup):
    assert src.standup.standup_active_v1(setup[0]['token'], setup[2]['channel_id']) == {
        'is_active': False, 
        'time_finish': None
    }

    src.standup.standup_start_v1(setup[0]['token'], setup[2]['channel_id'], 0.1)

    assert src.standup.standup_active_v1(setup[0]['token'], setup[2]['channel_id'])['is_active'] == True

    src.other.clear_v1()


