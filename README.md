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


| CLI argument                 | Env. Variable     |   Type   | Required | Description                                                                                                       |
|:-----------------------------|:------------------|:--------:|:--------:|:------------------------------------------------------------------------------------------------------------------|
| **&#x2011;&#x2011;help**     |                   | `switch` |    No    | Show help and exit                                                                                                |
| **&#x2011;&#x2011;user-key** | `WS_USERKEY`      | `string` |   Yes    | Mend User Key                                                                                                     |
| **&#x2011;&#x2011;api-key**  | `WS_APIKEY`       | `string` |   Yes    | Mend API Key                                                                                                      |
| **&#x2011;&#x2011;url**      | `WS_URL`          | `string` |   Yes    | Mend Server URL                                                                                                   |
| **&#x2011;&#x2011;yaml**     | `WS_YAML`         | `string` |   Yes    | Yaml file's name for parsing in case `mode` is equal `load`. If `mode` is `create` then Yaml file will be created |
| **&#x2011;&#x2011;mode**     | `WS_MODE`         | `string` |   Yes    | `create` or `load` value                                                                                          |
| **&#x2011;&#x2011;product**  | `WS_PRODUCTTOKEN` | string  |    No    | Empty String <br />(Include all products) | Comma-separated list of Mend Product Tokens that should be included |
| **&#x2011;&#x2011;scope**    | `WS_PROJECTTOKEN` | string  |    No    | Empty String <br />(Include all projects) | Comma-separated list of Mend Project Tokens that should be included                                               |
| **&#x2011;&#x2011;exclude**  | `WS_EXCLUDETOKEN` | string  |    No    | Empty String <br /> (No exclusions) | Comma-separated list of Mend Project Tokens that should be excluded                                           |
| **&#x2011;&#x2011;ghpat**    | `WS_GHPAT`        | `string` |    No    | GitHub PAT                                                                                                        |
| **&#x2011;&#x2011;ghowner**  | `WS_GHOWNER`      | `string` |    No    | GitHub Owner                                                                                                      |
| **&#x2011;&#x2011;ghrepo**   | `WS_GHREPO`       | `string` |    No    | GitHub Repo name                                                                                                  |

## Usage
**Using command-line arguments only:**
```shell
ignore_alerts --user-key WS_USERKEY --api-key WS_APIKEY --url $WS_WSS_URL --yaml $WS_YAML --mode create --product xxxxx
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

## Execution Examples

> **Note:** In the following examples, $WS_USERKEY, $WS_APIKEY, $WS_URL and $WS_MODE are assumed to have been exported as environment variables.  

```shell
$ ignore_alerts --yaml whaiverexample.yml --scope xxxxxxx,yyyyyyy --product zzzzzzzzz
```

Usind examplewaiver.yml file from some Repo

```shell
$ ignore_alerts --yaml whaiverexample.yml --ghpat xxxxxxx --ghowner Owner --ghrepo RepoName --product xxxxxxx,yyyyyyyyyy --exclude zzzzzzzzzz 
```
