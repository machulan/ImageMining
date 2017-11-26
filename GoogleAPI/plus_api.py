import apiclient
import oauth2client
import httplib2
import time
import random
import json

import GoogleAPI.constants as constants


# import file_handler


def get_OAuth_2_credentials():
    store = oauth2client.file.Storage(constants.CREDENTIAL_PATH)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = oauth2client.client.flow_from_clientsecrets(constants.CLIENT_SECRET_FILE, constants.SCOPES)
        flow.user_agent = constants.APPLICATION_NAME
        credentials = oauth2client.tools.run_flow(flow, store)
        print('Storing credentials to ' + constants.CREDENTIAL_PATH)
    return credentials


def get_plus_service_through_API_key():
    return apiclient.discovery.build('plus', 'v1', developerKey=constants.API_KEY)


def get_plus_service_through_OAuth_2():
    credentials = get_OAuth_2_credentials()
    http = credentials.authorize(httplib2.Http())
    return apiclient.discovery.build('plus', 'v1', http=http)
    # ,discoveryServiceUrl='https://people.googleapis.com/$discovery/rest')


def get_plus_service(credentials_type='API key'):
    print('getting Google+ service through {}...'.format(credentials_type))
    plus_service = None
    if credentials_type == 'API key':
        plus_service = get_plus_service_through_API_key()
    elif credentials_type == 'OAuth 2.0':
        plus_service = get_plus_service_through_OAuth_2()
    return plus_service


def profile_id_to_google_plus_url(profile_id):
    return 'https://plus.google.com/' + profile_id


def get_profile_data_as_json(profile_id, credentials_type='API key'):
    print('getting data of https://plus.google.com/u/0/{} as json through {}...'.format(profile_id, credentials_type))
    plus_service = get_plus_service(credentials_type=credentials_type)
    return plus_service.people().get(userId=profile_id).execute()


def query_generator():
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


def get_unique_profile_ids(count=10, credentials_type='API key', verbose=False):
    print('searching for {} unique Google profile IDs...'.format(count))

    unique_profile_ids = set()

    plus_service = get_plus_service(credentials_type=credentials_type)
    people_resource = plus_service.people()
    # max_results = 10

    query_gen = query_generator()
    query = next(query_gen)
    next_page_token = ''
    current_count = 0
    query_count = 0
    MAX_QUERY_COUNT = 25000
    while current_count < count and query_count < MAX_QUERY_COUNT:
        max_results = min(50, count - current_count)
        people_document = people_resource.search(query=query, maxResults=max_results,
                                                 pageToken=next_page_token).execute()
        query_count += 1
        ids = [item['id'] for item in people_document['items']]
        next_page_token = people_document['nextPageToken']

        # if len(ids) < 10:
        if next_page_token == '':
            query = next(query_gen)

        prev_len = len(unique_profile_ids)
        unique_profile_ids.update(ids)
        current_count += len(unique_profile_ids) - prev_len

        time.sleep(1)

        if verbose:
            print('{} | +{} | query: {} | nextPageToken: {}'.format(current_count, current_count - prev_len, query,
                                                                    next_page_token))

    return list(unique_profile_ids)


def get_profile_display_name(profile_id, credentials_type='API key', verbose=False):
    print('getting profile display name through {}...'.format(credentials_type))
    plus_service = get_plus_service(credentials_type=credentials_type)
    people_resource = plus_service.people()
    people_document = people_resource.get(userId=profile_id).execute()
    display_name = people_document['displayName']
    return display_name


def get_profile_image_url(profile_id, credentials_type='API key', verbose=False):
    print('getting profile image url through {}...'.format(credentials_type))
    plus_service = get_plus_service(credentials_type=credentials_type)
    people_resource = plus_service.people()
    people_document = people_resource.get(userId=profile_id).execute()
    image_url = people_document['image']['url']
    return image_url


def get_profile_image_urls(profile_ids, credentials_type='API key', verbose=False):
    print('getting profile image urls through {}...'.format(credentials_type))
    profile_image_urls = []

    plus_service = get_plus_service(credentials_type=credentials_type)
    people_resource = plus_service.people()
    for i, profile_id in enumerate(profile_ids):
        people_document = people_resource.get(userId=profile_id).execute()
        image_url = people_document['image']['url']
        profile_image_urls.append(image_url)
        if verbose:
            print('{} | {} | {} | {}'.format(i, profile_id, profile_id_to_google_plus_url(profile_id), image_url))

    return profile_image_urls


def get_profile_display_names(profile_ids, credentials_type='API key', verbose=False):
    print('getting profile display names through {}...'.format(credentials_type))
    display_names = []

    plus_service = get_plus_service(credentials_type=credentials_type)
    people_resource = plus_service.people()
    for i, profile_id in enumerate(profile_ids):
        people_document = people_resource.get(userId=profile_id).execute()
        display_name = people_document['displayName']
        display_names.append(display_name)
        if verbose:
            print('{} | {} | {} | {}'.format(i, profile_id, profile_id_to_google_plus_url(profile_id), display_name))

    return display_names


def get_profiles(count, credentials_type='API key', verbose=False):
    """
    [
        {
            profile_id,
            profile_url,
            display_name,
            image_url
        }
    ]
    """
    print('getting profiles through {}...'.format(credentials_type))

    # getting profiles information
    profile_ids = get_unique_profile_ids(count, credentials_type=credentials_type, verbose=verbose)
    profile_urls = list(map(profile_id_to_google_plus_url, profile_ids))
    display_names = get_profile_display_names(profile_ids, credentials_type=credentials_type, verbose=verbose)
    image_urls = get_profile_image_urls(profile_ids, credentials_type=credentials_type, verbose=verbose)

    # saving as plain text
    txt_filename = 'results/plus-api-profiles.txt'
    if verbose:
        print('saving profiles as plain text to {}...'.format(txt_filename))
    result_str = ''
    for profile in zip(profile_ids, profile_urls, display_names, image_urls):
        result_str += '\n'.join(profile) + '\n\n'
    profiles_file = open(txt_filename, 'w', encoding='utf-8')
    profiles_file.write(result_str)
    profiles_file.close()

    # saving as json
    json_filename = 'results/plus-api-profiles.json'
    if verbose:
        print('saving profiles as json to {}...'.format(json_filename))
    result_list = []
    json_fields = ('profileId', 'profileUrl', 'displayName', 'imageUrl')
    for profile in zip(profile_ids, profile_urls, display_names, image_urls):
        result_list.append(dict(zip(json_fields, profile)))
    json_str = json.dumps(result_list)
    profiles_file = open(json_filename, 'w', encoding='utf-8')
    profiles_file.write(json_str)
    profiles_file.close()


if __name__ == '__main__':
    get_profiles(10, verbose=True, credentials_type='OAuth 2.0')

    # unique_profile_ids = get_unique_profile_ids(2000, verbose=True)
    # # print('{} ids'.format(len(unique_profile_ids)))
    # file_handler.write_list_to('unique-profile-ids.txt', unique_profile_ids)
    # # print_urls(list(map(profile_id_to_google_plus_url, unique_profile_ids)))
    #
    # ids = file_handler.read_list_from('unique-profile-ids.txt')
    # profile_ids = ids[:100]
    # display_names = get_profile_display_names(profile_ids, verbose=True)
    # file_handler.write_list_to('unique-profile-display-names.txt', display_names)


    # profile_image_urls = get_profile_image_urls(profile_ids, verbose=True)
    # profile_urls = list(map(profile_id_to_google_plus_url, profile_ids))
    # file_handler.write_list_to('unique-profile-image-urls.txt', profile_image_urls)
    # for profile_url, image_url in zip(profile_urls, profile_image_urls):
    #     print('{} {}'.format(profile_url, image_url))
    # print(len(ids))
    # print(ids[:10])
    # unique_profile_urls = list(map(profile_id_to_google_plus_url, ids))
    # file_handler.write_list_to('unique-profile-urls.txt', unique_profile_urls)
