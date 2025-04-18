import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

import texts, coach_matic_base

def get_tendency(any_list):
    weeks_num = [i for i in range(0, len(any_list))]
    x = np.array([weeks_num, any_list])
    res = stats.linregress(x)
    x_trend = list(map(lambda a: res.intercept + res.slope*a, any_list))
    x_trend = res.slope*np.array(weeks_num) + res.intercept
    # on first day of the week we will have to few hours. Getting tendency on
    # last two weeks
    tendency = 1 - (x_trend[0] / max(x_trend[-1], x_trend[-2]))
    
    return tendency

####################################################################
# sum of effort per state
def effort_who(all_issues):
    all_display_names = {}
    for issue in all_issues:
        if "worklog" not in vars(issue.fields):
            continue
        for worklog in issue.fields.worklog.worklogs:
            author = f"{worklog.author.displayName} ({worklog.author.key})"
            if author not in all_display_names:
                all_display_names[author] = set()
            all_display_names[author].add(issue.fields.issuetype.name)

    result = texts.effort_who
    names_ordered = list(all_display_names.keys())
    names_ordered.sort()
    for name in names_ordered:
        result += "- {}: {}<br/>".format(name, ", ".join(all_display_names[name]))
    return "<br/>" + result + "<br/>"

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
    with open(csv_file_name, "w", encoding="UTF-8") as f:
        f.write("issue\t" + "\t".join(config.export_csv_add_fields) + "\t" + \
                "\t".join(config.all_statuses) + "\t?\n")
        for issue in sum_per_issue:
            f.write(f"{issue}\t")
            
            added_fields = df[df["Key"] == issue][config.export_csv_add_fields]
            if len(added_fields) >= 1:
                values_added = list(added_fields.iloc[0])
                for i in range(len(config.export_csv_add_fields)):
                    v = values_added[i]
                    if type(v) == int or type(v) == float or \
                            type(v) == np.float64:
                        v = "{:.2f}".format(v).replace(".", ",")
                    f.write(f"{v}\t")
            else:
                for i in range(len(config.export_csv_add_fields)):
                    f.write("-\t")
                
            for status in config.all_statuses + ["?"]:
                effort_h = sum_per_issue[issue][status] / (60*60) if status in sum_per_issue[issue] else 0
                f.write("{:.2f}\t".format(effort_h).replace(".", ","))
            f.write("\n")
    final_result.all_files.add(csv_file_name)
    
    return ""

####################################################################
# sum of effort per issuetype
def effort_per_issuetype(final_result, config, all_issues, df):
    df[config.effort_axis_friendly] = np.where(df[config.effort_axis_friendly] == "", \
                                                0, \
                                                df[config.effort_axis_friendly])
    df[config.effort_axis_friendly] = df[config.effort_axis_friendly].astype("int")
    df_sum = df.groupby(by="issuetype")[config.effort_axis_friendly].sum()
    df_sum_dict = df_sum.to_dict()

    total_hours = df[config.effort_axis_friendly].sum()
    per_issuetype = []
    for issuetype in df_sum_dict:    
        time_spent_hours = "{:.2f}h".format(df_sum_dict[issuetype] / (1*1))
        percent = (df_sum_dict[issuetype] / total_hours) * 100
        per_issuetype.append("{}: {} ({:.2f}%)".format(issuetype, 
                                                   time_spent_hours,
                                                   percent))

    result = texts.effort_issuetype.format(config.effort_axis_friendly,
                                           ", ".join(per_issuetype))

    return result

####################################################################
# effort analysis
def effort_tendency(all_issues):
    effort_per_week = {}

    dt = datetime.now()
    one_week = timedelta(days=7)
    for w in range(4 * 3): # 21 weeks,
        effort_per_week[dt.strftime("%V-%Y")] = 0
        dt = dt - one_week
        
    for issue in all_issues:
        if "worklog" not in vars(issue.fields):
            continue
        for worklog in issue.fields.worklog.worklogs:
            created_str = worklog.created[0:10]
            created = datetime.strptime(created_str, "%Y-%m-%d")
            week_year = created.strftime("%V-%Y")
            
            if week_year in effort_per_week:
                effort_per_week[week_year] += worklog.timeSpentSeconds
                           
    weeks_num = [i for i in range(0, len(effort_per_week))]
    effort_week = list(effort_per_week.values())
    effort_week.reverse()
    x = np.array([weeks_num, effort_week])
    res = stats.linregress(x)
    x_trend = list(map(lambda a: res.intercept + res.slope*a, effort_week))
    x_trend = res.slope*np.array(weeks_num) + res.intercept
    # on first day of the week we will have to few hours. Getting tendency on
    # last two weeks
    tendency = 1 - (x_trend[0] / max(x_trend[-1], x_trend[-2]))
    
    return texts.effort_tendency.format(tendency * 100)
                
def effort_sum(final_result, config, all_issues, df):
    total_sum = 0
    sum_per_issue = {}
    issues_with_spenttime_not_zero = 0
    
    for key, effort in df[["Key", config.effort_axis_friendly]].itertuples(index=False):
        try:
            effort_h = effort / (1*1)
        except:
            effort_h = 0
        sum_per_issue[key] = effort_h
        total_sum += effort_h
        issues_with_spenttime_not_zero += 1 if effort_h > 0 else 0

    average_per_issue = total_sum / issues_with_spenttime_not_zero if issues_with_spenttime_not_zero != 0 else 0
        
    keys = list(sum_per_issue.keys())
    values = list(sum_per_issue.values())
    position_outliers = coach_matic_base.calculate_outliers(values)
    outliers_str = []
    for pos in position_outliers:
        pct_hours = (values[pos] / total_sum) * 100
        time_spent_hours = "{:.2f}h ({:.2f}%)".format(values[pos], pct_hours)
        outliers_str.append(f"<a href=\"{config.jira_url}/browse/{keys[pos]}\">{keys[pos]}</a>: {time_spent_hours}")
    
    result = texts.effort_total_sum.format(total_sum)
    result += texts.effort_average.format(average_per_issue, issues_with_spenttime_not_zero)
    if len(outliers_str) > 0:
        result += texts.effort_outliers.format(",".join(outliers_str))
    else:
        result += texts.effort_no_outliers
        
    return result

####################################################################
# methods for effort vs throughput
def chart_throughput_effort(final_result, config, week_days, weekly_throughput, weekly_effort):
    plt.clf()

    x = [i for i in range(len(week_days))]
    max_throughput = max(weekly_throughput)
    if max_throughput != 0:
        y1 = [t / max_throughput for t in weekly_throughput]
    else:
        y1 = [0 for t in weekly_throughput]
    max_effort = max(weekly_effort)
    if max_effort != 0:
        y2 = [e / max_effort for e in weekly_effort]
    else:
        y2 = [0 for e in weekly_effort]
    
    labels = [d.strftime("%Y-%m-%d") for d in week_days]
    # plt.plot(x, y1, label="Vazão semanal", color='blue')
    # plt.plot(x, y2, label="Esforço semanal", color='orange')
    # You can specify a rotation for the tick
    # labels in degrees or with keywords.
    plt.xticks(x, labels, rotation =45)

    # for yc in range(10, 100, 10):
    #     plt.axhline(y=yc, color='lightgray', linestyle='--')

    # Pad margins so that markers don't get
    # clipped by the axes
    plt.margins(0.2)

    # Tweak spacing to prevent clipping of tick-labels
    plt.subplots_adjust(bottom = 0.15)

    res = stats.linregress(x, y1)
    x_trend = list(map(lambda a: res.intercept + res.slope*a, x))
    plt.plot(x, x_trend, 'r', linestyle='dashed', color='blue',  label='Tendência vazão')
    
    res = stats.linregress(x, y2)
    x_trend = list(map(lambda a: res.intercept + res.slope*a, x))
    plt.plot(x, x_trend, 'r', linestyle='dashed', color='orange',  label='Tendência esforço')
    
    plt.title(texts.effort_chart_title.format(config.project_name))
    plt.xlabel(texts.effort_chart_x)
    plt.ylabel(texts.effort_chart_y)
    plt.legend()

    plt.tight_layout(w_pad = 2.0)

    image_file_name = "throughput_effort.png"
    chart_file_name = final_result.temp_dir + image_file_name
    plt.savefig(chart_file_name)
    final_result.all_files.add(chart_file_name)
    
    result = f'<img src="{image_file_name}"/><br/>'
    return result

def get_weekly_throughput(config, df):
    week_days = []
    weekly_throughput = []
    
    today = datetime.today()
    today = today - timedelta(hours=today.hour, minutes=today.minute,
                              seconds=today.second, microseconds=today.microsecond)
    sunday = today - timedelta(days=datetime.today().isoweekday() % 7)
    less_7_days = timedelta(days = -7)
    for week in range(12, 0, -1): # 12 weeks -> 3 months
        last_sunday = sunday
        sunday  = sunday + less_7_days

        df[(df[config.downstream_stop] <= last_sunday)]
        throughput_week = df[(df[config.downstream_stop] <= last_sunday) & (
            df[config.downstream_stop] > sunday)][config.downstream_stop].count()
    
        week_days.insert(0, last_sunday)
        weekly_throughput.insert(0, throughput_week)
        
    return week_days, weekly_throughput
    
def get_weekly_effort(week_days, all_issues):
    weekly_effort = [0 for i in range(len(week_days))]
    for issue in all_issues:
        if "worklog" not in vars(issue.fields):
            continue
        for worklog in issue.fields.worklog.worklogs:
            created_str = worklog.created[0:10]
            created = datetime.strptime(created_str, "%Y-%m-%d")
            
            for idx in range(len(week_days)):
                start_week = week_days[idx - 1] if idx > 0 else week_days[0] - timedelta(days = 7)
                end_week = week_days[idx]
                if created > start_week and created <= end_week:
                    weekly_effort[idx] += worklog.timeSpentSeconds
                    break

    return weekly_effort

def effort_throughput(final_result, config, all_issues, df):
    week_days, weekly_throughput = get_weekly_throughput(config, df)
    weekly_effort = get_weekly_effort(week_days, all_issues)

    max_throughput = max(weekly_throughput)
    if max_throughput != 0:
        leveled_throughput = [t / max_throughput for t in weekly_throughput]
    else:
        leveled_throughput = [0 for t in weekly_throughput]
    max_effort = max(weekly_effort)
    if max_effort != 0:
        leveled_effort = [e / max_effort for e in weekly_effort]
    else:
        leveled_effort = [0 for e in weekly_effort]

    throughput_tendency = get_tendency(leveled_throughput)
    effort_tendency = get_tendency(leveled_effort)

    result = ""    
    if throughput_tendency - effort_tendency > 0.15:
        result = texts.effort_productivity_more
    elif throughput_tendency - effort_tendency < -0.15:
        result = texts.effort_productivity_less
        
    result += texts.effort_productivity_ratio.format((throughput_tendency - effort_tendency) * 100)
    
    result += chart_throughput_effort(final_result, config, week_days, weekly_throughput, weekly_effort)
    
    return result
    
####################################################################
# effort analysis
def effort_analysis(final_result, config, all_issues, df):
    result = texts.effort_title
    
    result += effort_sum(final_result, config, all_issues, df)
    result += effort_tendency(all_issues)
    
    if config.effort_per_state:
        result += effort_per_status(final_result, config, all_issues, df)
    if config.effort_per_issuetype:
        result += effort_per_issuetype(final_result, config, all_issues, df)
    if config.effort_who:
        result += effort_who(all_issues)
    if config.effort_throughput:
        result += effort_throughput(final_result, config, all_issues, df)
        
    final_result.text_result["effort"] = result
