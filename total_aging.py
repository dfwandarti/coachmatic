import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

import coach_matic_base, texts, outliers

def analyse_total_aging(final_result, df_aging, config):
    result = ""

    df2 = df_aging.copy()
    df2["total age"] = 0.0
    df2["total moves"] = 0
    for count_type in [" age", " moves"]:
        for status in config.downstream_statuses:
            df2["total" + count_type] = df2["total" + count_type] + \
                                            df2[status + count_type]
    
    # look for outliers for each column, for age as well transitions
    for count_type, desc_type in [[" age", texts.total_aging_day], \
                                  [" moves", texts.total_aging_transition]]:
        for status in ["total"] + config.downstream_statuses:
            column = status + count_type
            df_outliers = outliers.get_outliers(df2, column)
            
            interm_result = []
            for key, col_value in df_outliers[["Key", column]].itertuples(index=False):
                if type(col_value) == float:
                    formated_col_value = "{:.2f}".format(col_value)
                else:
                    formated_col_value = "{}".format(col_value)
                interm_result.append("{} - {} {}".format(key, formated_col_value, desc_type))

            if len(interm_result) > 0:                
                result += texts.total_aging_outlier_age.format(desc_type, status, ", ".join(interm_result))
    
    if len(result) > 0:
        result = texts.total_aging_title + result
    else:
        result = texts.total_aging_title + texts.total_aging_no_outlier
    
    final_result.text_result["total_age"] = result
    
def calc_percentil(final_result, config, df_aging):
    
    result = "<br/><table><tr><td></td>"
    for status in config.all_statuses[0:-1]:
        result += "<td>{}</td>".format(status)
    result += "</tr>"
    
    result += "<tr><td>85%</td>"    
    for status in config.all_statuses[0:-1]:
        cycle_times = df_aging[status + " age"].values
        if len(cycle_times) == 0:
            result += "<td>-</td>"
        else:
            cycle_time_pct85 = np.percentile(cycle_times, 85, interpolation="lower")
            result += "<td>{:.2f}</td>".format(cycle_time_pct85)
    result += "</tr>"
    
    result += "<tr><td>Média</td>"    
    for status in config.all_statuses[0:-1]:
        cycle_times = df_aging[status + " age"].values
        if len(cycle_times) == 0:
            result += "<td>-</td>"
        else:
            average = np.average(cycle_times)
            result += "<td>{:.2f}</td>".format(average)
    result += "</tr>"
    
    result += "<tr><td>Desv.Pad.</td>"
    for status in config.all_statuses[0:-1]:
        cycle_times = df_aging[status + " age"].values
        if len(cycle_times) == 0:
            result += "<td>-</td>"
        else:
            std = np.std(cycle_times)
            result += "<td>{:.2f}</td>".format(std)
    result += "</tr>"
    
    result += "<tr><td>Max</td>"    
    for status in config.all_statuses[0:-1]:
        cycle_times = df_aging[status + " age"].values
        if len(cycle_times) == 0:
            result += "<td>-</td>"
        else:
            max_ct = np.max(cycle_times)
            result += "<td>{:.2f}</td>".format(max_ct)
    result += "</tr>"
    
    result += "</table><br/><br/>"
    
    final_result.text_result["total_age"] += result
    
    return 0

def total_aging(final_result, all_issues, config):
    status_columns = []
    for status in config.all_statuses:
        status_columns.append(status + " age")
    for status in config.all_statuses:
        status_columns.append(status + " moves")
    status_columns.append(config.downstream_stop)
 
    df_aging = pd.DataFrame(columns=["Key","expedite","issuetype","status","CycleTime"] + status_columns)

    for issue in all_issues:
        expedite = False # TODO: config.is_expedite(issue)
        creation_date = datetime.strptime(issue.fields.created[0:10], "%Y-%m-%d")

        last_transition_dt = creation_date
        last_status = config.all_statuses[0] 
        cycle_time = 0.0
        
        if last_status not in config.all_statuses:
            raise Exception("Status {} not in all_status".format(last_status))
        
        issue_aging = {"Key": issue.key, 
                       "status": coach_matic_base.get_status(config, issue), 
                       "expedite": expedite,
                       "issuetype": issue.fields.issuetype.name}
        for field_name in config.export_csv_add_fields:
            custom_field_name = coach_matic_base.get_custom_field_name(config, field_name)
            issue_aging[field_name] = coach_matic_base.get_custom_field_value(config, issue, field_name, custom_field_name)
            
        for status in config.all_statuses:
            issue_aging[status + " age"] = 0.0
            issue_aging[status + " moves"] = 0

        for history in coach_matic_base.ensure_history_order_reverse(issue, reverse=False):
            for item in history.items:
                if item.field == "status" and \
                          coach_matic_base.get_status(config, status=item.toString) in config.all_statuses and \
                          coach_matic_base.get_status(config, status=item.toString) != coach_matic_base.get_status(config, status=item.fromString):
                    dt = datetime.strptime(history.created[0:10], "%Y-%m-%d")

                    diff_in_days = (dt - last_transition_dt).total_seconds() / (60*60*24)
                    cycle_time += diff_in_days
                    issue_aging[last_status + " age"] = issue_aging[last_status + " age"] + diff_in_days
                    
                    last_transition_dt = dt
                    last_status = coach_matic_base.get_status(config, None, item.toString)
                    issue_aging[last_status + " moves"] = issue_aging[last_status + " moves"] + 1
                    
                    if coach_matic_base.get_status(config, None, item.toString) == config.downstream_stop: 
                        issue_aging[config.downstream_stop] = dt

        current_status = coach_matic_base.get_status(config, issue)
        diff_in_days = (datetime.now() - last_transition_dt).total_seconds() / (60*60*24)
        cycle_time += diff_in_days
        if current_status + " age" in issue_aging:
            issue_aging[current_status + " age"] = issue_aging[current_status + " age"] + diff_in_days
        
        cycle_time -= issue_aging[config.all_statuses[-1] + " age"]
        issue_aging["CycleTime"] = cycle_time
        
        df_aging = coach_matic_base.concat(df_aging, issue_aging)

    analyse_total_aging(final_result, df_aging, config)
    
    if config.total_age_percentil:
        calc_percentil(final_result, config, df_aging)
    
    if not config.detailing_per_field:
        file_name_temp = config.project_name.replace("/", "-").replace("\\", "-")
        csv_file_name = final_result.temp_dir + "total_aging" + file_name_temp + ".csv"
        df_aging.to_csv(csv_file_name, sep="\t", decimal=',', index=False)
        final_result.all_files.add(csv_file_name)
    
    final_result.df_aging = df_aging

    return df_aging
