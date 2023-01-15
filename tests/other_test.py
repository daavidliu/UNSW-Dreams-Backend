''' 
Tests for the Other program,
'''
import pytest
import src.other
import src.channels
import src.auth
import src.message
from datetime import timezone, datetime
from src.data import data
from src.error import InputError
from src.error import AccessError

@pytest.fixture
def setup():
    src.other.clear_v1()
    auth_user_id = src.auth.auth_register_v1('abcdefgh@ifk.com', 'password', 'john', 'smith')
    return auth_user_id
#tests the clear function returns nothing
def test_clear():
    assert src.other.clear_v1() == {}

#runs the clear function
#ensures the users, channel(s), and messages have been cleared successfully.
def test_clear_successful(setup):
    # Clear 
    src.other.clear_v1()
    # Check there is input error when logging in with previously registered details
    with pytest.raises(InputError):
        src.auth.auth_login_v1('example@email.com', 'password')

    # Make new user & channel
    auth_user_id = src.auth.auth_register_v1('example@email.com', 'password', 'john', 'smith')
    src.channels.channels_create_v1(auth_user_id['token'], 'test', True)
    # Clear
    src.other.clear_v1()
    # Check there are no channels
    assert data['users'] == []
    assert data['channels'] == []
    assert data['dms'] == []
    assert data['messages'] == []
    
#runs the serch function
def test_other_serch_v2(setup):
    print('hello world')
    demo_string = 'how are you'
    new_channel = src.channels.channels_create_v1(setup['token'], 'testchannel', True)
    new_channel2 = src.channels.channels_create_v1(setup['token'], 'testchannel', True)
    src.message.message_send_v1(setup['token'], new_channel['channel_id'], demo_string)
    src.message.message_send_v1(setup['token'], new_channel2['channel_id'], 'working fine')
    messageTime = src.other.search_v2(setup['token'], demo_string)['messages'][0]['time_created']
    assert src.other.search_v2(setup['token'], demo_string) == {
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
    
    src.other.clear_v1()
#checks the if the string isn't too ling
def test_other_serch_longStrning(setup):
    long_string = 'hi'*1100 
    with pytest.raises(InputError):
        src.other.search_v2(setup['token'], long_string)

    src.other.clear_v1()


