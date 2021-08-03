"""Manage configuration for application."""
import os
import yaml
from .logger import Logger


class ConfigHelper(object):
    """Gather configuration from environment variables.

    Attributes:
        halo_api_key (str): Auditor API key for CloudPassage Halo.
        halo_api_secret_key (str): Halo API secret.
        halo_api_hostname (str): Halo API hostname.
        snow_api_user (str): Username for ServiceNow.
        snow_api_pwd (str): Password for ServiceNow.
        snow_api_url (str): URL for ServiceNow instance.
    """

    def __init__(self):
        self.logger = Logger()
        self.rules = self.set_rules()
        self.config = self.set_config()
        self.halo_api_key = os.getenv('HALO_API_KEY') or self.config.get('HALO_API_KEY')
        self.halo_api_secret_key = os.getenv('HALO_API_SECRET_KEY') or self.config.get('HALO_API_SECRET_KEY')
        self.halo_api_hostname = os.getenv('HALO_API_HOSTNAME') or \
                                 self.config.get('HALO_API_HOSTNAME', "api.cloudpassage.com")
        self.snow_api_user = os.getenv('SNOW_API_USER') or self.config.get('SNOW_API_USER')
        self.snow_api_pwd = os.getenv('SNOW_API_PWD') or self.config.get('SNOW_API_PWD')
        self.snow_api_url = os.getenv('SNOW_API_URL') or self.config.get('SNOW_API_URL')


    def validate_config(self):
        """Return True if all required vars are set, False otherwise."""
        validation_passed = True
        validation_passed = self.validate_creds()
        return validation_passed


    def validate_creds(self):
        missing_vars = []
        if not self.halo_api_key:
            missing_vars.append('HALO_API_KEY')
        if not self.halo_api_secret_key:
            missing_vars.append('HALO_API_SECRET_KEY')
        if not self.halo_api_hostname:
            missing_vars.append('HALO_API_HOSTNAME')
        if not self.snow_api_user:
            missing_vars.append('SNOW_API_USER')
        if not self.snow_api_pwd:
            missing_vars.append('SNOW_API_PWD')
        if not self.snow_api_url:
            missing_vars.append('SNOW_API_URL')

        if missing_vars:
            self.logger.critical(f"Missing config attributes: {','.join(missing_vars)}")
            return False
        return True


    def set_config(self):
        config = {}
        config_dir = self.relpath_to_abspath('../config/etc')
        if not os.path.exists(config_dir):
            return config
        try:
            file_path = list(os.scandir(config_dir))[0].path
            return self.open_yaml(file_path)
        except IndexError:
            return config

    def set_rules(self):
        rules = []
        rules_dir = self.relpath_to_abspath('../config/routing')
        if not os.path.exists(rules_dir):
            return rules
        for file in os.scandir(rules_dir):
            rule = self.open_yaml(file.path)
            rule['name'] = file.path.split('/')[-1]
            rules.append(rule)
        return rules

    def open_yaml(self, path):
        with open(path, 'r') as stream:
            try:
                return yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                self.logger.error(exc)

    @staticmethod
    def relpath_to_abspath(rel_path):
        here_dir = os.path.abspath(os.path.dirname(__file__))
        abs_path = os.path.join(here_dir, rel_path)
        return abs_path
