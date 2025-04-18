import numpy as np
import coach_matic_base

from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
from traceback import extract_tb

def plot_distributions(final_result, all_distributions, axis, most_reported_issuetype):
    plt.clf()

    for calc_type in all_distributions:
        y = [y + 1 for y in range(0, len(all_distributions[calc_type]))]
        plt.plot(y, all_distributions[calc_type], label=calc_type)

    # Pad margins so that markers don't get
    # clipped by the axes
    plt.margins(0.2)

    # Tweak spacing to prevent clipping of tick-labels
    plt.subplots_adjust(bottom = 0.15)
    legend_pseudo = [f"M{i}" for i in range(1, len(all_distributions.keys()) + 1)]
    plt.legend(legend_pseudo, loc="upper left")
    
    plt.xticks(ticks=[1, 2, 3, 4, 5], labels=["PP", "P", "M", "G", "GG"])
    
    plt.title(f"Clusterização {axis} para {most_reported_issuetype}")
    plt.xlabel("T-Shirt")
    plt.ylabel("Horas")
    
    plt.tight_layout(w_pad = 2.0)
        
    image_file_name = f"clusters {axis}.png"
    path_file_name = final_result.temp_dir + image_file_name
    plt.savefig(path_file_name)
    final_result.all_files.add(path_file_name)

    result = f'<img src="{image_file_name}"/><br/>'
    return result

def calc_kmeans(final_result, df, calc_type, sizes, y_axis, most_reported_issuetype):
    distribution = []
    cluster_size = len(sizes)
    
    all_issuetypes = set(df["issuetype"])
    
    html = f"<b>Cluster por {calc_type}</b><br/>" + \
        "<table border=\"1\">" + \
        "<tr><td>Issue type</td><td>" + \
            "</td><td>".join(sizes) + "</td></tr>"

    for issuetype in all_issuetypes:
        html += f"<tr><td>{issuetype}</td>"
        
        df_it = df[df["issuetype"] == issuetype]
        df_it2 = df_it[["cluster axis", y_axis]].copy()
        df_it2['cluster axis'] = df_it2['cluster axis'].apply(convert_to_float).astype('float')
        df_it2[y_axis] = df_it2[y_axis].apply(convert_to_float).astype('float')
        df_it2 = df_it2.dropna()
        
        if len(df_it2) >= cluster_size:
            kmeanModel = KMeans(n_clusters = cluster_size)
            kmeanModel.fit(df_it2)
    
            df_it2['k_means'] = kmeanModel.predict(df_it2)
            
            if y_axis == "cluster axis":
                values = [df_it2[df_it2['k_means'] == k]["cluster axis"].max().iloc[0] for k in range(0, cluster_size)]
            else:
                values = [df_it2[df_it2['k_means'] == k]["cluster axis"].max() for k in range(0, cluster_size)]
            values.sort()
        else:
            values = [0] * cluster_size
        
        for effort in values:
            html += f"<td>{effort:.0f}</td>"
    
        if issuetype == most_reported_issuetype:
            distribution = values
        
    html += "</table><br/>"
    
    return html, distribution
    
def calc_percentil(final_result, df, calc_type, sizes, quantiles, most_reported_issuetype, unique=False):
    html = f"<b>Cluster por {calc_type}</b><br/>"
    distribution = []
    
    all_issuetypes = set(df["issuetype"])
    
    html += "<table border=\"1\">" + \
        "<tr><td>Issue type</td><td>" + \
            "</td><td>".join(sizes) + "</td></tr>"

    for issuetype in all_issuetypes:
        html += f"<tr><td>{issuetype}</td>"
        
        df_it = df[df["issuetype"] == issuetype]
        if unique:
            efforts = np.array(df_it["cluster axis"].unique())
        else:
            efforts = np.array(df_it["cluster axis"])
        
        for this_quantile in quantiles:
            html += f"<td>{np.quantile(efforts, this_quantile / 100):.0f}</td>"
        
        if issuetype == most_reported_issuetype:
            distribution = [np.quantile(efforts, this_quantile / 100) for this_quantile in quantiles]
                
    html += "</table><br/>"
    
    return html, distribution
    
def calc_all_methods(final_result, config, axis, df, most_reported_issuetype):
    all_distributions = {}
    m_code = 1
    html = ""

    ############################
    for num_clusters in range(3, 6):
        calc_type = f"{axis} Percentil Linear - {num_clusters} clusters (M{m_code})"
        sizes = ["PP", "P", "M", "G", "GG"][0:num_clusters]
        quantile_increment = int((1 / num_clusters) * 100)
        quantiles = [quantile_increment * i for i in range(1, len(sizes) + 1)]
        new_html, distribution = calc_percentil(final_result, df, calc_type, sizes, \
                                                quantiles, most_reported_issuetype)
        html += new_html
        all_distributions[calc_type] = distribution
        m_code += 1

    ############################
    for num_clusters in range(3, 6):
        calc_type = f"{axis} Percentil Linear Valores Unicos - {num_clusters} clusters (M{m_code})"
        sizes = ["PP", "P", "M", "G", "GG"][0:num_clusters]
        quantile_increment = int((1 / num_clusters) * 100)
        quantiles = [quantile_increment * i for i in range(1, len(sizes) + 1)]
        new_html, distribution = calc_percentil(final_result, df, calc_type, sizes, \
                                                quantiles, most_reported_issuetype, unique=True)
        html += new_html
        all_distributions[calc_type] = distribution
        m_code += 1
        
    ############################
    for num_clusters in range(3, 6):
        calc_type = f"{axis} Percentil Exponencial - {num_clusters} clusters (M{m_code})"
        sizes = ["PP", "P", "M", "G", "GG"][0:num_clusters]
        quantiles = [int(100 / pow(2, p)) * 2 for p in range(1, num_clusters + 1)]
        quantiles.reverse()
        new_html, distribution = calc_percentil(final_result, df, calc_type, sizes, \
                                                quantiles, most_reported_issuetype)
        html += new_html
        all_distributions[calc_type] = distribution
        m_code += 1
 
    ############################
    for num_clusters in range(3, 6):
        calc_type = f"{axis} Percentil Exponencial Valores Unicos - {num_clusters} clusters (M{m_code})"
        sizes = ["PP", "P", "M", "G", "GG"][0:num_clusters]
        quantiles = [int(100 / pow(2, p)) * 2 for p in range(1, num_clusters + 1)]
        quantiles.reverse()
        new_html, distribution = calc_percentil(final_result, df, calc_type, sizes, \
                                                quantiles, most_reported_issuetype, unique=True)
        html += new_html
        all_distributions[calc_type] = distribution
        m_code += 1
 
    ############################
    for num_clusters in range(3, 6):
        calc_type = f"{axis} K-means cycletime no eixo Y - {num_clusters} clusters (M{m_code})"
        sizes = ["PP", "P", "M", "G", "GG"][0:num_clusters]
        try:
            new_html, distribution = calc_kmeans(final_result, df, calc_type, sizes, \
                                                 "cluster axis", most_reported_issuetype)
            html += new_html
            all_distributions[calc_type] = distribution
            m_code += 1
        except Exception as e:
            msg = str(e)
            coach_matic_base.print_and_log("Erro na execução: {}".format(msg))
            coach_matic_base.print_and_log(str(extract_tb(e.__traceback__)))
        
    ############################
    for num_clusters in range(3, 6):
        calc_type = f"{axis} K-means effort no eixo Y - {num_clusters} clusters (M{m_code})"
        sizes = ["PP", "P", "M", "G", "GG"][0:num_clusters]
        try:
            new_html, distribution = calc_kmeans(final_result, df, calc_type, sizes, \
                                                 "kmeans axis", most_reported_issuetype)
            html += new_html
            all_distributions[calc_type] = distribution
            m_code += 1
        except Exception as e:
            msg = str(e)
            coach_matic_base.print_and_log("Erro na execução: {}".format(msg))
            coach_matic_base.print_and_log(str(extract_tb(e.__traceback__)))
        
    html = html.replace("<tr>", "<tr style=\"border: 1px border-style: solid none solid none;\">")
    html = html.replace("<td>", "<td style=\"border-style: solid solid none none;\">")

    html += plot_distributions(final_result, all_distributions, axis, most_reported_issuetype)

    final_result.text_result[f"Recluster {axis}"] = html        
    # with open("c:\\temp\\cluster.html", "w", encoding="utf-8") as f:
    #     f.write(html)
    
    return 0

def convert_to_float(val):
    try:
        return float(val)
    except:
        return np.nan

def remove_outliers_and_rename(df, first_column, second_column):
    df2 = df[["issuetype", first_column, second_column]].copy()
    
    df2.rename(columns = {first_column: "cluster axis", second_column: "kmeans axis"}, inplace = True)
    df2['cluster axis'] = df2['cluster axis'].apply(convert_to_float).astype('float')
    df2['kmeans axis'] = df2['kmeans axis'].apply(convert_to_float).astype('float')
    df2 = df2.dropna()
    
    all_issuetypes = set(df["issuetype"])
    for issuetype in all_issuetypes:
        cond1 = df2["issuetype"] == issuetype

        first_outlier = coach_matic_base.first_outlier_value(df2[cond1]["cluster axis"])
        if first_outlier != 0:
            cond2 = df2["cluster axis"] >= first_outlier
            df2 = df2[~(cond1 & cond2)]
            
    return df2
    
def post_process(final_result, config, all_issues, all_subtasks, df):
    df_orig = df   # só enquanto programo... depois apago
    df = df_orig
    
    aggregatetimespent_fieldname = coach_matic_base.get_user_field_name(config, "aggregatetimespent")
    df[aggregatetimespent_fieldname] = df[aggregatetimespent_fieldname].apply(convert_to_float).astype('float')
    df_sum_issuetype = df.groupby(by="issuetype").sum()
    coach_matic_base.print_and_log(f"{df_sum_issuetype.columns}")
    coach_matic_base.print_and_log(f"{config.export_csv_add_fields}")
    df_sum_issuetype = df_sum_issuetype.sort_values(by=aggregatetimespent_fieldname, ascending=False)
    most_reported_issuetype = df_sum_issuetype.index[0]
    
    # removes outliers
    df2 = remove_outliers_and_rename(df, "CycleTime", aggregatetimespent_fieldname)
    calc_all_methods(final_result, config, "Cycletime", df2, most_reported_issuetype)

    # removes outliers
    df2 = remove_outliers_and_rename(df, aggregatetimespent_fieldname, "CycleTime")
    calc_all_methods(final_result, config, "Esforço", df2, most_reported_issuetype)
    
