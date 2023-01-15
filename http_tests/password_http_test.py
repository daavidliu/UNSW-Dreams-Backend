'''
White box test for password reset function
'''

import pytest
from requests.api import request
from src import error
from src.error import InputError
from src.error import AccessError
import requests
import json
from src import config
from src.passwordreset import request_reset, reset_password
from src.data import data

@pytest.fixture
def setup():
    requests.delete(config.url + "clear/v1")
    #create a new user, create a new channel belonging to that user, then create a new user and add them to the channel
    auth_user = requests.post(config.url + "auth/register/v2", json={'email' : 'example@notrealemail.com', 'password' : 'password', 'name_first' : 'john', 'name_last' : 'smith'})
    
    return [auth_user]

def test_code(setup):
    #assert a code is generated
    email = 'example@notrealemail.com'
    requests.post(config.url + "auth/passwordreset/request/v1", json={'email' : email})
    for user in data['users']:
        if email == user['email']:
            assert user['code'] != ''

def test_reset(setup):
    code = 'notacode'
    email = 'example@notrealemail.com'
    requests.post(config.url + "auth/passwordreset/request/v1", json={'email' : email})
    requests.post(config.url + "auth/passwordreset/request/v1", json={'email' : email})
    print('here')
    for user in data['users']:
        print('HERE')
        if email == user['email']:
            assert user['code'] != ''
            code = user['code']
            print(code)
            requests.post(config.url + "auth/passwordreset/reset/v1", json={'reset_code' : code, 'new_password' : 'newpassword'})
            assert user['password'] == 'newpassword' 
            

def test_invalid_code(setup):
    email = 'example@notrealemail.com'
    code = 'notacode'
    request_reset(email)
    with pytest.raises(InputError):
        reset_password(code, 'newpassword')


    
