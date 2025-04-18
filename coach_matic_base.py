from traceback import extract_tb
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import subprocess, json, os, re
from os import listdir

class OneIssue:
    key = ""
    value = ""
    
    def toString(self):
        return self.value
    
def print_and_log(str):
    print(str)
    with open("log.txt", "a", encoding="UTF-8") as f:
        f.write("{}: {}".format(datetime.now(), str))
        f.write("\n")


#######################################################################
# concat a dataframe and dict
def concat(df, d):
    for k in d:
        d[k] = [d[k]]
    
    df_concat = pd.DataFrame(data=d)
    return pd.concat([df, df_concat], ignore_index=False)

def get_link_jira_key(url, key):
    return f'<a href="{url}/browse/{key}">{key}</a>'

#######################################################################
# get from extract_jira
def transform_json_into_issue(one_issue, j):
    for key in j:
        value = j[key]
        if type(value) == str or type(value) == int:
            setattr(one_issue, key, value)
        elif type(value) == dict:
            one_issue_part = OneIssue()
            setattr(one_issue, key, one_issue_part)
            transform_json_into_issue(one_issue_part, value)
        elif type(value) == list:
            new_list = list()
            setattr(one_issue, key, new_list)
            for each_value in value:
                if type(each_value) == dict:
                    new_list.append(transform_json_into_issue(OneIssue(), each_value))
                else:
                    new_list.append(each_value)
            
    return one_issue

        
def load_each_file(final_result, config):
    all_issues = []
    for file_name in listdir(final_result.temp_dir):
        if file_name[-5:] != ".json":
            continue
        
        print(f"{file_name}")
        with open(final_result.temp_dir + file_name, "r", encoding="utf-8") as f:
            json_line = f.readlines()[-1]
            j = json.loads(json_line)

            one_issue = OneIssue()
            transform_json_into_issue(one_issue, j)
            all_issues.append(one_issue)
    return all_issues

def get_all_issues_from_file(final_result, config):
    zip_file_name = final_result.temp_dir + "extract_jira.zip"
    with open(zip_file_name, "wb") as f:
        f.write(config.extract_jira_zip)
        
    cmd = "unzip " + zip_file_name + " -d " + final_result.temp_dir
    if os.name == "nt":
        subprocess.run(cmd)
    else:
        subprocess.run(cmd, shell=True, check=True, capture_output=True)
    
    return load_each_file(final_result, config)

#######################################################################
# jira connection and data manipulation
def get_all_issues(jira_conn, config, other_fields=None, expand=['changelog']):
    fields = "parent,issuetype,created,summary,description,status"
    if other_fields is not None:
        fields += "," + other_fields()
        
    expand=['changelog']
    if config.expand_worklog:
        expand.append("worklog")
        fields += ",worklog"
        
    # in a try block, maybe the value doesn't exist in config file
    # if "additional_fields_on_jql" in vars(config):
    #     fields += config.additional_fields_on_jql
    
    if len(config.export_csv_add_fields_custom) > 0:
        fields += "," + ",".join(config.export_csv_add_fields_custom)
    
    start_at = 0
    returned = 1
    all_issues = []

    while returned > 0:
        jql = config.jql#.replace(chr(92), chr(92)+chr(92))
        chunck = jira_conn.search_issues(jql, expand=expand, startAt=start_at, fields=fields)
        all_issues += chunck.iterable

        returned = len(chunck)
        start_at += len(chunck)

    return all_issues

#################################################################
# ensure order in history
def ensure_history_order_reverse(issue, reverse=True, num_days=1095):
    today = datetime.now()
    start_day = today - timedelta(days=num_days, hours=today.hour, \
                           minutes=today.minute, \
                           seconds=today.second)
    
    all_histories_dict = {}
    
    for history in issue.changelog.histories:
        created_dt = datetime.strptime(history.created[0:10], "%Y-%m-%d")
        if created_dt > start_day:
            created_str = history.created
            while created_str in all_histories_dict:
                created_str += "0" # avoid omiting when has exaclty same created date
            all_histories_dict[created_str] = history
        
    all_histories = []
    for k in sorted(all_histories_dict.keys(), reverse=reverse):
        all_histories.append(all_histories_dict[k])
        
    return all_histories

#######################################################################
# history date handling
def fill_missing_dates(config, issue_dates):
    last_date = None
    for state in config.all_statuses[::-1]:
        if state not in issue_dates:
            issue_dates[state] = last_date
        else:
            last_date = issue_dates[state]

def fix_issues_got_status_back(df, config):
    for i in range(len(config.all_statuses) - 1):
        this_status = config.all_statuses[i]
        next_status = config.all_statuses[i + 1]
        this_status_idx = list(df.columns).index(this_status)
        this_status_general_idx = config.all_statuses.index(this_status)
        next_status_idx = list(df.columns).index(next_status)

        for row in range(len(df)):
            current_status = df["status"].iloc[row].lower()
            if current_status in config.all_statuses:
                current_status_idx = config.all_statuses.index(current_status)
            else:
                current_status_idx = 0
            
            if current_status_idx < this_status_general_idx:
                df.iat[row, next_status_idx] = pd.NaT# np.nan
            elif type(df.iat[row, this_status_idx]) != pd._libs.tslibs.timestamps.Timestamp or \
                  type(df.iat[row, next_status_idx]) != pd._libs.tslibs.timestamps.Timestamp or \
                  df.iat[row, this_status_idx] == np.nan:
                df.iat[row, next_status_idx] = pd.NaT# pd._libs.tslibs.nattype.NaTType
            elif df.iat[row, this_status_idx] > df.iat[row, next_status_idx]:
                df.iat[row, next_status_idx] = df.iat[row, this_status_idx]#pd.NaT# np.nan

def field_value_to_str(field_value):
    try:
        if "key" in vars(field_value):
            field_value = field_value.key
        if "name" in vars(field_value):
            field_value = field_value.name
        elif "value" in vars(field_value):
            field_value = field_value.value
    finally:
        return field_value
    
#######################################################################
# get list of fields to return 
def get_optional_field_list(jira_conn, config):
    export_csv_add_fields = []
    export_csv_add_fields_custom = []
    fields_not_found = []
    allfields=jira_conn.fields()
    nameMap = {field['name']:field['id'] for field in allfields}
    
    if len(config.repeat_for_each_field_value) != 0 and \
            config.repeat_for_each_field_value not in config.export_csv_add_fields:
        config.export_csv_add_fields.append(config.repeat_for_each_field_value)
    
    if len(config.discriminated_throughput_field) != 0 and \
            config.discriminated_throughput_field not in config.export_csv_add_fields:
        config.export_csv_add_fields.append(config.discriminated_throughput_field)

    if len(config.blocker_field) != 0 and \
            config.blocker_field not in config.export_csv_add_fields:
        config.export_csv_add_fields.append(config.blocker_field)

    if len(config.bag_of_words_axis) != 0:
        for field in allfields:
            if field["id"] == config.bag_of_words_axis:
                config.bag_of_words_axis_friendly = field["name"]
                if config.bag_of_words_axis_friendly not in config.export_csv_add_fields:
                    config.export_csv_add_fields.append(config.bag_of_words_axis_friendly)
    
    if len(config.effort_axis) != 0:
        for field in allfields:
            if field["id"] == config.effort_axis:
                config.effort_axis_friendly = field["name"]
                if config.effort_axis_friendly not in config.export_csv_add_fields:
                    config.export_csv_add_fields.append(config.effort_axis_friendly)
                
    print(f"config.export_csv_add_fields: {config.export_csv_add_fields}")
    config.expot_csv_jql_fields = list(filter(lambda s: s[0:4] == "jql:", config.export_csv_add_fields))
    config.export_csv_add_fields = list(filter(lambda s: s[0:4] != "jql:", config.export_csv_add_fields))
    print(f"config.expot_csv_jql_fields: {config.expot_csv_jql_fields}")
    
    for field_name in config.export_csv_add_fields:
        field_name_noparent = field_name.replace("pai.", "").strip()
        if field_name_noparent == "":
            continue
        
        if field_name == "parent":
            export_csv_add_fields.append("parent")
            export_csv_add_fields_custom.append("parent")
        elif field_name_noparent not in nameMap:
            fields_not_found.append(field_name)
        else:
            export_csv_add_fields.append(field_name)
            export_csv_add_fields_custom.append(nameMap[field_name_noparent])
        
    if len(fields_not_found) > 0:
        print_and_log("Lista de campos encontrados: {}".format(",".join(list(nameMap.keys()))))
        raise Exception("Não encontrei os campos {}.".format(",".join(fields_not_found)))
        
    config.export_csv_add_fields = export_csv_add_fields
    config.export_csv_add_fields_custom = export_csv_add_fields_custom
            
def run_jql_cache(config, jql, fields):
    if "jql_cache" not in vars(config):
        config.jql_cache = {}
        
    if jql in config.jql_cache:
        return config.jql_cache[jql]
    result = config.jira_conn.search_issues(jql, fields=config.export_csv_add_fields_custom)
    if len(result) > 0:
        config.jql_cache[jql] = result[0]
    else:
        config.jql_cache[jql] = None
    return config.jql_cache[jql]
    
    
def get_custom_field_value(config, issue, field_name, custom_field_name):
    if issue == None:
        return ""
    
    if "pai." in field_name:
        parent_key = issue.fields.parent
        fields = f"{custom_field_name},summary"
        parent_issue = run_jql_cache(config, f"issue = {parent_key}", fields)
        v = get_custom_field_value(config, parent_issue, field_name.replace("pai.", ""), custom_field_name)
        return v
        
    field_value = None
    if custom_field_name in vars(issue.fields):
        field_value = getattr(issue.fields, custom_field_name)
        
        if field_value != None:
            field_value = field_value_to_str(field_value)
            if type(field_value) == list:
                all_field_values = []
                for fv in field_value:
                    all_field_values.append(field_value_to_str(fv))
                field_value = ",".join(all_field_values)
    elif custom_field_name == "issuekey":
        field_value = issue.key
        
    if field_value is None:
        field_value = ""
        
    if "Tempo Gasto" in field_name:
        try:
            field_value = int(field_value) / (60 * 60)
        except:
            nothing = True
            
    return field_value

def get_custom_field_name(config, field_name):
    idx = config.export_csv_add_fields.index(field_name)
    return config.export_csv_add_fields_custom[idx]

def get_user_field_name(config, field_name):
    for user_name, custom_name in zip(config.export_csv_add_fields, config.export_csv_add_fields_custom):
        if custom_name == field_name and user_name[0:4] != "pai.":
            return user_name
    
def get_custom_field_value_by_field_name(config, issue, field_name):
    custom_field_name = get_custom_field_name(config, field_name)
    return get_custom_field_value(config, issue, field_name, custom_field_name)
    
def get_jql_field_value(config, issue, jql_field):
    try:
        splited = re.split("[:\[]", jql_field)
        field_name = splited[1]
        jql = splited[2].replace("?", issue.key)[0:-1]
        issue_related = run_jql_cache(config, jql, field_name)
        if issue_related == None:
            return "jql:" + field_name, ""
            
        if field_name == "Chave":
            return "jql:" + field_name, issue_related.key
        custom_field_name = get_custom_field_name(config, field_name)
        return "jql:" + field_name, getattr(issue_related.fields, custom_field_name)
    except Exception as e:
        msg = str(e)
        print_and_log("Erro na execução: {}".format(msg))
        print_and_log(str(extract_tb(e.__traceback__)))

        return "jql:" + field_name, "(erro no jql)"
    
def get_dates_from_jira_history(all_issues, config):
    df = pd.DataFrame(columns=["Key","expedite","check scope","issuetype","status","title"]+config.all_statuses)

    for issue in all_issues:
        issue_dates = {"Key": issue.key, 
                       "status": get_status(config, issue),
                       "issuetype": issue.fields.issuetype.name,
                       "title": issue.fields.summary,
                       "expedite": "-",
                       "check scope": "no"}

        for idx in range(len(config.export_csv_add_fields)):
            field_name = config.export_csv_add_fields[idx]
            custom_field_name = config.export_csv_add_fields_custom[idx]
            
            field_value = get_custom_field_value(config, issue, field_name, custom_field_name)
            
            issue_dates[field_name] = field_value
            
        for jql_field in config.expot_csv_jql_fields:
            field_name, field_value = get_jql_field_value(config, issue, jql_field)
            issue_dates[field_name] = field_value
            
                    
        for history in ensure_history_order_reverse(issue):
            for item in history.items:
                if item.field == "status" and get_status(config, status=item.toString) in config.all_statuses:
                    new_state = get_status(config, None, item.toString)
                    
                    dt = datetime.strptime(history.created[0:10], "%Y-%m-%d")

                    if new_state in issue_dates: # gets higher dates for each column
                        dt2 = issue_dates[new_state]
                        if dt2 > dt and new_state != config.all_statuses[0]:
                            dt = dt2
                    issue_dates[new_state] = dt

        issue_dates[config.all_statuses[0]] = datetime.strptime(issue.fields.created[0:10], "%Y-%m-%d")
        
        fill_missing_dates(config, issue_dates)

        # df = df.append(issue_dates, ignore_index=True)
        df = concat(df, issue_dates)

    fix_issues_got_status_back(df, config)
    
    return df

#########################################################################
# calculate cycle time and wait time
def calculate_cycle_time(config, df):
    df["CycleTime"] = (pd.to_datetime(df[config.downstream_stop]) -
                       pd.to_datetime(df[config.downstream_start])).dt.days
    df["CycleTime"] = np.where(df["CycleTime"] < 0, 0, df["CycleTime"])

    # TODO: talvez rever e deixar calculados para todos...
    for one_waiting_status in config.waiting_statuses:
        idx = config.all_statuses.index(one_waiting_status)
        next_status = config.all_statuses[idx + 1]
    
        column_name = one_waiting_status + " wait"
        df[column_name] = (pd.to_datetime(df[next_status]) - pd.to_datetime(df[one_waiting_status])).dt.days

    return df

######################################################################
# search subtasks based on subjql 
def search_subtasks(jira_conn, subjql, df):
    if subjql.strip() == "":
        return []
    
    parents = "\"" + "\",\"".join(df["Key"]) + "\""
    jql = subjql.format(parents)

    start_at = 0
    returned = 1
    all_subtasks = []

    while returned > 0:
        chunck = jira_conn.search_issues(
            jql, startAt=start_at, fields="summary,description,parent")
        all_subtasks += chunck.iterable

        returned = len(chunck)
        start_at += len(chunck)

    return all_subtasks

#######################################################################
# defs to handle all statuses
def prepare_all_statuses(config, all_statuses):
    for status in all_statuses.split(","):
        status = status.strip().lower()
        all_sub_statuses = status.split("/")
        config.all_statuses.append(all_sub_statuses[0])
        config.all_sub_statuses.append(all_sub_statuses)
    
def get_status(config, issue=None, status=None):
    if status is None:
        issue_status = issue.fields.status.name.lower()
    else:
        issue_status = status.lower()
        
    for sub_statuses in config.all_sub_statuses:
        if issue_status in sub_statuses:
            return sub_statuses[0]
    return issue_status
    
##################################################################
# calc outliers
def convert_to_float(val):
    try:
        return float(val)
    except:
        return np.nan

def calculate_outliers(list_itens):
    # ensures only float
    list_itens = list(filter(lambda f: f>=0.0, [convert_to_float(f) for f in list_itens]))
    
    np_list_itens = np.array(list_itens)
    mean = np_list_itens.mean()
    std_dev = np_list_itens.std()
    
    if std_dev == 0:
        return []
    
    np_zscore = (np_list_itens - mean) / std_dev
    
    outliers_position = []
    for idx in range(len(np_zscore)):
        if np_zscore[idx] >= 3 or np_zscore[idx] <= -3:
            outliers_position.append(idx)
            
    return outliers_position

def first_outlier_value(list_itens):
    pos_itens = calculate_outliers(list_itens)
    if len(pos_itens) == 0:
        return 0
    
    if type(list_itens) == pd.core.series.Series:
        outlier_values = [list_itens.iloc[p] for p in pos_itens]
    else:
        outlier_values = [list_itens[p] for p in pos_itens]
    
    return min(outlier_values)
    