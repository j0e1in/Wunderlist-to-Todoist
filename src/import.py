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


def get_notes(task_id, data):
    notes = []
    for n in data['notes']:
        if n['task_id'] == task_id:
            # remove unnecessary info
            del n['created_by_request_id']
            del n['revision']
            del n['type']

            notes.append(n)
    return notes


def get_reminder(task_id, data):
    for r in data['reminders']:
        if r['task_id'] == task_id:
            # remove unnecessary info
            del r['updated_at']
            del r['created_at']
            del r['created_by_request_id']
            del r['revision']
            del r['type']
            return r
    return None


def get_subtasks(task_id, data):
    subtasks = []
    for sub in data['subtasks']:
        if sub['task_id'] == task_id:
            # remove unnecessary info
            if sub['completed'] is True:
                del sub['completed_at']
            del sub['created_at']
            del sub['created_by_id']
            del sub['created_by_request_id']
            del sub['revision']
            del sub['type']

            subtasks.append(sub)
    return subtasks


def get_tasks(list_id, data):
    tasks = []
    for t in data['tasks']:
        if t['list_id'] == list_id:
            # add elements that belongs to the task
            t['notes'] = get_notes(t['id'], data)
            t['reminder'] = get_reminder(t['id'], data)
            t['subtasks'] = get_subtasks(t['id'], data)

            # remove unnecessary info
            if t['completed'] is True:
                del t['completed_by_id']
                del t['completed_at']
            del t['created_by_id']
            del t['created_by_request_id']
            del t['created_at']
            del t['revision']
            del t['type']

            tasks.append(t)
    return tasks


def update_item_orders(begin_order):
    """Update tasks' order that are greater than `begin_order`."""
    for task in t_tasks.values():
        if task['item_order'] >= begin_order:
            api.items.get_by_id(task['id']).update(item_order=task['item_order']+1)


def read_wunderlist_data(data_file):
    with open(data_file) as f:
        data = json.loads(f.read())['data']

    ## Reconstruct lists data
    c_lists = {} # constructed lists

    for list in data['lists']:
        c_lists[list['id']] = {
            'id'   : list['id'],
            'title': list['title'],
            'tasks': get_tasks(list['id'], data)
        }
    return c_lists


def write_json_to_file(obj_list, dest_file):
    data = []
    for o in obj_list:
        tmp = {}
        for col in ['id', 'name']:
            tmp[col] = o[col]
        data.append(tmp)

    with open(dest_file, 'a') as f:
        json.dump(data, f)
        f.write('\n')


if __name__ == '__main__':

    auth_file = "../data/_auth.json"
    wunderlist_export_file = "../data/test_wunderlist.json"

    api = get_authed_api_session(auth_file)
    w_lists = read_wunderlist_data(wunderlist_export_file)

    # Create a root project for containing lists from Wunderlist
    root_project = api.projects.add('Imported from Wunderlist')

    api.commit()

    # Get the item order of the next project
    order = root_project['item_order'] + 1

    # Create projects from lists in Wunderlist
    t_projects = {}
    for list in w_lists.values():
        t_projects[list['id']] = api.projects.add(list['title'], indent=2, item_order=order)
        order += 1

    api.commit()

    # Add tasks to Todoist
    t_tasks = {}
    for list in w_lists.values():
        for t in list['tasks']:
            pri = 1 if t['starred'] is False else 2
            if t['completed'] == False: # to ignore completed tasks
                t_tasks[t['id']] = api.items.add(t['title'], t_projects[list['id']]['id'], priority=pri)
            else:
                t_tasks[t['id']] = api.items.add(t['title'], t_projects[list['id']]['id'], priority=pri, checked=1)

    api.commit()

    # Add subtasks, reminder and notes to tasks
    for list in w_lists.values():
        for t in list['tasks']:
            # Add subtasks
            order = t_tasks[t['id']]['item_order'] + 1
            for sub in t['subtasks']:
                if sub['completed'] == False:  # to ignore completed tasks
                    tmp_sub = api.items.add(sub['title'], t_projects[list['id']]['id'], indent=2, item_order=order)
                else:
                    tmp_sub = api.items.add(sub['title'], t_projects[list['id']]['id'], indent=2, item_order=order, checked=1)

                update_item_orders(order)
                t_tasks[sub['id']] = tmp_sub
                order += 1

            # Add reminder
            if t['reminder'] != None:
                api.reminders.add(t_tasks[t['id']]['id'], service='email', date_string=t['reminder']['date'])

            # Add notes
            for note in t['notes']:
                api.notes.add(t_tasks[t['id']]['id'], note['content'])

    api.commit()
