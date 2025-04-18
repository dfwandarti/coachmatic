import re
from traceback import extract_tb
import coach_matic, coach_matic_base, send_email

def add_to_results_html(config):
    all_links = []
    
    with open("all_day.sh", "r", encoding="UTF-8") as f:
        all_lines = f.readlines()
        for line in all_lines:
            line = line.replace("\n", "").replace("\r", "")
            mod_name = re.sub(r"python3 (.*) #.*", "\\1", line)
            
            if len(mod_name) >= 39 and len(mod_name) <= 40:
                try:
                    with open(mod_name, "r", encoding="UTF-8") as f:
                        all_lines = f.readlines()
                        one_big_line = " ".join(all_lines).replace("\n", "").replace("\r", "")
                        project_name = re.sub(r".*config.project_name='([^']*).*", "\\1", one_big_line)
                        mod_name = mod_name.replace(".py", "")
                        link = f'<a href="temp/{mod_name}/resultado.html">{project_name}</a></br>'
                        all_links.append(link)
                except:
                    does_nothing = True
            
    with open("resultados.html", "w", encoding="UTF-8") as f:
        f.write(f"<html><body>{' '.join(all_links)}</body></html>")
        
def schedule(final_result, config):
    try:
        if "schedule" in config.which_analysis:
            config.which_analysis.remove("schedule")
            
        # create .py file
        with open(final_result.uuid + ".py", "w", encoding="UTF-8") as f:
            f.write("import coach_matic\n\n")
            f.write("config = coach_matic.Config()\n")
            for var_name in vars(config):
                var_value = getattr(config, var_name)
                if type(var_value) == str:
                    var_value = var_value.replace("'", "'+chr(39)+'")
                    var_value = var_value.replace(chr(92), chr(92)+chr(92))
                    coach_matic_base.print_and_log("config.{}='{}'\n".format(var_name, var_value))
                    f.write("config.{}='{}'\n".format(var_name, var_value))
                elif type(var_value) == list or \
                      type(var_value) == bool or \
                      type(var_value) == int:
                    coach_matic_base.print_and_log("config.{}={}\n".format(var_name, var_value))
                    f.write("config.{}={}\n".format(var_name, var_value))
                else:
                    coach_matic_base.print_and_log(f"type for {var_name} = {type(var_value)}.")
            f.write("\n")
            f.write("coach_matic.run_and_email(config, preset_uuid='{}')\n".format(
                final_result.uuid))

        # schedule crontab
        cmd_line = "python3 {}.py # jql:{}\n".format(
            final_result.uuid, config.jql)
        with open(config.schedule_day, "a") as f:
            f.write("{}\n".format(cmd_line))
        coach_matic_base.print_and_log(
            "Scheduling with cmd: {}".format(cmd_line))
        
        if config.schedule_day == "all_day.sh":
            add_to_results_html(config)
    except Exception as e:
        msg = str(e)
        coach_matic_base.print_and_log("Erro na execução: {}".format(msg))
        coach_matic_base.print_and_log(str(extract_tb(e.__traceback__)))

        out = "Falha na análise do seu projeto: {}".format(msg)
        if "schedule" in config.which_analysis:
            out += "<br/><br/><font color=""gray"">UUID={}</font>".format(final_result.uuid)

        send_email.send_email("Dados " + config.project_name, out, 
                              receiver_address=config.receiver_email)
