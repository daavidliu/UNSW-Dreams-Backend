''' 
Tests for the User program,
'''
import pytest

import src.user
import src.auth
import src.other
from src.error import InputError
from src.error import AccessError

@pytest.fixture
def setup():
    src.other.clear_v1()
    user = src.auth.auth_register_v1('example@email.com', 'password', 'john', 'smith')
    user2 = src.auth.auth_register_v1('example@gmail.com', 'password', 'martha', 'jones')
    return [
        {'token': user['token'], 'id': user['auth_user_id']},
        {'token': user2['token'], 'id': user2['auth_user_id']}
    ]

def test_user_profile(setup):
    assert src.user.user_profile(setup[0]['token'], setup[0]['id']) == {'user': 
        {'u_id': setup[0]['id'], 
        'email': 'example@email.com', 
        'name_first': 'john', 
        'name_last': 'smith', 
        'handle_str': 'johnsmith',
        'profile_img_url' : '',}
    }
    src.other.clear_v1()

def test_user_profile_invalid():
    invalid_id = 24601
    invalid_token = 24601
    with pytest.raises(InputError):
        src.user.user_profile(invalid_token, invalid_id)
    src.other.clear_v1()

def test_user_profile_setname(setup):
    #check for correct reuturn type
    assert src.user.user_profile_setname(setup[0]['token'], 'david', 'liu') == {}
    #check for profile update
    assert src.user.user_profile(setup[0]['token'], setup[0]['id']) == {'user': 
        {'u_id': setup[0]['id'], 
        'email': 'example@email.com', 
        'name_first': 'david', 
        'name_last': 'liu', 
        'handle_str': 'johnsmith',
        'profile_img_url' : '',}
    }
    src.other.clear_v1()

def test_user_profile_setname_invalid(setup):
    short_name = ''
    long_name = '123456789012345678901234567890123456789012345678901'
    with pytest.raises(InputError):
        src.user.user_profile_setname(setup[0]['token'], short_name, 'liu') #name_first too short
    with pytest.raises(InputError):
        src.user.user_profile_setname(setup[0]['token'], 'david', short_name) #name_last too short
    with pytest.raises(InputError):
        src.user.user_profile_setname(setup[0]['token'], long_name, 'liu') #name_first too long
    with pytest.raises(InputError):
        src.user.user_profile_setname(setup[0]['token'], 'david', long_name) #name_last too long

    #test invalid token
    invalid_token = 24601 
    with pytest.raises(InputError):
        src.user.user_profile_setname(invalid_token, 'david', 'liu')
    src.other.clear_v1()

def test_setemail(setup):
    assert src.user.user_profile_setemail(setup[0]['token'], 'update@email.com') == {}
    assert src.user.user_profile(setup[0]['token'], setup[0]['id']) == {'user': 
        {'u_id': setup[0]['id'], 
        'email': 'update@email.com', 
        'name_first': 'john', 
        'name_last': 'smith', 
        'handle_str': 'johnsmith',
        'profile_img_url' : '',}
    }

    src.other.clear_v1()

def test_setemail_invalid(setup):
    with pytest.raises(InputError):
        src.user.user_profile_setemail(setup[0]['token'], 'updateemailcom')
    with pytest.raises(InputError):
        src.user.user_profile_setemail(setup[0]['token'], 'update@emailcom')

    #email is already being used by another user
    with pytest.raises(InputError):
        src.user.user_profile_setemail(setup[0]['token'], 'example@gmail.com')
    

    src.other.clear_v1()


def test_sethandle(setup): 
    assert src.user.user_profile_sethandle(setup[0]['token'], 'uphotdog') == {}
    assert src.user.user_profile(setup[0]['token'], setup[0]['id']) == {'user': 
        {'u_id': setup[0]['id'], 
        'email': 'example@email.com', 
        'name_first': 'john', 
        'name_last': 'smith', 
        'handle_str': 'uphotdog',
        'profile_img_url' : '',}
    }

    src.other.clear_v1()

def test_sethandle_invalid(setup):
    short_name = 'jo'
    long_name = 'mamamamamamamamamamama'
    with pytest.raises(InputError):
        src.user.user_profile_setemail(setup[0]['token'], short_name)
    with pytest.raises(InputError):
        src.user.user_profile_setemail(setup[0]['token'], long_name)

    #handle is already being used by another user
    with pytest.raises(InputError):
        src.user.user_profile_setemail(setup[0]['token'], 'marthajones')

    src.other.clear_v1()


def test_user_all(setup):
    assert src.user.user_profile_all(setup[0]['token']) == {'users': 
        [
            {'u_id': setup[0]['id'], 
            'email': 'example@email.com', 
            'name_first': 'john', 
            'name_last': 'smith', 
            'handle_str': 'johnsmith',
            'profile_img_url' : '',},
            {'u_id': setup[1]['id'], 
            'email': 'example@gmail.com', 
            'name_first': 'martha', 
            'name_last': 'jones', 
            'handle_str': 'marthajones',
            'profile_img_url' : '',}
        ]
    }

    src.other.clear_v1()

def test_user_all_invalid(setup):
    invalid_token = 24601
    with pytest.raises(InputError):
        src.user.user_profile_all(invalid_token)

    src.other.clear_v1()
    
