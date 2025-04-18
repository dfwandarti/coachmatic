import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import copy

import texts, total_aging

class OneTicket:
    mean_value = 0
    std_value = 0
    upper_limit3 = 0
    upper_limit2 = 0
    upper_limit1 = 0
    bar_value = 0
    x_label = ""
    status = ""
    items_that_status = 0

    def __init__(self, mean_value, std_value, bar_value, x_label, status, items_that_status):
        self.mean_value = mean_value
        self.std_value = std_value
        self.upper_limit3 = mean_value + 3 * std_value
        self.upper_limit2 = mean_value + 2 * std_value
        self.upper_limit1 = mean_value + 1 * std_value
        self.bar_value = bar_value
        self.x_label = x_label
        self.status = status
        self.items_that_status = items_that_status
    
def one_spc_chart(final_result, all_tickets, chart_title, \
              spc_chart_x_aging, spc_chart_y_aging):
    bar_width = 4
    
    plt.clf()
    original_figsize = plt.rcParams["figure.figsize"]
    original_autolayout = plt.rcParams["figure.autolayout"]
    plt.rcParams["figure.figsize"] = [len(all_tickets), 4.8] 
    plt.rcParams["figure.autolayout"] = True
    fig, ax = plt.subplots()
    ax.set_xlim(0, len(all_tickets) * bar_width, auto=True)
    
    labels = []
    x_pos = 0
    mean_values = []
    upper3_values = []
    upper2_values = []
    upper1_values = []
    max_value = 0
    x_values = []
    status_num_tickets = {}
    last_upper_limit3 = None
    for one_ticket in all_tickets:
        if one_ticket.bar_value < one_ticket.upper_limit1:
            color = "green"
        elif one_ticket.bar_value < one_ticket.upper_limit2:
            color = "orange"
        elif one_ticket.bar_value < one_ticket.upper_limit3:
            color = "red"
        else:
            color = "purple"
            
        ax.bar(x_pos, one_ticket.bar_value, color=color, width=2)
        ax.text(x_pos, one_ticket.bar_value, "{:.0f}".format(one_ticket.bar_value), 
            color = 'black', fontsize="x-small")
        
        # this is to make difference between limits less smoth
        if last_upper_limit3 != None and last_upper_limit3 != one_ticket.upper_limit3:
            x_values.append(x_pos - int(bar_width / 2))
            mean_values.append(mean_values[-1])
            upper3_values.append(upper3_values[-1])
            upper2_values.append(upper2_values[-1])
            upper1_values.append(upper1_values[-1])
            x_values.append(x_pos - int(bar_width / 2))
            mean_values.append(one_ticket.mean_value)
            upper3_values.append(one_ticket.upper_limit3)
            upper2_values.append(one_ticket.upper_limit2)
            upper1_values.append(one_ticket.upper_limit1)
            labels.append("")
            labels.append("")
        
        x_values.append(x_pos)
        x_pos += bar_width
        
        labels.append(one_ticket.x_label)#.replace("-", "\n"))
        mean_values.append(one_ticket.mean_value)
        upper3_values.append(one_ticket.upper_limit3)
        upper2_values.append(one_ticket.upper_limit2)
        upper1_values.append(one_ticket.upper_limit1)
        max_value = max(max_value, one_ticket.bar_value)
        
        last_upper_limit3 = one_ticket.upper_limit3
        
        status_num_tickets[one_ticket.status] = one_ticket.items_that_status
        
    # x_values = [x for x in range(0, len(all_tickets) * bar_width, bar_width)]
    ax.plot(x_values, mean_values, color='lightgray', linestyle='--', label="média")
    ax.plot(x_values, upper3_values, color='red', linestyle='--', label="crítico")
    ax.plot(x_values, upper2_values, color='orange', linestyle='--', label="atenção")
    ax.plot(x_values, upper1_values, color='green', linestyle='--', label="ok")

    cumulative_tickets = 0
    y_shift = 10
    for status in status_num_tickets:
        x_pos = (cumulative_tickets * bar_width) - 1
        ax.vlines(x_pos, ymin=0, ymax=max_value+10+y_shift, colors="lightgray", linestyles="dotted")
        ax.text(
            x_pos, max_value + 10 + y_shift, status, ha="left", va="center", size="x-small",
            bbox=dict(boxstyle="round,pad=0.3", fc="cyan", ec="b", lw=2))
        cumulative_tickets += status_num_tickets[status]
        y_shift = (y_shift + 10) % 20
        
    
    ax.set_xticks(x_values)
    ax.set_xticklabels(labels)#, fontsize="x-small")
    ax.tick_params(axis='x', labelrotation=90)

    # ax.legend(loc='upper right')
    ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0.)
    
    ax.set_title(chart_title)
    ax.set_xlabel(spc_chart_x_aging)
    ax.set_ylabel(spc_chart_y_aging)

    plt.tight_layout(w_pad = 2.0)

    image_file_name = final_result.temp_dir + "one_spc_aging.png"
    plt.savefig(image_file_name)
    final_result.all_files.add(image_file_name)
    
    plt.rcParams["figure.autolayout"] = original_autolayout
    plt.rcParams["figure.figsize"] = original_figsize # restore size for others charts
    
    return 0

def aging_status_spc_analysis_all_together(final_result, config, all_issues, df_aging):
    # df_aging = df_aging.sort_values(by=column_name)
    # df_aging["status"] = ""
    all_tickets = []

    for status in config.downstream_statuses[:-1]:
        age_column_name = status + " age"
        move_column_name = status + " moves"
        
        items_that_status = len(df_aging[df_aging["status"] == status])
        
        # at least 25 tickets moved to that state, and one ticket to show in the chart
        if items_that_status != 0:
            df_aging_status = df_aging[df_aging["status"] == status]
            if len(df_aging[df_aging[move_column_name] > 0]) > 25:
                mean_value = df_aging[age_column_name].mean()
                std_value = df_aging[age_column_name].std()
            else:
                mean_value = df_aging[age_column_name].max()
                std_value = 0.1
            
            for key, age in df_aging_status[["Key", age_column_name]].itertuples(index=False):
                one_ticket = OneTicket(mean_value, std_value, age, key, status, items_that_status)
                all_tickets.append(one_ticket)
        # if len(df_aging[df_aging[move_column_name] > 0]) > 25 and \
        #         items_that_status != 0:
        #     df_aging_status = df_aging[df_aging["status"] == status]
            
        #     mean_value = df_aging[age_column_name].mean()
        #     std_value = df_aging[age_column_name].std()    
            
        #     for key, age in df_aging_status[["Key", age_column_name]].itertuples(index=False):
        #         one_ticket = OneTicket(mean_value, std_value, age, key, status, items_that_status)
        #         all_tickets.append(one_ticket)

    chart_title = texts.spc_aging_chart_title.format(status, config.project_name)
    one_spc_chart(final_result, all_tickets, chart_title, \
                  texts.spc_aging_chart_x, texts.spc_aging_chart_y)

##########################################################################
# one chart per status
def chart_spc(final_result, df, df_aging, status, column_name, filename, chart_title, \
              spc_chart_x_aging, spc_chart_y_aging):
    df_aging_status = df_aging[df_aging["status"] == status]
    if len(df_aging_status) == 0:
        return

    bar_width = 1
    
    plt.clf()
    original_figsize = plt.rcParams["figure.figsize"]
    if len(df_aging_status) > 4:
        plt.rcParams["figure.figsize"] = [len(df_aging_status), 4.8] 
        plt.rcParams["figure.autolayout"] = True
    fig, ax = plt.subplots()
    ax.set_xlim(1, (len(df_aging_status) * bar_width) - 1, auto=True)
    
    if len(df_aging[df_aging[status + " moves"] > 0]) > 25:
        mean_value = df_aging[column_name].mean()
        std_throughput = df_aging[column_name].std()    
        upper_limit3 = mean_value + 3 * std_throughput
        upper_limit2 = mean_value + 2 * std_throughput
        upper_limit1 = mean_value + 1 * std_throughput
        limit_to_show_in_gray = 0
    else:
        mean_value = df_aging[column_name].mean()
        limit_to_show_in_gray = upper_limit3 = upper_limit2 = \
            upper_limit1 = max(df_aging[column_name]) + 1

    labels = []
    x_pos = 0
    for key, age in df_aging_status[["Key", column_name]].itertuples(index=False):
        # age = df_aging[df_aging["Key"] == key][column_name].iat[0]
        
        if age < limit_to_show_in_gray:
            color = "gray"
        elif age < upper_limit1:
            color = "green"
        elif age < upper_limit2:
            color = "orange"
        elif age < upper_limit3:
            color = "red"
        else:
            color = "purple"
            
        ax.bar(x_pos, age, color=color)
        ax.text(x_pos, age, "{:.0f}".format(age), 
            color = 'black')
        x_pos += bar_width
        labels.append(key) #.replace("-", "\n"))
        
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels)
    ax.tick_params(axis='x', labelrotation=90)

    ax.axhline(y=mean_value, color='lightgray', linestyle='--', label="média")
    if limit_to_show_in_gray == 0:
        ax.axhline(y=upper_limit1, color='green', linestyle='--', label="ok")
        ax.axhline(y=upper_limit2, color='orange', linestyle='--', label="atenção")
        ax.axhline(y=upper_limit3, color='red', linestyle='--', label="crítico")

    ax.legend()
    
    ax.set_title(chart_title)
    ax.set_xlabel(spc_chart_x_aging)
    ax.set_ylabel(spc_chart_y_aging)

    plt.tight_layout(w_pad = 2.0)

    image_file_name = final_result.temp_dir + filename
    plt.savefig(image_file_name)
    final_result.all_files.add(image_file_name)

    plt.rcParams["figure.figsize"] = original_figsize # restore size for others charts
    
# SPC para aging para cada estado de downstream
def aging_status_spc_analysis(final_result, config, all_issues, df):
    result = texts.aging_title
    
    if "df_aging" in vars(final_result):
        df_aging = final_result.df_aging
    else:
        fr = copy.deepcopy(final_result)
        df_aging = total_aging.total_aging(fr, all_issues, config)

    if "one_chart_aging_spc" in config.which_analysis:
        for status in config.downstream_statuses[:-1]:
            for key in df[df["status"] == status]["Key"]:
                df_aging.loc[df_aging["Key"] == key, "status"] = status
        aging_status_spc_analysis_all_together(final_result, config, all_issues, df_aging)
        result += '<img src="one_spc_aging.png"/><br/>'
        final_result.text_result["aging"] = result
        return 
    
    df_aging["status"] = ""
    
    for status in config.downstream_statuses[:-1]:
        column_name = status + " age"
        
        df_aging = df_aging.sort_values(by=column_name)
        
        for key in df[df["status"] == status]["Key"]:
            df_aging.loc[df_aging["Key"] == key, "status"] = status
            print(status)
        
        filename = "spc_aging_{}.png".format(status)
        chart_title = texts.spc_aging_chart_title.format(status, config.project_name)
        
        chart_spc(final_result, df, df_aging, status, column_name, filename, 
                  chart_title, texts.spc_aging_chart_x, texts.spc_aging_chart_y)
        result += f'<img src="{filename}"/><br/>'
    
    final_result.text_result["aging"] = result
