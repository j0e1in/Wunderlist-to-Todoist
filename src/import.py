import todoist
import json
from pprint import pprint as pp

def get_authed_api_session(auth_file):
    # Load user login info
    with open(auth_file) as f:
        auth = json.loads(f.read())

    if 'access_token' not in list(auth.keys()):
        raise AssertionError("No access_token found in the AUTH FILE!")
    else:
        if auth['access_token'] == '':
            print("Please fill in your access token in file {}".format(auth_file))
            print('You can get your access token from Todoist\'s \n'
                'Settings > Account Tab > API token\n'
                'Copy it to the auth file like this:\n'
                '{\n'
                '  "access_token": "[your access token]"\n'
                '}')
            exit(1)

    # Authenticate Todoist api
    api = todoist.TodoistAPI(auth['access_token'])
    return api

def reconstruct_lists_structure(data):
    c_lists = {} # constructed lists

    # Construct list
    for list in data['lists']:
        c_lists[list['id']] = {
            "id"   : list['id'],
            "title": list['title'],
        }

if __name__ == '__main__':

    auth_file = "../data/_auth.json"
    api = get_authed_api_session(auth_file)

    # Read json file
    # with open('../data/test_wunderlist.json') as f:
    #     wunderlist_data = json.loads(f.read())['data']
    #
    # constructed_lists = reconstruct_lists_structure(wunderlist_data)



#+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=#
#           Todoist APIs             #
#+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=#

#--- https://developer.todoist.com ---#

### Project APIs
# api.projects.add(, item_order=) // add a new project
# api.projects.get_by_id(128501815).update(options...) // update a project's arguments
# api.projects.get_by_id(128501815).delete() // delete a project
# api.projects.get_by_id(128501815).archive() // delete a project
# api.projects.get_by_id(128501815).unarchive() // delete a project
# api.projects.update_orders_indents({128501470: [42, 1], 128501607: [43, 1]}) // project_id: [item_order, indent]
# api.templates.import_into_project(128501470, 'example.csv') // import data
# api.templates.export_as_file(128501470) // export as a file
# api.templates.export_as_url(128501470) // export as an url

### Item APIs
# api.items.add('Task1', 128501470)


# api.commit() // commit changes made above
