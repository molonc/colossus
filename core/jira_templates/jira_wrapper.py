from jira import JIRA, JIRAError
from colossus.settings import JIRA_URL

'''
Creates a JIRA Ticket
Returns the string URL of the JIRA Ticket
'''
def create_ticket(username,
                  password,
                  project,
                  title,
                  description,
                  reporter,
                  assignee=None,
                  watchers=None,
                ):
    try:
        Jira = JIRA(JIRA_URL, basic_auth=(username, password), max_retries=0)
        issue_dict = {
            'project': {'id': int(project)},
            'summary': title,
            'description': description,
            'issuetype': {'name': 'Task'},
            'reporter': {'name': reporter},
            'assignee': {'name': assignee},
        }
        new_issue = Jira.create_issue(fields=issue_dict)
        for watcher in watchers:
            jira.add_watcher(new_issue.id, watcher)
        Jira.kill_session()
        return str(new_issue)
    except JIRAError as e:
        raise JIRAError(text="JIRA Error {}: {}".format(e.response.status_code, e.response.reason))


'''
Returns a list of Jira Projects, sorted alphabetically
'''
def get_projects(username, password):
    Jira = JIRA(JIRA_URL, basic_auth=(username, password), max_retries=0)
    projects = sorted(Jira.projects(), key=lambda project: project.name.strip())
    return projects

'''
Gets a project ID from the provided project Name
Example: 'Single Cell' returns 11220
'''
def get_project_id_from_name(username, password, name):
    try:
        Jira = JIRA(JIRA_URL, basic_auth=(username, password), max_retries=0)
        projects = sorted(Jira.projects(), key=lambda project: project.name.strip())
        for project in projects:
            if(project.name == name):
                return project.id
        return None
    except JIRAError as e:
        raise JIRAError(text="JIRA Error {}: {}".format(e.response.status_code, e.response.reason))

'''
Checks whether the provided username/password combo are valid, returns true if valid
'''
def validate_credentials(username, password):
    try:
        Jira = JIRA(JIRA_URL, basic_auth=(username, password), max_retries=0)
        return True
    except JIRAError as e:
        return False

'''
Validates the usernames provided in the Django Database when displaying users
'''
def validate_all_users(username, password, *usernames):
    valid_users = []
    invalid_users = []
    Jira = JIRA(JIRA_URL, basic_auth=(username, password), max_retries=0)
    for user in usernames:
        try:
            user = Jira.user(user)
            vaild_users.append(user)
        except JIRAError as e:
            invalid_users.append(user)
    return valid_users, invalid_users
