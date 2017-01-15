import argparse
import todoist
import json
from pprint import pprint as pp

MAX_CMD_COUNTS = 60

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
            if 'created_by_id' in n:
                del n['created_by_id']
            if 'created_by_request_id' in n:
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
            if 'created_by_request_id' in r:
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
            if 'created_by_id' in sub:
                del sub['created_by_id']
            if 'created_by_request_id' in sub:
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
                if 'completed_by_id' in t:
                    del t['completed_by_id']
                if 'completed_at' in t:
                    del t['completed_at']
            if 'created_by_id' in t:
                del t['created_by_id']
            if 'created_by_request_id' in t:
                del t['created_by_request_id']
            del t['created_at']
            del t['revision']
            del t['type']

            tasks.append(t)
    return tasks


def is_in_the_same_proj(task, projects):
    proj_ids = [proj['id'] for proj in projects]
    if task['project_id'] in proj_ids:
        return True
    else:
        return False


def update_item_orders(begin_order, t_task, projects, api, cmd_count):
    """Update tasks' order that are greater than `begin_order`."""
    for task in t_tasks.values():
        if is_in_the_same_proj(task, projects) and task['item_order'] >= begin_order:
            api.items.get_by_id(task['id']).update(item_order=task['item_order']+1)
            update_cmd_count(api)


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


def update_cmd_count(api):
    if not hasattr(update_cmd_count, 'count'):
        update_cmd_count.count = 0

    if update_cmd_count.count >= MAX_CMD_COUNTS:
        res = api.commit()
        pp('//////')
        pp(res)
        update_cmd_count.count = 0
    else:
        update_cmd_count.count += 1


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

    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--wunderlist_backup_file', help='Path to your Wunderlist backup file', required=True)
    parser.add_argument('-a', '--access_token', help='Your Todoist access token', required=True)
    parser.add_argument('-i', '--ignore_complete', help='To ignore completed tasks. (Optional, Default: True)', default=True)

    args = parser.parse_args()
    wunderlist_export_file = args.wunderlist_backup_file
    access_token = args.access_token
    ignore_complete = args.ignore_complete

    # Initialize Todoist API and then reconstruct lists from Wunderlist
    # api = get_authed_api_session(auth_file)
    api = todoist.TodoistAPI(access_token)
    w_lists = read_wunderlist_data(wunderlist_export_file)

    # Create a root project for containing lists from Wunderlist
    root_project = api.projects.add('Imported from Wunderlist')

    res = api.commit()
    if 'error' in res: # check access token is valid
        print("Err: {}".format(res['error']))
        exit(1)

    # Get the item order of the next project
    order = root_project['item_order'] + 1

    cmd_count = 0 # Command counts for Todoist API, which only accepts upto 199 cmds per sync operation

    # Create projects from lists in Wunderlist
    t_projects = {}
    for list in w_lists.values():
        t_projects[list['id']] = api.projects.add(list['title'], indent=2, item_order=order)
        order += 1

        update_cmd_count(api)

    res = api.commit()
    pp('*****')
    pp(res)

    # Add tasks to Todoist
    t_tasks = {}
    for list in w_lists.values():
        for t in list['tasks']:
            pri = 1 if t['starred'] is False else 2
            if not ignore_complete and t['completed'] == False: # to ignore completed tasks
                t_tasks[t['id']] = api.items.add(t['title'], t_projects[list['id']]['id'], priority=pri)
            else:
                t_tasks[t['id']] = api.items.add(t['title'], t_projects[list['id']]['id'], priority=pri, checked=1)

            update_cmd_count(api)

    res = api.commit()
    pp('-----')
    pp(res)

    # Add subtasks, reminder and notes to tasks
    for list in w_lists.values():
        for t in list['tasks']:
            # Add subtasks
            if 'item_order' not in t_tasks[t['id']]:
                print()
            else:
                order = t_tasks[t['id']]['item_order'] + 1
            for sub in t['subtasks']:
                if not ignore_complete and sub['completed'] == False:  # to ignore completed tasks
                    tmp_sub = api.items.add(sub['title'], t_projects[list['id']]['id'], indent=2, item_order=order)
                else:
                    tmp_sub = api.items.add(sub['title'], t_projects[list['id']]['id'], indent=2, item_order=order, checked=1)

                update_cmd_count(api)

                update_item_orders(order, t_tasks, t_projects, api, cmd_count)
                t_tasks[sub['id']] = tmp_sub
                order += 1

            # Add reminder
            if t['reminder'] != None:
                api.reminders.add(t_tasks[t['id']]['id'], service='email', date_string=t['reminder']['date'])

            # Add notes
            for note in t['notes']:
                api.notes.add(t_tasks[t['id']]['id'], note['content'])
                update_cmd_count(api)

    res = api.commit()
    pp('+++++')
    pp(res)
