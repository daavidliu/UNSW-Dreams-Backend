import src.tokenhandler
from flask import request
from src.data import data
from src.data import save_data
from src.error import InputError
from src.error import AccessError
import requests
from PIL import Image
import random



FILE_PATH = 'src/images/'

def upload_photo(token, img_url, x_start, y_start, x_end, y_end):
    current_path = request.url_root

    #check validity of token
    checked_user = src.tokenhandler.check_token(token)
    letters = 'abcdefghijklmnopqrstuvwxyz1234567890'
    random_string = ''.join(random.choice(letters) for i in range(10))
    file_name = str(checked_user['user_id']) + random_string + '.jpg'
    full_path = FILE_PATH + file_name
    
    with open(full_path, 'wb') as handler:
        response = requests.get(img_url, stream=True)

        if not response.ok:
            raise InputError(description='HTTP status error')

        for block in response.iter_content(1024):
            if not block:
                break

            handler.write(block)


    i = Image.open(full_path)
    #check image dimensions, and given coordinates
    check_dimensions(i, x_start, y_start, x_end, y_end)
    
    im = i.crop((x_start, y_start, x_end, y_end))
    
    im.save(full_path)

    #set user profile picture to image
    for user in data['users']:
        if checked_user['user_id'] == user['user_id']:
            user['profile_img_url'] = current_path + 'imgurl/' + file_name
            save_data()

    return {}
    


def check_dimensions(i, x_start, y_start, x_end, y_end):
    width, height = i.size
    if x_start < 0 or x_end < 0 or y_start < 0 or y_end < 0:
        raise InputError(description='given crop coordinates out of bounds')
    
    if x_start > width or x_end > width or y_start > height or y_end > height:
        raise InputError(description='given crop coordinates out of bounds')

    

    
