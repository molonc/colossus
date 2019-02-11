from jira import JIRA, JIRAError
from colossus.settings import JIRA_URL

def create_ticket(username,
                  password,
                  instance,
                  title,
                  description,
                  reporter,
                  assignee=None,
                  watchers=None,
                ):
    Jira = JIRA(JIRA_URL, basic_auth=(username, password), max_retries=0)
    print(Jira.project('11220').name)

    Jira.kill_session()

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
