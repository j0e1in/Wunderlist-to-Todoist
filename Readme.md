# Wunderlist to Todoist

A tool for importing Wunderlist backup file to Todoist by using its API.

# Requirement

- Python 3.4+
- todoist-python

# Usage

```
$ git clone https://github.com/j0e1in/Wunderlist-to-Todoist.git

$ cd Wunderlist-to-Todoist

$ pip install todoist-python

$ python src/import.py -f [path/to/wunderlist_backup_file.json] -a [todoist_access_token]

# Optional argument:
#    `-i false` => do not ignore completed tasks (defualt: true)
#    `-p false` => non-premium account (defualt: true)

```

***Note:***

You can download Wunderlist backup in Wunderlist > Account Settings > Account > Account Backup > Create Backup

You can get your Todoist access token by opening Todoist client > Todoist Settings > Account > API token


# Supported Features

- Premium Uesrs
    - Lists
    - Tasks
    - Subtasks
    - Starred
    - Reminders
    - Notes

- Non-premium Users
    - Lists
    - Tasks
    - Subtasks
    - Starred

***Note:*** Reminders and Notes are not premium features

***Hint:*** Start free premium trial before import.

# Terms

Term equivalence of Wunderlist and Todoist.

| Wunderlsit | Todoist                   |
| ---------- | ------------------------- |
| List       | Project                   |
| Subtask    | Task with indentation = 2 |
| Star       | Priority = 2              |

# Limitations

The limitations when importing lists to Todoist.

These limitations are due to no information is provided in the backup file generated by Wunderlist, so the same happens when restoring backups to Wunderlist.

- Lists that are grouped in a folder in Wunderlist will be flattened in Todoist.
- Lists are not in order
- No file attachment

# Not supported

- Order of tasks in a list
- Order of subtasks in a task.

# ISSUE

If you have any issue or problem please don't hesitate to open one or email me.
