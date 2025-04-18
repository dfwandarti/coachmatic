import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import os

import texts

def chart_spc(final_result, df_weekly_count, column_name, filename, chart_title, chart_x, \
              chart_y, min_upper_value=0):
    plt.clf()

    mean_value = df_weekly_count["num_items"].mean()
    std_throughput = df_weekly_count["num_items"].std()
    upper_limit3 = mean_value + 3 * std_throughput
    lower_limit3 = max(mean_value - 3 * std_throughput, min_upper_value)

    df_weekly_count = df_weekly_count.sort_values(by="end_of_week")
    x_values = [x for x in range(min(len(df_weekly_count), 25))] # chart only last 25 items, avoid chart to crowded
    y_values = df_weekly_count["num_items"][-25:].tolist()
    labels = df_weekly_count["end_of_week"][-25:].tolist()
    plt.plot(x_values, y_values)
        
    # You can specify a rotation for the tick
    # labels in degrees or with keywords.
    plt.xticks(x_values, labels, rotation=90)

    plt.axhline(y=mean_value, color='gray', linestyle='--')
    plt.axhline(y=upper_limit3, color='red', linestyle='--')
    plt.axhline(y=lower_limit3, color='red', linestyle='--')
    
    x = 0
    for y in y_values:
        if y > upper_limit3 or y < lower_limit3:
            y_plus = 1 if y > 0 else -1
            plt.text(x - 0.5, y + y_plus, "+", color='red')
        x += 1
    # for x in range(min(len(df_weekly_count), 25)):
    #     if y[x] >= upper_limit3 or y[x] <= lower_limit3:
    #         y_plus = 1 if y[x] > 0 else -1
    #         plt.text(x - 0.5, y[x] + y_plus, "+", color='red')

    # Pad margins so that markers don't get
    # clipped by the axes
    plt.margins(0.2)

    # Tweak spacing to prevent clipping of tick-labels
    plt.subplots_adjust(bottom = 0.15)

    plt.tight_layout(w_pad = 2.0)
    
    plt.title(chart_title)
    plt.xlabel(chart_x)
    plt.ylabel(chart_y)

    plt.tight_layout(w_pad = 2.0)
    
    image_file_name = final_result.temp_dir + filename
    plt.savefig(image_file_name)
    final_result.all_files.add(image_file_name)
    
    return mean_value, upper_limit3, lower_limit3

def prepare_data(final_result, config, df, column_name, spc_type):
    time_window = config.spc_time_window
    
    df_temp = df[["Key", column_name]].copy()
    df_temp = df_temp.dropna()
    df_temp[column_name] = pd.to_datetime(df_temp[column_name])
    
    df_weekly_count = pd.DataFrame(columns=["end_of_week","num_items"])

    first_date = df_temp[column_name].min()
    total_time_window = int((datetime.today() - first_date).days / time_window)
    
    sunday = datetime.today() - timedelta(days=datetime.today().isoweekday() % time_window)
    less_time_window_days = timedelta(days = -time_window)
    for week in range(total_time_window, 0, -1): 
        last_sunday = sunday
        sunday  = sunday + less_time_window_days

        count_created_week = df_temp[(df_temp[column_name] <= last_sunday) & (
            df_temp[column_name] > sunday)][column_name].count()
        d = {"end_of_week": [sunday.strftime("%Y-%m-%d")],
             "num_items": [count_created_week]}
        df_concat = pd.DataFrame(data=d)
        df_weekly_count = pd.concat([df_weekly_count, df_concat], ignore_index=False)
        # df_weekly_count = df_weekly_count.ignore_index=True)
    
    #we should have at least 25 items
    if len(df_weekly_count) < 25:
        result = texts.spc_title.format(spc_type)
        result += texts.spc_to_few_data.format(spc_type, len(df_weekly_count))
        final_result.text_result["spc " + spc_type] = result
        return []
    
    return df_weekly_count

def analyze_data(final_result, spc_type, df_weekly_count, mean_value, upper_limit, lower_limit, count_or_diff, day_or_week):
    result = ""
    
    df_weekly_count = df_weekly_count.sort_values(by="end_of_week")
    
    upper_weeks = []
    lower_weeks = []
    for week, num_items in df_weekly_count[["end_of_week", "num_items"]][-25:].itertuples(index=False):
        if num_items > upper_limit:
            upper_weeks.append("{} ({} {})".format(week, num_items, texts.spc_items))
        if num_items < lower_limit:
            lower_weeks.append("{} ({} {})".format(week, num_items, texts.spc_items))
            
    if len(upper_weeks) > 0:
        result += texts.spc_upper_limits.format(spc_type, count_or_diff, day_or_week, ", ".join(upper_weeks))
    if len(lower_weeks) > 0:
        result += texts.spc_lower_limits.format(spc_type, count_or_diff, day_or_week, ", ".join(lower_weeks))
    
    return result

# calculate difference of values between couting                                                
def prepare_diff(df_weekly_count):
    df_weekly_diff = pd.DataFrame(columns=["end_of_week","num_items"])
    
    last_value = None
    for week, num_items in df_weekly_count[["end_of_week", "num_items"]].itertuples(index=False):
        if last_value != None:
            diff = num_items - last_value
            df_concat = pd.DataFrame(data={"end_of_week": [week], 
                                           "num_items": [diff]})
            df_weekly_diff = pd.concat([df_weekly_diff, df_concat], ignore_index=False)
        
        last_value = num_items
    
    return df_weekly_diff

# SPC para vazão
def spc_throughput(final_result, config, df):
    if config.spc_time_window == 1:
        spc_type = texts.spc_type1_daily
        day_or_week = texts.spc_day
    else:
        spc_type = texts.spc_type1_weekly
        day_or_week = texts.spc_week
        
    column_name = config.downstream_statuses[-1]
    df_weekly_count = prepare_data(final_result, config, df, column_name, spc_type)
    
    if len(df_weekly_count) > 0:
        result = ""
        
        mean_value, upper_limit, lower_limit = chart_spc(
            final_result, df_weekly_count, column_name, "spc_through.png", texts.spc_chart_title.format(spc_type, config.project_name),
            texts.spc_chart_x_throughput, texts.spc_chart_y)
        result = analyze_data(final_result, spc_type, df_weekly_count,
                     mean_value, upper_limit, lower_limit, texts.spc_couting, day_or_week)
        result += '<img src="spc_through.png"/><br/>'
        
        df_weekly_diff = prepare_diff(df_weekly_count)
        mean_value, upper_limit, lower_limit = chart_spc(
            final_result, df_weekly_diff, column_name, "spc_through_diff.png", texts.spc_chart_variation_title.format(
                spc_type, config.project_name),
            texts.spc_chart_x_throughput, texts.spc_chart_y, min_upper_value=-10000)
        result += analyze_data(final_result, spc_type, df_weekly_diff,
                     mean_value, upper_limit, lower_limit, texts.spc_difference, day_or_week)

        if result != "":
            result += texts.spc_upper_limits_explain
        else:
            result = texts.spc_ok_throughput

        result += '<img src="spc_through_diff.png"/><br/>'
        result = texts.spc_title.format(spc_type) + result
        
        final_result.text_result["spc throughput"] = result

# SPC para criação de itens                                                
def spc_creation(final_result, config, df):
    if config.spc_time_window == 1:
        spc_type = texts.spc_type2_daily
        day_or_week = texts.spc_day
    else:
        spc_type = texts.spc_type2_weekly
        day_or_week = texts.spc_week

    column_name = config.all_statuses[0]
    df_weekly_count = prepare_data(final_result, config, df, column_name, spc_type)
    
    if len(df_weekly_count) > 0:
        result = ""
        
        mean_value, upper_limit, lower_limit = chart_spc(
            final_result, df_weekly_count, column_name, "spc_create.png", texts.spc_chart_title.format(spc_type, config.project_name),
            texts.spc_chart_x_throughput, texts.spc_chart_y)
        result += analyze_data(final_result, spc_type, df_weekly_count,
                     mean_value, upper_limit, lower_limit, texts.spc_couting, day_or_week)
        result += '<img src="spc_create.png"/><br/>'

        df_weekly_diff = prepare_diff(df_weekly_count)
        mean_value, upper_limit, lower_limit = chart_spc(
            final_result, df_weekly_diff, column_name, "spc_create_diff.png", texts.spc_chart_variation_title.format(
                spc_type, config.project_name),
            texts.spc_chart_x_throughput, texts.spc_chart_y, min_upper_value=-10000)
        result += analyze_data(final_result, spc_type, df_weekly_diff,
                     mean_value, upper_limit, lower_limit, texts.spc_difference, day_or_week)
        result += '<img src="spc_create_diff.png"/><br/>'

        if result != "":
            result += texts.spc_upper_limits_explain_creation
        else:
            result = texts.spc_ok_throughput

        result = texts.spc_title.format(spc_type) + result

        final_result.text_result["spc creation"] = result
