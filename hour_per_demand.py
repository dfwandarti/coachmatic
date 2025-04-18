import pandas as pd
import numpy as np
from datetime import datetime
import coach_matic_base

#########################
# handle export_csv to summarize hours per OS and subtasks types

def cpi_spi_color(index):
    if index < 0: # means there is no cpi/spi
        return "white"
    if index < 0.5:
        return "purple"
    if index < 0.95:
        return "red"
    if index <= 1.05:
        return "yellow"
    else:
        return "green"
    
# return negative cpi/spi if something wrong. Zero means it is really bad
def calc_cost_and_sched_variation(total_estimated, reported, pct_done, start_date, expected_date):
    try:
        total_days = (expected_date - start_date).days
        days_from_start = (datetime.now() - start_date).days
        pct_days_from_start = days_from_start / total_days
        
        pv = total_estimated * pct_days_from_start
        ac = reported
        ev = total_estimated * (pct_done / 100)
        
        # CPI = Earned Value / Actual Cost
        # SPI = Earned Value / Planned Value
        cpi = ev / ac if ac != 0 else -1
        spi = ev / pv if pv != 0 else -1
    
        return cpi, spi, start_date.strftime("%d-%m-%Y"), expected_date.strftime("%d-%m-%Y")
    except:
        try:
            return -1, -1, "-", expected_date.strftime("%d-%m-%Y")
        except:
            return -1, -1, "-", "-"
    
    
def summary_hours(final_result, config, all_issues, all_subtasks, df_export, df_sum):
    html = "<table style=\"border:1px solid\">" + \
          "<tr><td>Demanda</td><td>Resumo</td><td>Situação</td><td>OS com subtarefas</td><td>Orçamento<br/>Técnico<br/>Total</td><td>" + \
          "Reportado</td><td>% Reportado/Orçado</td><td>% tarefas<br/>fábrica completadas</td>" + \
          "<td>Cost Variance</td><td>Sched Variance</td>" + \
          "<td>Data início/fim</td></tr>"
    for k, v in df_sum.items():
        demand_key = k[0]
        demand_summary = k[1]
        demand_status = k[2]
        demand_total_estimation = k[3]
        
        try:
            start_date = df_export[(df_export["jql:Chave"] == demand_key) &
                      (df_export["issuetype"] == "Tarefa de Fábrica")]["in progress"].min()
            expected_date = df_export[(df_export["jql:Chave"] == demand_key)].iloc[0]["jql:Data para Ficar Pronto"]
        except:
            start_date = None
            expected_date = None
        
        pct_estimated_spent = (v / demand_total_estimation)*100 \
               if demand_total_estimation != 0 and type(demand_total_estimation) == float \
               else 0
        
        types_subtasks = ["Tarefa de Fábrica", "Teste (Alfa)", "Bug de Alfa", "Análise Desenvolvimento"]
        tasks_not_done = len(df_export[(df_export["jql:Chave"] == demand_key) & \
                                    (df_export["issuetype"].isin(types_subtasks)) &
                                   ((df_export["status"] != "cancelado") & \
                                    (df_export["status"] != "done"))])
        tasks_done = len(df_export[(df_export["jql:Chave"] == demand_key) & \
                                   (df_export["issuetype"].isin(types_subtasks)) &
                                   ((df_export["status"] == "cancelado") | \
                                    (df_export["status"] == "done"))])
        total_tasks = tasks_done + tasks_not_done
        pct_done = (tasks_done / total_tasks) * 100 if total_tasks != 0 else 0
        
        cpi, spi, d1, d2 = calc_cost_and_sched_variation(demand_total_estimation, v, pct_done, \
                                                 start_date, expected_date)

        os_list = set(df_export[df_export["jql:Chave"] == demand_key]["pai.Chave"])
        pai_fechado = lambda pai_chave: len(df_export[(df_export["pai.Chave"] == pai_chave) &\
                                           (df_export["pai.Situação"].isin(["Fechado", "Cancelado"]))]) > 0
        strike = lambda pai_chave: "<del>"+coach_matic_base.get_link_jira_key(config.jira_url, pai_chave)+"</del>" \
                                   if pai_fechado(pai_chave) else \
                                   coach_matic_base.get_link_jira_key(config.jira_url, pai_chave)
        os_list_html = [strike(pai_chave) for pai_chave in os_list]
        os_list_html = [element + ("<br/>" if element in os_list_html[2::2] else "") for element in os_list_html]
        
        cpi_str = f"{cpi:.2f}\t".replace(".", ",") if cpi >= 0 else ""
        spi_str = f"{spi:.2f}\t".replace(".", ",") if spi >= 0 else ""
            
        html += "<tr>"
        html += "<td>{}</td>".format(coach_matic_base.get_link_jira_key(config.jira_url, demand_key))
        html += "<td>{}</td>".format(demand_summary)
        html += "<td>{}</td>".format(demand_status)
        html += "<td>{}</td>".format("/".join(os_list_html))
        html += "<td><font color=\"{}\">{:.2f}</font></td>".format("red" if demand_total_estimation == 0.0 else "black", demand_total_estimation)
        html += "<td><font color=\"{}\">{:.2f}</font></td>".format("red" if v == 0.0 else "black", v)
        html += "<td>{:.2f}%</td>".format(pct_estimated_spent)
        html += "<td>{}/{}: {:.2f}%</td>".format(tasks_done, total_tasks, pct_done)
        html += "<td>{} <p style=""background-color:{}"">&nbsp;&nbsp;</p></td>".format(cpi_str, cpi_spi_color(cpi))
        html += "<td>{} <p style=""background-color:{}"">&nbsp;&nbsp;</p></td>".format(spi_str, cpi_spi_color(spi))
        html += f"<td><font color=\"{'red' if d1 == '-' else 'black'}\">{d1} a {d2}</font></td>"
        html += "</tr>"
    html += "</table></br></br>"
    
    all_texts = ["adiantado", "em dia", "atrasado", "muito atrasado"]
    all_values = [1.5, 1, 0.8, 0.4]
    for text, value in zip(all_texts, all_values):
        html += "Cost/Sched Variance {}: <font style=\"background-color:{}\">&nbsp;&nbsp;</font><br/>".format(text, cpi_spi_color(value))

    html = html.replace("<tr>", "<tr style=\"border:1px solid\">")
    html = html.replace("<td>", "<td style=\"border:1px solid\">")
    
    final_result.text_result["Follow up Demandas"] = html
    return html

def csv_demand_issuetype(final_result, config, all_issues, all_subtasks, df_export, df_sum):
    all_issue_types = list(set(df_export["issuetype"]))
    all_issue_types.sort()
    out = "Demanda\tResumo\tSituação\tOS com subtarefas\tOrçamento Técnico Total\t" + \
          "Reportado\t% Reportado/Orçado\t% tarefas fábrica completadas\t" + \
          "Cost Variance\tSched Variance\tData Início\tData Fim\t" + \
          "\t".join(all_issue_types) + "\n"

    for k, v in df_sum.items():
        demand_key = k[0]
        demand_summary = k[1]
        demand_status = k[2]
        demand_total_estimation = k[3]
        
        try:
            start_date = df_export[(df_export["jql:Chave"] == demand_key) &
                      (df_export["issuetype"] == "Tarefa de Fábrica")]["in progress"].min()
            expected_date = df_export[(df_export["jql:Chave"] == demand_key)].iloc[0]["jql:Data para Ficar Pronto"]
        except:
            start_date = None
            expected_date = None
        
        pct_estimated_spent = (v / demand_total_estimation)*100 \
               if demand_total_estimation != 0 and type(demand_total_estimation) == float \
               else 0
        
        types_subtasks = ["Tarefa de Fábrica", "Teste (Alfa)", "Bug de Alfa", "Análise Desenvolvimento"]
        tasks_not_done = len(df_export[(df_export["jql:Chave"] == demand_key) & \
                                   (df_export["issuetype"].isin(types_subtasks)) &
                                   ((df_export["status"] != "cancelado") & \
                                    (df_export["status"] != "done"))])
        tasks_done = len(df_export[(df_export["jql:Chave"] == demand_key) & \
                                   (df_export["issuetype"].isin(types_subtasks)) &
                                   ((df_export["status"] == "cancelado") | \
                                    (df_export["status"] == "done"))])
        total_tasks = tasks_done + tasks_not_done
        pct_done = (tasks_done / total_tasks) * 100 if total_tasks != 0 else 0
        
        cpi, spi, d1, d2 = calc_cost_and_sched_variation(demand_total_estimation, v, pct_done, \
                                                 start_date, expected_date)
        
        os_list = set(df_export[df_export["jql:Chave"] == demand_key]["pai.Chave"])
        
        cpi_str = f"{cpi:.2f}\t".replace(".", ",") if cpi >= 0 else "\t"
        spi_str = f"{spi:.2f}\t".replace(".", ",") if spi >= 0 else "\t"
        out += f"{demand_key}\t" + \
               f"{demand_summary}\t" + \
               f"{demand_status}\t" + \
               f"{'/'.join(os_list)}\t" + \
               f"{demand_total_estimation:.2f}\t".replace(".", ",") + \
               f"{v:.2f}\t".replace(".", ",") + \
               f"{pct_estimated_spent:.2f}%\t".replace(".", ",") + \
               f"{tasks_done}/{total_tasks}: {pct_done:.0f}%\t" + \
               cpi_str + \
               spi_str + \
               f"{d1}\t" + \
               f"{d2}\t"
        
        for issue_type in all_issue_types:
            df_temp = df_export[(df_export["jql:Chave"] == demand_key) & 
                                (df_export["issuetype"] == issue_type)]
            total_hours_issue_type = df_temp["Σ Tempo Gasto"].sum()
            out += f"{total_hours_issue_type:.2f}\t".replace(".", ",")
        out += "\n"
    
    image_file_name = final_result.temp_dir + "horas_demanda.csv"
    
    with open(image_file_name, "w", encoding="UTF-8") as f:
        f.write(out)
    final_result.all_files.add(image_file_name)

def post_process(final_result, config, all_issues, all_subtasks, df):
    df_export = final_result.df_result["export_csv"]

    df_export["issuetype"] = df["issuetype"].astype("string")
    df_export["Σ Tempo Gasto"] = df["Σ Tempo Gasto"].astype("int")
    df_export["jql:Situação"] = df["jql:Situação"].astype("string")
    df_export["in progress"] =  pd.to_datetime(df_export['in progress'])
    df_export["jql:Data para Ficar Pronto"] =  pd.to_datetime(df_export['jql:Data para Ficar Pronto'])
    df_export["jql:Orçamento Técnico Total"] = np.where(df_export["jql:Orçamento Técnico Total"].isnull(),
                                                0,
                                                df_export["jql:Orçamento Técnico Total"])
    
    
    df_sum = df_export.groupby(["jql:Chave", "jql:Resumo", "jql:Situação", \
                                "jql:Orçamento Técnico Total"])["Σ Tempo Gasto"].sum()

    html = summary_hours(final_result, config, all_issues, all_subtasks, df_export, df_sum)
    csv_demand_issuetype(final_result, config, all_issues, all_subtasks, df_export, df_sum)
