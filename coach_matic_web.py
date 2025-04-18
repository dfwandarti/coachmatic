from http.server import BaseHTTPRequestHandler, HTTPServer, ThreadingHTTPServer
import os, cgi, threading, mimetypes, subprocess, urllib, re
from datetime import datetime, timedelta
from traceback import extract_tb

import coach_matic, coach_matic_base, schedule

class ForecastThread(threading.Thread):
    def run(self):
        print("recalculando forecast...")
        subprocess.run("cd forecast; python3 dashboard_ps.py", shell=True, check=True, capture_output=True)
        print("forecast finalizado.")
    
class AnalysisThread(threading.Thread):
    config = coach_matic.Config
    
    def run(self):
        final_result = coach_matic.run_and_email(self.config)
        if "schedule" in self.config.which_analysis:
            schedule.schedule(final_result, self.config)
        
def get_value_or_default(postvars, key, default_if_empty=""):
    if key in postvars and postvars[key][0] == "":
        return default_if_empty
    elif key in postvars:
        return postvars[key][0]
    else:
        return ""
    
# split csv_fields, using regex as it may have comma inside a jql which is between [ and ]
def split_fields(csv_fields):
    # csv_fields = "Taskboard Project Id, jql:Taskboard Project Id[issuetype=Demanda and issueFunction in linkedIssuesOf(\"issue = ?\", \"demandou\")]"
    print(f"csv_fields:{csv_fields}")
    all_jql = re.findall("jql:[^\[]*\[[^\]]*\]", csv_fields)
    for each_jql in all_jql:
        csv_fields = csv_fields.replace(each_jql, "")
    splited_fields = list(filter(lambda f: len(f.strip()) > 0, csv_fields.split(","))) + all_jql
    print(f"splited_fields:{splited_fields}")
    return splited_fields
    
def handle_request(postvars):
    config = coach_matic.Config()
    
    try:
        config.project_name = postvars["project_name"][0]
        config.jira_url = postvars["jira_url"][0]
        
        if "objective.com.br" in config.jira_url:
            config.jira_user = "svc_jira-sync-customers"
            config.jira_key = "0tl9-gi5oXIw3tEch3gl"
        else:
            config.jira_user = postvars["jira_user"][0]
            config.jira_key = postvars["jira_key"][0]
            
        config.jql = postvars["jql"][0]
        
        config.extract_jira_zip = postvars["filename"][0]
        if len(config.extract_jira_zip) == 0:
            config.extract_jira_zip = None
            # need to validate only if user did NOT enter a zip with extracted jira tickets
            if "resolved" not in config.jql and "created" not in config.jql and "after" not in config.jql:
                raise Exception("Sua pesquisa pode ser muito ampla. Limite seu jql com resolved ou created.")
                
        all_statuses = postvars["all_statuses"][0]
        coach_matic_base.prepare_all_statuses(config, all_statuses)
            
        config.downstream_start = get_value_or_default(
            postvars, "downstream_start", default_if_empty=config.all_statuses[1])
        config.downstream_stop = get_value_or_default(
            postvars, "downstream_stop", default_if_empty=config.all_statuses[-1])
        config.downstream_start = config.downstream_start.lower()
        config.downstream_stop = config.downstream_stop.lower()
        
        idx_down_start = config.all_statuses.index(config.downstream_start)
        idx_down_stop = config.all_statuses.index(config.downstream_stop)
        config.downstream_statuses = config.all_statuses[idx_down_start:idx_down_stop + 1]

        config.receiver_email = postvars["receiver_email"][0]
        config.language = postvars["language"][0]
        
        config.which_analysis = []
        if "schedule" in postvars and postvars["schedule"][0] == "Yes":
            config.which_analysis.append("schedule")
            config.schedule_day = postvars["schedule_day"][0]
        if "repeat_for_each_field_value_chk" in postvars and postvars["repeat_for_each_field_value_chk"][0] == "Yes":
            config.which_analysis.append("repeat_for_each_field_value_chk")
            config.repeat_for_each_field_value = postvars["repeat_for_each_field_value"][0].strip()
            if "," in config.repeat_for_each_field_value or config.repeat_for_each_field_value == "":
                raise Exception("Informe apenas um e apenas um campo por vez. {} não pode.".format(config.export_csv_add_fields))
        if "export_csv" in postvars and postvars["export_csv"][0] == "Yes":
            config.which_analysis.append("export_csv")
            if config.extract_jira_zip is None:
                config.export_csv_add_fields = split_fields(postvars["export_csv_add_fields"][-1])
            else:
                config.export_csv_add_fields = split_fields(postvars["export_csv_add_fields_zip"][-1])
        if "total_age" in postvars and postvars["total_age"][0] == "Yes":
            config.which_analysis.append("total_age")
            config.total_age_percentil = "total_age_percentil" in postvars and postvars["total_age_percentil"][0] == "Yes"
        if "bag_of_words" in postvars and postvars["bag_of_words"][0] == "Yes":
            config.which_analysis.append("bag_of_words")
            config.bag_of_words_axis = postvars["bag_of_words_axis"][0]
            config.bag_of_words_exclude = postvars["bag_of_words_exclude"][0]
            config.subjql = postvars["subjql"][0]
        if "blockers" in postvars and postvars["blockers"][0] == "Yes":
            config.which_analysis.append("blockers")
            config.blocker_days = int(get_value_or_default(
                postvars, "blocker_days", default_if_empty="30"))
        config.blocker_field = get_value_or_default(
            postvars, "blocker_field", default_if_empty="Flagged")
        config.blocker_field_description = get_value_or_default(
            postvars, "blocker_field_description", default_if_empty="")
        if "cfd" in postvars and postvars["cfd"][0] == "Yes":
            config.which_analysis.append("cfd")
            config.wip_evolution_chart = "wip_evolution_chart" in postvars and postvars["wip_evolution_chart"][0] == "Yes"
        if "spc_throughput" in postvars and postvars["spc_throughput"][0] == "Yes":
            config.which_analysis.append("spc_throughput")
            config.spc_time_window = int(postvars["spc_time_window"][0])
        if "spc_creation" in postvars and postvars["spc_creation"][0] == "Yes":
            config.which_analysis.append("spc_creation")
            config.spc_time_window = int(postvars["spc_time_window"][0])
        if "weekly_transition_heatmap" in postvars and postvars["weekly_transition_heatmap"][0] == "Yes":
            config.which_analysis.append("weekly_transition_heatmap")
        if "aging_spc" in postvars and postvars["aging_spc"][0] == "Yes":
            config.which_analysis.append("aging_spc")
            if "one_chart_aging_spc" in postvars and postvars["one_chart_aging_spc"][0] == "Yes":
                config.which_analysis.append("one_chart_aging_spc")
        if "discriminated_throughput" in postvars and postvars["discriminated_throughput"][0] == "Yes":
            config.which_analysis.append("discriminated_throughput")
            config.discriminated_throughput_field = postvars["discriminated_throughput_field"][0]
            if "discriminated_throughput_creation" in postvars and postvars["discriminated_throughput_creation"][0] == "Yes":
                config.discriminated_throughput_creation = True
        if "tail_analysis" in postvars and postvars["tail_analysis"][0] == "Yes":
            config.which_analysis.append("tail_analysis")
            config.tail_analysis_axis = postvars["tail_analysis_axis"][0]
            config.tail_analysis_exclude = postvars["tail_analysis_exclude"][0]
        if "effort" in postvars and postvars["effort"][0] == "Yes":
            config.which_analysis.append("effort")
            config.effort_axis = postvars["effort_axis"][0]
            config.expand_worklog = True
            if "effort_per_state" in postvars and postvars["effort_per_state"][0] == "Yes":
                config.effort_per_state = True
            if "effort_per_issuetype" in postvars and postvars["effort_per_issuetype"][0] == "Yes":
                config.effort_per_issuetype = True
            if "effort_who" in postvars and postvars["effort_who"][0] == "Yes":
                config.effort_who = True
            if "effort_throughput" in postvars and postvars["effort_throughput"][0] == "Yes":
                config.effort_throughput = True
        if "pct_ca" in postvars and postvars["pct_ca"][0] == "Yes":
            config.which_analysis.append("pct_ca")
            config.user_pct_ca = postvars["user_pct_ca"][0]
            config.expand_worklog = True
            config.count_bugs_jql = postvars["count_bugs_jql"][0]
        if "recluster" in postvars and postvars["recluster"][0] == "Yes":
            config.post_processing_modules = "recluster"
    except Exception as e:
        coach_matic_base.print_and_log("Erro nos parametros")
        coach_matic_base.print_and_log(str(extract_tb(e.__traceback__)))
        raise Exception("Erro nos parametros: {}".format(e))

    thread = AnalysisThread()
    thread.config = config
    thread.start()
    
class HandleRequests(BaseHTTPRequestHandler):
    last_run = datetime.now() - timedelta(days=1)
    user_map = None
    ticket_per_user = None

    def return_file(self, file_name):
        print(f"returning {file_name}...")
        
        if os.path.exists(file_name):
            content_type, encoding = mimetypes.guess_type(file_name)

            if content_type is None or encoding is not None:
                content_type = 'application/octet-stream'
            main_type, sub_type = content_type.split('/', 1)
            if file_name[-4:] == '.csv':
                with open(file_name, "r", encoding="UTF-8") as f:
                    file_content = f.read()
                content_type = 'text/csv;charset=UTF-8'
            elif main_type == 'text':
                with open(file_name, "r", encoding="UTF-8") as f:
                    file_content = f.read()
                content_type = 'text/html;charset=UTF-8'
            # elif main_type == 'image':
            else:
                with open(file_name, "rb") as f:
                    file_content = f.read()
             
            print(f"   content_type {content_type}...")
            self.send_response(200)
            self.send_header('Content-Type', content_type)
            self.end_headers()
            
            if main_type == 'text':
                self.wfile.write(file_content.encode())
            else:
                self.wfile.write(file_content)
        else:
            self.send_response(404)
            self.end_headers()
    
    def _set_headers(self, http_code=200):
        self.send_response(http_code)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

    def do_GET(self):
        if self.path == "/":
            self.return_file("coach-matic.html")
        else:
            file_name = urllib.parse.unquote(self.path[1:], encoding="UTF-8")
            if os.name == "nt":
                file_name = file_name.replace("/", "\\")
            else:
                file_name = file_name

            self.return_file(file_name)
        # self.wfile.write("{webResponse.status: 200}".encode())
        
    def do_POST(self):
        print("Chegou POST. ip: {} para {}".format(self.address_string(), self.path))

        ctype, pdict = cgi.parse_header(self.headers["content-type"])
        pdict["boundary"] = bytes(pdict["boundary"], "utf-8")
        postvars = cgi.parse_multipart(self.rfile, pdict)
        
        try:
            if self.path == "/forecast":
                forecast_thread = ForecastThread()
                forecast_thread.start()
                self._set_headers()
                self.wfile.write("Recalculado. Recarregue a página original em alguns minutos.".encode())
            else:
                handle_request(postvars)
                self._set_headers()
                self.wfile.write("Recebido. Aguarde no seu e-mail!".encode())
            
        except Exception as e:
            self._set_headers()
            msg = "Erro: {}".format(e)
            self.wfile.write(msg.encode())

    def do_PUT(self):
        self.do_POST()
                
if os.name == "nt":
    host = 'localhost'
else:
    host = '10.45.1.68'
port = 8088
print("Listening on {}:{}".format(host, port))
HTTPServer((host, port), HandleRequests).serve_forever()
# httpd = ThreadingHTTPServer((host, port), HandleRequests)
# httpd.serve_forever()

