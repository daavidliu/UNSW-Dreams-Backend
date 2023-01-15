from werkzeug.exceptions import BadRequest
from src import error
from src.error import InputError
from src.error import AccessError
import pytest
import requests
import json
from src import config

#function to test the logout function
def test_logout():
    requests.delete(config.url + "clear/v1")
    #register a user
    auth_user = requests.post(config.url + "auth/register/v2", json = {
        'email' : 'example@email.com', 
        'password' : 'password', 
        'name_first' : 'john', 
        'name_last' : 'smith'
    }).json()

    #check for successful logout
    assert requests.post(config.url + "auth/logout/v1", json = {
        'token': auth_user['token']
    }).json() == {
        'is_success': True
    }

    assert requests.post(config.url + "channels/create/v2", json = {
        'token': auth_user['token'],
        'name': 'new channel',
        'is_public': True
    }).json()['name'] == 'System Error'

#test for unsuccessful logout
def test_logout_unsuccessful():
    #register a user
    invalid_token = 'invalid_token'

    #check for successful logout
    assert requests.post(config.url + "auth/logout/v1", json = {
        'token': invalid_token
    }).json() == {
        'is_success': False
    }
