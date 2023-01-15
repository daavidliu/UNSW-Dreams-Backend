import pytest
from werkzeug.exceptions import BadRequest
from src import error
from src.error import InputError
from src.error import AccessError
import requests
import json
from src import auth, config, message, notifications, channel, channels, dm

@pytest.fixture
def setup():
    #Clear data
    requests.delete(config.url + "clear/v1")
    #Create 2 new users
    auth_user = requests.post(config.url + "auth/register/v2", json = {
        'email' : 'example@email.com', 
        'password' : 'password', 
        'name_first' : 'john', 
        'name_last' : 'smith'
    })

    second_user = requests.post(config.url + "auth/register/v2", json = {
        'email' : 'example2@email.com', 
        'password' : 'password', 
        'name_first' : 'martha', 
        'name_last' : 'jones'
    })
    
    return [auth_user, second_user]

#test that a user can be successfully removed by the admin
def test_admin_user_remove(setup):
    #admin removes user, function returns an empty dictionary
    assert requests.delete(config.url + "admin/user/remove/v1", json={
        'token': setup[0].json()['token'], 
        'u_id': setup[1].json()['auth_user_id']
    }).json() == {}

    #Check that login details & token are now invalid
    assert requests.post(config.url + 'auth/login/v2', json={
        'email' : 'example2@email.com', 
        'password' : 'password'
    }).json()['name'] == 'System Error'
    assert requests.get(config.url + 'channels/list', params = {
        'token': setup[1].json()['token'] 
    }).json()['name'] == 'System Error'


#test the details of the removed user
def test_admin_user_remove_details(setup):
    #User 1 creates a channel and invites user 2 to it
    channel_id = requests.post(config.url + "channels/create/v2", json = {
        "token" : setup[0].json()['token'],  
        "name" : "channel", 
        "is_public" : True
    }).json()['channel_id']
    assert requests.post(config.url + "channel/invite/v2", json = {
        "token" : setup[0].json()['token'],  
        "channel_id" : channel_id, 
        "u_id" : setup[1].json()['auth_user_id']
    }).json() == {}

    #User 2 sends a message in the channel
    requests.post(config.url + "message/send/v2", json = {
        "token" : setup[1].json()['token'], 
        "channel_id" : channel_id, 
        "message" : "Test message"
    })

    #admin removes user, function returns an empty dictionary
    assert requests.delete(config.url + "admin/user/remove/v1", json={
        'token': setup[0].json()['token'], 
        'u_id': setup[1].json()['auth_user_id']
    }).json() == {}

    #user profile is still retrievable by the profile function
    profile = requests.get(config.url + 'user/profile/v2', params = {
        'token': setup[0].json()['token'], 
        'u_id': setup[1].json()['auth_user_id']
    }).json()['user']
    assert profile['name_first'] == 'Removed'
    assert profile['name_last'] == 'user'

    #check the content of channel messages
    messages = requests.get(config.url + 'channel/messages/v2', params = {
        "token" : setup[0].json()['token'], 
        "channel_id" : channel_id, 
        "start" : 0
    }).json()['messages']
    assert messages[0]['message'] == 'Removed user'

#test that a user without admin permission cannot access the admin privilages 
def test_admin_unauthorised(setup):
    #unauthorised use attempts to admin remove
    response = requests.delete(config.url + "admin/user/remove/v1", json = {
        'token': setup[1].json()['token'], 
        'u_id': setup[0].json()['auth_user_id']
    }).json()
    assert response['code'] == 403

    #unauthorised use attempts to admin change permission
    response = requests.post(config.url + "admin/userpermission/change/v1", json = {
        'token': setup[1].json()['token'], 
        'u_id': setup[0].json()['auth_user_id'],
        'permission_id': 2
    }).json()
    assert response['code'] == 403

#test that a user without admin permission cannot access the admin privilages 
def test_admin_permission_change(setup):
    #change admin permission of user2 to admin
    response = requests.post(config.url + "admin/userpermission/change/v1", json = {
        'token': setup[0].json()['token'], 
        'u_id': setup[1].json()['auth_user_id'],
        'permission_id': 1
    }).json()
    assert response == {}

    #change admin permission of user1 to user
    response = requests.post(config.url + "admin/userpermission/change/v1", json = {
        'token': setup[1].json()['token'], 
        'u_id': setup[0].json()['auth_user_id'],
        'permission_id': 2
    }).json()
    assert response == {}

    #remove user1 
    assert requests.delete(config.url + "admin/user/remove/v1", json={
        'token': setup[1].json()['token'], 
        'u_id': setup[0].json()['auth_user_id']
    }).json() == {}