####################################################################
# tail analysis based on KMM formula and its outliers
import pandas as pd
import numpy as np
from scipy import stats
from datetime import datetime
import copy

import texts, total_aging

tail_idx_reference = 5.6

####################################################################
# tendency analysis
def get_amplite_per_week(config, df):
    df2 = (df[["TailAnalysisAxis", config.downstream_stop]]).copy()
    df2 = df2.dropna()
    df2[config.downstream_stop] = pd.to_datetime(df2[config.downstream_stop])
    
    range_of_weeks = 10
    today = datetime.now()
    weekly_cycle_time = [0] * range_of_weeks
    weekly_amplitude = [0] * range_of_weeks
    
    for week in range(range_of_weeks):
        weekly_cycle_time[week] = []
        
    for cycle_time, end_downstream_dt in df2[["TailAnalysisAxis", config.downstream_stop]].itertuples(index=False):
        if type(end_downstream_dt) != pd._libs.tslibs.timestamps.Timestamp:
            continue
            
        diff_days = (today - end_downstream_dt).days
        diff_weeks = (range_of_weeks - int(diff_days / 7)) - 1
        if diff_weeks >= 0:
            weekly_cycle_time[diff_weeks].append(cycle_time)
            
    for week in range(range_of_weeks):
        if len(weekly_cycle_time[week]) > 0:
            min_cycle_time = min(weekly_cycle_time[week])
            max_cycle_time = max(weekly_cycle_time[week])
        else:
            min_cycle_time = 0
            max_cycle_time = 0
        weekly_amplitude[week] = max_cycle_time - min_cycle_time

    return weekly_amplitude
        
def tail_tendency(final_result, config, df_downstream):
    weekly_amplitude = get_amplite_per_week(config, df_downstream)
    weeks_num = [i for i in range(0, len(weekly_amplitude))]
    res = stats.linregress(weekly_amplitude, weeks_num)
    x_trend = list(map(lambda a: res.intercept + res.slope*a, weekly_amplitude))
    tendency = x_trend[0] / x_trend[-1]
    
    if tendency < 0.7:
        return texts.tail_analysis_amplitude_decreasing.format(tendency * 100)
    elif tendency < 1.3:
        return texts.tail_analysis_amplitude_increasing.format(tendency * 100)
        
####################################################################
# check if thin tail
def calculate_tail_idx(final_result, df):
    df_ta = df.copy()
    df_ta = df_ta.dropna(subset=["TailAnalysisAxis"])

    cicle_times = df_ta["TailAnalysisAxis"].values
    if len(cicle_times) > 0:
        cicle_time_pct98 = np.percentile(cicle_times, 98, interpolation="lower")
    else:
        cicle_time_pct98 = 0

    median = df_ta["TailAnalysisAxis"].median() 
    median = max(1, median)

    tail_idx = cicle_time_pct98 / median

    final_result.cicle_time_pct98 = cicle_time_pct98
    final_result.tail_idx = tail_idx
    final_result.is_thin_tail = tail_idx <= tail_idx_reference

    return final_result, df_ta

def look_for_end_of_tail(final_result, df, keys_on_tail, end_tail_cycle_time=0):
    # keys_on_tail = []
    df_ta = df.copy()
    df_ta = df_ta.dropna(subset=["TailAnalysisAxis"])

    max_cycle_time = df_ta["TailAnalysisAxis"].max()
    df_ta[df_ta["TailAnalysisAxis"] == max_cycle_time]["Key"].tolist()
    keys_on_tail += df_ta[df_ta["TailAnalysisAxis"] == max_cycle_time]["Key"].tolist()

    if end_tail_cycle_time == 0:
        end_tail_cycle_time = max_cycle_time
        
    # sets max TailAnalysisAxis no second max    
    df_ta = df_ta[df_ta["TailAnalysisAxis"] != max_cycle_time].copy() # drop those with max cycle
    
    final_result, df_tail = calculate_tail_idx(final_result, df_ta)
    
    if not final_result.is_thin_tail:
        return look_for_end_of_tail(final_result, df_ta, keys_on_tail, end_tail_cycle_time)
    else:
        second_max_cycle_time = df_ta["TailAnalysisAxis"].max()
        return texts.tail_analysis_find.format(second_max_cycle_time,
                 end_tail_cycle_time, ", ".join(keys_on_tail))
        
def tail_analysis(final_result, config, all_issues, df):
    if config.tail_analysis_axis == "CycleTime":
        df["TailAnalysisAxis"] = df["CycleTime"]
        df_ta = df
    elif config.tail_analysis_axis == "TotalAge":
        if "df_aging" in vars(final_result): # did we already ran totalage?
            df_ta = final_result.df_aging
        else:
            fr = copy.deepcopy(final_result)
            df_ta = total_aging.total_aging(fr, all_issues, config)
        df_ta["TailAnalysisAxis"] = df_ta["CycleTime"]
        
        for exc in config.tail_analysis_exclude.split(","):
            exc = exc.strip().lower()
            df_ta["TailAnalysisAxis"] -= df_ta[exc + " age"]
        
    result = texts.tail_analysis_title
    
    final_result, df_tail = calculate_tail_idx(final_result, df_ta)

    if final_result.is_thin_tail:
        result += texts.tail_analysis_thin_tail.format(
            final_result.tail_idx)
    else:
        result += texts.tail_analysis_fat_tail.format(
            final_result.tail_idx)

    # is it possible to identify tail offensor? 
    if not final_result.is_thin_tail:
        result += look_for_end_of_tail(final_result, df_ta, keys_on_tail=[])
        
        # TODO: add tail offensors...
        # final_result = analysis_on_tail(final_result, df_tail, pct=98)
        # if final_result.is_thin_tail:  # seems feasible to have a thin tail
        #     final_result = check_tail_offensors(
        #         final_result, config.all_statuses, config.waiting_statuses, df_tail)

    # avoiding verbosity on tail tendency for ALL situations
    if final_result.tail_idx > tail_idx_reference * 0.75:
        result += tail_tendency(final_result, config, df_ta)
    
    final_result.text_result["tail_analysis"] = result

    return final_result

