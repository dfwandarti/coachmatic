import pandas as pd
import numpy as np

def export_csv(final_result, config, df):
    df["link"] = "{}/browse/".format(config.jira_url)
    df["link"] = df["link"] + df["Key"]
    
    # Key and columns with dates first. Others later
    first_columns = ["Key", "link", "title"] + config.all_statuses
    other_columns = []
    for col in df.columns:
        if col not in first_columns:
            other_columns.append(col)
    
    
    df2 = df[first_columns + other_columns]
    df2.rename(columns = {'Key':'ID'}, inplace = True)
    if type(final_result.df_blockers) == pd.core.frame.DataFrame:
        df2["blocked days"] = 0
        for key, blocked_days in final_result.df_blockers.groupby(by="Key")["blocked days"].sum().iteritems():
            df2["blocked days"] = np.where(df2["ID"] == key,
                                           blocked_days,
                                           df2["blocked days"])
    
    file_name_temp = config.project_name.replace("/", "-").replace("\\", "-")
    file_name = final_result.temp_dir + file_name_temp + ".csv"
    df2.to_csv(file_name, sep=",", encoding="utf-8", index=False)
    final_result.all_files.add(file_name)

    final_result.df_result["export_csv"] = df2.copy()
