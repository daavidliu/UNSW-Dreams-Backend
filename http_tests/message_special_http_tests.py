from werkzeug.exceptions import BadRequest
from src import error
from src.error import InputError
from src.error import AccessError
import pytest
import requests
import json
from src import config, server
from datetime import datetime, timedelta
import time

@pytest.fixture
def setup():
    requests.delete(config.url + "clear/v1")

    james_auth = requests.post(config.url + "auth/register/v2", json={
        "email" : "jamesj@gmail.com", 
        "password" : "password", 
        "name_first" : "James", 
        "name_last" : "Jules"
    })
    first_channel = requests.post(config.url + "channels/create/v2", json={
        "token" : james_auth.json()["token"], 
        "name" : "James", 
        "is_public" : True
    })
    Nat_auth = requests.post(config.url + "auth/register/v2", json={
        "email" : "natnot@gmail.com", 
        "password" : "password", 
        "name_first" : "Nat", 
        "name_last" : "Alie"})
    
    first_dm = requests.post(config.url + "dm/create/v1", json={
        "token" : james_auth.json()["token"],
        "u_ids" : [Nat_auth.json()["auth_user_id"]]
    })
    
    dave_auth = requests.post(config.url + "auth/register/v2", json={
        "email" : "daveee@gmail.com", 
        "password" : "password", 
        "name_first" : "Dave", 
        "name_last" : "Sam"
    })
    
    return [james_auth, Nat_auth, first_channel, first_dm, dave_auth]

#test for message sendlater dm
def test_message_sendlater(setup):
    delayed_time = datetime.now() + timedelta(0,0.1)

    requests.post(config.url + "message/sendlater/v1", json = {
        "token": setup[0].json()["token"], 
        'channel_id': setup[2].json()['channel_id'],
        "message" : "Test message",
        'time_sent': delayed_time.timestamp()
    })

    #check the content of channel messages
    messages = requests.get(config.url + 'channel/messages/v2', params = {
        "token" : setup[0].json()['token'], 
        "channel_id" : setup[2].json()['channel_id'],
        "start" : 0
    }).json()['messages']

    assert len(messages) == 0

    time.sleep(0.2)

    #check the content of channel messages
    messages = requests.get(config.url + 'channel/messages/v2', params = {
        "token" : setup[0].json()['token'], 
        "channel_id" : setup[2].json()['channel_id'],
        "start" : 0
    }).json()['messages']

    assert len(messages) == 1


#test for message sendlater dm
def test_message_sendlaterdm(setup):
    delayed_time = datetime.now() + timedelta(0,0.1)

    requests.post(config.url + "message/sendlaterdm/v1", json = {
        "token": setup[0].json()["token"], 
        'dm_id': setup[3].json()['dm_id'],
        "message" : "Test message",
        'time_sent': delayed_time.timestamp()
    })

    #check the content of channel messages
    messages = requests.get(config.url + 'dm/messages/v1', params = {
        "token" : setup[0].json()['token'], 
        "dm_id" : setup[3].json()['dm_id'],
        "start" : 0
    }).json()['messages']
    assert len(messages) == 0
    
    time.sleep(0.2)

    #check the content of channel messages
    messages = requests.get(config.url + 'dm/messages/v1', params = {
        "token" : setup[0].json()['token'], 
        "dm_id" : setup[3].json()['dm_id'],
        "start" : 0
    }).json()['messages']
    assert len(messages) == 1

#test for message sendlater errors for sending in the past
def test_message_sendlater_past_invalid(setup):
    past_time = datetime.now() - timedelta(0,0.1)

    assert requests.post(config.url + "message/sendlater/v1", json = {
        "token": setup[0].json()["token"], 
        'channel_id': setup[2].json()['channel_id'],
        "message" : "Test message",
        'time_sent': past_time.timestamp()
    }).json()['code'] == 400

    assert requests.post(config.url + "message/sendlaterdm/v1", json = {
        "token": setup[0].json()["token"], 
        'dm_id': setup[3].json()['dm_id'],
        "message" : "Test message",
        'time_sent': past_time.timestamp()
    }).json()['code'] == 400

#testing errors when the sender is not a part of the channel/DM
def test_message_sendlater_not_in_channel(setup):
    delayed_time = datetime.now() + timedelta(0,0.1)

    assert requests.post(config.url + "message/sendlater/v1", json = {
        "token": setup[4].json()["token"], 
        'channel_id': setup[2].json()['channel_id'],
        "message" : "Test message",
        'time_sent': delayed_time.timestamp()
    }).json()['code'] == 403

    assert requests.post(config.url + "message/sendlaterdm/v1", json = {
        "token": setup[4].json()["token"], 
        'dm_id': setup[3].json()['dm_id'],
        "message" : "Test message",
        'time_sent': delayed_time.timestamp()
    }).json()['code'] == 403

#test for message react
def test_message_react(setup):
    message = requests.post(config.url + "message/send/v2", json={
        "token" : setup[0].json()["token"], 
        "channel_id" : setup[2].json()["channel_id"], 
        "message" : "Test message"
    }).json()

    assert requests.post(config.url + "message/react/v1", json={
        "token" : setup[0].json()["token"], 
        "message_id" : message['message_id'],
        "react_id": 1
    }).json() == {}

    #check the content of channel messages
    messages = requests.get(config.url + 'channel/messages/v2', params = {
        "token" : setup[0].json()['token'], 
        "channel_id" : setup[2].json()["channel_id"],
        "start" : 0
    }).json()['messages']
    assert messages[0]['reacts'][0]['is_this_user_reacted'] == True
    assert messages[0]['reacts'][0]['u_ids'] == [setup[0].json()['auth_user_id']]
    assert messages[0]['reacts'][0]['react_id'] == 1

    assert requests.post(config.url + "message/unreact/v1", json={
        "token" : setup[0].json()["token"], 
        "message_id" : message['message_id'],
        "react_id": 1
    }).json() == {}

    #check the content of channel messages
    messages = requests.get(config.url + 'channel/messages/v2', params = {
        "token" : setup[0].json()['token'], 
        "channel_id" : setup[2].json()["channel_id"],
        "start" : 0
    }).json()['messages']
    assert messages[0]['reacts'][0]['is_this_user_reacted'] == False
    assert messages[0]['reacts'][0]['u_ids'] == []
    assert messages[0]['reacts'][0]['react_id'] == 1

#test for message pin
def test_message_pin(setup):
    message = requests.post(config.url + "message/send/v2", json={
        "token" : setup[0].json()["token"], 
        "channel_id" : setup[2].json()["channel_id"], 
        "message" : "Test message"
    }).json()

    assert requests.post(config.url + "message/pin/v1", json={
        "token" : setup[0].json()["token"], 
        "message_id" : message['message_id']
    }).json() == {}

    #check the content of channel messages
    messages = requests.get(config.url + 'channel/messages/v2', params = {
        "token" : setup[0].json()['token'], 
        "channel_id" : setup[2].json()["channel_id"],
        "start" : 0
    }).json()['messages']
    assert messages[0]['is_pinned'] == True

    assert requests.post(config.url + "message/unpin/v1", json={
        "token" : setup[0].json()["token"], 
        "message_id" : message['message_id']
    }).json() == {}

    #check the content of channel messages
    messages = requests.get(config.url + 'channel/messages/v2', params = {
        "token" : setup[0].json()['token'], 
        "channel_id" : setup[2].json()["channel_id"],
        "start" : 0
    }).json()['messages']
    assert messages[0]['is_pinned'] == False
