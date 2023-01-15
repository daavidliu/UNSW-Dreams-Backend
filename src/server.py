import sys

from os.path import dirname, abspath
d = dirname(dirname(abspath(__file__))) 
sys.path.append(d)

from json import dumps
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from src.error import InputError
from src import config
from werkzeug.exceptions import HTTPException
import src.auth
import src.channel
import src.channels
import src.message
import src.data
import src.dm
import src.user
import src.other
import src.admin
import src.notifications
import src.passwordreset
import src.stats
import src.photo
import src.standup

############
#Don't touch

def defaultHandler(err):
    response = err.get_response()
    print('response', err, err.get_response())
    response.data = dumps({
        "code": err.code,
        "name": "System Error",
        "message": err.get_description(),
    })
    response.content_type = 'application/json'
    return response

APP = Flask(__name__, static_folder='images')
CORS(APP)

APP.config['TRAP_HTTP_EXCEPTIONS'] = True
APP.register_error_handler(Exception, defaultHandler)

#APP.config['IMAGES'] = '/Users/sander/Code/uni/git/project-backend/src/images'
#Don't touch
############

# Example
@APP.route("/echo", methods=['GET'])
def echo():
    dataInput = request.args.get('data')
    if dataInput == 'echo':
   	    raise InputError(description='Cannot echo "echo"')
    return dumps({
        'data': dataInput
    })

@APP.route("/auth/login/v2", methods=['POST'])
def auth_login():
    dataInput = request.get_json()
    email = dataInput['email']
    password = dataInput['password']
    return dumps(src.auth.auth_login_v1(email, password))

@APP.route("/auth/register/v2", methods=['POST'])
def auth_register():
    dataInput = request.get_json()
    email = dataInput['email']
    password = dataInput['password']
    name_first = dataInput['name_first']
    name_last = dataInput['name_last']
    return dumps(src.auth.auth_register_v1(email, password, name_first, name_last))

@APP.route("/auth/logout/v1", methods=['POST'])
def auth_logout():
    dataInput = request.get_json()
    token = dataInput['token']
    return dumps(src.auth.logout_v1(token))

@APP.route("/channel/invite/v2", methods=['POST'])
def channel_invite():
    dataInput = request.get_json()
    token = dataInput['token']
    channel_id = int(dataInput['channel_id'])
    u_id = int(dataInput['u_id'])
    return dumps(src.channel.channel_invite_v1(token, channel_id, u_id))

@APP.route("/channel/details/v2", methods=['GET'])
def channel_details():
    token = request.args.get('token')
    channel_id = int(request.args.get('channel_id'))
    return dumps(src.channel.channel_details_v1(token, channel_id))

@APP.route("/channel/messages/v2", methods=['GET'])
def channel_messages():
    token = request.args.get('token')
    channel_id = int(request.args.get('channel_id'))
    start = request.args.get('start')
    return dumps(src.channel.channel_messages_v1(token, channel_id, start))

@APP.route("/channel/join/v2", methods=['POST'])
def channel_join():
    dataInput = request.get_json()
    token = dataInput['token']
    channel_id = int(dataInput['channel_id'])
    return dumps(src.channel.channel_join_v1(token, channel_id))

@APP.route("/channel/addowner/v1", methods=['POST'])
def channel_addowner():
    dataInput = request.get_json()
    token = dataInput['token']
    channel_id = int(dataInput['channel_id'])
    u_id = int(dataInput['u_id'])
    return dumps(src.channel.channel_addowner_v1(token, channel_id, u_id))

@APP.route("/channel/removeowner/v1", methods=['POST'])
def channel_removeowner():
    dataInput = request.get_json()
    token = dataInput['token']
    channel_id = int(dataInput['channel_id'])
    u_id = int(dataInput['u_id'])
    return dumps(src.channel.channel_removeowner_v1(token, channel_id, u_id))

@APP.route("/channel/leave/v1", methods=['POST'])
def channel_leave():
    dataInput = request.get_json()
    token = dataInput['token']
    channel_id = int(dataInput['channel_id'])
    return dumps(src.channel.channel_leave_v1(token, channel_id))

@APP.route("/channels/list/v2", methods=['GET'])
def channels_list():
    token = request.args.get('token')
    return dumps(src.channels.channels_list_v1(token))

@APP.route("/channels/listall/v2", methods=['GET'])
def channels_listall():
    token = request.args.get('token')
    return dumps(src.channels.channels_listall_v1(token))

@APP.route("/channels/create/v2", methods=['POST'])
def channels_create():
    dataInput = request.get_json()
    token = dataInput['token']
    name = dataInput['name']
    is_public = dataInput['is_public']
    return dumps(src.channels.channels_create_v1(token, name, is_public))

@APP.route("/message/send/v2", methods=['POST'])
def message_send():
    dataInput = request.get_json()
    token = dataInput['token']
    channel_id = int(dataInput['channel_id'])
    message = dataInput['message']
    return dumps(src.message.message_send_v1(token, channel_id, message))

@APP.route("/message/edit/v2", methods=['PUT'])
def message_edit():
    dataInput = request.get_json()
    token = dataInput['token']
    message_id = int(dataInput['message_id'])
    message = dataInput['message']
    return dumps(src.message.message_edit_v1(token, message_id, message))

@APP.route("/message/remove/v1", methods=['DELETE'])
def message_remove():
    dataInput = request.get_json()
    token = dataInput['token']
    message_id = int(dataInput['message_id'])
    return dumps(src.message.message_remove_v1(token, message_id))

@APP.route("/message/share/v1", methods=['POST'])
def message_share():
    dataInput = request.get_json()
    token = dataInput['token']
    og_message_id = int(dataInput['og_message_id'])
    message = dataInput['message']
    channel_id = int(dataInput['channel_id'])
    dm_id = int(dataInput['dm_id'])
    return dumps(src.message.message_share_v1(token, og_message_id, message, channel_id, dm_id))

@APP.route("/message/sendlater/v1", methods=['POST'])
def message_send_later():
    dataInput = request.get_json()
    token = dataInput['token']
    message = dataInput['message']
    channel_id = int(dataInput['channel_id'])
    time_sent = dataInput['time_sent']
    return dumps(src.message.message_sendlater_v1(token, channel_id, message, time_sent))


@APP.route("/message/sendlaterdm/v1", methods=['POST'])
def message_senddm_later():
    dataInput = request.get_json()
    token = dataInput['token']
    dm_id = int(dataInput['dm_id'])
    message = dataInput['message']
    time_sent = dataInput['time_sent']
    return dumps(src.message.message_sendlaterdm_v1(token, dm_id, message, time_sent))

@APP.route("/message/react/v1", methods=['POST'])
def message_react():
    dataInput = request.get_json()
    token = dataInput['token']
    message_id = int(dataInput['message_id'])
    react_id = int(dataInput['react_id'])
    return dumps(src.message.message_react_v1(token, message_id, react_id))

@APP.route("/message/unreact/v1", methods=['POST'])
def message_unreact():
    dataInput = request.get_json()
    token = dataInput['token']
    message_id = int(dataInput['message_id'])
    react_id = int(dataInput['react_id'])
    return dumps(src.message.message_unreact_v1(token, message_id, react_id))

@APP.route("/message/pin/v1", methods=['POST'])
def message_pin():
    dataInput = request.get_json()
    token = dataInput['token']
    message_id = int(dataInput['message_id'])
    return dumps(src.message.message_pin_v1(token, message_id))

@APP.route("/message/unpin/v1", methods=['POST'])
def message_unpin():
    dataInput = request.get_json()
    token = dataInput['token']
    message_id = int(dataInput['message_id'])
    return dumps(src.message.message_unpin_v1(token, message_id))

@APP.route("/dm/details/v1", methods=['GET'])
def dm_details():
    token = request.args.get('token')
    dm_id = int(request.args.get('dm_id'))
    return dumps(src.dm.dm_details_v1(token, dm_id))

@APP.route("/dm/list/v1", methods=['GET'])
def dm_list():
    token = request.args.get('token')
    return dumps(src.dm.dm_list_v1(token))

@APP.route("/dm/create/v1", methods=['POST'])
def dm_create():
    dataInput = request.get_json()
    token = dataInput['token']
    u_ids = dataInput['u_ids']
    return dumps(src.dm.dm_create_v1(token, u_ids))

@APP.route("/dm/remove/v1", methods=['DELETE'])
def dm_remove():
    dataInput = request.get_json()
    token = dataInput['token']
    dm_id = int(dataInput['dm_id'])
    return dumps(src.dm.dm_remove_v1(token, dm_id))

@APP.route("/dm/invite/v1", methods=['POST'])
def dm_invite():
    dataInput = request.get_json()
    token = dataInput['token']
    dm_id = int(dataInput['dm_id'])
    u_id = int(dataInput['u_id'])
    return dumps(src.dm.dm_invite_v1(token, dm_id, u_id))

@APP.route("/dm/leave/v1", methods=['POST'])
def dm_leave():
    dataInput = request.get_json()
    token = dataInput['token']
    dm_id = int(dataInput['dm_id'])
    return dumps(src.dm.dm_leave_v1(token, dm_id))


@APP.route("/dm/messages/v1", methods=['GET'])
def dm_messages():
    token = request.args.get('token')
    dm_id = int(request.args.get('dm_id'))
    start = request.args.get('start')
    return dumps(src.dm.dm_messages_v1(token, dm_id, start))

@APP.route("/message/senddm/v1", methods=['POST'])
def dm_send():
    dataInput = request.get_json()
    token = dataInput['token']
    dm_id = int(dataInput['dm_id'])
    message = dataInput['message']
    return dumps(src.message.message_senddm_v1(token, dm_id, message))

@APP.route("/user/profile/v2", methods=['GET'])
def user_profile():
    token = request.args.get('token')
    u_id = int(request.args.get('u_id'))
    return dumps(src.user.user_profile(token, u_id))

@APP.route("/user/profile/setname/v2", methods=['PUT'])
def user_setname():
    dataInput = request.get_json()
    token = dataInput['token']
    name_first = dataInput['name_first']
    name_last = dataInput['name_last']
    return dumps(src.user.user_profile_setname(token, name_first, name_last))

@APP.route("/user/profile/setemail/v2", methods=['PUT'])
def user_setemail():
    dataInput = request.get_json()
    token = dataInput['token']
    email = dataInput['email']
    return dumps(src.user.user_profile_setemail(token, email))

@APP.route("/user/profile/sethandle/v1", methods=['PUT'])
def user_sethandle():
    dataInput = request.get_json()
    token = dataInput['token']
    handle_str = dataInput['handle_str']
    return dumps(src.user.user_profile_sethandle(token, handle_str))

@APP.route("/users/all/v1", methods=['GET'])
def user_all():
    token = request.args.get('token')
    return dumps(src.user.user_profile_all(token))


@APP.route("/user/stats/v1", methods=['GET'])
def user_stats():
    token = request.args.get('token')
    return dumps(src.stats.user_stat_v1(token))

@APP.route("/users/stats/v1", methods=['GET'])
def users_stats():
    token = request.args.get('token')
    return dumps(src.stats.users_stats_v1(token))



@APP.route("/search/v2", methods=['GET'])
def search():
    token = request.args.get('token')
    query_str = request.args.get('query_str')
    return dumps(src.other.search_v2(token, query_str))

@APP.route("/admin/user/remove/v1", methods=['DELETE'])
def admin_remove():
    dataInput = request.get_json()
    token = dataInput['token']
    u_id = int(dataInput['u_id'])
    return dumps(src.admin.admin_user_remove(token, u_id))

@APP.route("/admin/userpermission/change/v1", methods=['POST'])
def admin_userpermission():
    dataInput = request.get_json()
    token = dataInput['token']
    u_id = int(dataInput['u_id'])
    permission_id = int(dataInput['permission_id'])
    return dumps(src.admin.admin_permission_change(token, u_id, permission_id))

@APP.route("/notifications/get/v1", methods=['GET'])
def notifications_get():
    token = request.args.get('token')
    return dumps(src.notifications.notifications_get_v1(token))

@APP.route("/clear/v1", methods=['DELETE'])
def other_clear():
    return dumps(src.other.clear_v1())

@APP.route("/save", methods=['GET'])
def save():
    return dumps(src.data.save_data())

@APP.route("/auth/passwordreset/request/v1", methods=['POST'])
def reset_request():
    dataInput = request.get_json()
    email = dataInput['email']
    return dumps(src.passwordreset.request_reset(email))

@APP.route("/auth/passwordreset/reset/v1", methods=['POST'])
def password_reset():
    dataInput = request.get_json()
    code = dataInput['reset_code']
    new_password = dataInput['new_password']
    return dumps(src.passwordreset.reset_password(code, new_password))

@APP.route("/user/profile/uploadphoto", methods=['POST'])
def upload_photo():
    dataInput = request.get_json()
    token = dataInput['token']
    img_url = dataInput['img_url']
    x_start = dataInput['x_start']
    y_start = dataInput['y_start']
    x_end = dataInput['x_end']
    y_end = dataInput['y_end']
    return dumps(src.photo.upload_photo(token, img_url, x_start, y_start, x_end, y_end))

@APP.route("/imgurl/<img>")
def get_image(img):
    print(f'\n\n\n\n\n{sys.path}\n\n\n\n\n\n ')
    '''
    try:
        return send_from_directory(APP.config['IMAGES'], filename=img, as_attachment=False)
    except:
        raise InputError("file not found")
    '''
    #return send_from_directory(APP.static_url_path, img)
    return send_from_directory(APP.static_folder, filename=img, as_attachment=False)

@APP.route("/standup/start/v1", methods=['POST'])
def standup_start():
    dataInput = request.get_json()
    token = dataInput['token']
    channel_id = int(dataInput['channel_id'])
    length = dataInput['length']
    return dumps(src.standup.standup_start_v1(token, channel_id, length))

@APP.route("/standup/active/v1", methods=['GET'])
def standup_active():
    token = request.args.get('token')
    channel_id = int(request.args.get('channel_id'))
    return src.standup.standup_active_v1(token, channel_id)

@APP.route("/standup/send/v1", methods=['POST'])
def standup_send():
    dataInput = request.get_json()
    token = dataInput['token']
    channel_id = int(dataInput['channel_id'])
    message = dataInput['message']
    return dumps(src.standup.standup_send_v1(token, channel_id, message))

if __name__ == "__main__":
    # src.data.load_data()
    # print(src.data.data)
    APP.run(port=config.port) # Do not edit this port
    
