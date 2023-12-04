from enum import Enum
import os


class aliases(Enum): # List of aliases for params
    apikey = ("--apiKey","--api-key", "--orgToken", "-o")
    userkey = ("--user-key", "--userKey","-k")
    url = ("--url", "--mendUrl", "-u")
    projectkey = ("--scope", "--projectToken", "-t")
    productkey = ("--productToken", "--product", "-d")
    exclude = ("--exclude", "-exclude")
    yaml = ("--yaml", "-yaml")
    githubpat = ("--ghpat", "-ghpat")
    githubowner = ("--ghowner", "-ghowner")
    githubrepo = ("--ghrepo", "-ghrepo")
    output = ("--out", "-out")
    mode = ("--mode", "-mode")
    prjname = ("--prjname", "--projectname")
    baseline = ("-b", "--baselineProjectToken")
    destprjname = ("-n", "--destProjectName")
    destprjver = ("-v", "--destProjectVersion")
    whitelist = ("-w", "--whitelist")


    @classmethod
    def get_aliases_str(cls, key):
        res = list()
        for elem_ in cls.__dict__[key].value:
            res.append(elem_)
            if elem_ != elem_.lower():
                res.append(elem_.lower())
        return res


class varenvs(Enum): # Lit of Env.variables
    wsuserkey = ("WS_USERKEY", "MEND_USERKEY")
    wsapikey = ("MEND_APIKEY","WS_APIKEY","WS_TOKEN")
    wsurl = ("WS_WSS_URL","MEND_WSS_URL","WS_URL","MEND_URL")
    wsscope = ("WS_SCOPE","MEND_SCOPE")
    wsproduct = ("WS_PRODUCTTOKEN", "MEND_PRODUCTTOKEN")
    wsproject = ("WS_PROJECTTOKEN", "MEND_PROJECTTOKEN")
    wsexclude = ("WS_EXCLUDETOKEN", "MEND_EXCLUDETOKEN")
    yaml = ("MEND_YAML", "WS_YAML")
    githubpat = ("WS_GHPAT", "MEND_GHPAT", "GHPAT")
    githubowner = ("WS_GHOWNER", "MEND_GHOWNER", "GHOWNER")
    githubrepo = ("WS_GHREPO", "MEND_GHREPO", "GHREPO")
    wsmode = ("WS_MODE","MEND_MODE")

    @classmethod
    def get_env(cls, key):
        res = ""
        for el_ in cls.__dict__[key].value:
            res = os.environ.get(el_)
            if res:
                break
        return res
