import os

class ImportEnv:

    @property
    def api_key(self):
        return os.environ.get('PIPEDRIVE_API_KEY')

    @property
    def company_domain(self):
        return os.environ.get('COMPANY_DOMAIN')

envs = ImportEnv()