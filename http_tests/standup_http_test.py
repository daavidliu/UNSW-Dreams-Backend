
from src.error import InputError
from src.error import AccessError
import requests
import pytest
import src.tokenhandler
from datetime import datetime, timedelta
import time
from src import auth, config, message

@pytest.fixture
def setup():
    requests.delete(config.url + 'clear/v1')
    user1 = requests.post(config.url + "auth/register/v2", json={'email' : 'example1@email.com', 'password' : 'password', 'name_first' : 'john', 'name_last' : 'one'}).json()
    user2 = requests.post(config.url + "auth/register/v2", json={'email' : 'example2@gmail.com', 'password' : 'password2', 'name_first' : 'martha', 'name_last' : 'two'}).json()
    new_channel = requests.post(config.url + "channels/create/v2", json={'token' : user1['token'], 'name' : 'testchannel', 'is_public' : True}).json()
    user3 = requests.post(config.url + "auth/register/v2", json={'email' : 'example3@gmail.com', 'password' : 'password3', 'name_first' : 'nick', 'name_last' : 'three'}).json()
    user4 = requests.post(config.url + "auth/register/v2", json={'email' : 'example4@gmail.com', 'password' : 'password2', 'name_first' : 'david', 'name_last' : 'four'}).json()

    requests.post(config.url + "channel/join/v2", json={'token' : user2['token'], 'channel_id' : new_channel['channel_id']})
    requests.post(config.url + "channel/join/v2", json={'token' : user3['token'], 'channel_id' : new_channel['channel_id']})
    return [
        {'token': user1['token'], 'id': user1['auth_user_id']},
        {'token': user2['token'], 'id': user2['auth_user_id']},
        {'channel_id': new_channel['channel_id']},
        {'token': user4['token'], 'id': user4['auth_user_id']},
        {'token': user3['token'], 'id': user3['auth_user_id']},
    ]

# checks inputerror for standup start/active/send
def test_channel_id_not_valid(setup): 
    invalid_channel_id = 459786235
    length = 3
    tempo_msg = 'standup test check'
    result = requests.post(config.url + "standup/start/v1", json={'token' : setup[0]['token'], 'channel_id' : invalid_channel_id, 'length' : length})
    assert result.json()['code'] == 400
    result = requests.post(config.url + "standup/start/v1", json={'token' : setup[0]['token'], 'channel_id' : invalid_channel_id, 'length' : tempo_msg})
    assert result.json()['code'] == 400
    requests.delete(config.url + 'clear/v1')


#checks inputerror standup start 
def test_active_standup_currently_running(setup):
    requests.post(config.url + "standup/start/v1", json={'token' : setup[0]['token'], 'channel_id' : setup[2]['channel_id'], 'length' : 0.1})
    assert requests.get(config.url + "standup/active/v1", params={'token' : setup[1]['token'], 'channel_id' : setup[2]['channel_id']}).json()['is_active'] == True
    result = requests.post(config.url + "standup/start/v1", json={'token' : setup[1]['token'], 'channel_id' : setup[2]['channel_id'], 'length' : 1})
    assert result.json()['code'] == 400
    time.sleep(0.2)

    assert requests.get(config.url + "standup/active/v1", params={'token' : setup[1]['token'], 'channel_id' : setup[2]['channel_id']}).json()['is_active'] == False
    requests.delete(config.url + 'clear/v1')

#checks inputerror standup send 
def test_active_channel_not_currently_running(setup):
    result = requests.post(config.url + "standup/send/v1", json={'token' : setup[0]['token'], 'channel_id' : setup[2]['channel_id'], 'message' : 'message'})
    assert result.json()['code'] == 400
    requests.delete(config.url + 'clear/v1')


#checks inputerror for standup send 
def test_message_longer_than_1kchar(setup): ############# DONE
    requests.post(config.url + "standup/start/v1", json={'token' : setup[0]['token'], 'channel_id' : setup[2]['channel_id'], 'length' : 0.1})
    invalid_message = 'h'*1001
    result = requests.post(config.url + "standup/send/v1", json={'token' : setup[0]['token'], 'channel_id' : setup[2]['channel_id'], 'message' : invalid_message})
    assert result.json()['code'] == 400
    requests.delete(config.url + 'clear/v1')

#checks for input error for standup start
def test_accesError_auth_user_not_member_of_channel(setup): ########### DONE
    length = 4
    tempo_msg = 'checking if the member is in the messages for standup send'
    result = requests.post(config.url + "standup/start/v1", json={'token' : setup[3]['token'], 'channel_id' : setup[2]['channel_id'], 'length' : length})
    assert result.json()['code'] == 403

    requests.post(config.url + "standup/start/v1", json={'token' : setup[0]['token'], 'channel_id' : setup[2]['channel_id'], 'length' : length})
    result = requests.post(config.url + "standup/send/v1", json={'token' : setup[3]['token'], 'channel_id' : setup[2]['channel_id'], 'message' : tempo_msg})
    assert result.json()['code'] == 403
    requests.delete(config.url + 'clear/v1')

# checks if the rquired functions work as they should
def test_standup_start_andSend(setup):
    requests.post(config.url + "standup/start/v1", json={'token' : setup[0]['token'], 'channel_id' : setup[2]['channel_id'], 'length' : 0.1})
    requests.post(config.url + "standup/send/v1", json={'token' : setup[0]['token'], 'channel_id' : setup[2]['channel_id'], 'message' : 'message1'})
    requests.post(config.url + "standup/send/v1", json={'token' : setup[1]['token'], 'channel_id' : setup[2]['channel_id'], 'message' : 'message2'})
    requests.post(config.url + "standup/send/v1", json={'token' : setup[4]['token'], 'channel_id' : setup[2]['channel_id'], 'message' : 'message3'})

    result = requests.get(config.url + "channel/messages/v2", params={'token': setup[0]['token'], 'channel_id' : setup[2]['channel_id'], 'start' : 0})
    assert result.json()['messages'] == []
    
    time.sleep(0.2)
    result = requests.get(config.url + "channel/messages/v2", params={'token': setup[0]['token'], 'channel_id' : setup[2]['channel_id'], 'start' : 0})
    print(result)
    assert result.json()['messages'][0]['message'] == 'johnone: message1\nmarthatwo: message2\nnickthree: message3'

    requests.delete(config.url + 'clear/v1')


def test_standup_active(setup):
    result = requests.get(config.url + "standup/active/v1", params={'token': setup[0]['token'], 'channel_id' : setup[2]['channel_id']})
    assert result.json() == {
        'is_active': False, 
        'time_finish': None
    }

    requests.post(config.url + "standup/start/v1", json={'token' : setup[0]['token'], 'channel_id' : setup[2]['channel_id'], 'length' : 0.1})
    result = requests.get(config.url + "standup/active/v1", params={'token': setup[0]['token'], 'channel_id' : setup[2]['channel_id']})
    assert result.json()['is_active'] == True

    requests.delete(config.url + 'clear/v1')
