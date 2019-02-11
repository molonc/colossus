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
    try:
        Jira = JIRA(JIRA_URL, basic_auth=(username, password), max_retries=0)
        issue_dict = {
            'project': {'id': int(project)},
            'summary': title,
            'description': description,
            'issuetype': {'name': 'Task'},
            'reporter': {'name': reporter},
        }
        new_issue = Jira.create_issue(fields=issue_dict)
        Jira.kill_session()
        return str(new_issue)
    except JIRAError as e:
        raise JIRAError(text="JIRA Error {}: {}".format(e.response.status_code, e.response.reason))


def get_projects(username, password):
    Jira = JIRA(JIRA_URL, basic_auth=(username, password), max_retries=0)
    projects = sorted(Jira.projects(), key=lambda project: project.name.strip())
    return projects

def get_project_id_from_name(username, password, name):
    Jira = JIRA(JIRA_URL, basic_auth=(username, password), max_retries=0)
    projects = sorted(Jira.projects(), key=lambda project: project.name.strip())
    for project in projects:
        if(project.name == name):
            return project.id
    return None
