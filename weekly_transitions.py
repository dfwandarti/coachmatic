import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from dateutil import parser, tz
import os

import texts, coach_matic_base

###############################################################################
# count changes for one field over week
# group_hours: should sum for every each hour? or every two hours?
def changes_over_week_state(final_result, config, all_issues, status_friendly_name, shift_in_min, group_hours):
    change_over_week_range_days = 30

    changes_over_week = [0] * 7
    for weekday_num in range(7):
        changes_over_week[weekday_num] = [0] * int((24 / group_hours))
    
    # TODO: rever o timezone...
    adjust_hour_timezone = timedelta(hours=0, minutes=shift_in_min)
    # adjust_hour_timezone = timedelta(hours=-3, minutes=shift_in_min)
    
    for issue in all_issues:
        for history in coach_matic_base.ensure_history_order_reverse(issue, num_days=change_over_week_range_days):
            for item in history.items:
                if item.field == "status" and coach_matic_base.get_status(config, None, item.toString) in config.all_statuses:
                    dt_change = parser.parse(history.created)
                    dt_change += adjust_hour_timezone
                    week_day = int(dt_change.weekday())
                    hour = int(dt_change.hour / group_hours)

                    changes_over_week[week_day][hour] += 1
                    
                    continue

    total_transitions = sum([sum(changes_over_week[day]) for day in range(7)])
    
    if total_transitions == 0:
        return "", [], changes_over_week

    # any smoke on hour change?
    all_pcts = []
    transitions_per_hour = {}
    pct_transitions_per_hour = [0] * int(24 / group_hours)
    for hour in range(int(24 / group_hours)):
        total_transitions_hour = sum([changes_over_week[day][hour] for day in range(7)])
        transitions_per_hour[total_transitions_hour] = hour
        pct_transitions_per_hour[hour] = (total_transitions_hour / total_transitions) * 100
        
    ordered_transitions = sorted(transitions_per_hour.keys(), reverse=True)
    if ordered_transitions[0] / total_transitions > 0.5:
        pct = ordered_transitions[0] / total_transitions
        hour = "{}h{}".format(
            transitions_per_hour[ordered_transitions[0]] - (1 if shift_in_min > 0 else 0) * group_hours, 
            shift_in_min)
        result = texts.weekly_transition_find_per_hour.format(
            pct * 100, status_friendly_name, hour)
    elif (ordered_transitions[0] + ordered_transitions[1]) / total_transitions > 0.5:
        pct = (ordered_transitions[0] +
                ordered_transitions[1]) / total_transitions
        hour = "{}h{}, {}h{}".format(transitions_per_hour[ordered_transitions[0]] * group_hours - (1 if shift_in_min > 0 else 0),
                                      shift_in_min, transitions_per_hour[ordered_transitions[1]] * group_hours - (1 if shift_in_min > 0 else 0), shift_in_min)
        result = texts.weekly_transition_find_per_hour.format(
            pct * 100, status_friendly_name, hour)
    else:
        result = ""
        pct = 0
    all_pcts.append(pct)

    # any smoke on day change?
    transitions_per_day = {}
    pct_transitions_per_day = [0] * 7
    for day in range(7):
        total_transitions_day = sum(changes_over_week[day])
        transitions_per_day[total_transitions_day] = day
        pct_transitions_per_day[day] = (total_transitions_day / total_transitions) * 100
    ordered_transitions = sorted(transitions_per_day.keys(), reverse=True)
    if ordered_transitions[0] / total_transitions > 0.5:
        pct = ordered_transitions[0] / total_transitions
        day_1 = transitions_per_day[ordered_transitions[0]]
        day = "{}".format(texts.weekly_transition_weekday[day_1])
        result += texts.weekly_transition_find_per_hour.format(
            pct * 100, status_friendly_name, day)
    elif (ordered_transitions[0] + ordered_transitions[1]) / total_transitions > 0.5:
        pct = (ordered_transitions[0] +
                ordered_transitions[1]) / total_transitions
        day_1 = transitions_per_day[ordered_transitions[0]]
        day_2 = transitions_per_day[ordered_transitions[1]]
        day = "{}, {}".format(texts.weekly_transition_weekday[day_1], \
                                texts.weekly_transition_weekday[day_2])
        result += texts.weekly_transition_find_per_day.format(
            pct * 100, status_friendly_name, day)
    else:
        pct = 0
    all_pcts.append(pct)
    
    # save in .csv for analysis in excel...
    file_name = final_result.temp_dir + "changes_over_week.csv"
    with open(file_name, "a") as f:
        hours_day = ["{}h{}".format(h - (1 if shift_in_min > 0 else 0), shift_in_min) for h in range(int(24 / group_hours))]
        f.write("{},{},{},%\n".format(status_friendly_name, texts.weekly_transition_title_csv, ",".join(hours_day)))
            
        for weekday_num in range(len(changes_over_week)):
            weekday_str = texts.weekly_transition_weekday[weekday_num]
            changes = [str(c) for c in changes_over_week[weekday_num]]
            
            f.write("{},{},{},{:.2f}%\n".format(status_friendly_name, weekday_str, ",".join(
                changes), pct_transitions_per_day[weekday_num]))
        
        
        total_hours_pct = ["{:.2f}%".format(pct) for pct in pct_transitions_per_hour]
        f.write("Total, ,{}, \n\n".format(",".join(total_hours_pct)))
        
    return result, all_pcts, changes_over_week
            
def plot_heatmap(final_result, config, changes_over_week):
    fig, ax = plt.subplots()
    im = ax.imshow(changes_over_week, cmap="Reds")
    
    group_hours = int(24 / len(changes_over_week[0]))
    daily_hours = ["{}h".format(h * group_hours) for h in range(0, int(24 / group_hours))]
    
    # Show all ticks and label them with the respective list entries
    ax.set_xticks(np.arange(len(daily_hours)))
    ax.set_xticklabels(daily_hours)
    ax.set_yticks(np.arange(len(texts.weekly_transition_weekday)))
    ax.set_yticklabels(texts.weekly_transition_weekday)
    
    # Rotate the tick labels and set their alignment.
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right",
             rotation_mode="anchor")
    
    # Loop over data dimensions and create text annotations.
    for day in range(len(changes_over_week)):
        for hour in range(len(changes_over_week[0])):
            ax.text(hour, day, changes_over_week[day][hour],
                           ha="center", va="center", color="w")
    
    ax.set_title(texts.weekly_transition_chart_title.format(30, config.project_name))
    fig.tight_layout()
    # plt.show()
    
    image_file_name = final_result.temp_dir + "weekly_trans_heatmap.png"
    plt.savefig(image_file_name)
    final_result.all_files.add(image_file_name)

    
def weekly_transitions(final_result, config, all_issues, df):
    all_results = []
    all_pcts = []
    all_changes_over_week = []

    # reset file, each analisys will append it
    file_name = final_result.temp_dir + "changes_over_week.csv"
    with open(file_name, "w") as f:
        f.write("")
        
    for group_hours in [1, 2]:
        for shift_in_min in [0, 30]:
            result, pct, changes_over_week = changes_over_week_state(
                final_result, config, all_issues, texts.weekly_transition_all_statuses, 
                shift_in_min, group_hours)
            
            all_results.append(result)
            all_pcts.append(pct)
            all_changes_over_week.append(changes_over_week)
            
            # TODO: it would be nice to get heatmap per state. Too complicated for now
            # for status in config.all_statuses:
            #     changes_over_week_state(
            #         final_result, all_issues, df, status, status, shift_in_min)

    # look for higher percentage of grouping hours
    max_pct = 0
    idx_max = -1
    for i in range(len(all_pcts)):
        m = max(all_pcts[i])
        if m > max_pct:
            idx_max = i
    
    if idx_max >= 0:
        result = texts.weekly_transition_title + all_results[idx_max]
    else:
        result = texts.weekly_transition_title + texts.weekly_transition_not_found
        
    final_result.text_result["weekly_transition"] = result
    
    plot_heatmap(final_result, config, all_changes_over_week[idx_max])
    
    final_result.all_files.add(file_name)

