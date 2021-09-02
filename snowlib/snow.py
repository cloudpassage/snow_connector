import requests
import json
import urllib
import xmltodict

from .logger import Logger


class Snow(object):
    def __init__(self, config, rule):
        self.config = config
        self.username = config.snow_api_user
        self.password = config.snow_api_pwd
        self.url = config.snow_api_url
        self.log = Logger(rule=rule)
        return


    def push_halo_issues(self, halo_issues):
        for halo_issue in halo_issues:
            existing_issue = self.check_issue_exists(halo_issue)
            if not existing_issue:
                self.create_new_issue(halo_issue)


    def create_new_issue(self, halo_issue):
        url_final = self.url + f'api/now/table/{self.config.table}'
        formatted_issue = json.dumps(halo_issue, indent=2)

        # Set proper headers
        headers = {"Content-Type":"application/xml","Accept":"application/json"}

        # Do the HTTP request
        response = requests.post(
            url_final,
            auth=(self.username, self.password),
            headers=headers,
            data=f"<request>"
                 f"<entry>"
                 f"<short_description>{halo_issue['asset_name']}: {halo_issue['name']}</short_description>"
                 f"<description>{formatted_issue}</description>"
                 f"<{self.config.type_field}>{halo_issue['type']}</{self.config.type_field}>"
                 f"<{self.config.source_field}>CloudPassage</{self.config.source_field}>"
                 f"<cmdb_ci>{halo_issue['asset_name']}</cmdb_ci>"
                 f"<{self.config.issue_id_field}>{halo_issue['id']}</{self.config.issue_id_field}>"
                 f"</entry>"
                 f"</request>"
        )

        # Check for HTTP codes other than 201
        if response.status_code != 201:
            self.log.error(
                f'Status: {response.status_code}'
                f'Headers: {response.headers}'
                f'Error Response: {response.content}'
            )


    def check_issue_exists(self, halo_issue):
        issue_id = halo_issue["id"]

        headers = {"Accept":"application/xml"}
        params = {self.config.issue_id_field: issue_id, "active": "true"}
        url_final = self.url + f'api/now/table/{self.config.table}?' + urllib.parse.urlencode(params)

        response = requests.get(url_final, auth=(self.username, self.password), headers=headers)

        if response.status_code != 200:
            self.log.error(
                f'Status: {response.status_code}'
                f'Headers: {response.headers}'
                f'Error Response: {response.content}'
            )

        return xmltodict.parse(response.content)['response']


    def update_all_issues(self, halo):
        url = self.url + f'api/now/table/{self.config.table}?'
        params = {self.config.source_field: "CloudPassage", "active": "true"}
        url_final = url + urllib.parse.urlencode(params)

        headers = {"Accept":"application/xml"}

        response = requests.get(url_final, auth=(self.username, self.password), headers=headers)

        if response.status_code != 200:
            self.log.error(
                f'Status: {response.status_code}'
                f'Headers: {response.headers}'
                f'Error Response: {response.content}'
            )

        snow_issues = xmltodict.parse(response.content)['response']['result']

        halo_issues, issue_sys_map = self.get_halo_issues(halo, snow_issues)
        halo_issues = halo.get_asset_and_findings(halo_issues)
        halo_issues = halo.get_cve_details(halo_issues)

        for issue in halo_issues:
            self.update_issue_in_snow(issue, issue_sys_map)



    def get_halo_issues(self, halo, snow_issues):
        halo_issues = []
        issue_sys_map = {}
        for snow_issue in snow_issues:
            halo_issue = halo.issue.describe(snow_issue[self.config.issue_id_field])
            halo_issues.append(halo_issue['issue'])
            issue_sys_map[halo_issue['issue']['id']] = snow_issue['sys_id']
        return halo_issues, issue_sys_map



    def update_issue_in_snow(self, halo_issue, issue_sys_map):
        url = self.url + f'api/now/table/{self.config.table}/{issue_sys_map[halo_issue["id"]]}'
        headers = {"Content-Type":"application/xml", "Accept":"application/xml"}

        formatted_issue = json.dumps(halo_issue, indent=2)

        status = ""
        if halo_issue["status"] == "resolved":
            status = "<state>Closed</state>"

        response = requests.patch(
            url,
            auth=(self.username, self.password),
            headers=headers,
            data=f"<request>"
                 f"<entry>"
                 f"<short_description>{halo_issue['asset_name']}: {halo_issue['name']}</short_description>"
                 f"<description>{formatted_issue}</description>"
                 f"<{self.config.type_field}>{halo_issue['type']}</{self.config.type_field}>"
                 f"<{self.config.source_field}>CloudPassage</{self.config.source_field}>"
                 f"<cmdb_ci>{halo_issue['asset_name']}</cmdb_ci>"
                 f"<{self.config.issue_id_field}>{halo_issue['id']}</{self.config.issue_id_field}>"
                 f"{status}"
                 f"</entry>"
                 f"</request>"
        )

        if response.status_code != 200:
            self.log.error(
                f'Status: {response.status_code}'
                f'Headers: {response.headers}'
                f'Error Response: {response.content}'
            )