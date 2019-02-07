from jira import JIRA, JIRAError
from colossus.settings import JIRA_URL

class JiraWrapper:
    #Initiate a JIRA Instance
    def __init__(self, username, password):
        try:
            self.jira = JIRA(JIRA_URL, basic_auth=(username, password), max_retries=0)
        except JIRAError as e:
            error_code = e.response.status_code
            error_message = e.response.reason
            raise JIRAError(text="Error code {}: {}".format(error_code, error_message))

    def create_ticket(self, instance, title, description, reporter, assignee=None, watchers=None):
        # Build the title - use the fact that DLP has pool_id field
        # to differentiate the library classes
        if hasattr(instance, 'pool_id'):
            # Use the DLP pool ID
            title = (str(instance.sample)
                     + "-" + str(instance.pool_id)
                     + "-" + str(title))
        else:
            title = str(instance.sample) + "-" + str(title)

    def add_comment(self, comment):
        pass

    def update_ticket(self):
        pass

    def list_projects(self):
        return self.jira.projects()
