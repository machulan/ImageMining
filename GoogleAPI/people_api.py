import apiclient
import oauth2client
import httplib2
import time
import random
import json

import GoogleAPI.constants as constants
import GoogleAPI.file_handler as file_handler

import GoogleAPI.plus_api
# from plus_api import get_unique_profile_ids, profile_id_to_google_plus_url


def get_OAuth_2_credentials():
    store = oauth2client.file.Storage(constants.OAUTH_2_CREDENTIALS_PATH)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = oauth2client.client.flow_from_clientsecrets(constants.CLIENT_SECRET_PATH, constants.SCOPES)
        flow.user_agent = constants.APPLICATION_NAME
        credentials = oauth2client.tools.run_flow(flow, store)
        print('Storing credentials to ' + constants.OAUTH_2_CREDENTIALS_PATH)
    return credentials


def get_people_service_through_API_key():
    api_key_file = open(constants.API_KEY_CREDENTIALS_PATH, 'r', encoding='utf-8')
    api_key = api_key_file.read().strip()
    return apiclient.discovery.build('people', 'v1', developerKey=api_key)


def get_people_service_through_OAuth_2():
    credentials = get_OAuth_2_credentials()
    http = credentials.authorize(httplib2.Http())
    return apiclient.discovery.build('people', 'v1', http=http)
    # ,discoveryServiceUrl='https://people.googleapis.com/$discovery/rest')


def get_people_service(credentials_type=constants.API_KEY_CREDENTIALS_TYPE):
    print('getting People API service through {}...'.format(credentials_type))
    people_service = None
    if credentials_type == constants.API_KEY_CREDENTIALS_TYPE:
        people_service = get_people_service_through_API_key()
    elif credentials_type == constants.OAUTH_2_CREDENTIALS_TYPE:
        people_service = get_people_service_through_OAuth_2()
    return people_service


def get_profile_display_names_and_image_urls_with_getBatchGet(profile_ids,
                                                              credentials_type=constants.API_KEY_CREDENTIALS_TYPE,
                                                              verbose=False):
    print('getting profile display names and image urls through {}...'.format(credentials_type))
    display_names = []
    image_urls = []

    people_service = get_people_service(credentials_type=credentials_type)
    people_resource = people_service.people()

    BATCH_SIZE = 50
    error_counter = 0
    i = 0
    while i < len(profile_ids):
        time.sleep(0.5)

        current_part_size = min(BATCH_SIZE, len(profile_ids) - i)
        current_profile_ids = profile_ids[i: i + current_part_size]
        resource_names = list(map(lambda string: 'people/' + string, current_profile_ids))

        # trying to get people document
        people_document = None
        delay = 0.5
        while people_document is None:
            time.sleep(delay)
            try:
                people_document = people_resource.getBatchGet(resourceNames=resource_names,
                                                              personFields='names,photos').execute()
            except apiclient.errors.HttpError:
                delay = 2
                print('{} | ERROR (apiclient.errors.HttpError [429])'.format(i))
                error_counter += 1
                continue

        # adding new data to display_names and image_urls
        new_data = {}
        for response in people_document['responses']:
            person = response.get('person', None)
            if person is None:
                print('Bad response: {}'.format(response))
                resource_name = response['requestedResourceName']
                person = {'resourceName': resource_name}

            resource_name = person['resourceName']  # 'people/114822392780451536009'
            profile_id = resource_name.split('/')[1]  # '114822392780451536009'
            # getting displayName
            if person.get('names', None) is None:
                print('{} | {} | Error. Names through People API is not available.'.format(profile_id,
                                                                                           plus_api.profile_id_to_google_plus_url(profile_id)))
                print('trying to get profile display name through Google+ API...')
                display_name = plus_api.get_profile_display_name(profile_id, credentials_type=credentials_type,
                                                                 verbose=verbose)
                print('received display name: {}'.format(display_name))
                print('{} | {} | {}'.format(profile_id, plus_api.profile_id_to_google_plus_url(profile_id),
                                            display_name))
            else:
                display_name = person['names'][0]['displayName']
            # getting imageUrl
            if person.get('photos', None) is None:
                print('{} | {} | {} | Error. Photos through People API is not available.'.format(profile_id,
                                                                                                 plus_api.profile_id_to_google_plus_url(profile_id), display_name))
                print('trying to get profile image url through Google+ API...')
                image_url = plus_api.get_profile_image_url(profile_id, credentials_type=credentials_type, verbose=verbose)
                print('received image url: {}'.format(image_url))
                print('{} | {} | {} | {}'.format(profile_id, plus_api.profile_id_to_google_plus_url(profile_id), display_name, image_url))
            else:
                image_url = person['photos'][0]['url']
            new_data[profile_id] = {'displayName': display_name, 'imageUrl': image_url}

        for profile_id in current_profile_ids:
            display_names.append(new_data[profile_id]['displayName'])
            image_urls.append(new_data[profile_id]['imageUrl'])

        i += current_part_size

        if verbose:
            print('{} | +{}'.format(i, current_part_size))

    if error_counter != 0:
        print('{} errors (apiclient.errors.HttpError [429])'.format(error_counter))

    # people_document = people_resource.getBatchGet(resourceNames=['people/114822392780451536009', 'people/106651989741536097256'], personFields='names,photos').execute()

    return display_names, image_urls


def get_profile_display_names_and_image_urls(profile_ids, credentials_type=constants.API_KEY_CREDENTIALS_TYPE, verbose=False):
    print('getting profile display names and image urls through {}...'.format(credentials_type))
    display_names = []
    image_urls = []

    people_service = get_people_service(credentials_type=credentials_type)
    people_resource = people_service.people()

    error_counter = 0
    for i, profile_id in enumerate(profile_ids):
        people_document = None
        delay = 0.5
        while people_document is None:
            time.sleep(delay)
            try:
                people_document = people_resource.get(resourceName='people/{}'.format(profile_id),
                                                      personFields='names,photos').execute()
            except apiclient.errors.HttpError:
                delay = 2
                print('{} | {} | ERROR'.format(i, profile_id))
                error_counter += 1
                continue
        display_name = people_document['names'][0]['displayName']
        display_names.append(display_name)
        image_url = people_document['photos'][0]['url']
        image_urls.append(image_url)
        if verbose:
            print('{} | {} | {} | {} | {}'.format(i, profile_id, plus_api.profile_id_to_google_plus_url(profile_id),
                                                  display_name, image_url))
        # time.sleep(0.5)
    print('{} errors'.format(error_counter))

    return display_names, image_urls


def get_profiles(count, credentials_type=constants.API_KEY_CREDENTIALS_TYPE, verbose=False):
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
    profile_ids = plus_api.get_unique_profile_ids(count, credentials_type=credentials_type, verbose=verbose)
    profile_urls = list(map(plus_api.profile_id_to_google_plus_url, profile_ids))
    # display_names, image_urls = get_profile_display_names_and_image_urls(profile_ids, credentials_type=credentials_type,
    #                                                                      verbose=verbose)
    display_names, image_urls = get_profile_display_names_and_image_urls_with_getBatchGet(profile_ids,
                                                                                          credentials_type=credentials_type,
                                                                                          verbose=verbose)

    # saving as plain text
    txt_filename = 'results/people-api-profiles.txt'
    if verbose:
        print('saving profiles as plain text to {}...'.format(txt_filename))
    result_str = ''
    for profile in zip(profile_ids, profile_urls, display_names, image_urls):
        result_str += '\n'.join(profile) + '\n\n'
    profiles_file = open(txt_filename, 'w', encoding='utf-8')
    profiles_file.write(result_str)
    profiles_file.close()

    # saving as json
    json_filename = 'results/people-api-profiles.json'
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
    start_time = time.time()
    get_profiles(10000, verbose=True)
    print('Total time: {} s'.format(round(time.time() - start_time, 2)))

    # TODO get_profiles_through_generator
    # TODO unique_profile_ids_generator OR pass new_seed (custom start query, not 'a') to query_generator

