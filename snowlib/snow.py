import requests
import json
import urllib
import xmltodict
from pprint import pprint

from .logger import Logger


class Snow(object):
    def __init__(self, usr, pwd, url, rule):
        self.username = usr
        self.password = pwd
        self.url = url
        self.log = Logger(rule=rule)
        return


    def push_halo_issues(self, halo_issues):
        for halo_issue in halo_issues:
            existing_issue = self.check_issue_exists(halo_issue)
            if not existing_issue:
                self.create_new_issue(halo_issue)


    def create_new_issue(self, halo_issue):
        url_final = self.url + 'api/now/table/sn_si_incident'
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
                 f"<alert_sensor>{halo_issue['type']}</alert_sensor>"
                 f"<contact_type>CloudPassage</contact_type>"
                 f"<cmdb_ci>{halo_issue['asset_name']}</cmdb_ci>"
                 f"<vendor_reference>{halo_issue['id']}</vendor_reference>"
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
        params = {"vendor_reference": issue_id, "active": "true"}
        url_final = self.url + 'api/now/table/sn_si_incident?' + urllib.parse.urlencode(params)

        response = requests.get(url_final, auth=(self.username, self.password), headers=headers)

        if response.status_code != 200:
            self.log.error(
                f'Status: {response.status_code}'
                f'Headers: {response.headers}'
                f'Error Response: {response.content}'
            )

        return xmltodict.parse(response.content)['response']


    def update_all_issues(self, halo):
        url = self.url + 'api/now/table/sn_si_incident?'
        params = {"contact_type": "CloudPassage", "active": "true"}
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
            halo_issue = halo.issue.describe(snow_issue['vendor_reference'])
            halo_issues.append(halo_issue['issue'])
            issue_sys_map[halo_issue['issue']['id']] = snow_issue['sys_id']
        return halo_issues, issue_sys_map



    def update_issue_in_snow(self, halo_issue, issue_sys_map):
        url = self.url + f'api/now/table/sn_si_incident/{issue_sys_map[halo_issue["id"]]}'
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
                 f"<alert_sensor>{halo_issue['type']}</alert_sensor>"
                 f"<contact_type>CloudPassage</contact_type>"
                 f"<cmdb_ci>{halo_issue['asset_name']}</cmdb_ci>"
                 f"<vendor_reference>{halo_issue['id']}</vendor_reference>"
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