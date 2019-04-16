import os
from storages.backends.azure_storage import AzureStorage
from colossus.settings import AZURE_ACCOUNT_KEY

class AzureMediaStorage(AzureStorage):
    account_name = 'olympusbackups' # Must be replaced by your <storage_account_name>
    account_key = AZURE_ACCOUNT_KEY # Must be replaced by your <storage_account_key>
    azure_container = 'colossus-media'
    expiration_secs = None

class AzureStaticStorage(AzureStorage):
    account_name = 'olympusbackups' # Must be replaced by your storage_account_name
    account_key = os.environ.get('STORAGE_SECRET_KEY') # Must be replaced by your <storage_account_key>
    azure_container = 'colossus-static'
    expiration_secs = None
