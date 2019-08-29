from jira import JIRA, JIRAError
from colossus.settings import JIRA_URL


def create_ticket(username,
                  password,
                  project,
                  title,
                  description,
                  reporter,
                  assignee=None,
                  watchers=None,
                ):
    '''
    Creates a JIRA Ticket
    Returns the string URL of the JIRA Ticket
    '''
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
        if watchers is not None:
            for watcher in watchers:
                jira.add_watcher(new_issue.id, watcher)
        Jira.kill_session()
        return str(new_issue)
    except JIRAError as e:
        raise JIRAError()


def update_description(username, password, issue, new_description):
    try:
        Jira = JIRA(JIRA_URL, basic_auth=(username, password), max_retries=0)
        existing_issue = Jira.issue(issue)
        existing_issue.update(description=new_description)
        Jira.kill_session()
    except JIRAError as e:
        raise JIRAError()


def get_projects(username, password):
    '''
    Returns a list of Jira Projects, sorted alphabetically
    '''
    Jira = JIRA(JIRA_URL, basic_auth=(username, password), max_retries=0)
    projects = sorted(Jira.projects(), key=lambda project: project.name.strip())
    return projects

def get_project_id_from_name(username, password, name):
    '''
    Gets a project ID from the provided project Name
    Example: 'Single Cell' returns 11220
    '''
    try:
        Jira = JIRA(JIRA_URL, basic_auth=(username, password), max_retries=0)
        projects = sorted(Jira.projects(), key=lambda project: project.name.strip())
        for project in projects:
            if(project.name == name):
                return project.id
        return None
    except JIRAError as e:
        raise JIRAError()


def add_watchers(username, password, issue, watchers):
    '''
    Given a list of watchers, add them to the provided JIRA Issue
    '''
    print("jira add watchers")
    print(issue,watchers)
    Jira = JIRA(JIRA_URL, basic_auth=(username, password), max_retries=0)
    print(Jira)
    try:
        print("jira issue")
        jira_issue = Jira.issue(issue)
        print(jira_issue)
    except JIRAError as e:
        print("ERROR")
        print(e)
        raise JIRAError()
    for watcher in ['coflanagan']:
        print(watcher)

        Jira.add_watcher(jira_issue, watcher)


def add_jira_comment(username, password, issue, comment):
    '''
    Given a comment, add it to the provided JIRA Issue
    '''
    Jira = JIRA(JIRA_URL, basic_auth=(username, password), max_retries=0)
    try:
        jira_issue = Jira.issue(issue)
    except JIRAError as e:
        raise JIRAError(text="JIRA Error {}: {}".format(e.response.status_code, e.response.reason))
    Jira.add_comment(jira_issue, comment)


def validate_credentials(username, password):
    '''
    Checks whether the provided username/password combo are valid, returns true if valid
    '''
    try:
        Jira = JIRA(JIRA_URL, basic_auth=(username, password), max_retries=0)
        return True
    except JIRAError as e:
        return False


def validate_all_users(username, password, *usernames):
    '''
    Validates the usernames provided in the Django Database when displaying users
    '''
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
