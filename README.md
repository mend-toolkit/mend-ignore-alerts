[![Logo](https://resources.mend.io/mend-sig/logo/mend-dark-logo-horizontal.png)](https://www.mend.io/)  

[![License](https://img.shields.io/badge/License-Apache%202.0-yellowgreen.svg)](https://opensource.org/licenses/Apache-2.0)
[![CI](https://github.com/whitesource-ps/mend-import-sbom/actions/workflows/ci.yml/badge.svg)](https://github.com/whitesource-ps/mend-import-sbom/actions/workflows/ci.yml/badge.svg)
[![GitHub release](https://img.shields.io/github/v/release/whitesource-ps/ws-import-sbom)](https://github.com/whitesource-ps/ws-import-sbom/releases/latest)  

# Ignore Alerts

Set Ignore status for alert based on whaiver Yaml  

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

| CLI argument                 | Env. Variable   |   Type   | Required | Description                       |
|:-----------------------------|:----------------|:--------:|:--------:|:----------------------------------|
| **&#x2011;&#x2011;help**     |                 | `switch` |    No    | Show help and exit                |
| **&#x2011;&#x2011;user-key** | `WS_USERKEY`    | `string` |   Yes    | Mend User Key                     |
| **&#x2011;&#x2011;api-key**  | `WS_APIKEY`     | `string` |   Yes    | Mend API Key                      |
| **&#x2011;&#x2011;url**      | `WS_WSS_URL`    | `string` |   Yes    | Mend Server URL                   |
| **&#x2011;&#x2011;waiver**   | `WS_WAIVER`    | `string` |   Yes    | Filename of Yaml file for parsing |


## Usage
**Using command-line arguments only:**
```shell
import_sbom --user-key WS_USERKEY --api-key WS_APIKEY --url $WS_WSS_URL --waiver $WS_WAIVER
```
**Using environment variables:**
```shell
export WS_USERKEY=xxxxxxxxxxx
export WS_APIKEY=xxxxxxxxxxx
export WS_WSS_URL=https://saas.mend.io
export WS_WAYVER=waiverexample.yml

ignore_alerts
```
> **Note:** Either form is accepted. For the rest of the examples, the latter form would be used  

## Execution Examples

> **Note:** In the following examples, $WS_USERKEY, $WS_APIKEY and $WS_WSS_URL are assumed to have been exported as environment variables.  

Import SPDX SBOM into a new Mend project

```shell
$ import_sbom --scope "$WS_PRODUCTNAME//$WS_PROJECTNAME" --dir $HOME/reports --input $HOME/reports/$WS_PROJECTNAME-sbom.json
```

Convert SPDX SBOM to an [offline update request](https://docs.mend.io/bundle/wsk/page/understanding_update_requests.html) file for creating a new Mend project under a specific product

```shell
$ import_sbom --scope "$WS_PRODUCTNAME//$WS_PROJECTNAME" --dir $HOME/reports --input $HOME/reports/my-project-sbom.json --offline True
```

Convert SPDX SBOM to an [offline update request](https://docs.mend.io/bundle/wsk/page/understanding_update_requests.html) file for overriding an existing Mend project

```shell
$ import_sbom --scope "$WS_PRODUCTNAME//$WS_PROJECTNAME" --dir $HOME/reports --input $HOME/reports/my-project-sbom.json --offline True

$ import_sbom --scope $WS_PROJECTTOKEN --dir $HOME/reports --input $HOME/reports/my-project-sbom.json --offline True
```

Convert SPDX SBOM to an [offline update request](https://docs.mend.io/bundle/wsk/page/understanding_update_requests.html) file for appending to an existing Mend project

```shell
$ import_sbom --scope "$WS_PRODUCTNAME//$WS_PROJECTNAME" --dir $HOME/reports --input $HOME/reports/my-project-sbom.json --offline True --updateType APPEND

$ import_sbom --scope $WS_PROJECTTOKEN --dir $HOME/reports --input $HOME/reports/my-project-sbom.json --offline True --updateType APPEND
```

## Other Section

### Other Subsection
Details  

