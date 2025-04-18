import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

import texts, coach_matic_base

def chart_throughput(final_result, config, df_evolution, column_name, description, weekly_intake):
    plt.clf()

    all_field_values = [fv for fv in df_evolution.groupby(by=column_name)[column_name].count().index]
    sum_per_week = df_evolution.groupby(by="end_of_week")["throughput_week"].sum()
    
    df_evolution = df_evolution.sort_values(by="end_of_week")
    all_end_of_weeks = df_evolution["end_of_week"].unique()
    x = [x for x in range(len(all_end_of_weeks))]
    # y = df_evolution[column_name].tolist()
    y = [y for y in range(max(sum_per_week) + 1)]
    x_labels = all_end_of_weeks

    last_throughput = [0 for x in range(len(sum_per_week))]
    for field_value in all_field_values:
        throughput = df_evolution[df_evolution[column_name] == field_value]["throughput_week"].tolist()
        plt.bar(x, throughput, bottom=last_throughput)
        last_throughput = [t+lt for t,lt in zip(throughput, last_throughput)]
    
    # You can specify a rotation for the tick
    # labels in degrees or with keywords.
    plt.xticks(x, x_labels, rotation=90)
    # plt.yticks(y)
    
    if weekly_intake != None:
        plt.plot(x, weekly_intake, 'r', color='black',  label='Entrada')
        all_field_values.insert(0, "Entrada")

    # Pad margins so that markers don't get
    # clipped by the axes
    plt.margins(0.2)

    # Tweak spacing to prevent clipping of tick-labels
    plt.subplots_adjust(bottom = 0.15)
    plt.legend(all_field_values)
    
    plt.title(texts.discriminated_throughput_chart_title.format(description, config.project_name))
    plt.xlabel(texts.discriminated_throughput_chart_xlabel)
    plt.ylabel(texts.discriminated_throughput_chart_ylabel)
    
    plt.tight_layout(w_pad = 2.0)

    image_file_name = "chart_throughput_{}.png".format(description).replace(" ", "_")
    path_file_name = final_result.temp_dir + image_file_name
    plt.savefig(path_file_name)
    final_result.all_files.add(path_file_name)

    result = f'<img src="{image_file_name}"/><br/>'
    return result

def get_six_most_common(config, df):
    count = df.groupby(by=config.discriminated_throughput_field)[config.discriminated_throughput_field].count()
    six_most_common = list(count.sort_values().index[-6:])
    
    df["six_common"] = df[config.discriminated_throughput_field]
    df["six_common"] = np.where(df["six_common"].isin(six_most_common), \
                                df["six_common"], \
                                texts.discriminated_throughput_other)
    
def get_weekly_throughput(config, df):
    get_six_most_common(config, df)
    
    df_evolution = pd.DataFrame(columns=["end_of_week","throughput_week", config.discriminated_throughput_field])
    
    sunday = datetime.today() - timedelta(days=datetime.today().isoweekday() % 7)
    less_7_days = timedelta(days = -7)
    for week in range(12, 0, -1): # 12 weeks -> 3 months

        last_sunday = sunday
        sunday  = sunday + less_7_days

        for field_value in df.groupby(by="six_common")["six_common"].count().index:
            throughput_week = df[(df[config.downstream_stop] <= last_sunday) & (
                df[config.downstream_stop] > sunday) & (
                df["six_common"] == field_value)][config.downstream_stop].count()
        
            d = {"end_of_week": sunday.strftime("%Y-%m-%d"),
                  "throughput_week": throughput_week,
                  config.discriminated_throughput_field: field_value}
            
            df_evolution = coach_matic_base.concat(df_evolution, d) 

    df_evolution = df_evolution.dropna()
    
    return df_evolution

def get_weekly_creation(config, df):
    first_status = config.all_statuses[0]
    
    weekly_intake = []
    sunday = datetime.today() - timedelta(days=datetime.today().isoweekday() % 7)
    less_7_days = timedelta(days = -7)
    for week in range(12, 0, -1): # 12 weeks -> 3 months

        last_sunday = sunday
        sunday  = sunday + less_7_days

        intake_week = df[(df[first_status] <= last_sunday) & (
            df[first_status] > sunday)][first_status].count()
        weekly_intake.insert(0, intake_week)
    
    return weekly_intake
    
def discriminated_throughput(final_result, config, df):
    df_evolution = get_weekly_throughput(config, df)
    if config.discriminated_throughput_creation:
        weekly_intake = get_weekly_creation(config, df)
    else:
        weekly_intake = None
    
    result = chart_throughput(final_result, config, df_evolution, \
                    config.discriminated_throughput_field, \
                    config.discriminated_throughput_field, \
                    weekly_intake)
    
    final_result.text_result["discriminated_throughput"] = result