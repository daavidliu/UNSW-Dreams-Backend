from werkzeug.exceptions import BadRequest
from src import error
from src.error import InputError
from src.error import AccessError
import pytest
import requests
import json
from src import auth, config, message


@pytest.fixture
def setup():
    requests.delete(config.url + "clear/v1")

    james_auth = requests.post(config.url + "auth/register/v2", json={"email" : "jamesj@gmail.com", "password" : "password", "name_first" : "James", "name_last" : "Jules"})
    first_channel = requests.post(config.url + "channels/create/v2", json={"token" : james_auth.json()["token"], "name" : "James", "is_public" : True})
    Nat_auth = requests.post(config.url + "auth/register/v2", json={"email" : "natnot@gmail.com", "password" : "password", "name_first" : "Nat", "name_last" : "Alie"})
    
    first_dm = requests.post(config.url + "dm/create/v1", json={"token" : james_auth.json()["token"],"u_ids" : [Nat_auth.json()["auth_user_id"]]})
    
    dave_auth = requests.post(config.url + "auth/register/v2", json={"email" : "daveee@gmail.com", "password" : "password", "name_first" : "Dave", "name_last" : "Sam"})
    
    return [james_auth, first_channel, Nat_auth, first_dm, dave_auth]


#MESSAGE_SEND
def test_message_send_v1(setup):
    requests.post(config.url + "message/send/v2", json={
        "token" : setup[0].json()["token"], 
        "channel_id" : setup[1].json()["channel_id"], 
        "message" : "Test message"
    }).json()

    #check the content of channel messages
    messages = requests.get(config.url + 'channel/messages/v2', params = {
        "token" : setup[0].json()['token'], 
        "channel_id" : setup[1].json()["channel_id"],
        "start" : 0
    }).json()['messages']
    assert messages[0]['message'] == "Test message"
    requests.delete(config.url + "clear/v1")

def test_message_send_message_too_long(setup):
    result = requests.post(config.url + "message/send/v2", json={"token" : setup[0].json()["token"], "channel_id" : setup[1].json()["channel_id"], "message" : 1000*"ea"})
    assert result.json()['name'] == 'System Error'
    requests.delete(config.url + "clear/v1")
 
def test_message_send_auth_not_in_channel(setup):
    result = requests.post(config.url + "message/send/v2", json={"token" : setup[2].json()["token"], "channel_id" : setup[1].json()["channel_id"], "message" : "Random other message"})
    assert result.json()['name'] == 'System Error'
    requests.delete(config.url + "clear/v1")
    
#MESSAGE_EDIT
def test_message_edit_v1(setup):
    message1_id = requests.post(config.url + "message/send/v2", json={"token" : setup[0].json()["token"], "channel_id" : setup[1].json()["channel_id"], "message" : "Test message"})
    result = requests.put(config.url + "message/edit/v2", json={"token" : setup[0].json()["token"], "message_id" : message1_id.json()["message_id"], "message" : "Message edit works"})
    assert result.json() == {}
    #check the content of channel messages
    messages = requests.get(config.url + 'channel/messages/v2', params = {
        "token" : setup[0].json()['token'], 
        "channel_id" : setup[1].json()["channel_id"],
        "start" : 0
    }).json()['messages']
    assert messages[0]['message'] == "Message edit works"
    requests.delete(config.url + "clear/v1")

def test_message_edit_message_too_long(setup):
    message1_id = requests.post(config.url + "message/send/v2", json={"token" : setup[0].json()["token"], "channel_id" : setup[1].json()["channel_id"], "message" : "Test message"})
    result = requests.put(config.url + "message/edit/v2", json={"token" : setup[0].json()["token"], "message_id" : message1_id.json()["message_id"], "message" : 1001*"e"})
    assert result.json()['name'] == 'System Error'
    requests.delete(config.url + "clear/v1")

def test_message_edit_deleted_message(setup):
    message1_id = requests.post(config.url + "message/send/v2", json={"token": setup[0].json()["token"], "channel_id" : setup[1].json()["channel_id"], "message" : "Test message"})
    print(message1_id.json())

    assert requests.delete(config.url + "message/remove/v1", json={
        "token" : setup[0].json()["token"], 
        "message_id" : message1_id.json()["message_id"]
    }).json() == {}

    result = requests.put(config.url + "message/edit/v2", json={"token" : setup[0].json()["token"], "message_id" : message1_id.json()["message_id"], "message" : "add"})
    assert result.json()['code'] == 400
    requests.delete(config.url + "clear/v1")

def test_message_edit_No_user(setup):   
    message1_id = requests.post(config.url + "message/send/v2", json={"token" : setup[0].json()["token"], "channel_id" : setup[1].json()["channel_id"], "message" : "Test message"})
    result = requests.put(config.url + "message/edit/v2", json={"token" : setup[4].json()["token"], "message_id" : message1_id.json()["message_id"], "message" : "Random other message"})
    assert result.json()['code'] == 403
    requests.delete(config.url + "clear/v1")

#MESSAGE_REMOVE
#remove fucntion

def test_message_remove_nomessage(setup):
    message1_id = requests.post(config.url + "message/send/v2", json={"token" : setup[0].json()["token"], "channel_id" : setup[1].json()["channel_id"], "message" : "Test message"})
    requests.delete(config.url + "message/remove/v1", json={"token" : setup[0].json()["token"], "message_id" : message1_id.json()["message_id"]})
    result = requests.delete(config.url + "message/remove/v1", json={"token" : setup[0].json()["token"], "message_id" : message1_id.json()["message_id"]})
    assert result.json()['code'] == 400
    requests.delete(config.url + "clear/v1")

def test_message_remove_no_user(setup):
    message1_id = requests.post(config.url + "message/send/v2", json={"token" : setup[0].json()["token"], "channel_id" : setup[1].json()["channel_id"], "message" : "Test message"})
    result = requests.delete(config.url + "message/remove/v2", json={"token" : setup[4].json()["token"], "message_id" : message1_id.json()["message_id"]})
    assert result.json()['code'] == 404
    requests.delete(config.url + "clear/v1")


def test_message_share_channel(setup):
    og_message1_id = requests.post(config.url + "message/send/v2", json={
        "token" : setup[0].json()["token"], 
        "channel_id" : setup[1].json()["channel_id"], 
        "message" : "will share the message"
    })
    shared1_message1_id = requests.post(config.url + "message/share/v1", json={
        "token" : setup[0].json()["token"], 
        "og_message_id" : og_message1_id.json()["message_id"], 
        "message" : "will share the message", 
        "channel_id" : setup[1].json()["channel_id"], 
        "dm_id": -1
    })
    
    #check the content of channel messages
    messages = requests.get(config.url + 'channel/messages/v2', params = {
        "token" : setup[0].json()['token'], 
        "channel_id" : setup[1].json()["channel_id"],
        "start" : 0
    }).json()['messages']
    assert len(messages) == 2
    assert messages[0]['message_id'] == shared1_message1_id.json()['shared_message_id']
    assert messages[0]['u_id'] == setup[0].json()["auth_user_id"]

    requests.delete(config.url + "clear/v1")

def test_message_share_dm(setup):
    og_message1_id = requests.post(config.url + "message/send/v2", json={
        "token" : setup[0].json()["token"], 
        "channel_id" : setup[1].json()["channel_id"], 
        "message" : "will share the message"
    })

    shared1_message1_id = requests.post(config.url + "message/share/v1", json={
        "token" : setup[2].json()["token"], 
        "og_message_id" : og_message1_id.json()["message_id"], 
        "message" : "will share the message", 
        'channel_id': -1, 
        "dm_id" : setup[3].json()["dm_id"]
    })

    #check the content of channel messages
    
    messages = requests.get(config.url + 'dm/messages/v1', params = {
        "token" : setup[2].json()['token'], 
        "dm_id" : setup[3].json()["dm_id"],
        "start" : 0
    }).json()['messages']

    assert len(messages) == 1
    assert messages[0]['message_id'] == shared1_message1_id.json()['shared_message_id']
    assert messages[0]['u_id'] == setup[2].json()["auth_user_id"]

#Member is not a part of the dm
def test_message_share_AccessError(setup):

    og_message1_id = requests.post(config.url + "message/send/v2", json={
        "token" : setup[0].json()["token"], 
        "channel_id" : setup[1].json()["channel_id"], 
        "message" : "will share the message"
    })

    shared1_message1_id = requests.post(config.url + "message/share/v1", json={
        "token" : setup[4].json()["token"], 
        "og_message_id" : og_message1_id.json()["message_id"], 
        "message" : "will share the message", 
        'channel_id': -1, 
        "dm_id" : setup[3].json()["dm_id"]
    })

    assert shared1_message1_id.json()['code'] == 403


