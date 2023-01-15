''' 
Tests for the Other program,
'''
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
    requests.delete(config.url + 'clear/v1')
    auth_user = requests.post(config.url + "auth/register/v2", json={'email' : 'abcdefgh@ifk.com', 'password' : 'password', 'name_first' : 'john', 'name_last' : 'smith'}).json()
    return auth_user
    
#runs the serch function

def test_other_serch_v2(setup):
    print('hello world')
    demo_string = 'how are you'
    new_channel = requests.post(config.url + "channels/create/v2", json={'token' : setup['token'], 'name' : 'testchannel', 'is_public' : True}).json()
    new_channel2 = requests.post(config.url + "channels/create/v2", json={'token' : setup['token'], 'name' : 'testchannel2', 'is_public' : True}).json()
    
    requests.post(config.url + "message/send/v2", json={'token' : setup['token'], 'channel_id' : new_channel['channel_id'], 'message' : demo_string})
    requests.post(config.url + "message/send/v2", json={'token' : setup['token'], 'channel_id' : new_channel2['channel_id'], 'message' : 'working fine'})

    result = requests.get(config.url + 'search/v2', params={'token' : setup['token'], 'query_str' : demo_string})
    messageTime = result.json()['messages'][0]['time_created']
    assert requests.get(config.url + 'search/v2', params={'token' : setup['token'], 'query_str' : demo_string}).json() == {
        'messages': [
            {
                'message_id': 1, 
                'channel_id': 1, 
                'dm_id': -1, 
                'u_id': 1 ,
                'message': demo_string,
                'time_created': messageTime,
                'is_pinned': False,
                'reacts': [
                    {
                        'is_this_user_reacted': False,
                        'react_id': 1,
                        'u_ids': []
                    }
                ],
            }
        ]
    }
    
    requests.delete(config.url + 'clear/v1')
    
#checks the if the string isn't too ling
def test_other_serch_longStrning(setup):
    long_string = 'hi'*1100 
    result = requests.get(config.url + 'search/v2', params={'token' : setup['token'], 'query_str' : long_string})
    assert result.json()['code'] == 400
    requests.delete(config.url + 'clear/v1')