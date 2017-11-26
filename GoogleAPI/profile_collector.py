import random
import time
import json
import logging

import apiclient

import GoogleAPI.constants as constants
import GoogleAPI.plus_api as plus_api
import GoogleAPI.people_api as people_api


def get_google_plus_url(profile_id):
    return 'https://plus.google.com/' + profile_id


def query_generator():
    print('starting query generator...')

    russian_alphabet = 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя'
    english_alphabet = 'abcdefghijklmnopqrstuvwxyz'
    digits = '0123456789'
    for char in english_alphabet:
        yield char
    for char in russian_alphabet:
        yield char
    for char in digits:
        yield char
    for first_char in english_alphabet:
        for second_char in english_alphabet:
            yield first_char + second_char
    for first_char in russian_alphabet:
        for second_char in russian_alphabet:
            yield first_char + second_char

    yield str(random.randint(0, 10000000))


def unique_profile_id_generator(credentials_type=constants.API_KEY_CREDENTIALS_TYPE, verbose=False):
    print('searching for unique Google profile IDs...')
    print('starting unique profile id generator...')
    start_time = time.time()
    current_time = start_time

    unique_profile_ids = set()

    plus_service = plus_api.get_plus_service(credentials_type=credentials_type)
    people_resource = plus_service.people()

    queries = query_generator()
    query = next(queries)
    next_page_token = ''
    count = 0
    MAX_RESULTS = 50

    while True:
        previous_time = current_time

        people_document = people_resource.search(query=query, maxResults=MAX_RESULTS,
                                                 pageToken=next_page_token).execute()
        profile_ids = [item['id'] for item in people_document['items']]

        next_page_token = people_document['nextPageToken']
        if next_page_token == '':
            query = next(queries)

        previous_count = count

        for profile_id in profile_ids:
            if not (profile_id in unique_profile_ids):
                yield profile_id
                unique_profile_ids.add(profile_id)
                count += 1

        time.sleep(1)

        current_time = time.time()

        if verbose:
            print('{:<10} {} | +{} | query: "{}" | nextPageToken: "{}"'.format('ids', count, count - previous_count,
                                                                               query, next_page_token))
            # if verbose:
            #     print('{:<10} {:>10}s * {:>5}s * '
            #           '{} | +{} | query: "{}" | nextPageToken: "{}"'.format('ids', round(current_time - start_time, 2),
            #                                                                 round(current_time - previous_time, 2),
            #                                                                 count, count - previous_count, query,
            #                                                                 next_page_token))


def profile_generator(credentials_type=constants.API_KEY_CREDENTIALS_TYPE, verbose=False):
    print('getting profiles through {}...'.format(credentials_type))

    people_service = people_api.get_people_service(credentials_type=credentials_type)
    people_resource = people_service.people()

    unique_profile_ids = unique_profile_id_generator(credentials_type=credentials_type, verbose=verbose)
    current_count = 0

    BATCH_SIZE = 50

    while True:
        resource_names = ['people/' + next(unique_profile_ids) for _ in range(BATCH_SIZE)]

        # trying to get people document
        delay = 0.5
        people_document = None
        while people_document is None:
            time.sleep(delay)
            try:
                people_document = people_resource.getBatchGet(resourceNames=resource_names,
                                                              personFields='names,photos').execute()
            except apiclient.errors.HttpError:
                delay = 2
                print('{} | Error [apiclient.errors.HttpError]. '
                      'Cannot get people document through getBatchGet.'.format(current_count))
                continue

        previous_count = current_count

        for response in people_document['responses']:
            status = response['status']
            if status != {}:
                continue

            person = response.get('person', None)
            if person is None:
                continue

            names = person.get('names', None)
            if names is None:
                continue

            photos = person.get('photos', None)
            if photos is None:
                continue

            display_name = names[0]['displayName']
            image_url = photos[0]['url']
            resource_name = response['requestedResourceName']  # 'people/114822392780451536009'
            profile_id = resource_name.split('/')[1]  # '114822392780451536009'
            google_plus_url = get_google_plus_url(profile_id)

            yield (profile_id, google_plus_url, display_name, image_url)

            current_count += 1

        if verbose:
            print('{:<10} {} | +{}'.format('profiles', current_count, current_count - previous_count))


def get_profiles(count, credentials_type=constants.API_KEY_CREDENTIALS_TYPE, verbose=False):
    print('getting profiles through {}...'.format(credentials_type))
    start_time = time.time()
    current_time = start_time

    result = []

    people_service = people_api.get_people_service(credentials_type=credentials_type)
    people_resource = people_service.people()

    unique_profile_ids = unique_profile_id_generator(credentials_type=credentials_type, verbose=verbose)
    current_count = 0

    MAX_BATCH_SIZE = 50

    while current_count < count:
        previous_time = current_time

        batch_size = min(MAX_BATCH_SIZE, count - current_count)
        resource_names = ['people/' + next(unique_profile_ids) for _ in range(batch_size)]

        # trying to get people document
        delay = 0.5
        people_document = None
        while people_document is None:
            time.sleep(delay)
            try:
                people_document = people_resource.getBatchGet(resourceNames=resource_names,
                                                              personFields='names,photos').execute()
            except apiclient.errors.HttpError:
                delay = 2
                print('{} | Error [apiclient.errors.HttpError]. '
                      'Cannot get people document through getBatchGet.'.format(current_count))
                continue

        previous_count = current_count

        for response in people_document['responses']:
            status = response['status']
            if status != {}:
                print('status is empty')
                continue

            person = response.get('person', None)
            if person is None:
                print('person is empty')
                continue

            names = person.get('names', None)
            if names is None:
                print('names is empty')
                continue

            photos = person.get('photos', None)
            if photos is None:
                print('photos is empty')
                continue

            display_name = names[0]['displayName']
            image_url = photos[0]['url']
            resource_name = response['requestedResourceName']  # 'people/114822392780451536009'
            profile_id = resource_name.split('/')[1]  # '114822392780451536009'
            google_plus_url = get_google_plus_url(profile_id)

            result.append((profile_id, google_plus_url, display_name, image_url))

            current_count += 1

        current_time = time.time()

        if verbose:
            print('{:<10} {:>10}s * {:>5}s * {} | +{}'.format('profiles', round(current_time - start_time, 2),
                                                              round(current_time - previous_time, 2), current_count,
                                                              current_count - previous_count))

    return result


def save_profiles_as_txt(profiles, filename):
    print('saving profiles as json to {}...'.format(filename))

    result_str = ''
    for profile in profiles:
        result_str += '\n'.join(profile) + '\n\n'
    profiles_file = open(filename, 'w', encoding='utf-8')
    profiles_file.write(result_str)
    profiles_file.close()


def save_profiles_as_json(profiles, filename):
    print('saving profiles as json to {}...'.format(filename))

    result = []
    JSON_FIELDS = ('profileId', 'profileUrl', 'displayName', 'imageUrl')
    for profile in profiles:
        result.append(dict(zip(JSON_FIELDS, profile)))

    json_str = json.dumps(result)
    profiles_file = open(filename, 'w', encoding='utf-8')
    profiles_file.write(json_str)
    profiles_file.close()


if __name__ == '__main__':
    # profiles = get_profiles(3000, credentials_type=constants.API_KEY_CREDENTIALS_TYPE, verbose=True)
    profile_gen = profile_generator(credentials_type=constants.API_KEY_CREDENTIALS_TYPE, verbose=True)
    profiles = [next(profile_gen) for _ in range(100)]

    for profile in profiles[-10:]:
        print(profile)

    save_profiles_as_txt(profiles, 'results/txts/profiles.txt')
    save_profiles_as_json(profiles, 'results/jsons/profiles.json')
