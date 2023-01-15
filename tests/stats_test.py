import pytest

import src.user
import src.auth
import src.other
import src.stats
import src.channels
import src.message
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

def test_user_stats_v1(setup):
    #new_channel = src.channels.channels_create_v1(setup[0]['token'], 'testchannel', True)
    #new_message_id = src.message.message_send_v1(setup[0]['token'], newchannel['channel_id'], 'is someone here')
    
    '''
    assert src.user.user_stat_v1(setup[0]['token']) == {'user_stats': 
    [{'channels_joined': [{num_channels_joined, time_stamp}],
    ?'dms_joined': [{num_dms_joined, time_stamp}], 
    ?'messages_sent': [{num_messages_sent, time_stamp}], 
    ?involvement_rate}]}
    '''

    stats_list = src.stats.user_stat_v1(setup[0]['token'])
    assert stats_list['user_stats']['channels_joined'][-1]['num_channels_joined'] == 0
    assert stats_list['user_stats']['dms_joined'][-1]['num_dms_joined'] == 0
    assert stats_list['user_stats']['messages_sent'][-1]['num_messages_sent'] == 0
    assert stats_list['user_stats']['involvement_rate'] == 1

    
    new_channel = src.channels.channels_create_v1(setup[0]['token'], 'testchannel', True)
    
    src.dm.dm_create_v1(setup[0]['token'], [ setup[1]['id'] ])
    
    src.message.message_send_v1(setup[0]['token'], new_channel['channel_id'], 'is someone here')
    
    stats_list = src.stats.user_stat_v1(setup[0]['token'])
    assert stats_list['user_stats']['channels_joined'][-1]['num_channels_joined'] == 1
    assert stats_list['user_stats']['dms_joined'][-1]['num_dms_joined'] == 1
    assert stats_list['user_stats']['messages_sent'][-1]['num_messages_sent'] == 1
    assert stats_list['user_stats']['involvement_rate'] == 1

    src.other.clear_v1()

def test_stats_v1_invalidToken(setup):
    invalid_token = 3423423
    with pytest.raises(InputError):
        src.stats.user_stat_v1(invalid_token)
    with pytest.raises(InputError):
        src.stats.users_stats_v1(invalid_token)

    src.other.clear_v1()

def test_users_stats_v1(setup):

    dstats_list = src.stats.users_stats_v1(setup[0]['token'])
    assert dstats_list['dreams_stats']['channels_exist'][0] == 0
    assert dstats_list['dreams_stats']['dms_exist'][0] == 0
    assert dstats_list['dreams_stats']['messages_exist'][0] == 0
    assert dstats_list['dreams_stats']['utilization_rate'] == 0

    new_channel = src.channels.channels_create_v1(setup[0]['token'], 'testchannel', True)
    src.dm.dm_create_v1(setup[0]['token'], [setup[1]['id']])
    src.message.message_send_v1(setup[0]['token'], new_channel['channel_id'], 'is someone here')

    dstats_list = src.stats.users_stats_v1(setup[0]['token'])
    assert dstats_list['dreams_stats']['channels_exist'][0] == 1
    assert dstats_list['dreams_stats']['dms_exist'][0] == 1
    assert dstats_list['dreams_stats']['messages_exist'][0] == 1
    assert dstats_list['dreams_stats']['utilization_rate'] == 1

    src.other.clear_v1()