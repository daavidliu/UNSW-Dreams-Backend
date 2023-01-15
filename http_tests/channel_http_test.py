''' 
HTTP Tests for the Channel program,
'''
from werkzeug.exceptions import BadRequest
from src import error
from src.error import InputError
from src.error import AccessError
import pytest
import requests
import json
from src import auth, config, message

#test functions
@pytest.fixture
def setup():
    requests.delete(config.url + "clear/v1")
    #create a new user, create a new channel belonging to that user, then create a new user and add them to the channel
    auth_user = requests.post(config.url + "auth/register/v2", json={'email' : 'example@email.com', 'password' : 'password', 'name_first' : 'john', 'name_last' : 'smith'})
    second_user = requests.post(config.url + "auth/register/v2", json={'email' : 'example2@email.com', 'password' : 'password', 'name_first' : 'johns', 'name_last' : 'smiths'})
    new_channel = requests.post(config.url + "channels/create/v2", json={'token' : auth_user.json()['token'], 'name' : 'testchannel', 'is_public' : True})
    
    return [auth_user, second_user, new_channel]

def test_channel_invite_valid(setup):
    requests.post(config.url + "channel/invite/v2", json={'token' : setup[0].json()['token'], 'channel_id' : setup[2].json()['channel_id'], 'u_id' : setup[1].json()['auth_user_id']}) == {}
    assert requests.get(config.url + "channels/list/v2", params={'token' : setup[0].json()['token']}).json() == {
        'channels': [{'channel_id': setup[2].json()['channel_id'], 'name': 'testchannel'}]
    }
    requests.delete(config.url + "clear/v1")

def test_channel_invite_users(setup):
    #second user is not in any channels
    assert requests.get(config.url + "channels/list/v2", params={'token' : setup[1].json()['token']}).json() == {'channels': []}
    
    requests.post(config.url + "channel/invite/v2", json={'token' : setup[0].json()['token'], 'channel_id' : setup[2].json()['channel_id'], 'u_id' : setup[1].json()['auth_user_id']})
    
    #check that the user is in new_channel
    assert requests.get(config.url + "channels/list/v2", params={'token' : setup[1].json()['token']}).json() == {
        'channels': [{'channel_id': setup[2].json()['channel_id'], 'name': 'testchannel'}]
    }

    assert requests.get(config.url + "channel/details/v2", params={
        'token' : setup[1].json()['token'],
        'channel_id' : setup[2].json()['channel_id']
    }).json()['all_members'][1]['u_id'] == setup[1].json()['auth_user_id']
    
    requests.delete(config.url + "clear/v1")

#test if correct input errors are produced with invlalid auth user inputs 
def test_channel_invite_auth_error(setup):
    invalid_token = 'invalidToken'
    result = requests.post(config.url + "channel/invite/v2", json={'token' : invalid_token, 'channel_id' : setup[2].json()['channel_id'], 'u_id' : setup[1].json()['auth_user_id']})
    assert result.json()['name'] == 'System Error'
    #with pytest.raises(BadRequest):
        
    requests.delete(config.url + "clear/v1")

#test if correct input errors are produced with invlalid user inputs 
def test_channel_invite_user_error(setup):
    
    invalid_id = -10000
    result = requests.post(config.url + "channel/invite/v2", json={'token' : setup[0].json()['token'], 'channel_id' : setup[2].json()['channel_id'], 'u_id' : invalid_id})
    assert result.json()['name'] == 'System Error'
    #inviting user is not in the channel
    result2 = requests.post(config.url + "channel/invite/v2", json={'token' : "not a token", 'channel_id' : setup[2].json()['channel_id'], 'u_id' : setup[1].json()['auth_user_id']})
    assert result2.json()['name'] == 'System Error'

    #inviting user who already exists in channel
    requests.post(config.url + "channel/invite/v2", json={'token' : setup[0].json()['token'], 'channel_id' : setup[2].json()['channel_id'], 'u_id' : setup[1].json()['auth_user_id']})
    result3 = requests.post(config.url + "channel/invite/v2", json={'token' : setup[0].json()['token'], 'channel_id' : setup[2].json()['channel_id'], 'u_id' : setup[1].json()['auth_user_id']})
    print(result3.json())  
    assert result3.json() == {}
    requests.delete(config.url + "clear/v1")

##test if correct input errors are produced with invlalid channel inputs 
def test_channel_invite_channel_error(setup):
    result = requests.post(config.url + "channel/invite/v2", json={'token' : setup[0].json()['token'], 'channel_id' : 'not a channel id', 'u_id' : setup[1].json()['auth_user_id']})
    assert result.json()['name'] == 'System Error'

    requests.delete(config.url + "clear/v1")

#test the channel add owner and remove owner functions
def test_channel_addremoveowner_success(setup):
    #add user to the channel
    requests.post(config.url + "channel/invite/v2", json={
        'token' : setup[0].json()['token'], 
        'channel_id' : setup[2].json()['channel_id'], 
        'u_id' : setup[1].json()['auth_user_id']
    })
    #make user the owner
    assert requests.post(config.url + 'channel/addowner/v1', json={
        'token' : setup[0].json()['token'], 
        'channel_id' : setup[2].json()['channel_id'], 
        'u_id' : setup[1].json()['auth_user_id']
    }).json() == {}

    assert requests.get(config.url + "channel/details/v2", params={
        'token' : setup[1].json()['token'],
        'channel_id' : setup[2].json()['channel_id']
    }).json()['owner_members'][1]['u_id'] == setup[1].json()['auth_user_id']

    #remove user as the owner
    assert requests.post(config.url + 'channel/removeowner/v1', json={
        'token' : setup[0].json()['token'], 
        'channel_id' : setup[2].json()['channel_id'], 
        'u_id' : setup[1].json()['auth_user_id']
    }).json() == {}

    owner_list = requests.get(config.url + "channel/details/v2", params={
        'token' : setup[1].json()['token'],
        'channel_id' : setup[2].json()['channel_id']
    }).json()['owner_members']
    
    assert len(owner_list) == 1

#test the channel leave function
def test_channel_leave_success(setup):
    #add user to the channel
    requests.post(config.url + "channel/invite/v2", json={
        'token' : setup[0].json()['token'], 
        'channel_id' : setup[2].json()['channel_id'], 
        'u_id' : setup[1].json()['auth_user_id']
    })
    assert requests.post(config.url + "channel/leave/v1", json={
        'token' : setup[1].json()['token'], 
        'channel_id' : setup[2].json()['channel_id'], 
    }).json() == {}

    member_list = requests.get(config.url + "channel/details/v2", params={
        'token' : setup[0].json()['token'],
        'channel_id' : setup[2].json()['channel_id']
    }).json()['all_members']

    assert len(member_list) == 1

    assert requests.get(config.url + "channel/details/v2", params={
        'token' : setup[1].json()['token'],
        'channel_id' : setup[2].json()['channel_id']
    }).json()['name'] == 'System Error'


