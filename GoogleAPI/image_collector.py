import json

import requests
import time

import GoogleAPI.constants as constants


def get_content(url):
    try:
        response = requests.get(url)
    except requests.exceptions.ConnectTimeout:
        print('Connection timeout occured while requesting {}...'.format(url))
        return constants.EMPTY_BINARY_STRING
    except requests.exceptions.ReadTimeout:
        print('Read timeout occured while requesting {}...'.format(url))
        return constants.EMPTY_BINARY_STRING
    except requests.exceptions.ConnectionError:
        print('Connection error occured while requesting {}...'.format(url))
        return constants.EMPTY_BINARY_STRING
    except requests.exceptions.HTTPError as error:
        print('HTTP error occured while requesting {}...'.format(url))
        return constants.EMPTY_BINARY_STRING
    except requests.exceptions.RequestException:
        print('Unknown error occured while requesting {}...'.format(url))
        return constants.EMPTY_BINARY_STRING
    return response.content


def get_and_save_profile_image(profile, foldername, image_size=50):
    profile_id, _, _, image_url = profile
    image_content = get_content('{}?sz={}'.format(image_url, image_size))
    # image_content = get_content(image_url)
    file = open(foldername + '/' + profile_id + '.jpg', 'wb')
    file.write(image_content)
    file.close()


def save_profile_image_blobs_as_json(profiles, filename, image_size=50):
    print('saving profile images as json to {}...'.format(filename))

    result = []
    JSON_FIELDS = ('id', 'image')
    for profile_id, _, _, image_url in profiles:
        image_content = get_content('{}?sz={}'.format(image_url, image_size))
        image_content = ''
        result.append(dict(zip(JSON_FIELDS, (profile_id, image_content))))
    json_str = json.dumps(result)

    file = open(filename, 'w', encoding='utf-8')
    file.write(json_str)
    file.close()


def save_profile_image_blobs_as_txt(profiles, filename, image_size=50):
    print('saving profiles as txt to {}...'.format(filename))

    result_str = ''
    for profile_id, _, _, image_url in profiles:
        image_content = get_content('{}?sz={}'.format(image_url, image_size))
        result_str += '\n'.join((profile_id, str(image_content))) + '\n\n'
    file = open(filename, 'w', encoding='utf-8')
    file.write(result_str)
    file.close()


if __name__ == '__main__':
    import GoogleAPI.profile_collector as profile_collecor

    profiles = profile_collecor.profile_generator(credentials_type=constants.API_KEY_CREDENTIALS_TYPE, verbose=True)
    start_time = time.time()
    for _ in range(200):
        get_and_save_profile_image(next(profiles), 'results/images', image_size=50)
    # ps = []
    # for _ in range(100):
        # ps.append(next(profiles))
    # save_profile_image_blobs_as_json(ps, filename='results/jsons/profile-images.json', image_size=50)
    # save_profile_image_blobs_as_txt(ps, filename='results/txts/profile-images.txt', image_size=50)
    print('Total time: {}s'.format(round(time.time() - start_time, 2)))
