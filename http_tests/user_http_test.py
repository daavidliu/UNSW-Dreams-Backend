''' 
HTTP Tests for the User program,
'''
from random import lognormvariate
from requests.api import request
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
    user = requests.post(config.url + "auth/register/v2", json={'email' : 'example@email.com', 'password' : 'password', 'name_first' : 'john', 'name_last' : 'smith'}).json()
    user2 = requests.post(config.url + "auth/register/v2", json={'email' : 'example2@email.com', 'password' : 'password', 'name_first' : 'martha', 'name_last' : 'jones'}).json()
    return [
        {'token': user['token'], 'id': user['auth_user_id']},
        {'token': user2['token'], 'id': user2['auth_user_id']}
    ]

def test_user_profile(setup):

    result = requests.get(config.url + 'user/profile/v2', params={'token' : setup[0]['token'], 'u_id' : setup[0]['id']})
    img_url = result.json()['user']['profile_img_url']
    assert result.json() == {'user': 
        {'u_id': setup[0]['id'], 
        'email': 'example@email.com', 
        'name_first': 'john', 
        'name_last': 'smith', 
        'handle_str': 'johnsmith',
        'profile_img_url' : img_url,}
    }
    requests.delete(config.url + 'clear/v1')

def test_user_profile_invalid():
    invalid_id = 24601
    invalid_token = 24601
    result = requests.get(config.url + 'user/profile/v2', params={'token' : invalid_token, 'u_id' : invalid_id})
    assert result.json()['code'] == 400
    requests.delete(config.url + 'clear/v1')


def test_user_profile_setname(setup):
    #check for correct return type
    result = requests.put(config.url + 'user/profile/setname/v2', json={'token' : setup[0]['token'], 'name_first' : 'david', 'name_last' : 'liu',})
    assert result.json() == {}
    #check for profile update
    result = requests.get(config.url + 'user/profile/v2', params={'token' : setup[0]['token'], 'u_id' : setup[0]['id']})
    img_url = result.json()['user']['profile_img_url']
    assert result.json() == {'user': 
        {'u_id': setup[0]['id'], 
        'email': 'example@email.com', 
        'name_first': 'david', 
        'name_last': 'liu', 
        'handle_str': 'johnsmith',
        'profile_img_url' : img_url,}
    }
    requests.delete(config.url + 'clear/v1')

def test_user_profile_setname_invalid(setup):
    short_name = ''
    long_name = '123456789012345678901234567890123456789012345678901'
    result = requests.put(config.url + 'user/profile/setname/v2', json={'token' : setup[0]['token'], 'name_first' : short_name, 'name_last' : 'liu',})
    assert result.json()['code'] == 400
    result = requests.put(config.url + 'user/profile/setname/v2', json={'token' : setup[0]['token'], 'name_first' : 'david', 'name_last' : short_name,})
    assert result.json()['code'] == 400
    result = requests.put(config.url + 'user/profile/setname/v2', json={'token' : setup[0]['token'], 'name_first' : long_name, 'name_last' : 'liu',})
    assert result.json()['code'] == 400
    result = requests.put(config.url + 'user/profile/setname/v2', json={'token' : setup[0]['token'], 'name_first' : 'david', 'name_last' : long_name,})
    assert result.json()['code'] == 400

    #test invalid token
    invalid_token = 24601 
    result = requests.put(config.url + 'user/profile/setname/v2', json={'token' : invalid_token, 'name_first' : 'david', 'name_last' : 'liu',})
    assert result.json()['code'] == 400
    requests.delete(config.url + 'clear/v1')

def test_setemail(setup):
    result = requests.put(config.url + 'user/profile/setemail/v2', json={'token' : setup[0]['token'], 'email' : 'update@email.com'})
    assert result.json() == {}
    result = requests.get(config.url + 'user/profile/v2', params={'token' : setup[0]['token'], 'u_id' : setup[0]['id']})
    img_url = result.json()['user']['profile_img_url']
    assert result.json() == {'user': 
        {'u_id': setup[0]['id'], 
        'email': 'update@email.com', 
        'name_first': 'john', 
        'name_last': 'smith', 
        'handle_str': 'johnsmith',
        'profile_img_url' : img_url,}
    }

    requests.delete(config.url + 'clear/v1')

def test_setemail_invalid(setup):
    result = requests.put(config.url + 'user/profile/setemail/v2', json={'token' : setup[0]['token'], 'email' : 'updateemailcom'})
    assert result.json()['code'] == 400
    result = requests.put(config.url + 'user/profile/setemail/v2', json={'token' : setup[0]['token'], 'email' : 'update@emailcom'})
    assert result.json()['code'] == 400

    #email is already being used by another user
    result = requests.put(config.url + 'user/profile/setemail/v2', json={'token' : setup[0]['token'], 'email' : 'example2@email.com'})
    assert result.json()['code'] == 400
    

    requests.delete(config.url + 'clear/v1')


def test_sethandle(setup): 
    result = requests.put(config.url + 'user/profile/sethandle/v1', json={'token' : setup[0]['token'], 'handle_str' : 'uphotdog'})
    assert result.json() == {}
    result = requests.get(config.url + 'user/profile/v2', params={'token' : setup[0]['token'], 'u_id' : setup[0]['id']})
    img_url = result.json()['user']['profile_img_url']
    assert result.json() == {'user': 
        {'u_id': setup[0]['id'], 
        'email': 'example@email.com', 
        'name_first': 'john', 
        'name_last': 'smith', 
        'handle_str': 'uphotdog',
        'profile_img_url' : img_url,}
    }

    requests.delete(config.url + 'clear/v1')

def test_sethandle_invalid(setup):
    short_name = 'jo'
    long_name = 'mamamamamamamamamamamamamamamamamamamamamama'
    result = requests.put(config.url + 'user/profile/sethandle/v1', json={'token' : setup[0]['token'], 'handle_str' : short_name})
    assert result.json()['code'] == 400
    result = requests.put(config.url + 'user/profile/sethandle/v1', json={'token' : setup[0]['token'], 'handle_str' : long_name})
    assert result.json()['code'] == 400

    #handle is already being used by another user
    result = requests.put(config.url + 'user/profile/sethandle/v1', json={'token' : setup[0]['token'], 'handle_str' : 'marthajones'})
    assert result.json()['code'] == 400

    requests.delete(config.url + 'clear/v1')


def test_user_all(setup):
    result = requests.get(config.url + 'users/all/v1', params={'token' : setup[0]['token']})
    
    img_url1 = result.json()['users'][0]['profile_img_url']
    img_url2 = result.json()['users'][1]['profile_img_url']
    assert result.json() == {'users': 
        [
            {'u_id': setup[0]['id'], 
            'email': 'example@email.com', 
            'name_first': 'john', 
            'name_last': 'smith', 
            'handle_str': 'johnsmith',
            'profile_img_url' : img_url1,},
            {'u_id': setup[1]['id'], 
            'email': 'example2@email.com', 
            'name_first': 'martha', 
            'name_last': 'jones', 
            'handle_str': 'marthajones',
            'profile_img_url' : img_url2,}
        ]
    }

    requests.delete(config.url + 'clear/v1')

def test_user_all_invalid(setup):
    invalid_token = 24601
    result = requests.get(config.url + 'users/all/v1', params={'token' : invalid_token})
    assert result.json()['code'] == 400

    requests.delete(config.url + 'clear/v1')

def test_upload_photo(setup):
    result = requests.post(config.url + 'user/profile/uploadphoto', json={'token' : setup[0]['token'], 'img_url' : 'https://upload.wikimedia.org/wikipedia/commons/3/37/African_Bush_Elephant.jpg', 'x_start' : 250, 'y_start' : 800, 'x_end' : 2250, 'y_end' : 2800})
    assert result.json() == {}

def test_upload_photo_invalid(setup):
    result = requests.post(config.url + 'user/profile/uploadphoto', json={'token' : setup[0]['token'], 'img_url' : 'https://upload.wikimedia.org/wikipedia/commons/3/37/African_Bush_Elephant.jpg', 'x_start' : -250, 'y_start' : 800, 'x_end' : 2250, 'y_end' : 2800})
    assert result.json()['code'] == 400
    result = requests.post(config.url + 'user/profile/uploadphoto', json={'token' : setup[0]['token'], 'img_url' : 'https://upload.wikimedia.org/wikipedia/commons/3/37/African_Bush_Elephant.jpg', 'x_start' : 250, 'y_start' : -800, 'x_end' : 2250, 'y_end' : 2800})
    assert result.json()['code'] == 400
    result = requests.post(config.url + 'user/profile/uploadphoto', json={'token' : setup[0]['token'], 'img_url' : 'https://upload.wikimedia.org/wikipedia/commons/3/37/African_Bush_Elephant.jpg', 'x_start' : 250, 'y_start' : 800, 'x_end' : -2250, 'y_end' : 2800})
    assert result.json()['code'] == 400
    result = requests.post(config.url + 'user/profile/uploadphoto', json={'token' : setup[0]['token'], 'img_url' : 'https://upload.wikimedia.org/wikipedia/commons/3/37/African_Bush_Elephant.jpg', 'x_start' : 250, 'y_start' : 800, 'x_end' : 2250, 'y_end' : -2800})
    assert result.json()['code'] == 400

