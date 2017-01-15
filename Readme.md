# Wunderlist to Todoist

A tool for importing Wunderlist backup file to Todoist by using its API.

# Supported Features



# Terms

Term equivalence of Wunderlist and Todoist.

| Wunderlsit | Todoist                   |
| ---------- | ------------------------- |
| List       | Project                   |
| Subtask    | Task with indentation = 2 |

# Limitations

The limitations when importing lists to Todoist.

These limitations are due to lack information is provided in the backup file generated by Wunderlist, so the same happens when restoring backups to Wunderlist.

- Lists that are grouped in a folder in Wunderlist will be flattened in Todoist.
- Lists are not in order
- No file attachment

# Not supported

- Order of tasks in a list
- Order of subtasks in a task.