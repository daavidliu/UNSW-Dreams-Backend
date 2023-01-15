''' 
HTTP Tests for the Channels program,
'''
from werkzeug.exceptions import BadRequest
from src import error
from src.error import InputError
from src.error import AccessError
import pytest
import requests
import json
from src import auth, config, message

#resp = requests.get(config.url + "echo", params={"data": "hello"})
# helper function

@pytest.fixture
def setup():
    requests.delete(config.url + 'clear/v1')
#create a new user, create a new channel belonging to that user, then create a new user and add them to the channel
    requests.delete(config.url + "clear/v1")
    #create a new user, create a new channel belonging to that user, then create a new user and add them to the channel
    auth_user = requests.post(config.url + "auth/register/v2", json={'email' : 'example@email.com', 'password' : 'password', 'name_first' : 'john', 'name_last' : 'smith'})
    second_user = requests.post(config.url + "auth/register/v2", json={'email' : 'example2@email.com', 'password' : 'password', 'name_first' : 'johns', 'name_last' : 'smiths'})
    new_channel = requests.post(config.url + "channels/create/v2", json={'token' : auth_user.json()['token'], 'name' : 'testchannel', 'is_public' : True})
    new_channel2 = requests.post(config.url + "channels/create/v2", json={'token' : auth_user.json()['token'], 'name' : 'testchannel2', 'is_public' : True})
    return [auth_user, second_user, new_channel, new_channel2]

#TESTS FOR channels_list_v1
def test_channels_list_v1(setup):
    assert requests.get(config.url + "channels/list/v2", params={'token' : setup[1].json()['token']}).json() == {'channels': []}

    # user joins channel 
    requests.post(config.url + "channel/join/v2", json={'token' : setup[1].json()['token'], 'channel_id' : setup[2].json()['channel_id']})

    assert requests.get(config.url + "channels/list/v2", params={'token' : setup[1].json()['token']}).json() == {'channels': [{'channel_id': setup[2].json()['channel_id'], 'name': 'testchannel'}]}
    
    # create another new channel, user joins channel
    requests.post(config.url + "channel/join/v2", json={'token' : setup[1].json()['token'], 'channel_id' : setup[3].json()['channel_id']})

    assert requests.get(config.url + "channels/list/v2", params={'token' : setup[1].json()['token']}).json() == {'channels': [{'channel_id': setup[2].json()['channel_id'], 'name': 'testchannel'}, {'channel_id': setup[3].json()['channel_id'], 'name': 'testchannel2'}]}

    requests.delete(config.url + 'clear/v1')

def test_not_verified():
    invalid_user_id = 24678

    result = requests.get(config.url + "channels/list/v2", params={'token' : invalid_user_id})
    assert result.json()['name'] == 'System Error'
    requests.delete(config.url + 'clear/v1')
  
#TESTS FOR channels_listall_v1

def test_channels_listall_v1(setup):
    result = requests.get(config.url + "channels/listall/v2", params={'token' : setup[0].json()['token']})
    assert result.json() == {'channels' : [{'channel_id': setup[2].json()['channel_id'], 'name': 'testchannel'}, {'channel_id': setup[3].json()['channel_id'], 'name': 'testchannel2'}]}

    requests.delete(config.url + 'clear/v1')
