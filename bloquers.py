import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from dateutil import parser
import os

import coach_matic_base, texts

def break_status(status):
    if len(status) < 10:
        return status
    
    break_status = status.split(" ")
    each_word_size = int(10 / len(break_status))
    for s in break_status: s[:each_word_size]
    return ".".join([break_status[i][:each_word_size] for i in range(0, len(break_status))])
    
def chart_blockers(final_result, config, df_blockers):
    sum_status = df_blockers.groupby("status").sum("blocked_days")
    sum_status["status"] = sum_status.index
    
    if len(sum_status) == 0:
        return
    
    plt.clf()
    fig, ax = plt.subplots()#figsize=(30,20))
    ax.autoscale(enable=True)#, axis='x')

    labels = []
    x_pos = 0
    for status, blocked_days in sum_status[["status", "blocked_days"]].itertuples(index=False):
        ax.bar(x_pos, blocked_days)
        ax.text(x_pos, blocked_days, str(blocked_days), 
            color = 'black', horizontalalignment='center')
        x_pos += 1
        labels.append(break_status(status))

    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, fontsize=8) #rotation=90, 
    
    ax.set_title(texts.blockers_chart_title.format(config.project_name))
    ax.set_xlabel(texts.blockers_chart_xlabel)
    ax.set_ylabel(texts.blockers_chart_ylabel)
    ax.legend()
    
    plt.tight_layout(w_pad = 2.0)

    image_file_name = final_result.temp_dir + "status_blockeddays.png"
    plt.savefig(image_file_name)
    final_result.all_files.add(image_file_name)
    
def iterate_blocked(config, df_blockers, text_blockers_current):
    all_bloquers = []
    for key, status, start_flagged, stop_flagged, blocked_days, issuetype, description, current in df_blockers[["Key", "status", 
                              "start_flagged", "stop_flagged", "blocked_days", 
                              "issuetype", "description", "current"]].itertuples(index=False):
        block_description = "<tr><td><a href=""{}/browse/{}"">{}</a></td><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>".format(
            config.jira_url, key, key, blocked_days, issuetype, status, start_flagged.strftime("%Y-%m-%d"), stop_flagged.strftime("%Y-%m-%d"), 
            description)
        if current:
            all_bloquers.append("<b>" + block_description + "</b>")
        else:
            all_bloquers.append(block_description)

    return text_blockers_current + "".join(all_bloquers)
        
def analisa_blockers(final_result, config, all_issues):
    blocker_field = config.blocker_field
    blocker_field_description = config.blocker_field_description
    now = datetime.now()
    time_between_history_for_description = timedelta(hours=4)
    
    all_fields = set()  # debug only, may delete in the future
    
    df_blockers = pd.DataFrame(columns=["Key","status","start_flagged","stop_flagged", "current", "issuetype", "description"])
    for issue in all_issues:
        last_history_change = None
        
        one_blocker = {"Key": issue.key, "status": "", "description": "",
                       "stop_flagged": "", "current": False,
                       "issuetype": issue.fields.issuetype.name}

        df_blockers["status"] = np.where(df_blockers["status"] == "", 
                                         "-",
                                         df_blockers["status"])
        inside_block = coach_matic_base.get_custom_field_value_by_field_name(config, issue, blocker_field) != ""
        
        for history in coach_matic_base.ensure_history_order_reverse(issue):
            this_history_change = parser.parse(history.created)
            if last_history_change != None:
                history_change_close_last_one = last_history_change - \
                    this_history_change < time_between_history_for_description
                    
                if inside_block == False and \
                        last_history_change - this_history_change > time_between_history_for_description:
                    # reset description if history has more than 4h from last one
                    one_blocker["description"] = ""
            else:
                history_change_close_last_one = False
            
            last_history_change = this_history_change                

            for item in history.items:
                all_fields.add(item.field)
                to_value_is_empty = item.toString == "" or item.toString == None
                
                if (item.field == blocker_field_description or item.field == "Last Block Reason") \
                              and not to_value_is_empty:
                    if len(df_blockers) > 0 and \
                            df_blockers["description"].iloc[-1] == "" and \
                            df_blockers["Key"].iloc[-1] == issue.key and \
                            history_change_close_last_one:
                        df_blockers.iat[-1, -1] = item.toString
                    elif one_blocker["description"] == "" and (history_change_close_last_one or inside_block):
                        one_blocker["description"] = item.toString
                    
                if item.field == "status":
                    current_status = coach_matic_base.get_status(config, status=item.toString)
                    df_blockers["status"] = np.where(df_blockers["status"] == "", 
                                                     current_status,
                                                     df_blockers["status"])
                if item.field == blocker_field or item.field == "Blocked": # TODO: problema de tradução do Jira
                    dt = datetime.strptime(history.created[0:10], "%Y-%m-%d")

                    if to_value_is_empty: #item.toString == "" or item.toString == "None": # ended blocker
                        one_blocker["stop_flagged"] = dt
                        inside_block = True
                    else:
                        inside_block = False
                        if one_blocker["stop_flagged"] == "": # still blocked?
                            one_blocker["stop_flagged"] = now
                            one_blocker["current"] = True
                            
                        one_blocker["start_flagged"] = dt
                        df_blockers = coach_matic_base.concat(df_blockers, one_blocker)
                        # df_blockers = df_blockers.append(one_blocker, ignore_index=True)

                        one_blocker = {"Key": issue.key, "status": "", "description": "",
                                       "stop_flagged": "", "current": False}
                
                # all items in same history are close changes
                # it will reset whenn gets new history registry
                history_change_close_last_one = True 
                
    df_blockers["blocked_days"] = (pd.to_datetime(df_blockers["stop_flagged"]) - 
                                pd.to_datetime(df_blockers["start_flagged"])).dt.days
    df_blockers["blocked_days"] += 1
    
    df_blockers = df_blockers[df_blockers["status"] != "-"].copy() # how to drop?
    df_blockers["blocked days"] = (pd.to_datetime(df_blockers["stop_flagged"]) -
                       pd.to_datetime(df_blockers["start_flagged"])).dt.days + 1
    final_result.df_blockers = df_blockers
    
    chart_days = timedelta(days=config.blocker_days)
    last_days = datetime.now() - chart_days  
    df_blockers = df_blockers[df_blockers["stop_flagged"] > last_days].copy() # how to drop?
    
    result = texts.blockers_head.format(config.blocker_days)
    if len(df_blockers) > 0:
        result += texts.blockers_description
        result += iterate_blocked(config, df_blockers[df_blockers["current"] == False], "")
        result += iterate_blocked(config, df_blockers[df_blockers["current"] == True], texts.blockers_current)
        result += texts.blockers_foot
    else:
        result += texts.blockers_not_found
        
    result += '<img src="status_blockeddays.png"/><br/>'
    
    final_result.text_result["bloquers"] = result
    
    chart_blockers(final_result, config, df_blockers)
