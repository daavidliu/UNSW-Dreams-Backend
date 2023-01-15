import pytest

from src.auth import auth_register_v1
from src.channels import channels_create_v1
from src.channel import channel_invite_v1, channel_details_v1
from src.notifications import notifications_get_v1
from src.dm import dm_create_v1
from src.message import message_senddm_v1, message_send_v1
from src.other import clear_v1

@pytest.fixture
def setup():
    clear_v1()
    user = auth_register_v1('example@email.com', 'password', 'john', 'smith')
    user_2 = auth_register_v1('example2@email.com', 'password', 'martha', 'jones')
    channel = channels_create_v1(user['token'], 'testchannel', True)
    return {'user': user, 'user_2': user_2, 'channel': channel}

#Tests for notifications get functions

#Test basic functionality for notifications in dms
def test_notifications(setup):
    #no initial notifications
    assert len(notifications_get_v1(setup['user_2']['token'])['notifications']) == 0
    
    #1 notification after being invited into a channel
    channel_invite_v1(setup['user']['token'], setup['channel']['channel_id'], setup['user_2']['auth_user_id'])
    assert len(notifications_get_v1(setup['user_2']['token'])['notifications']) == 1

    notification = notifications_get_v1(setup['user_2']['token'])['notifications'][0]
    assert notification['channel_id'] == setup['channel']['channel_id']
    assert notification['dm_id'] == -1
    assert notification['notification_message'] == 'johnsmith added you to testchannel'

    
    #2 notifications after being invited into a dm
    dm = dm_create_v1(setup['user']['token'], [setup['user_2']['auth_user_id']])
    assert len(notifications_get_v1(setup['user_2']['token'])['notifications']) == 2
    
    notification = notifications_get_v1(setup['user_2']['token'])['notifications'][0]
    assert notification['channel_id'] == -1
    assert notification['dm_id'] == dm['dm_id']
    assert notification['notification_message'] == 'johnsmith added you to johnsmith,marthajones'
    
    #3 notifications after being mentioned in a dm message
    message_senddm_v1(setup['user']['token'], dm['dm_id'], 'hi @marthajones')
    assert len(notifications_get_v1(setup['user_2']['token'])['notifications']) == 3

    notification = notifications_get_v1(setup['user_2']['token'])['notifications'][0]
    assert notification['channel_id'] == -1
    assert notification['dm_id'] == dm['dm_id']
    assert notification['notification_message'] == 'johnsmith tagged you in johnsmith,marthajones: hi @marthajones'
    
    #4 notifications after being mentioned in a channel message
    message_send_v1(setup['user']['token'], setup['channel']['channel_id'], '@marthajones hello')
    assert len(notifications_get_v1(setup['user_2']['token'])['notifications']) == 4

    notification = notifications_get_v1(setup['user_2']['token'])['notifications'][0]
    assert notification['channel_id'] == setup['channel']['channel_id']
    assert notification['dm_id'] == -1
    assert notification['notification_message'] == 'johnsmith tagged you in testchannel: @marthajones hello'

#test whether the 20 most recent notifications are sent
def test_notifications_more_messages(setup):
    #invite user_2 to 21 different channels 
    x = 0
    while x < 21:
        new_channel = channels_create_v1(setup['user']['token'], 'channel' + str(x), True)
        channel_invite_v1(setup['user']['token'], new_channel['channel_id'], setup['user_2']['auth_user_id'])
        x += 1
    
    assert len(notifications_get_v1(setup['user_2']['token'])['notifications']) == 20
   
