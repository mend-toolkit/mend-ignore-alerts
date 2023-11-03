import argparse
import inspect
import json
import logging
import os
import re
import sys

import requests
import yaml
from github import Github
from datetime import datetime

from mend_ignore_alerts._version import __version__, __tool_name__, __description__
from mend_ignore_alerts.const import aliases, varenvs
from importlib import metadata

logger = logging.getLogger(__tool_name__)
logger.setLevel(logging.DEBUG)
try:
    is_debug = logging.DEBUG if os.environ.get("DEBUG").lower() == 'true' else logging.INFO
except:
    is_debug = logging.INFO

formatter = logging.Formatter('[%(asctime)s] %(levelname)5s %(message)s', "%Y-%m-%d %H:%M:%S")
s_handler = logging.StreamHandler()
s_handler.setFormatter(formatter)
s_handler.setLevel(is_debug)
logger.addHandler(s_handler)
logger.propagate = False

try:
    APP_VERSION = metadata.version(f'mend_{__tool_name__}') if metadata.version(f'mend_{__tool_name__}') else __version__
except:
    APP_VERSION = __version__
APP_TITLE = "Ignore Alerts Parsing"
API_VERSION = "1.4"
args = None
short_lst_prj = []
token_pattern = r"^[0-9a-zA-Z]{64}$"
uuid_pattern = r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"
AGENT_INFO = {"agent": f"ps-{__tool_name__.replace('_', '-')}", "agentVersion": APP_VERSION}
IGNORE_PERIOD = 0


def try_or_error(supplier, msg):
    try:
        return supplier()
    except:
        return msg


def fn():
    fn_stack = inspect.stack()[1]
    return f'{fn_stack.function}:{fn_stack.lineno}'


def ex():
    e_type, e_msg, tb = sys.exc_info()
    return f'{tb.tb_frame.f_code.co_name}:{tb.tb_lineno}'


def check_patterns():
    res = []
    if not (re.match(uuid_pattern, args.ws_user_key) or re.match(token_pattern, args.ws_user_key)):
        res.append("MEND_USERKEY")
    if not (re.match(uuid_pattern, args.ws_token) or re.match(token_pattern, args.ws_token)):
        res.append("MEND_APIKEY")
    if args.producttoken:
        prods = args.producttoken.split(",")
        for prod_ in prods:
            if not (re.match(uuid_pattern, prod_) or re.match(token_pattern, prod_)):
                res.append("MEND_PRODUCTTOKEN")
                break
    if args.projecttoken:
        projs = args.projecttoken.split(",")
        for proj_ in projs:
            if not (re.match(uuid_pattern, proj_) or re.match(token_pattern, proj_)):
                res.append("MEND_PROJECTTOKEN")
                break
    if args.exclude:
        excludes = args.exclude.split(",")
        for excl_ in excludes:
            if not (re.match(uuid_pattern, excl_) or re.match(token_pattern, excl_)):
                res.append("MEND_EXCLUDETOKEN")
                break
    return res


def log_obj_props(obj, obj_title=""):
    masked_props = ["ws_user_key", "user_key"]
    prop_list = [obj_title] if obj_title else []
    try:
        obj_dict = obj if obj is dict else obj.__dict__
        for k in obj_dict:
            v = "******" if k in masked_props else obj_dict[k]
            prop_list.append(f'{k}={v}')
        logger.debug("\n\t".join(prop_list))
    except Exception as err:
        logger.error(f'[{fn()}] Failed: {err}')


def parse_args():
    parser = argparse.ArgumentParser(description=__description__)
    parser.add_argument(*aliases.get_aliases_str("userkey"), help="Mend user key", dest='ws_user_key',
                        default=varenvs.get_env("wsuserkey"), required=not varenvs.get_env("wsuserkey"))
    parser.add_argument(*aliases.get_aliases_str("apikey"), help="Mend API key", dest='ws_token',
                        default=varenvs.get_env("wsapikey"), required=not varenvs.get_env("wsapikey"))
    parser.add_argument(*aliases.get_aliases_str("url"), help="Mend server URL", dest='ws_url',
                        default=varenvs.get_env("wsurl"), required=not varenvs.get_env("wsurl"))
    parser.add_argument(*aliases.get_aliases_str("productkey"), help="Mend product scope", dest='producttoken',
                        default=varenvs.get_env("wsproduct"))
    parser.add_argument(*aliases.get_aliases_str("projectkey"), help="Mend project scope", dest='projecttoken',
                        default=varenvs.get_env("wsproject"))
    parser.add_argument(*aliases.get_aliases_str("exclude"), help="Exclude Mend project/product scope", dest='exclude',
                        default=varenvs.get_env("wsexclude"))
    parser.add_argument(*aliases.get_aliases_str("mode"), help="Creation YAML file or loading", dest='mode',
                        default=varenvs.get_env("wsmode"), required=not varenvs.get_env("wsmode"))
    parser.add_argument(*aliases.get_aliases_str("yaml"), help="Output or input YAML file", dest='yaml',
                        default=varenvs.get_env("yaml"))
    parser.add_argument(*aliases.get_aliases_str("githubpat"), help="GitHub PAT", dest='pat',
                        default=varenvs.get_env("githubpat"))
    parser.add_argument(*aliases.get_aliases_str("githubrepo"), help="GitHub Repo", dest='repo',
                        default=varenvs.get_env("githubrepo"))
    parser.add_argument(*aliases.get_aliases_str("githubowner"), help="GitHub Owner", dest='owner',
                        default=varenvs.get_env("githubowner"))
    arguments = parser.parse_args()

    return arguments


def get_project_list():
    def get_prj_name(token):
        data_prj = json.dumps({
            "requestType": "getProjectVitals",
            "userKey": args.ws_user_key,
            "projectToken": token
        })
        res = json.loads(call_ws_api(data=data_prj))
        return try_or_error(lambda: f'{res["projectVitals"][0]["productName"]}:{res["projectVitals"][0]["name"]}', try_or_error(lambda: res["errorMessage"],
                                                      f"Internal error during getting project data by token {token}"))

    res = []
    if args.projecttoken:
        res.extend([{x: get_prj_name(x)} for x in args.projecttoken.split(",")])
    print(varenvs.get_env("wsproduct"))
    print(f"Project: {args.projecttoken}. Product: {args.producttoken}. {res}")
    if args.producttoken:
        products = args.producttoken.split(",")
        for product_ in products:
            data_prj = json.dumps(
                {"requestType": "getAllProjects",
                 "userKey": args.ws_user_key,
                 "productToken": product_,
                 })
            try:
                prj_data = json.loads(call_ws_api(data=data_prj))["projects"]
                res.extend([{x["projectToken"]: get_prj_name(x["projectToken"])} for x in prj_data])  # x["projectName"]
            except Exception as err:
                pass
    elif not args.projecttoken:
        data_prj = json.dumps(
            {"requestType": "getOrganizationProjectVitals",
             "userKey": args.ws_user_key,
             "orgToken": args.ws_token,
             })
        try:
            prj_data = json.loads(call_ws_api(data=data_prj))["projectVitals"]
            res.extend([{x["token"]: get_prj_name(x["token"])} for x in prj_data])  # x["name"]
        except:
            pass
    print(f"Project: {args.projecttoken}. Product: {args.producttoken}. {res}")

    exclude_tokens = []
    if args.exclude:
        excludes = args.exclude.split(",")
        for exclude_ in excludes:
            data_prj = json.dumps(
                {"requestType": "getAllProjects",
                 "userKey": args.ws_user_key,
                 "productToken": exclude_,
                 })
            try:
                prj_data = json.loads(call_ws_api(data=data_prj))["projects"]
                exclude_tokens.extend([{x["projectToken"]: get_prj_name(x["projectToken"])} for x in prj_data])  #  x["projectName"]
            except:
                exclude_tokens.append(exclude_)
        res = list(set(res) - set(exclude_tokens))
    return res


def extract_url(url: str) -> str:
    url_ = url if url.startswith("https://") else f"https://{url}"
    url_ = url_.replace("http://", "")
    pos = url_.find("/", 8)  # Not using any suffix, just direct url
    return url_[0:pos] if pos > -1 else url_


def call_ws_api(data, header={"Content-Type": "application/json"}, method="POST"):
    global args
    data_json = json.loads(data)
    data_json["agentInfo"] = AGENT_INFO
    try:
        res_ = requests.request(
            method=method,
            url=f"{extract_url(args.ws_url)}/api/v{API_VERSION}",
            data=json.dumps(data_json),
            headers=header, )
        res = res_.text if res_.status_code == 200 else ""

    except Exception as err:
        res = f"Error was raised. {err}"
        logger.error(f'[{ex()}] {err}')
    return res


def create_yaml_ignored_alerts(prj_tokens):
    try:
        data_yml = []
        for token_ in prj_tokens:
            for key, value in token_.items():
                alerts = get_ignored_alerts(key)  # By project token
                vuln = []
                if alerts:
                    for alert_ in alerts:
                        for key_, value_ in alert_.items():
                            for note_, date_ in value_.items():
                                vuln.append(
                                    {
                                        'id_vuln': key_[0],
                                        'note': note_,
                                        'end_date': date_
                                    }
                                )
                if vuln:
                    val_arr = value.split(":")
                    data_yml.append({
                        'productname': val_arr[0],  # Product Name
                        'projectname': val_arr[1],  # Project Name
                        'vulns': vuln
                    })
        with open(f'{args.yaml}', 'w') as file:
            yaml.dump(data_yml, file)
        return f"The file {args.yaml} created successfully"
    except Exception as err:
        return f"The file {args.yaml} was not created. Details: {err}"


def create_waiver():
    global args
    data = json.dumps(
        {"requestType": "getProjectAlerts",
         "userKey": args.ws_user_key,
         "projectToken": args.scope_token,
         })
    data_prj = json.dumps(
        {"requestType": "getProjectVitals",
         "userKey": args.ws_user_key,
         "projectToken": args.scope_token,
         })
    prj_data = json.loads(call_ws_api(data=data_prj))
    prd_name = prj_data["projectVitals"][0]["productName"]
    prj_name = prj_data["projectVitals"][0]["name"]
    res = json.loads(call_ws_api(data=data))["alerts"]
    data_yml = {
        'app_id': 1,
        'name': prj_name,
        'vulns': []
    }
    for vuln_ in res:
        try:
            data_yml['vulns'].append({
                'vuln_id': vuln_["vulnerability"]["name"],
                'note': vuln_["vulnerability"]["description"],
                'effective_date': vuln_["vulnerability"]["lastUpdated"]
            })
        except Exception as err:
            pass
    with open(f'{prj_name}_waiver.yaml', 'w') as file:
        yaml.dump(data_yml, file)


def reactivate_alert(alert_uuid):
    data = json.dumps({
        "requestType": "setAlertsStatus",
        "orgToken": args.ws_token,
        "userKey": args.ws_user_key,
        "alertUuids": [alert_uuid],
        "status": "Active"
    })
    call_ws_api(data=data)


def restore_alerts(project):
    ign_alerts = json.dumps({
        "requestType" : "getProjectIgnoredAlerts",
        "userKey": args.ws_user_key,
        "projectToken" : project
    })
    res = [ x['alertUuid'] for x in json.loads(call_ws_api(data=ign_alerts))["alerts"]]

    data = json.dumps({
        "requestType": "setAlertsStatus",
        "orgToken": args.ws_token,
        "userKey": args.ws_user_key,
        "alertUuids": res,
        "status": "Active"
    })
    call_ws_api(data=data)


def get_ignored_alerts(project):
    ign_alerts = json.dumps({
        "requestType" : "getProjectIgnoredAlerts",
        "userKey": args.ws_user_key,
        "projectToken" : project
    })
    res = []
    try:
        res_ = json.loads(call_ws_api(data=ign_alerts))["alerts"]
        for vuln_ in res_:
            if vuln_["type"] == 'SECURITY_VULNERABILITY':
                res.append({
                    (vuln_["vulnerability"]["name"], vuln_["alertUuid"]): {vuln_["vulnerability"]["description"] : vuln_["vulnerability"]["lastUpdated"]}
                })
    except Exception as err:
        pass
    return res


def is_vuln_in_ignored(vulnerability, ign_list):
    if vulnerability:
        for ign_ in ign_list:
            for key, value in ign_.items():
                if vulnerability.strip() == key[1] or vulnerability.strip() == key[0]:
                    for note_, date_ in value.items():
                        return True, note_, key[1]
    return False, "",""


def read_yaml(yml_file):
    with open(yml_file, 'r') as file:
        data = yaml.safe_load(file)
    return data


def get_token_by_prj_name(prj_name, prd_name):
    for prj_ in short_lst_prj:
        for key, value in prj_.items():
            val_arr = value.split(":")
            if val_arr[1] == prj_name and (val_arr[0] == prd_name or not prd_name):
                if prd_name:
                    return key
                else:
                    logger.info(f"The product is not defined in the input file; "
                                f"the project was found just by project name {prj_name} (Product: {val_arr[0]})")
                    return key
    return ""


def get_alerts_by_type(prj_token, alert_type):
    try:
        data = json.dumps({
            "requestType": "getProjectAlertsByType",
            "userKey": args.ws_user_key,
            "alertType": alert_type,
            "projectToken": prj_token,
        })
        return json.loads(call_ws_api(data=data))["alerts"]
    except:
        return []


def get_all_alerts_by_project(prj_token):
    try:
        data = json.dumps({
            "requestType": "getProjectAlerts",
            "userKey": args.ws_user_key,
            "projectToken": prj_token,
        })
        return json.loads(call_ws_api(data=data))["alerts"]
    except:
        return []


def set_ignore_alert(alert_uuid, comment, vuln):
    try:
        data = json.dumps({
                  "requestType":"ignoreAlerts",
                  "orgToken": args.ws_token,
                  "userKey": args.ws_user_key,
                  "alertUuids": [alert_uuid],
                  "comments": comment
        })
        return f"{json.loads(call_ws_api(data=data))['message']}. Alert UUID {alert_uuid}. (vulnerability {vuln})"
    except:
        return f"Failed Ignore operation for alert UUID {alert_uuid}. (vulnerability {vuln})"


def get_alert_uuid(vulnid, alerts):
    for alert_ in alerts:
        if alert_["vulnerability"]["name"] == vulnid and "SNYK" not in vulnid:
            return alert_["alertUuid"]
    return ""


def exec_input_yaml(input_data):
    input_data_ = [input_data] if type(input_data) is dict else input_data
    for el_ in input_data_:
        prj_token = get_token_by_prj_name(prj_name=try_or_error(lambda: el_["name"], try_or_error(lambda: el_["projectname"], "")), prd_name=try_or_error(lambda : el_["productname"], ""))
        if prj_token:
            #restore_alerts(project=prj_token)
            ignored_al = get_ignored_alerts(project=prj_token)
            alerts = get_alerts_by_type(prj_token=prj_token, alert_type="SECURITY_VULNERABILITY")
            try:
                for data_ in el_["vulns"]:
                    note = data_["note"]
                    end_date_str = try_or_error(lambda: data_["effective_date"],
                                            try_or_error(lambda: data_["end_date"], ""))
                    if end_date_str:
                        end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
                        delta = (datetime.now() - end_date).days
                    else:
                        delta = 0

                    vuln_id = try_or_error(lambda: data_["vuln_id"], try_or_error(lambda: data_["id_vuln"], ""))

                    for ign_ in ignored_al:
                        for key, value in ign_.items():
                            if key[0] == vuln_id:
                                    if delta > IGNORE_PERIOD:
                                        reactivate_alert(alert_uuid=key[1])
                                        logger.info(f"The alert {key[1]} (vulnerability {vuln_id}) in the project {try_or_error(lambda: el_['name'], try_or_error(lambda: el_['projectname'], ''))}"
                                                    f" was reactivated. The end date has passed")
                                    else:
                                        for key_, value_ in value.items():
                                            logger.warning(
                                                f"The alert {key[1]} (vulnerability {vuln_id}) in the project {try_or_error(lambda: el_['name'], try_or_error(lambda: el_['projectname'], ''))} "
                                                f"has been ignored already with comment: {key_}")

                    for alert_ in alerts:
                        if alert_["vulnerability"]["name"] == vuln_id and "SNYK" not in vuln_id:
                            if delta < IGNORE_PERIOD:
                                logger.info(set_ignore_alert(alert_uuid=alert_["alertUuid"],comment=note, vuln=vuln_id))
                            else:
                                logger.warning(f"The alert {alert_['alertUuid']} (vulnerability {vuln_id}) in the project "
                                               f"{try_or_error(lambda: el_['name'], try_or_error(lambda: el_['projectname'], ''))} "
                                               f"was not ignored")
            except Exception as err:
                logger.error(f"Error: {err}")
        else:
            logger.warning(f"The project {try_or_error(lambda: el_['name'], try_or_error(lambda: el_['projectname'], ''))} was not identified")


def main():
    global args
    global short_lst_prj

    hdr_title = f'{APP_TITLE} {__version__}'
    hdr = f'\n{len(hdr_title)*"="}\n{hdr_title}\n{len(hdr_title)*"="}'
    logger.info(hdr)
    input_data = None

    try:
        args = parse_args()
        chp_ = check_patterns()
        if chp_:
            logger.error("Missing or malformed configuration parameters:")
            [logger.error(el_) for el_ in chp_]
            exit(-1)

        if args.pat and args.repo and (args.owner or "/" in args.repo):
            try:
                g = Github(args.pat)
                repo = g.get_repo(f'{args.repo}') if "/" in args.repo else g.get_repo(f'{args.owner}/{args.repo}')
                input_data = repo.get_contents(args.yaml).decoded_content.decode("utf-8")
            except Exception as err:
                logger.error(f"Access to {args.owner}/{args.repo} forbidden")
        logger.info(f'[{fn()}] Getting project list')
        short_lst_prj = get_project_list()
        print(short_lst_prj)
        if args.mode.lower() == "create":
            logger.info(create_yaml_ignored_alerts(short_lst_prj))
        elif args.yaml:
            try:
                input_data = yaml.safe_load(input_data) if input_data else read_yaml(args.yaml)
                exec_input_yaml(input_data=input_data)
            except Exception as err:
                logger.error(f"[{fn()}] Impossible to parse file {args.yaml}. Details: {err}")
        logger.info(f'[{fn()}] Operation was finished successfully')
    except Exception as err:
        logger.error(f'[{fn()}] Failed to getting project list. Details: {err}')
        exit(-1)


if __name__ == '__main__':
    sys.exit(main())
