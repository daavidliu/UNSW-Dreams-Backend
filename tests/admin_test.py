import pytest

import src.admin
import src.other
import src.user
import src.channel
import src.channels
import src.message
import src.auth
import src.dm

from src.error import InputError
from src.error import AccessError

@pytest.fixture
def setup():
    src.other.clear_v1()
    #create a new user, create a new channel belonging to that user, then create a new user and add them to the channel
    auth_user = src.auth.auth_register_v1('example@email.com', 'password', 'john', 'smith')
    second_user = src.auth.auth_register_v1('example2@email.com', 'password', 'johns', 'smiths')
    return {'owner': auth_user, 'user': second_user}

#test that a user can be removed by the admin
def test_admin_user_remove(setup):
    #admin removes user, function returns an empty dictionary
    assert src.admin.admin_user_remove(setup['owner']['token'], setup['user']['auth_user_id']) == {}
    

    #user login details are now invalid
    with pytest.raises(InputError):
        src.auth.auth_login_v1('example2@email.com', 'password')
    
    #user profile is still retrievable by the profile function
    assert src.user.user_profile(setup['owner']['token'], setup['user']['auth_user_id']) == {'user' : {
        'u_id' : setup['user']['auth_user_id'],
        'email' : 'removed@user.com',
        'name_first' : 'Removed',
        'name_last' : 'user',
        'handle_str' : 'removeduser',
        'profile_img_url' : ''
        }
    }


def test_admin_messages_remove(setup):
    #user creates a channel and sends a message
    channel_id = src.channels.channels_create_v1(setup['user']['token'], 'channel', True)['channel_id']
    src.channel.channel_invite_v1(setup['user']['token'], channel_id, setup['owner']['auth_user_id'])
    src.message.message_send_v1(setup['user']['token'], channel_id, 'hey')
    #user creates a dm and sends a message
    dm_id = src.dm.dm_create_v1(setup['user']['token'], [setup['user']['auth_user_id'], setup['owner']['auth_user_id']])['dm_id']
    src.message.message_senddm_v1(setup['user']['token'], dm_id, 'hey')

    #user is removed from dreams
    assert src.admin.admin_user_remove(setup['owner']['token'], setup['user']['auth_user_id']) == {}
    
    assert src.channel.channel_messages_v1(setup['owner']['token'], channel_id, 0)['messages'][0]['message'] ==  'Removed user'
    assert src.dm.dm_messages_v1(setup['owner']['token'], dm_id, 0)['messages'][0]['message'] == 'Removed user'


def test_admin_user_remove_error(setup):
    invalid_id = 24678
    with pytest.raises(AccessError):
        src.admin.admin_user_remove(setup['user']['token'], setup['owner']['auth_user_id'])

    with pytest.raises(InputError):
        src.admin.admin_user_remove(setup['owner']['token'], setup['owner']['auth_user_id'])
    
    with pytest.raises(InputError):
        src.admin.admin_user_remove(setup['owner']['token'], invalid_id)

def test_admin_permission_change(setup):
    assert src.admin.admin_permission_change(setup['owner']['token'], setup['user']['auth_user_id'], 1) == {}
    assert src.admin.admin_user_remove(setup['user']['token'], setup['owner']['auth_user_id']) == {}

def test_admin_permission_change2(setup):
    assert src.admin.admin_permission_change(setup['owner']['token'], setup['owner']['auth_user_id'], 2) == {}
    with pytest.raises(AccessError):
        src.admin.admin_user_remove(setup['owner']['token'], setup['user']['auth_user_id'])


def test_admin_permission_change_error(setup):
    invalid_id = 24678
    with pytest.raises(InputError):
        src.admin.admin_permission_change(setup['owner']['token'], invalid_id, 1)
    with pytest.raises(InputError):
        src.admin.admin_permission_change(setup['owner']['token'], setup['user']['auth_user_id'], 3)
    
    with pytest.raises(AccessError):
        src.admin.admin_permission_change(setup['user']['token'], setup['owner']['auth_user_id'], 2)