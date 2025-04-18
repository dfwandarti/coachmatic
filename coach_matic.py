from traceback import extract_tb
from jira import JIRA
import os, re, copy, uuid, importlib


import export_csv, total_aging, bag_words, bloquers, cfd, spc, weekly_transitions
import coach_matic_base, spc_aging, texts, discriminated_throughput, tail_analysis
import send_email, effort, pct_ca, recluster

class FinalResult:
    text_result = {}    
    df_result = {}    
    all_files = set()
    if os.name == "nt":
        temp_dir = "temp\\one\\"
    else:
        temp_dir = "temp/one/"
    uuid = ""
    df_blockers = None
    
    def __init__(self):
        self.text_result = dict().copy()
        self.all_files = set().copy() # TODO: we should not need copy()...

class Config:
    jira_conn = None
    detailing_per_field = False
    language = "PT"
    project_name = ""
    jira_url = ""
    jira_user = ""
    jira_key = ""
    jql = ""
    extract_jira_zip = None
    all_statuses = []
    all_sub_statuses = []
    downstream_start = ""
    downstream_stop = ""
    downstream_statuses = []
    waiting_statuses = []
    receiver_email = ""

    schedule_day = ""
    
    repeat_for_each_field_value = ""
    export_csv_add_fields = []
    export_csv_add_fields_custom = []
    expot_csv_jql_fields = []
    
    total_age_percentil = False

    bag_of_words_axis = ""    
    bag_of_words_axis_friendly = ""    
    bag_of_words_exclude = ""
    subjql = ""
    
    blocker_days = 30
    blocker_field = ""
    blocker_field_description = ""

    cfd_days = 90
    wip_evolution_chart = False
    
    spc_time_window = 1
    
    discriminated_throughput_field = ""
    discriminated_throughput_creation = False
    
    tail_analysis_axis = "CycleTime"
    tail_analysis_exclude = ""
    
    effort_axis = ""
    effort_axis_friendly = ""
    effort_per_state = False
    effort_per_issuetype = False
    effort_who = False
    effort_throughput = False
    
    which_analysis = []
    expand_worklog = False
    
    user_pct_ca = ""
    count_bugs_jql = ""
    
    post_processing_modules = ""
    
    def __init__(self):
        self.jira_conn = None
        self.detailing_per_field = False
        self.language = "PT"
        self.project_name = ""
        self.jira_url = ""
        self.jira_user = ""
        self.jira_key = ""
        self.jql = ""
        self.extract_jira_zip = None
        self.all_statuses = []
        self.all_sub_statuses = []
        self.downstream_start = ""
        self.downstream_stop = ""
        self.downstream_statuses = []
        self.waiting_statuses = []
        self.receiver_email = ""
        self.schedule_day = ""
        self.repeat_for_each_field_value = ""
        self.export_csv_add_fields = []
        self.export_csv_add_fields_custom = []
        self.expot_csv_jql_fields = []
        self.total_age_percentil = False
        self.bag_of_words_axis = ""    
        self.bag_of_words_axis_friendly = ""    
        self.bag_of_words_exclude = ""
        self.subjql = ""
        self.blocker_days = 30
        self.blocker_field = ""
        self.blocker_field_description = ""
        self.cfd_days = 90
        self.wip_evolution_chart = False
        self.spc_time_window = 1
        self.discriminated_throughput_field = ""
        self.discriminated_throughput_creation = False
        self.tail_analysis_axis = "CycleTime"
        self.tail_analysis_exclude = ""
        self.effort_axis = ""
        self.effort_axis_friendly = ""
        self.effort_per_state = False
        self.effort_per_issuetype = False
        self.effort_who = False
        self.effort_throughput = False
        self.which_analysis = []
        self.expand_worklog = False
        self.user_pct_ca = ""
        self.count_bugs_jql = ""

def text_for_index(index):
    if index == "bag_of_words":
        return "Bag of Words"
    if index == "sum_words_per_cycletime":
        return "Bag of Words por Cycle Time"
    elif index == "bloquers":
        return "Bloqueios"
    elif index == "total_age":
        return "Total Age"
    elif index == "cfd":
        return "CFD"
    elif index == "spc creation":
        return "SPC Criação"
    elif index == "spc throughput":
        return "SPC Vazão"
    elif index == "aging":
        return "Aging"
    elif index == "effort":
        return "Análise de esforço"
    elif index == "pct_ca":
        return "% C/A"
    elif index == "weekly_transition":
        return "Transições na semana"
    elif index == "tail_analysis":
        return "Análise de calda"
    else:
        return index
        
def print_html_as_output(final_result, config):
    html = f"<html><body><h1>{config.project_name}</h1>"
    
    for index in final_result.text_result:
        html += f'<p><a href="#{index}">{text_for_index(index)}</a></p><br/>'
    html += "<br/><br/>"

    html += f"jql: {config.jql}<br/>"
    
    # print html as output
    for index in final_result.text_result:
        html += f'<hr/><a id="{index}"/>{final_result.text_result[index]}<br/>'

    for img in final_result.all_files:
        img = img.split("/")[-1]
        img = img.split("\\")[-1]
        if "png" in img or "jpg" in img:
            html += f'<img src="{img}"/><br/>'
        else:
            html += f'<a href="{img}"/>{img}</a></br>'
    
    html += "</body></html>"
        
    with open(final_result.temp_dir + "resultado.html", "w", encoding="UTF-8") as f:
        f.write(html)
        
# pós processamento são módulos especiais para Objective, principalmente processo NG
def post_processing(final_result, config, all_issues, all_subtasks, df):
    for module_name in config.post_processing_modules.split(","):
        try:
            if module_name.strip() == "":
                continue
            module = __import__(module_name.strip())
            module.post_process(final_result, config, all_issues, all_subtasks, df)
        except Exception as e:
            msg = str(e)
            coach_matic_base.print_and_log("Erro na execução: {}".format(msg))
            coach_matic_base.print_and_log(str(extract_tb(e.__traceback__)))
        
def run_each_analysis(final_result, config, df, all_issues, all_subtasks, per_field=False):
    texts.language = config.language
    
    # reloads all texts in correct language
    global language
    language = config.language
    importlib.reload(texts)
    
    # dependencies: export_csv on blockers - if exporting blockers
    # aging_spc on total_age - to get total time in each status
    analysis_methods = {"blockers": [bloquers.analisa_blockers, (final_result, config, all_issues)],
            "total_age": [total_aging.total_aging, (final_result, all_issues, config)],
            "effort": [effort.effort_analysis, (final_result, config, all_issues, df)],
            "export_csv": [export_csv.export_csv, (final_result, config, df)],
            "bag_of_words": [bag_words.bag_words, (final_result, config, df, all_issues, all_subtasks)],
            "cfd": [cfd.cfd, (final_result, config, df)],
            "spc_throughput": [spc.spc_throughput, (final_result, config, df)],
            "spc_creation": [spc.spc_creation, (final_result, config, df)],
            "weekly_transition_heatmap": [weekly_transitions.weekly_transitions, (final_result, config, all_issues, df)],
            "discriminated_throughput": [discriminated_throughput.discriminated_throughput, (final_result, config, df)],
            "tail_analysis": [tail_analysis.tail_analysis, (final_result, config, all_issues, df)],
            "aging_spc": [spc_aging.aging_status_spc_analysis, (final_result, config, all_issues, df)],
            "pct_ca": [pct_ca.pct_ca, (final_result, config, all_issues, df)]}
    
    # run only at consolidated, doesn't make sense when running per field
    analysis_to_run_consolidated_only = ["export_csv", "weekly_transition_heatmap"]
    
    for analysis in analysis_methods.keys():
        if analysis in analysis_to_run_consolidated_only and per_field:
            continue
        
        if analysis in config.which_analysis:
            method = analysis_methods[analysis][0]
            args = analysis_methods[analysis][1]
            try:
                method(*args)
            except Exception as e:
                coach_matic_base.print_and_log(">>> Faiô chamando {}. jql: {}. name: {}".format(method, config.jql, config.project_name))
                coach_matic_base.print_and_log(str(e))
                coach_matic_base.print_and_log(str(extract_tb(e.__traceback__)))
            finally:
                ran = True  # do nothing, only for syntax purpose

def filter_issues(config, all_issues, value_to_filter):
    idx_custom_field = config.export_csv_add_fields.index(config.repeat_for_each_field_value)
    custom_field = config.export_csv_add_fields_custom[idx_custom_field]
    
    filtered_issues = []
    for issue in all_issues:
        field_value = coach_matic_base.get_custom_field_value(config, issue, custom_field, custom_field)
        if field_value == value_to_filter:
            filtered_issues.append(copy.deepcopy(issue))
    return filtered_issues

def run_several_analysis(final_result, config, df, all_issues, all_subtasks):
    run_each_analysis(final_result, config, df, all_issues, all_subtasks)

    consolidated_result = texts.each_field_result_consolidated
    for key in final_result.text_result.keys():
        consolidated_result += final_result.text_result[key]
        consolidated_result += texts.separator
    
    # get all values for informed field
    all_values = df.groupby(by=config.repeat_for_each_field_value)[config.repeat_for_each_field_value].count()
    all_values.sort_values(ascending=False, inplace=True)

    original_project_name = config.project_name
    original_temp_dir = final_result.temp_dir
    
    for value in all_values[0:20].index:
        final_result.text_result.clear()
        config.project_name = "{}-{}".format(original_project_name, value)
        config.detailing_per_field = True
        if os.name == "nt":
            final_result.temp_dir = "".join([original_temp_dir, value, "\\"])
        else:
            final_result.temp_dir = "".join([original_temp_dir, value, "/"])
        try:
            os.mkdir(final_result.temp_dir, )
        except:
            nothing = True # to ignore if there is one directory already
        
        filtered_issues = filter_issues(config, all_issues, value)
        df_filtered = df[df[config.repeat_for_each_field_value] == value].copy()
        
        run_each_analysis(final_result, config, df_filtered, filtered_issues, all_subtasks, per_field=True)
    
        consolidated_result = "".join([consolidated_result,
                                       texts.each_field_result.format(config.repeat_for_each_field_value, value),
                                       texts.each_field_num_rows.format(len(df_filtered))])
        for key in final_result.text_result.keys():
            consolidated_result += final_result.text_result[key]
            consolidated_result += texts.separator
        
    final_result.text_result.clear()
    final_result.text_result["all_toghether"] = consolidated_result
    config.project_name = original_project_name
    final_result.temp_dir = original_temp_dir

def break_csv_field_for_zipped(config):
    fields_not_ok = []
    for c in config.export_csv_add_fields:
        if ":" not in c:
            fields_not_ok.append(c)
            
    if len(fields_not_ok) != 0:
        raise Exception("Campo precisam ser formato custom:label. Corrija os campos {}".format(
                    ",".join(fields_not_ok)))
        
    config.export_csv_add_fields_custom = [c.split(":")[0] for c in config.export_csv_add_fields]
    config.export_csv_add_fields = [c.split(":")[1] for c in config.export_csv_add_fields]
    
def run_analysis(final_result, config):
    if config.extract_jira_zip == None:
        if os.name != "nt" and "objective" in config.jira_url:
            jira_conn = JIRA(server=config.jira_url, basic_auth=(
                config.jira_user, config.jira_key), options={"verify": False})
        else:
            jira_conn = JIRA(server=config.jira_url, basic_auth=(
                config.jira_user, config.jira_key))
        coach_matic_base.get_optional_field_list(jira_conn, config)
        all_issues = coach_matic_base.get_all_issues(jira_conn, config)
    else:
        jira_conn = None
        break_csv_field_for_zipped(config)
        all_issues = coach_matic_base.get_all_issues_from_file(final_result, config)
        
    config.jira_conn = jira_conn
    
    df = coach_matic_base.get_dates_from_jira_history(all_issues, config)
    df = coach_matic_base.calculate_cycle_time(config, df)
    all_subtasks = coach_matic_base.search_subtasks(jira_conn, config.subjql, df)
    
    if "repeat_for_each_field_value_chk" not in config.which_analysis:
        run_each_analysis(final_result, config, df, all_issues, all_subtasks)
    else:
        run_several_analysis(final_result, config, df, all_issues, all_subtasks)
        
    post_processing(final_result, config, all_issues, all_subtasks, df)
    
    return all_issues, all_subtasks, df

def run_and_email(config, preset_uuid=None):
    try:
        coach_matic_base.print_and_log(
            "----\njql:{}\nwhich_analysis:{}".format(config.jql, config.which_analysis))
        
        final_result = FinalResult()
        
        if preset_uuid == None:
            myUUID = uuid.uuid4()
            myUUIDString = str(myUUID)
        else:
            myUUIDString = preset_uuid
            config.export_csv_add_fields = config.export_csv_add_fields + \
                                             config.expot_csv_jql_fields
            
        final_result.uuid = myUUIDString
        if os.name == "nt":
            final_result.temp_dir = "temp\\{}\\".format(myUUIDString)
        else:
            final_result.temp_dir = "temp/{}/".format(myUUIDString)
        try:
            os.mkdir(final_result.temp_dir)
        except:
            do_nothing = True
        
        run_analysis(final_result, config)
    
        if config.extract_jira_zip == None:
            out = "jql: {}<br/><br/>".format(config.jql)
        else:
            out = "arquivo extraído do Jira.<br/><br/>"
            
        for key in final_result.text_result.keys():
            out += final_result.text_result[key]
            out += texts.separator
            
        if config.schedule_day != "":
            out += "<br/><br/><font color=""gray"">UUID={}</font>".format(final_result.uuid)
        
        print(f"config.schedule_day = {config.schedule_day}")
        if config.schedule_day == "all_day.sh":
            print_html_as_output(final_result, config)
            
        out_print = re.sub(r"<[^>]*>", "", out)
        out_print = out_print.replace("<br/>","\n")
        print(out_print)
    
        send_email.send_email("Dados " + config.project_name, out, 
                              img_attach=final_result.all_files, 
                              receiver_address=config.receiver_email)
        
        return final_result
    except Exception as e:
        msg = str(e)
        coach_matic_base.print_and_log("Erro na execução: {}".format(msg))
        coach_matic_base.print_and_log(str(extract_tb(e.__traceback__)))

        out = "Falha na análise do seu projeto: {}".format(msg)
        if config.schedule_day != "":
            out += "<br/><br/><font color=""gray"">UUID={}</font>".format(final_result.uuid)

        send_email.send_email("Dados " + config.project_name, out, 
                              receiver_address=config.receiver_email)
    
        raise Exception("Erro na execução: {}".format(msg))
