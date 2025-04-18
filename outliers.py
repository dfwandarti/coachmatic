#################################################################
# calculate outliers for every state by z-score
import pandas as pd
import numpy as np

#################################################################
# return which rows are outliers based on column
def get_outliers(df, column):
    df2 = df[["Key", column]].copy()
    
    column_z_score = column + " Z Score"
    mean = df2[column].mean()
    std_dev = df2[column].std()
    if std_dev != 0:
        df2[column_z_score] = (df2[column] - mean) / std_dev
    else:
        df2[column_z_score] = 0
        
    df_outliers = df2[(df2[column_z_score] <= -3) |
                                (df2[column_z_score] >= 3)]

    df_outliers = df_outliers.sort_values(by=column_z_score, ascending=False)
    
    return df_outliers

# #################################################################
# # ??
# def calculate_outliers(final_result, df_downstream, column, status_user_friendly):
#     column_z_score = column + " Z Score"
#     cycle_time_mean = df_downstream[column].mean()
#     cycle_time_std_dev = df_downstream[column].std()
#     df_downstream[column_z_score] = (
#         df_downstream[column] - cycle_time_mean) / cycle_time_std_dev
#     df_outliers = df_downstream[(df_downstream[column_z_score] <= -3) |
#                                 (df_downstream[column_z_score] >= 3)]
#     if len(df_outliers) == 0:
#         final_result.outliers_analysis_result  += texts.outliers_not_found.format(
#             status_user_friendly)
#     else:
#         outliers = []
#         for key in df_outliers["Key"]:
#             num_days = df_downstream[df_downstream["Key"]
#                                      == key][column].iloc[0]
#             outliers.append("{}({} {})".format(key, num_days, texts.outliers_days))
#         final_result.outliers_analysis_result  += texts.outliers_found.format(
#             status_user_friendly, ", ".join(outliers))

#     return final_result

# def outliers_analysis(final_result, df_downstream):
#     # TODO: este é o melhor lugar para calcular?
#     analisa_base.calculate_days_per_status(config.all_statuses, df_downstream)
#     final_result.outliers_analysis_result  += texts.outliers_title
#     final_result = calculate_outliers(
#         final_result, df_downstream, "CycleTime", "Whole Downstream")
    
#     for status in config.downstream_statuses:
#         status_days = status + texts.outliers_days
#         if status_days in df_downstream.columns:
#             final_result = calculate_outliers(
#                 final_result, df_downstream, status_days, status)

#     final_result.outliers_analysis_result  += texts.separator
    
#     return final_result
