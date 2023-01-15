from werkzeug.exceptions import BadRequest
from src import error
from src.error import InputError
from src.error import AccessError
import pytest
import requests
import json
from src import auth, config, message, notifications, channel, channels, dm

@pytest.fixture
def setup():
    requests.delete(config.url + "clear/v1")
    #create a new user, create a new channel belonging to that user, then create a new user and add them to the channel
    auth_user = requests.post(config.url + "auth/register/v2", json={'email' : 'example@email.com', 'password' : 'password', 'name_first' : 'john', 'name_last' : 'smith'})
    second_user = requests.post(config.url + "auth/register/v2", json={'email' : 'example2@email.com', 'password' : 'password', 'name_first' : 'martha', 'name_last' : 'jones'})
    new_channel = requests.post(config.url + "channels/create/v2", json={'token' : auth_user.json()['token'], 'name' : 'testchannel', 'is_public' : True})
    
    return [auth_user, second_user, new_channel]

def test_notification_from_channel(setup):
    requests.post(config.url + "channel/invite/v2", json={'token': setup[0].json()['token'], 'channel_id': setup[2].json()['channel_id'], 'u_id' : setup[1].json()['auth_user_id']})
    notifications = requests.get(config.url + "notifications/get/v1", params = {'token': setup[1].json()['token']}).json()['notifications']
    assert notifications[0]['channel_id'] == setup[2].json()['channel_id']
    assert notifications[0]['dm_id'] == -1
    assert notifications[0]['notification_message'] == 'johnsmith added you to testchannel'

    #auth user creates a new_dm and invites the second user
    requests.post(config.url + "message/send/v2", json={'token': setup[0].json()['token'], 'channel_id': setup[2].json()['channel_id'], 'message': '@marthajones wyd'})
    
    notifications = requests.get(config.url + "notifications/get/v1", params = {'token': setup[1].json()['token']}).json()['notifications']
    
    assert notifications[0]['channel_id'] == setup[2].json()['channel_id']
    assert notifications[0]['dm_id'] == -1
    assert notifications[0]['notification_message'] == 'johnsmith tagged you in testchannel: @marthajones wyd'

    assert notifications[1]['channel_id'] == setup[2].json()['channel_id']
    assert notifications[1]['dm_id'] == -1
    assert notifications[1]['notification_message'] == 'johnsmith added you to testchannel'
    
   
def test_notification_from_dm(setup):
    #auth user creates a new_dm and invites the second user
    dm = requests.post(config.url + "dm/create/v1", json={'token': setup[0].json()['token'], 'u_ids': [setup[1].json()['auth_user_id']]})
    requests.post(config.url + "dm/invite/v1", json={'token': setup[0].json()['token'], 'channel_id': setup[2].json()['channel_id'], 'u_id' : setup[1].json()['auth_user_id']})
    
    notifications = requests.get(config.url + "notifications/get/v1", params = {'token': setup[1].json()['token']}).json()['notifications']
    
    assert notifications[0]['channel_id'] == -1
    assert notifications[0]['dm_id'] == dm.json()['dm_id']
    assert notifications[0]['notification_message'] == 'johnsmith added you to johnsmith,marthajones'


    requests.post(config.url + "message/senddm/v1", json={'token': setup[0].json()['token'], 'dm_id': dm.json()['dm_id'], 'message': '@marthajones123456789'})
    
    notifications = requests.get(config.url + "notifications/get/v1", params = {'token': setup[1].json()['token']}).json()['notifications']
    
    assert notifications[0]['channel_id'] == -1
    assert notifications[0]['dm_id'] == dm.json()['dm_id']
    assert notifications[0]['notification_message'] == 'johnsmith tagged you in johnsmith,marthajones: @marthajones12345678'
    assert notifications[1]['channel_id'] == -1
    assert notifications[1]['dm_id'] == dm.json()['dm_id']
    assert notifications[1]['notification_message'] == 'johnsmith added you to johnsmith,marthajones'
    

def test_notification_less_than_20_20(setup):
    x = 0
    while x < 30:
        new_channel = requests.post(config.url + "channels/create/v2", json={'token': setup[0].json()['token'], 'name' : 'testchannel', 'is_public' : True})
        requests.post(config.url + "channel/invite/v2", json={'token': setup[0].json()['token'], 'channel_id': new_channel.json()['channel_id'], 'u_id' : setup[1].json()['auth_user_id']})
        x += 1

    assert len(requests.get(config.url + "notifications/get/v1", params = {'token': setup[1].json()['token']}).json()['notifications']) == 20