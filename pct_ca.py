from datetime import datetime

import texts, coach_matic_base

####################################################################
# sum of effort per state
def effort_who(all_issues):
    all_display_names = set()
    for issue in all_issues:
        if "worklog" not in vars(issue.fields):
            continue
        for worklog in issue.fields.worklog.worklogs:
            all_display_names.add()

    names_ordered = list(all_display_names)
    return "<br/>" + texts.effort_who + ", ".join(names_ordered) + "<br/>"
    
####################################################################
# sum of effort per state
def get_status_in_date(config, issue, created, df):
    row = df[df["Key"] == issue.key].iloc[0]
    
    state_for_effort = "?"
    for status in config.all_statuses:
        if created > row[status]:
            state_for_effort = status
    return state_for_effort
        
def effort_per_status(final_result, config, all_issues, df):
    sum_per_issue = {}
    sum_per_status = {}
    
    for issue in all_issues:
        sum_per_issue[issue.key] = {}
        
        # all_history = coach_matic_base.ensure_history_order_reverse(issue)
        
        # all_worklogs_this_issue = config.jira_conn.worklogs(issue)
        # for worklog in all_worklogs_this_issue:
        
        if "worklog" not in vars(issue.fields):
            continue
        for worklog in issue.fields.worklog.worklogs:
            created_str = worklog.created[0:10]
            created = datetime.strptime(created_str, "%Y-%m-%d")
            
            status = get_status_in_date(config, issue, created, df)
            if status in sum_per_status:
                sum_per_status[status] = sum_per_status[status] + worklog.timeSpentSeconds
            else:
                sum_per_status[status] = worklog.timeSpentSeconds
                
            if status not in sum_per_issue[issue.key]:
                sum_per_issue[issue.key][status] = 0
            sum_per_issue[issue.key][status] = sum_per_issue[issue.key][status] + worklog.timeSpentSeconds

    
    file_name_temp = config.project_name.replace("/", "-").replace("\\", "-")
    csv_file_name = final_result.temp_dir + "effort_status" + file_name_temp + ".csv"
    with open(csv_file_name, "w") as f:
        f.write("issue\t" + "\t".join(config.all_statuses) + "\n")
        for issue in sum_per_issue:
            f.write(f"{issue}\t")
            for status in config.all_statuses + ["?"]:
                effort_h = sum_per_issue[issue][status] / (60*60) if status in sum_per_issue[issue] else 0
                f.write("{:.2f}\t".format(effort_h).replace(".", ","))
            f.write("\n")
    final_result.all_files.add(csv_file_name)


    all_statuses_effort = []
    for status in config.all_statuses + ["?"]:
        effort_h = sum_per_status[status] / (60*60) if status in sum_per_status else 0
        all_statuses_effort.append("{}: {:.2f}h".format(status, effort_h))
    return "<br/>" + ", ".join(all_statuses_effort) + "<br/>" + texts.effort_status_disclaimer

def count_bugs(config, key):
    # count bugs for parent key
    if config.count_bugs_jql != "" and config.jira_conn != None:
        bugs_jql = config.count_bugs_jql.replace("?", key)
        issue_bugs = config.jira_conn.search_issues(bugs_jql, fields="key")
        num_of_bugs = len(issue_bugs)
        return num_of_bugs
    else:
        return 0

####################################################################
# check tendency on effort
def pct_ca(final_result, config, all_issues, df):
    worklog_by_parent = {}
    dev_user_keys = set()
    
    for issue in all_issues:
        if "parent" in vars(issue.fields):
            key_parent = issue.fields.parent.key
        else:
            key_parent = issue.key
            
        worklog_day_user = worklog_by_parent[key_parent] if key_parent in worklog_by_parent else {}
            
        if "worklog" not in vars(issue.fields):
            continue
        for worklog in issue.fields.worklog.worklogs:
            created_str = worklog.created[0:10]
            created = datetime.strptime(created_str, "%Y-%m-%d")
            author = worklog.author.key
            if author in config.user_pct_ca:
                if "pos" not in worklog_day_user:
                    worklog_day_user["pos"] = {}
                if created in worklog_day_user["pos"]:
                    worklog_day_user["pos"][created] = worklog_day_user["pos"][created] + worklog.timeSpentSeconds
                else:
                    worklog_day_user["pos"][created] = worklog.timeSpentSeconds
            else:
                dev_user_keys.add(author)
                if "pre" not in worklog_day_user:
                    worklog_day_user["pre"] = {}
                if created in worklog_day_user["pre"]:
                    worklog_day_user["pre"][created] = worklog_day_user["pre"][created] + worklog.timeSpentSeconds
                else:
                    worklog_day_user["pre"][created] = worklog.timeSpentSeconds
                
        worklog_by_parent[key_parent] = worklog_day_user
        
    total_complete_hours = 0
    total_dubious_hours = 0 # dev and QA worked in same day. We are not sure who worked before
    total_rework_hours = 0
    total_validation_hours = 0
    issues_pct_ca_csv = []
    issues_low_pctca = []
    issues_no_pre_pos_effort = 0
    total_bugs = 0
    for key_parent in worklog_by_parent:
        complete_hours = 0
        dubious_hours = 0 # dev and QA worked in same day. We are not sure who worked before
        rework_hours = 0
        validation_hours = 0
        worklog_day_user = worklog_by_parent[key_parent]
        if "pre" in worklog_day_user and "pos" in worklog_day_user:
            min_pos_date = min(list(worklog_day_user["pos"].keys()))
            for dt in worklog_day_user["pre"]:
                if dt < min_pos_date:
                    complete_hours += worklog_day_user["pre"][dt]
                elif dt == min_pos_date:
                    dubious_hours += worklog_day_user["pre"][dt]
                else:
                    rework_hours += worklog_day_user["pre"][dt]
                
            for dt in worklog_day_user["pos"]:
                validation_hours += worklog_day_user["pos"][dt]
                total_validation_hours += worklog_day_user["pos"][dt]
                
            num_of_bugs = count_bugs(config, key_parent)
            total_bugs += num_of_bugs
            
            pct_ca = 1 - (rework_hours / complete_hours) \
                      if complete_hours > 0 \
                      else 0
            s = "{}\t{:.2f}\t{:.2f}\t{:.2f}\t{:.2f}\t{:.2f}\t{}\n".format(key_parent, 
                                                            complete_hours / (60*60),
                                                            dubious_hours / (60*60),
                                                            rework_hours / (60*60),
                                                            validation_hours / (60*60),
                                                            pct_ca * 100,
                                                            num_of_bugs).replace(".", ",")
            issues_pct_ca_csv.append(s)

            if pct_ca < 0.7:
                issues_low_pctca.append("<a href=\"{}/browse/{}\">{}</a>".format(config.jira_url, key_parent, key_parent))
                
            total_complete_hours += complete_hours
            total_dubious_hours += dubious_hours
            total_rework_hours += rework_hours
        else:
            issues_no_pre_pos_effort += 1
            # just count bugs, without considering % C/A, as we didn't identify
            # time spent with QA
            num_of_bugs = count_bugs(config, key_parent)
            total_bugs += num_of_bugs
            
            s = "{}\t\t\t\t\t\t{}\n".format(key_parent, num_of_bugs)
            issues_pct_ca_csv.append(s)
            
    pct_ca1 = 1 - (total_rework_hours / total_complete_hours) \
              if total_complete_hours > 0 \
              else 0
    pct_ca2 = 1 - ((total_rework_hours + total_dubious_hours) / total_complete_hours) \
              if total_complete_hours > 0 \
              else 0

    result = texts.pctca_title
    result += texts.pctca_description1.format(total_complete_hours / (60*60),
                                              total_rework_hours / (60*60),
                                              total_dubious_hours / (60*60),
                                              total_validation_hours / (60*60))
    result += texts.pctca_description2.format(pct_ca1 * 100)
    result += texts.pctca_description3.format(pct_ca2 * 100)
    result += texts.pctca_description4.format(", ".join(issues_low_pctca))
    result += texts.pctca_description5.format(total_bugs, len(issues_pct_ca_csv), \
                total_bugs / len(issues_pct_ca_csv) if len(issues_pct_ca_csv) > 0 else 0)
    result += texts.pctca_description6.format(issues_no_pre_pos_effort,
                    (issues_no_pre_pos_effort / len(issues_pct_ca_csv) * 100 \
                     if len(issues_pct_ca_csv) > 0 \
                     else 0))
    result += texts.pctca_disclaimer
    result += texts.pctca_disclaimer2
    result += texts.pctca_disclaimer3
    result += texts.pctca_disclaimer4
    result += texts.pctca_disclaimer5
    result += texts.pctca_dev_users.format(", ".join(dev_user_keys))
    result += texts.pctca_qa_users.format(config.user_pct_ca)
    final_result.text_result["pct_ca"] = result
            
    file_name_temp = config.project_name.replace("/", "-").replace("\\", "-")
    csv_file_name = final_result.temp_dir + "pct_ca" + file_name_temp + ".csv"
    with open(csv_file_name, "w") as f:
        f.write("issue_parent\tcomplete_hours\tdubious_hours\trework_hours\tvalidation_hours\t% c/a\tNum bugs\n")
        for line in issues_pct_ca_csv:
            f.write(line)
    final_result.all_files.add(csv_file_name)

