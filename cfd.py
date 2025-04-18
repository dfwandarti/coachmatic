### analisa CFD
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from scipy.stats import linregress
from scipy import stats
import os, math

import texts, coach_matic_base

def count_issues(config, df):
    today = datetime.now()
    min_date = df[config.downstream_statuses[0]].copy().dropna().min()
    days_ago_90 = today - timedelta(days=config.cfd_days)
    start_date = max(min_date, days_ago_90)  # TODO: '>' not supported between instances of 'datetime.datetime' and 'float'
    num_of_days = (today - start_date).days
    num_of_statuses = len(config.downstream_statuses)

    # 2x2 array, one row per status
    issue_count = [[0]*num_of_days for i in range(num_of_statuses)]
    
    for num_day in range(num_of_days):
        dt_day = today - timedelta(days=num_day, hours=today.hour, minutes=today.minute,
                                   seconds=today.second, microseconds=today.microsecond)
        for idx_col in range(num_of_statuses):
            status = config.downstream_statuses[idx_col]
            
            if idx_col < num_of_statuses - 1:
                next_status = config.downstream_statuses[idx_col + 1]
                count_status_day = len(df[(df[status] <= dt_day) & (
                    (df[next_status].isnull()) | (df[next_status] > dt_day))])
            else:
                count_status_day = len(df[(df[status] <= dt_day)])

            issue_count[idx_col][(num_of_days - num_day) - 1] = count_status_day
            idx_col += 1
    return issue_count    
    
def prepare_cfd(issue_count):
    num_of_statuses = len(issue_count)
    num_of_days = len(issue_count[0])
    issue_cfd = [[0]*num_of_days for i in range(num_of_statuses)]
    
    for num_day in range(num_of_days):
        sum = issue_count[num_of_statuses - 1][num_day]
        issue_cfd[num_of_statuses - 1][num_day] = sum
        for idx_status in range(num_of_statuses - 2, 0, -1):
            sum = issue_count[idx_status][num_day] + sum
            issue_cfd[idx_status][num_day] = sum
            
    return issue_cfd
    
########################################################################
# aging spc chart
def chart_cfd(final_result, config, issue_count):
    plt.clf()
    # fig, ax = plt.subplots()
    
    num_of_days = len(issue_count[0])
    
    x = range(num_of_days) #int(num_of_days / 7))
    
    ic = issue_count[::-1]
    
    # reset day one for better cfd
    ic = ic.copy()
    itens_day_one_last_status = ic[0][0]
    for day in range(num_of_days):
        ic[0][day] -= itens_day_one_last_status
    
    plt.stackplot(x, ic)#, labels=config.downstream_statuses)
    plt.legend(loc='upper left', fontsize=8, labels=config.downstream_statuses[::-1])

    # list with dates for 
    day = datetime.now()
    labels = list()
    week_count = 7
    for i in range(num_of_days):
        if week_count == 7:
            labels.append(day.strftime("%Y-%m-%d"))
            week_count = 0
        else:
            labels.append(" ")
            week_count += 1
        day = day - timedelta(days=1)
    l1 = labels[::-1]
    plt.xticks(ticks=range(num_of_days), labels=l1, rotation=90)
    # plt.set_xticks(range(len(l1)))
    # plt.set_xticklabels(l1, rotation=90)
      
    plt.title("CFD ({})".format(config.project_name))

    plt.tight_layout(w_pad = 2.0)

    file_name = f"cfd{config.project_name}.png".replace(" ", "")
    image_file_name = final_result.temp_dir + file_name
    plt.savefig(image_file_name)
    final_result.all_files.add(image_file_name)
    return file_name
    
#################################################################
def pattern_disappearing_bands(config, issue_count):
    num_of_statuses = len(issue_count)
    num_of_days = len(issue_count[0])
    disappering_bands = []
    disappering_msg = ""
    
    for idx_status in range(num_of_statuses - 1):
        status = config.downstream_statuses[idx_status]
        if status in config.waiting_statuses:
            continue
        num_of_days_with_item = 0
        for day in range(num_of_days):
            if issue_count[idx_status][day] > 0:
                num_of_days_with_item += 1
        
        if 1 - (num_of_days_with_item / num_of_days) > 0.4:
            disappering_msg += texts.cfd_anomaly.format(
                status, num_of_days, num_of_days_with_item)
            
            disappering_bands.append(status)

    if disappering_msg != "":
        disappering_msg += texts.cfd_anomaly_foot1
        disappering_msg += texts.cfd_anomaly_foot2
        
    return disappering_msg, disappering_bands
            
#################################################################
def daily_wip_check_overrall(issue_count):
    result = ""
    num_of_statuses = len(issue_count)
    num_of_days = len(issue_count[0])
    
    daily_wip = []
    for day in range(num_of_days):
        daily_wip.append(sum([issue_count[c][day] for c in range(num_of_statuses - 2)]))
        np_daily_wip = np.array(daily_wip)
        
    max_wip = np_daily_wip.max()
    min_wip = np_daily_wip.min()
    mean_wip = np_daily_wip.mean()
    days_higher_wip = np.count_nonzero(np_daily_wip > mean_wip)
    days_lower_wip = np.count_nonzero(np_daily_wip < mean_wip)
    
    result += texts.cfd_wip_check.format(min_wip, max_wip)
    result += texts.cfd_wip_check_1.format(mean_wip, days_lower_wip, days_higher_wip)
    
    # is there a big variation
    today = datetime.now()
    for day in range(len(daily_wip) - 1):
        variation = daily_wip[day + 1] - daily_wip[day]
        
        if variation > mean_wip:
            dt_day = today - timedelta(days=day, hours=today.hour, minutes=today.minute,
                                       seconds=today.second, microseconds=today.microsecond)
            text = texts.cfd_wip_check_variation.format(
                dt_day.strftime("%Y-%m-%d"), daily_wip[day + 1], daily_wip[day])
            result += text
            
    if result != "":
        result += texts.cfd_wip_check_foot
        
    return result

#################################################################
# outlier
def calculate_outliers(list_itens):
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

def pattern_stair_step(config, issue_count, disappering_bands):
    num_of_statuses = len(issue_count)
    num_of_days = len(issue_count[0])
    step_msg = ""

    today = datetime.now()
    for status_idx in range(num_of_statuses):
        status = config.downstream_statuses[status_idx]
        # if status in disappering_bands:  # avoid false positives if it is in disappering bands
        #     continue 
        
        all_variations = []
        for day in range(1, num_of_days):
            variation = issue_count[status_idx][day - 1] - issue_count[status_idx][day]
            all_variations.append(variation)

        # np_issue_count_status = np.array(issue_count[status_idx])
        # mean_wip_status = np_issue_count_status.mean() # * 0.7 # picked any number - 70% by the way
        # min_variation = max(3, 0) # mean_wip_status * 0.6) # should consider mean wip?
        min_variation = 3 # mean_wip_status * 0.6) # should consider mean wip?
        
        outliers_position = calculate_outliers(all_variations) #issue_count[status])
        
        for idx in outliers_position:
            if abs(all_variations[idx]) > min_variation: #avoid false positivies, or minimal variations
                dt_day = today - timedelta(days=num_of_days - idx - 1, hours=today.hour, minutes=today.minute,
                                           seconds=today.second, microseconds=today.microsecond)
                step_msg += texts.cfd_stair_step.format(
                    dt_day.strftime("%Y-%m-%d"), status, issue_count[status_idx][idx], 
                    issue_count[status_idx][idx + 1])

    result = ""
    if step_msg != "":
        result += step_msg
        result += texts.cfd_stair_step_foot 
    return result 
    
#######################################################################
def chart_wip_evolution(final_result, config, df_evolution):
    plt.clf()

    df_evolution = df_evolution.sort_values(by="end_of_week")
    x = [x for x in range(len(df_evolution))]
    y = df_evolution["arrival_throughput_rate"].tolist()
    labels = df_evolution["end_of_week"].tolist()
    plt.plot(x, y, label="Razão entrada/saída")
    # You can specify a rotation for the tick
    # labels in degrees or with keywords.
    plt.xticks(x, labels, rotation =45)

    for yc in range(10, 100, 10):
        plt.axhline(y=yc, color='lightgray', linestyle='--')

    # Pad margins so that markers don't get
    # clipped by the axes
    plt.margins(0.2)

    # Tweak spacing to prevent clipping of tick-labels
    plt.subplots_adjust(bottom = 0.15)

    res = stats.linregress(x, y)
    x_trend = list(map(lambda a: res.intercept + res.slope*a, x))
    plt.plot(x, x_trend, 'r', linestyle='dashed', label='Tendência')
    
    plt.title(texts.cfd_in_out_chart_title.format(config.project_name))
    plt.xlabel(texts.cfd_in_out_chart_xlabel)
    plt.ylabel(texts.cfd_in_out_chart_ylabel)
    plt.legend()

    plt.tight_layout(w_pad = 2.0)

    image_file_name = final_result.temp_dir + "wip_evolution.png"
    plt.savefig(image_file_name)
    final_result.all_files.add(image_file_name)

def check_wip_evolution(df_evolution):
    df_evolution = (df_evolution.copy()).sort_values(by="end_of_week")
    
    try:
        res = linregress(range(len(df_evolution)), df_evolution["arrival_throughput_rate"])
    except:
        return "" # it is not working for some reason...

    if res.slope > 0.95 and res.slope < 1.1:
        result = texts.cfd_diff_gradient_evolution_1.format(res.slope)
    elif res.slope >= 1.1:
        result = texts.cfd_diff_gradient_evolution_2.format(res.slope)
    else:
        result = texts.cfd_diff_gradient_evolution_3.format(res.slope)
    
    result += texts.cfd_diff_gradient_foot.format(res.rvalue)
   
    return result
    
def pattern_difference_gradient(final_result, config, df):
    result = ""
    df_evolution = pd.DataFrame(columns=["end_of_week","arrival_throughput_rate","throughput_week"])

    df_rate = df.copy()
    df_rate = df_rate.sort_values(by=config.downstream_start)
    first_day = df_rate.iloc[0][config.downstream_start]
    num_days = (datetime.now() - first_day).days

    num_issues_in = df_rate[df_rate[config.downstream_start].notnull() == True][config.downstream_start].count()
    num_issues_out = df_rate[df_rate[config.downstream_stop].notnull() == True][config.downstream_stop].count()
        
    df_rate[(df_rate[config.downstream_start].notnull() == True)&(df_rate[config.downstream_stop].notnull() != True)]["Key"]
    
    rate_in = num_issues_in / num_days
    rate_out = num_issues_out / num_days

    in_out_rate = (rate_out / rate_in) * 100
    result += texts.cfd_diff_gradient_1 .format(in_out_rate)
    result += texts.cfd_diff_gradient_2
    if in_out_rate > 85:
        result += texts.cfd_diff_gradient_explain_1
    elif in_out_rate < 50:
        result += texts.cfd_diff_gradient_explain_2
    else:
        result += texts.cfd_diff_gradient_explain_3
        
    result += texts.cfd_diff_gradient_foot
    result += texts.cfd_diff_gradient_explan_1.format(rate_in)
    result += texts.cfd_diff_gradient_explan_2.format(rate_out)
    result += texts.cfd_diff_gradient_explan_3

    sunday = datetime.today() - timedelta(days=datetime.today().isoweekday() % 7)
    less_7_days = timedelta(days = -7)
    rate_evoluion = []
    for week in range(12, 0, -1): # 12 weeks -> 3 months
        num_issues_in = df[df[config.downstream_start] <= sunday][config.downstream_start].count()
        num_issues_out = df[df[config.downstream_stop] <= sunday][config.downstream_stop].count()

        rate_in = num_issues_in / num_days
        rate_out = num_issues_out / num_days
        
        if rate_in > 0:
            rate_evoluion.append("{:.2f}%".format((rate_out / rate_in) * 100))
    
            d = {"end_of_week": sunday.strftime("%Y-%m-%d"),
                 "arrival_throughput_rate": (rate_out / rate_in) * 100}
        else:
            rate_evoluion.append("{:.2f}%".format(0))
    
            d = {"end_of_week": sunday.strftime("%Y-%m-%d"),
                 "arrival_throughput_rate": None}

        last_sunday = sunday
        sunday  = sunday + less_7_days

        throughput_week = df[(df[config.downstream_stop] <= last_sunday) & (
            df[config.downstream_stop] > sunday)][config.downstream_stop].count()
        d["throughput_week"] = throughput_week

        # df_evolution = coach_matic_base.concat(df_evolution, d)
        df_evolution = df_evolution.append(d, ignore_index=True)

    rate_evoluion = rate_evoluion[::-1]
    result += ", ".join(rate_evoluion) + ".</font>\n"

    df_evolution = df_evolution.dropna()

    result += check_wip_evolution(df_evolution)
    
    final_result.df_evolution = df_evolution

    # itens started word, but went back    
    wip = max(0, num_issues_in - num_issues_out)
    result += texts.cfd_diff_gradient_curr_wip.format(wip)
    result += texts.cfd_diff_gradient_curr_wip_foot

    if config.wip_evolution_chart:
        chart_wip_evolution(final_result, config, df_evolution)
    # chart_throughput_spc(final_result, config, df_evolution, "throughput_week", texts.cfd_spc_chart_throughput)

    return result

#############################################################################
def message_flat_line(status_name, num_of_days, day_start_flag_line, day, num_of_days_with_flat_line):
    flat_line_message = ""
    if num_of_days_with_flat_line > 5:
        today = datetime.now()
        start_dt_day = today - timedelta(days=num_of_days - day_start_flag_line, hours=today.hour, minutes=today.minute,
                                   seconds=today.second, microseconds=today.microsecond)
        stop_dt_day = today - timedelta(days=num_of_days - day, hours=today.hour, minutes=today.minute,
                                   seconds=today.second, microseconds=today.microsecond)
        flat_line_message = texts.cfd_diff_flat_1.format(
            num_of_days_with_flat_line, status_name,
            start_dt_day.strftime("%Y-%m-%d"), stop_dt_day.strftime("%Y-%m-%d"))
    
    return flat_line_message

def pattern_flat_lines(config, issue_count):
    result = ""
    num_of_statuses = len(issue_count)
    num_of_days = len(issue_count[0])
    flat_line_message = ""

    for status_idx in range(num_of_statuses - 1):
        day_start_flag_line = 0
        num_of_days_with_flat_line = 0
        status_name = config.downstream_statuses[status_idx]        
    
        wip_next_statuses_last_day = -1
        for day in range(num_of_days):
            wip_next_statuses = sum([issue_count[next_status][day] for next_status in range(status_idx + 1, num_of_statuses)])
            
            # if issue_count[status_idx][day] == issue_count[status_idx][day + 1] and issue_count[status_idx][day] != 0:
            if wip_next_statuses == wip_next_statuses_last_day and issue_count[status_idx][day] != 0:
                if num_of_days_with_flat_line == 0:
                    day_start_flag_line = day
                num_of_days_with_flat_line += 1
            else:
                flat_line_message += message_flat_line(status_name, num_of_days, 
                                                       day_start_flag_line, day, 
                                                       num_of_days_with_flat_line)
                num_of_days_with_flat_line = 0
            
            wip_next_statuses_last_day = wip_next_statuses
            
    if flat_line_message == "":
        result = texts.cfd_diff_flat_2
    else:
        result += flat_line_message
    result += texts.cfd_diff_flat_foot
  
    return result

#############################################################################
def pattern_s_curve(issue_count):
    num_of_statuses = len(issue_count)
    num_of_days = len(issue_count[0])

    num_itens_day_one = sum([issue_count[status_idx][0] for status_idx in range(num_of_statuses)])

    # first_quarter_days = int(num_of_days / 4)
    # num_itens_first_quarter_days = sum([issue_count[status_idx][first_quarter_days] for status_idx in range(num_of_statuses)])

    half_days = int(num_of_days / 2)
    num_itens_half_days = issue_count[-1][half_days]
    num_itens_end_days = issue_count[-1][num_of_days - 1]
    # num_itens_half_days = sum([issue_count[status_idx][half_days] for status_idx in range(num_of_statuses)]) - num_itens_day_one
    # num_itens_end_days = sum([issue_count[status_idx][num_of_days - 1] for status_idx in range(num_of_statuses)]) - num_itens_day_one

    # degree_first_quarter = math.degrees(math.atan2(num_itens_first_quarter_days, first_quarter_days))
    degree_first_half = math.degrees(math.atan2(num_itens_half_days, half_days))
    degree_to_the_end = math.degrees(math.atan2(num_itens_end_days, num_of_days))
    
    result = ""
    if degree_to_the_end < degree_first_half * 0.70: # 70% to avoid being to harsh
        result = texts.cfd_s_curve_explan_3 # found S curve
        result += texts.cfd_s_curve_foot_3
    elif degree_to_the_end < degree_first_half * 0.85: # 85% to avoid being to harsh
        result = texts.cfd_s_curve_explan_1 # found S curve
        result += texts.cfd_s_curve_foot_1
    elif degree_first_half < degree_to_the_end * 0.85:
        result = texts.cfd_s_curve_explan_2 # found inverted S curve
        result += texts.cfd_s_curve_foot_2
        
    return result 
    
#############################################################################
# main        
def cfd(final_result, config, df):
    issue_count = count_issues(config, df)
    # issue_cfd = prepare_cfd(issue_count)
    image_file_name = chart_cfd(final_result, config, issue_count)
    
    result_disappear, disappering_bands = pattern_disappearing_bands(config, issue_count)
    result_wip = daily_wip_check_overrall(issue_count)
    result_stair = pattern_stair_step(config, issue_count, disappering_bands)
    result_gradient = pattern_difference_gradient(final_result, config, df)
    result_flat = pattern_flat_lines(config, issue_count)
    result_s = pattern_s_curve(issue_count)
    
    result = texts.cfd_main_title + result_disappear + result_wip + result_stair + \
          result_gradient + result_flat + result_s
          
    result += f'<img src="{image_file_name}"/><br/>'
    result += '<img src="wip_evolution.png"/><br/>'
    final_result.text_result["cfd"] = result
    
#############################################################################
# only for tests..
def testes_issue_count_big_delivery(issue_count):
    #simula entrega grande
    issue_count[-1][-2] = issue_count[-1][-3] * 10
    # issue_count = [[0, 0, 0, 0, 0],
    #                [7, 7, 7, 7, 0],
    #                [0, 0, 0, 0, 7]]
    
