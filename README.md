# snow_connector

Synchronize Halo issues with ServiceNow

## What it does

This tool filters issues discovered in Halo using issue attributes and then routes those issues to ServiceNow
specified in routing configuration files. These issues are then continuously synced.


## Requirements

* CloudPassage Halo API key (with auditor permissions)
* ServiceNow instance username and password (with read/write privileges)
* Scheduling system such as crontab
* Python 3.6+ including packages specified in "requirements.txt"

## Installation

```
git clone https://github.com/cloudpassage/snow_connector.git
pip install -r requirements.txt
```

## Configuration

### Define environment variables
Define the following environment variables:

| Name                | Example                          | Explanation     |
|---------------------|----------------------------------|-----------------|
| HALO_API_KEY        | ayj198p9                         |                 |
| HALO_API_SECRET_KEY | 6ulz0yy85xkxkjq8v9z5rahdm4aj909e |                 |
| SNOW_API_USER       | admin        | ServiceNow Username   |
| SNOW_API_PWD      | password         |                 |
| SNOW_API_URL        | https://dev10394.service-now.com/ | SNOW instance URL |
| TABLE | sn_si_incident |   ServiceNow Table to push issues into              |
| TYPE_FIELD       | alert_sensor      | ServiceNow field for issue type   |
| SOURCE_FIELD      | contact_type         |   ServiceNow field for issue source (CloudPassage)              |
| ISSUE_ID_FIELD        | vendor_reference | ServiceNow field for issue ID|


### Setup routing rules

Navigate to "/config/routing" and create routing files based on the template files given.
Delete template files when finished.

An example routing file:

```yaml
# For more information about filters go to https://api-doc.cloudpassage.com/help#issues-filtering-issues
filters:
  issue:
    asset_id: 9c226eaa-a050-44b1-af19-a1541e2b6b1d
    asset_name: ris-win2008r2-policy-test
    asset_type: server
    asset_fqdn: ip-172-31-6-100.us-west-1.compute.internal
    asset_hostname: ip-172-31-6-100
    cp_rule_id: CP:EC2:12
    critical: true
    csp_account_id: 849489318606
    csp_account_name: cloudpassage-qa
    csp_account_type: aws
    csp_image_id: ami-01bbe152bf19d0289
    csp_region: ap-south-1
    csp_resource_id: i-0d318864f4a276ea4
    csp_tags:
      - environment:development
      - Name:halo-aws-s1-ec2-bu01-02
    cve_id:
      - CVE-2017-10684
      - CVE-2017-10685
    first_seen_at: 2019-10-04T07:31:08.237537Z
    group_id: b3d8bec2-6d9a-11e8-a7c2-59b3c642f12b
    group_name: customer-success
    image_sha: null
    name: nameofissue
    source: server_secure
    type: sva
    last_seen_at: 2020-04-27T14:35:53.035654Z
    max_cvss_gte: 7.0
    os_type: linux
    policy_name: CIS AWS Foundations Benchmark Customized v1.2 2019-07-11
    registry_id: c11da753-c69e-4a73-b15b-52c317708df7
    registry_name: cloudpassage_registry
    repository_id: ed843ea1-1f75-47c3-85ef-49a330c686af
    repository_name: cloudpassage_repo
```


## Running (stand-alone)

cd into "snow_connector" directory

To invoke one time only:
```python
python application.py
```

For scheduled job:
(Crontab example)

```
crontab -e
*/2 * * * * /usr/bin/python application.py
```

<!---
#CPTAGS:community-supported integration automation
#TBICON:images/python_icon.png
-->