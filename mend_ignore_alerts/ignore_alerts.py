import argparse
import inspect
import json
import logging
import os
import sys

import requests
import yaml
from github import Github

from mend_ignore_alerts._version import __version__, __tool_name__, __description__
from mend_ignore_alerts.const import aliases, varenvs

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

APP_TITLE = "Ignore Alerts Parsing"
API_VERSION = "1.4"
args = None
short_lst_prj = []


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
             "orgToken": args.apikey,
             })
        try:
            prj_data = json.loads(call_ws_api(data=data_prj))["projectVitals"]
            res.extend([{x["token"]: get_prj_name(x["token"])} for x in prj_data])  # x["name"]
        except:
            pass

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
                alerts = get_ingnored_alerts(key)  # By project token
                vuln = []
                if alerts:
                    for alert_ in alerts:
                        for key_, value_ in alert_.items():
                            vuln.append(
                                {
                                    'id_vuln': key_,
                                    'note': value_,
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


def get_ingnored_alerts(project):
    ign_alerts = json.dumps({
        "requestType" : "getProjectIgnoredAlerts",
        "userKey": args.ws_user_key,
        "projectToken" : project
    })
    res = []
    try:
        res_ = json.loads(call_ws_api(data=ign_alerts))["alerts"]
        for vuln_ in res_:
            res.append({
                vuln_["vulnerability"]["name"]: vuln_["vulnerability"]["description"]
            })
    except Exception as err:
        pass
    return res


def is_vuln_in_ignored(vulnerability, ign_list):
    for ign_ in ign_list:
        for key, value in ign_.items():
            if vulnerability.strip() == key:
                return True, value
    return False, ""


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
                                f"the project was found just by project name {prj_name}")
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


def set_ignore_alert(alert_uuid, comment):
    try:
        data = json.dumps({
                  "requestType":"ignoreAlerts",
                  "orgToken": args.ws_token,
                  "userKey": args.ws_user_key,
                  "alertUuids": [alert_uuid],
                  "comments": comment
        })
        return f"{json.loads(call_ws_api(data=data))['message']}. Alert UUID {alert_uuid}"
    except:
        return f"Failed Ignore operation for alert UUID {alert_uuid}"


def exec_input_yaml(input_data):
    input_data_ = [input_data] if type(input_data) is dict else input_data
    for el_ in input_data_:
        prj_token = get_token_by_prj_name(prj_name=try_or_error(lambda: el_["name"], try_or_error(lambda: el_["projectname"], "")), prd_name=try_or_error(lambda : el_["productname"], ""))
        if prj_token:
            #restore_alerts(project=prj_token)
            ignored_al = get_ingnored_alerts(project=prj_token)
            alerts = get_alerts_by_type(prj_token=prj_token, alert_type="SECURITY_VULNERABILITY")
            try:
                for data_ in el_["vulns"]:
                    note = data_["note"]
                    vuln_id = try_or_error(lambda: data_["vuln_id"], try_or_error(lambda: data_["id_vuln"], ""))
                    status, note_ign = is_vuln_in_ignored(vulnerability=vuln_id,ign_list=ignored_al)
                    if not status:
                        alert_uuid = ""
                        for alert_ in alerts:
                            if alert_["vulnerability"]["name"] == vuln_id and "SNYK" not in vuln_id:
                                alert_uuid = alert_["alertUuid"]
                                break
                        if alert_uuid :
                            logger.info(set_ignore_alert(alert_uuid=alert_uuid,comment=note))
                        else:
                            logger.info(f"The {vuln_id} was not found in the project {try_or_error(lambda: el_['name'], try_or_error(lambda: el_['projectname'], ''))}")
                    else:
                        logger.warning(f"The vulnerability {vuln_id} in the project {try_or_error(lambda: el_['name'], try_or_error(lambda: el_['projectname'], ''))} "
                                    f"has been ignored already with comment: {note_ign}")
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
        if args.pat and args.repo and (args.owner or "/" in args.repo):
            try:
                g = Github(args.pat)
                repo = g.get_repo(f'{args.repo}') if "/" in args.repo else g.get_repo(f'{args.owner}/{args.repo}')
                input_data = repo.get_contents(args.yaml).decoded_content.decode("utf-8")
            except Exception as err:
                logger.error(f"Access to {args.owner}/{args.repo} forbidden")
        #create_waiver()
        logger.info(f'[{fn()}] Getting project list')
        '''
        load_prj = json.dumps({
            "requestType" : "getOrganizationProjectVitals",
             "userKey": args.ws_user_key,
             "orgToken" : args.ws_token
        })
        short_lst_prj = [{x["token"]: {"product": x["productName"], "name": x["name"]}} for x in json.loads(call_ws_api(data=load_prj))["projectVitals"]]
        logger.info(f'[{fn()}] Analyzing YAML file')
        '''
        short_lst_prj = get_project_list()
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
