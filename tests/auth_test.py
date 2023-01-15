''' 
Tests for the Authentication program, the funcitons auth_login_v1 & auth_register_v1.
'''
import pytest

import src.auth
import src.other
import src.user

from src.error import InputError
from src.error import AccessError

#test successful register & login without errors
def test_register_login():
    user_1 = src.auth.auth_register_v1('user1_random@domain.com' , 'passew@321', 'user1' , 'random')
    user_2 = src.auth.auth_register_v1('dummyemail_01@gmail.com', 'yewhawios098', 'Hailey', 'Scott')
    #check that the auth_user_id is the same
    assert user_1['auth_user_id'] == src.auth.auth_login_v1('user1_random@domain.com', 'passew@321')['auth_user_id']
    assert user_2['auth_user_id'] == src.auth.auth_login_v1('dummyemail_01@gmail.com', 'yewhawios098')['auth_user_id']

    #registering wit same name, should return a modified handle
    user_3 = src.auth.auth_register_v1('dummyemail_02@gmail.com', 'yewhawios098', 'Hailey', 'Scott')
    assert src.user.user_profile(user_3['token'], user_3['auth_user_id'])['user'] == {
        'u_id': user_3['auth_user_id'], 
        'email': 'dummyemail_02@gmail.com', 
        'name_first': 'Hailey', 
        'name_last': 'Scott', 
        'handle_str': 'haileyscott0',
        'profile_img_url' : '',
    } 

    #clear data
    src.other.clear_v1()

#test error if the user logging in is not registered
def test_login_not_registered():
    with pytest.raises(InputError):
        src.auth.auth_login_v1('unknownuserwrite123@', 'abcdefg12345')

#test login with incorrect details
def test_login_wrong_input():
    src.auth.auth_register_v1('hannajules15@gmail.com', 'sydney1507', 'Hanna', 'Jules')
    with pytest.raises(InputError):
        #Wrong email used
        src.auth.auth_login_v1('hannajules29@gmail.com', 'sydney1507') 

    src.auth.auth_register_v1('joleybess@gmail.com', 'jessboley', 'Bess', 'Joley')
    with pytest.raises(InputError):
        #Incorrect password used
        src.auth.auth_login_v1('joleybess@gmail.com', 'name1234') 
    
    #clear data
    src.other.clear_v1()

#test that function rejects invalid email formats     
def test_valid_email():
    #valid email formats 
    email_1 = "ankitrai326@gmail.com"
    email_2 = "my.ownsite@ourearth.org"
    src.auth.auth_register_v1(email_1, 'password', 'john', 'smith')
    src.auth.auth_register_v1(email_2, 'password', 'john', 'smith') 

    #invalid email formats
    email_3 = "ankitrai326.com"
    email_4 = "ankitrai326@google"
    with pytest.raises(InputError):
        src.auth.auth_register_v1(email_3, 'password', 'john', 'smith')
    with pytest.raises(InputError):
        src.auth.auth_register_v1(email_4, 'password', 'john', 'smith')

    #valid email, but already registered
    with pytest.raises(InputError):
        src.auth.auth_register_v1(email_1, 'password', 'john', 'smith')
    
    #clear data 
    src.other.clear_v1()

#test that function rejects invalid password formats    
def test_valid_password():
    #password is less than 6 characters
    password_1 = "hello"
    with pytest.raises(InputError):
        src.auth.auth_register_v1('email@email.com', password_1, 'john', 'smith')
    
    #password is 6 characters
    password_2 = "helloo"
    src.auth.auth_register_v1('email@email.com', password_2, 'john', 'smith')

    #clear data
    src.other.clear_v1()

#test that function rejects invalid first/last name formats     
def test_valid_name():
    #name less than 1 letter 
    name_first_1 = ""
    name_last_1 = ""
    with pytest.raises(InputError):
        src.auth.auth_register_v1('email1@email.com', 'password', name_first_1, 'smith') 
    with pytest.raises(InputError):
        src.auth.auth_register_v1('email@email1.com', 'password', 'john', name_last_1)

    #name longer than 50 letters
    name_first_2 = "abcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyz"
    name_last_2 = "abcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyz"
    with pytest.raises(InputError):
        src.auth.auth_register_v1('email2@email.com', 'password', name_first_2, 'smith')
    with pytest.raises(InputError):
        src.auth.auth_register_v1('email@email2.com', 'password', 'john', name_last_2) 

    #name with correct length
    name_first_3 = "Sanjana"
    name_last_3 = "Bombay"
    src.auth.auth_register_v1('email3@email.com', 'password', name_first_3, 'smith')
    src.auth.auth_register_v1('email@email3.com', 'password', 'john', name_last_3)

    #clear data 
    src.other.clear_v1()


def test_logout_successful():
    #test successful logout
    user = src.auth.auth_register_v1('email@email.com', 'password', 'john', 'smith')
    assert src.auth.logout_v1(user['token']) == {'is_success': True}
    src.other.clear_v1()

def test_logout_unsuccessful():
    #test unsuccessful logout
    invalid_token = 24678
    
    assert src.auth.logout_v1(invalid_token) == {'is_success': False}
    src.other.clear_v1()

