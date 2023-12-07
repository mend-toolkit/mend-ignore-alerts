[![Logo](https://resources.mend.io/mend-sig/logo/mend-dark-logo-horizontal.png)](https://www.mend.io/)  

[![License](https://img.shields.io/badge/License-Apache%202.0-yellowgreen.svg)](https://opensource.org/licenses/Apache-2.0)

# Ignore Alerts

Set Ignore status for alert based on input YAML file  

<hr>

- [Supported Operating Systems](#supported-operating-systems)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration Parameters](#configuration-parameters)
- [Usage](#usage)
- [Execution Examples](#execution-examples)
- [Other Section](#other-section)
  - [Other Subsection](#other-subsection)

<hr>

## Supported Operating Systems
- **Linux (Bash):**	CentOS, Debian, Ubuntu
- **Windows (PowerShell):**	10, 2012, 2016

## Prerequisites
- Python 3.9+
- Mend user with admin permissions

## Installation
```
$ pip install mend-ignore-alerts
```
> **Note:** Depending on whether the package was installed as a root user or not, you need to make sure the package installation location was added to the `$PATH` environment variable.

## Configuration Parameters
>**Note:** Parameters can be specified as either command-line arguments, environment variables, or a combination of both.  
> 
> Command-line arguments take precedence over environment variables.  


| CLI argument                                        | Env. Variable     |   Type   | Required | Description                                                                                                                                                                                                         |
|:----------------------------------------------------|:------------------|:--------:|:--------:|:--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **&#x2011;&#x2011;help**                            |                   | `switch` |    No    | Show help and exit                                                                                                                                                                                                  |
| **&#x2011;&#x2011;user-key, &#x2011;k**             | `WS_USERKEY`      | `string` |   Yes    | Mend User Key                                                                                                                                                                                                       |
| **&#x2011;&#x2011;api-key, &#x2011;o**              | `WS_APIKEY`       | `string` |   Yes    | Mend API Key                                                                                                                                                                                                        |
| **&#x2011;&#x2011;url, &#x2011;u**                  | `WS_URL`          | `string` |   Yes    | Mend Server URL                                                                                                                                                                                                     |
| **&#x2011;&#x2011;yaml**                            | `WS_YAML`         | `string` |    No    | Yaml file's name for parsing in case `mode` is equal `load`. If `mode` is `create` then Yaml file will be created                                                                                                   |
| **&#x2011;&#x2011;baselineProjectToken, &#x2011;b** |          | `string` |    No    | Token of the Mend project the ignored alerts are pulled from.                                                                                                                                                       |
| **&#x2011;&#x2011;destProjectName, &#x2011;n**      |          | `string` |    No    | Name of the Mend project where the alerts will be ignored.                                                                                                                                                          |
| **&#x2011;&#x2011;destProjectVersion, &#x2011;v**   |          | `string` |    No    | Version of the Mend project where the alerts will be ignored.                                                                                                                                                       |
| **&#x2011;&#x2011;mode**                            | `WS_MODE`         | `string` |    No    | `create` or `load` value                                                                                                                                                                                            |
| **&#x2011;&#x2011;product, &#x2011;d**              | `WS_PRODUCTTOKEN` | string  |    No    | Comma-separated list of Mend Product Tokens that should be included. Empty String (Include all products) <br /> Using a baseline project token, the provided product token will be used as the destination product. | 
| **&#x2011;&#x2011;scope, &#x2011;t**                | `WS_PROJECTTOKEN` | string  |    No    | Comma-separated list of Mend Project Tokens that should be included. Empty String (Include all projects) <br /> Using a baseline project token, the provided project token will be used as the destination project. | 
| **&#x2011;&#x2011;exclude**                         | `WS_EXCLUDETOKEN` | string  |    No    | Comma-separated list of Mend Project Tokens that should be excluded . Empty String <br /> (No exclusions)                                                                                                           | 
| **&#x2011;&#x2011;comment**                         |       | `string` |    No    | The default comment for ignoring process. If the parameter is not set then standard note “Automatically Ignored by Mend Utility” will be used                                                                       |
| **&#x2011;&#x2011;ghpat**                           | `WS_GHPAT`        | `string` |    No    | GitHub PAT                                                                                                                                                                                                          |
| **&#x2011;&#x2011;ghowner**                         | `WS_GHOWNER`      | `string` |    No    | GitHub Owner                                                                                                                                                                                                        |
| **&#x2011;&#x2011;ghrepo**                          | `WS_GHREPO`       | `string` |    No    | GitHub Repo name                                                                                                                                                                                                    |
`* Note:`

* The tool will create or load data using the input YAML file if a baseline project token is not provided. In case a baseline project token is provided it will be used to ignore alerts by this template (the YAML file would not used).
* WS_PROJECTTOKEN/--scope used for creating YAML file or as destination project token in case baseline project token provided.
* Pay attention:  The ignoring alerts process ignores all alerts depending on the “whitelist” CVEs or CVEs from the YAML file.
## The Config file example
```ini
[DEFAULT]
wsUrl=
userKey=
orgToken=
baselineProjectToken=
destProjectName=
destProjectVersion=
destProjectToken=  # This parameter associated with WS_PROJECTTOKEN (--product)
destProductToken=  # This parameter associated with WS_PRODUCTTOKEN (--scope)
whitelist=
mode=
yaml=
excludeTokens=
comment=  # The default comment for ignoring alerts process
GHPat=
GHRepo=
GHOwner=
```
## Input/Output YAML example
```yaml
- productname: Some Product Name  # Product Name  
  projectname: Some Project Name  # Project Name
  vulns:
  - end_date: 'YYYY-MM-DD'  # If the date passed, the alert related to CVE below (id_vuln) will not be ignored. 
                            # In other case if this CVE was ignored before then it will be reactivated.   
    id_vuln: CVE-XXXX-XXXXXXX  # The identification of a vulnerability
    note: 'Some alert note'  # The note is using as a comment for ignoring the process 
  - end_date: 'YYYY-MM-DD'
    id_vuln: CVE-XXXX-XXXXXXX
    note: 'Alert comment'
```
## Usage
**Using command-line arguments only (create YAML file):**
```shell
ignore_alerts --user-key WS_USERKEY --api-key WS_APIKEY --url $WS_WSS_URL --yaml $WS_YAML --mode create --product xxxxx
```
> **Note:** In the following example, $WS_USERKEY, $WS_APIKEY, $WS_URL and $WS_MODE are assumed to have been exported as environment variables.  

```shell
$ ignore_alerts --yaml whaiverexample.yml --scope xxxxxxx,yyyyyyy --product zzzzzzzzz
```
**Using command-line arguments only (use baseline project):**
```shell
ignore_alerts --user-key WS_USERKEY --api-key WS_APIKEY --url $WS_WSS_URL -b xxxxxx -n ProjectName -v ProjectVersion
```
**Using environment variables:**
```shell
export WS_USERKEY=xxxxxxxxxxx
export WS_APIKEY=xxxxxxxxxxx
export WS_URL=https://saas.mend.io
export WS_YAML=waiverexample.yml
export WS_PROJECTTOKEN = xxxxxxxxxx,yyyyyyyyyyyy

ignore_alerts --mode create
```
> **Note:** Either form is accepted. For the rest of the examples, the latter form would be used  

**Getting waiver file from GitHub Repo:**
```shell
export WS_USERKEY=xxxxxxxxxxx
export WS_APIKEY=xxxxxxxxxxx
export WS_URL=https://saas.mend.io
export WS_YAML=waiverexample.yml
export WS_GHPAT=xxxxxxxxxxx
export WS_GHOWNER = xxxxxxxxxxx
export WS_GHREPO = TestRepoName 

ignore_alerts --mode load
```

**Running script as part of CI process:**
The example of CI yaml file
```yaml
name: Ignore Alert Workflow

on:
  workflow_dispatch:

jobs:
  build:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.9']
    steps:
      - name: Checkout repository
        uses: actions/checkout@v2

      - name: Install dependencies
        run: |
          pip install mend-ignore-alerts

      - name: Run ignore_alert script
        env:
          WS_APIKEY: ${{ secrets.apikey }}
          USER_KEY: ${{ secrets.userkey }}
          WS_URL: "saas.mend.io"
          YAML: "examplewaiver.yml"
          
        run: 
          ignore_alerts --url $WS_URL --yaml $YAML --apiKey $WS_APIKEY --user-key $USER_KEY --mode load
```

The YAML file should be placed in the Repo folder on GitHub
