if "language" in vars():
    language = vars()["language"]
else:
    language = "PT"

def pick_language(options):
    
    if language == "PT":
        return options[0]
    if language == "EN":
        return options[1]
    
separator = pick_language(["-----------------------------------<br/>",
               "-----------------------------------<br/>"])

each_field_result_consolidated = pick_language(["<h1 style=""background-color:black;color:white"">Resultados consolidados</h1><br/>",
                                   "<h1 style=""background-color:black;color:white"">Consolidated results</h1><br/>"])
each_field_result = pick_language(["<h1 style=""background-color:black;color:white"">Resultados para {}={}</h1><br/>",
                                   "<h1 style=""background-color:black;color:white"">Results for {}={}</h1><br/>"])
each_field_num_rows = pick_language(["Total de itens com esta característica: {}<br/>",
                                   "Total of items with that characteristic: {}<br/>"])

total_aging_title = pick_language(["<b>Total aging</b><br/>",
                                   "<b>Total aging</b><br/>"])
total_aging_day = pick_language(["dias",
                                   "days"])
total_aging_transition = pick_language(["movidas",
                                   "moves"])
total_aging_outlier_age = pick_language(["Outliers de {} para {}: {}.<br/>",
                                         "Outliers of {} for {}: {}.<br/>"])
total_aging_no_outlier = pick_language(["Nenhum outlier encontrado.<br/>",
                                   "No outliers found.<br/>"])
total_aging_no_values = pick_language(["Não há valores para calcular percentil.<br/>",
                                   "No values to calculate percentil.<br/>"])

bagwords_title_cycletime = pick_language(["<b>Análise da ocorrência de palavras por CycleTime</b><br/>",
                                             "<b>Analysis of word occurrence by CycleTime</b><br/>"])
bagwords_title_timespent = pick_language(["<b>Análise da ocorrência de palavras por hora reportada</b><br/>",
                                             "<b>Analysis of word occurrence by time spent</b><br/>"])
bagwords_title_aggregatedtimespent = pick_language(["<b>Análise da ocorrência de palavras por hora reportada agregada</b><br/>",
                                             "<b>Analysis of word occurrence by aggregated time spent</b><br/>"])
bagwords_count = pick_language(["{}, ",
                                "{}, "])
bagwords_words = pick_language([" {},",
                                " {},"])
bagwords_investigate = pick_language(["Investige: {}.<br/>  <font color=""gray"">* Estas palavras podem dar uma dica sobre origem de lead times mais altos.</font><br/><br/>",
                                             "Investige: {}.<br/> <font color=""gray"">* These words can give you a hint about the origin of higher lead times.</font><br/>"])
bagwords_not_found = pick_language(["Não foi identificada palavra especial para investigação.<br/>",
                                    "No special investigation word identified.<br/>"])
bagwords_foot = pick_language(["",
                               ""])
bagwords_title_sum_cycletime = pick_language(["<b>Contagem de palavras somando o CycleTime</b><br/>",
                                    "<b>Count of word by summing the CycleTime</b><br/>"])
bagwords_title_sum_timespent = pick_language(["<b>Contagem de palavras somando o tempo registrado</b><br/>",
                                    "<b>Count of word by summing the time spent</b><br/>"])
bagwords_title_sum_aggregatedtimespent = pick_language(["<b>Contagem de palavras somando o tempo registrado agregado</b><br/>",
                                    "<b>Count of word by summing the aggregated time spent</b><br/>"])
bagwords_hour = pick_language(["horas",
                                   "hours"])
bagwords_total_spenttime = pick_language(["Total {}: {}<br/>",
                                   "Total {}: {}<br/>"])

blockers_head = pick_language(["<b> Resumo de bloqueios (últimos {} dias): </b><br/>",
                                    "<b> Blockers summary(last {} days): </b><br/>"])
blockers_description = pick_language(["<table><tr><td>Chave</td><td>Dias bloqueados</td><td>Tipo Issue</td><td>estado</td><td>início</td><td>fim</td><td>descrição</td></tr>",
                                    "<table><tr><td>Chave</td><td>Dias bloqueados</td><td>estado</td><td>start</td><td>end</td><td>descrição</td></tr>"])
blockers_current = pick_language(["<tr><td colspan=5><b>Marcado atualmente</b></td></tr>",
                                    "<tr><td colspan=5><b>Flagged nowadays</b></td></tr>"])
blockers_not_found = pick_language(["Nenhum bloqueio identificado no período.<br/>",
                                    "No blocking found at the ellapsed time.<br/>"])
blockers_foot = pick_language(["</table><br/><font color=""gray"">Linhas em negrito são bloqueios atuais.</font><br/>",
                                    "</table><br/><font color=""gray"">Lines in bold are currently bloqued.</font><br/>"])
blockers_chart_title = pick_language(["Dias bloqueados por status no período ({})",
                                    "Days blocked by status in the period ({})"])
blockers_chart_xlabel = pick_language(["estado",
                                    "status"])
blockers_chart_ylabel = pick_language(["Soma de dias",
                                    "# of days"])

cfd_main_title = pick_language(["<b>Análise do CFD</b><br/>",
               "<b>CFD Analysis</b><br/>"])
cfd_anomaly = pick_language(["Anomalia no estado {}. De {} dias, apenas {} tinham um item associado.<br/>",
               "Anomaly in state {}. Of {} days, only {} had an associated item.<br/>"])
cfd_anomaly_foot1 = pick_language(["<font color=""gray"">Isto pode representar: 1. um gargalo no estado anterior; 2. número de pessoas um superdimensionado; 3. talvez seja um estado que precisa ser revisto.</font><br/>",
                                   "<font color=""gray"">This could be: 1. a bottleneck in the previous state; 2. oversized number of people; 3. maybe it's a state that needs to be reviewed.</font><br/>"])
cfd_anomaly_foot2 = pick_language(["<font color=""gray"">Pattern: Disappearing bands.</font><br/><br/>",
                                   "<font color=""gray"">Pattern: Disappearing bands.</font><br/><br/>"])

cfd_wip_check = pick_language(["Seu menor e maior wip diário foram {} e {}.<br/>",
                                   "Your lowest and highest daily wip were {} and {}.<br/>"])
cfd_wip_check_1 = pick_language(["Dias abaixo e acima do wip médio {}: {}/{} dias.<br/>",
                                   "Days below and above average wip {}: {}/{} days.<br/>"])
cfd_wip_check_variation = pick_language(["Houve uma grande variação no dia {}, de {} para {}.<br/>",
                                   "There was a big variation on day {}, from {} to {}.<br/>"])
cfd_wip_check_foot = pick_language(["<font color=""gray"">Tá, e daí? O que fazer com esta info?.</font><br/><br/>",
                                   "<font color=""gray"">Okay, so what? What to do with this info?.</font><br/><br/>"])

# cfd_spc_chart_title = pick_language(["Statistical Process Control sobre {} ({})",
#                                     "Statistical Process Control over {} ({})"])
# cfd_spc_chart_xlabel = pick_language(["Semanas",
#                                     "Weeks"])
# cfd_spc_chart_ylabel = pick_language(["Itens entregues",
#                                     "Items delivered"])
cfd_spc_chart_throughput = pick_language(["vazão",
                                    "throughput"])
cfd_spc_chart_creation = pick_language(["criação",
                                    "creation"])

discriminated_throughput_chart_title = pick_language(["Vazão discriminada sobre {} ({})",
                                    "Discriminated throughput over {} ({})"])
discriminated_throughput_chart_xlabel = pick_language(["Semanas",
                                    "Weeks"])
discriminated_throughput_chart_ylabel = pick_language(["Itens entregues",
                                    "Items delivered"])
discriminated_throughput_other = pick_language(["Outros",
                                    "tbd..."])


cfd_diff_gradient_evolution_1 = pick_language(["<br/>  O controle de WIP está estável, na razão atual de {:.2f}.<br/>",
                                    "<br/> WIP control is stable, at current ratio of {:.2f}.<br/>"])
cfd_diff_gradient_evolution_2 = pick_language(["<br/>  <b>Parabéns!</b> O controle de WIP está aumentando a razão de {:.2f}.<br/>",
                                    "<br/> <b>Congratulations!</b> The WIP control is increasing the ratio of {:.2f}.<br/>"])
cfd_diff_gradient_evolution_3 = pick_language(["<br/>  <b>Cuidado!</b> O controle de WIP está diminuindo a razão de {:.2f}.<br/>",
                                    "<br/> <b>Caution!</b> The WIP control is decreasing the ratio of {:.2f}.<br/>"])
cfd_diff_gradient_foot = pick_language(["<font color=""gray"">  * Esta análise tem {:.2f}% de confiança.</font><br/>",
                                    "<font color=""gray""> * This analysis is {:.2f}% confident.</font><br/>"])
cfd_diff_gradient_1 = pick_language(["Taxa entrada/saída = {:.2f}%<br/>",
                                    "Input/output rate = {:.2f}%<br/>"])
cfd_diff_gradient_2 = pick_language(["<font color=""gray"">Não há um valor de referencia para esta taxa de entrada/saída. ",
                                    "<font color=""gray"">There is no reference value for this input/output rate. "])
cfd_diff_gradient_explain_1 = pick_language(["Este valor é saudável, sem dúvida, sinal que você finaliza o que inicia.</font><br/>",
                                    "This value is healthy, no doubt a sign that you finish what you start.</font><br/>"])
cfd_diff_gradient_explain_2 = pick_language(["Este valor é baixo, sem dúvida, e você está iniciando mais trabalho que termina.<br/>Sugestão é limitar WIP.</font><br/>",
                                    "This value is low, no doubt, and you're starting more work than you finish.<br/>Suggestion is to limit WIP.</font><br/>"])
cfd_diff_gradient_explain_3 = pick_language(["Este valor não é conclusivo.<br/>Sugestão é limitar WIP.</font><br/>",
                                    "This value is not conclusive.<br/>Suggestion is to limit WIP.</font><br/>"])
cfd_diff_gradient_foot = pick_language(["<font color=""gray"">Pattern: Difference Gradient</font><br/>",
                                    "<font color=""gray"">Pattern: Difference Gradient</font><br/>"])
cfd_diff_gradient_explan_1 = pick_language(["<font color=""gray"">  Taxa de entrada = {:.2f}</font><br/>",
                                    "<font color=""gray""> Entrance rate = {:.2f}</font><br/>"])
cfd_diff_gradient_explan_2 = pick_language(["<font color=""gray"">  Taxa de saída = {:.2f}</font><br/>",
                                    "<font color=""gray""> Output rate = {:.2f}</font><br/>"])
cfd_diff_gradient_explan_3 = pick_language(["<font color=""gray"">  Evolução: ",
                                    "<font color=""gray""> Evolution: "])

cfd_stair_step = pick_language(["Houve uma grande entrega no dia {} para status '{}', de {} para {} itens.<br/>",
                                    "There was a big delivery on {} to the status '{}', from {} to {} items.<br/>"])
cfd_stair_step_foot = pick_language(["<font color=""gray"">   Recomendado é trabalhar com lotes menores e entregas mais constantes.<br/>Pattern: stair steps.</font><br/><br/>",
                                    "<font color=""gray""> It is recommended to work with smaller batches and more constant deliveries.<br/>Pattern: stair steps.</font><br/><br/>"])

cfd_diff_gradient_curr_wip = pick_language(["<br/>WIP atual: {}<br/>",
                                    "<br/>Current WIP: {}<br/>"])
cfd_diff_gradient_curr_wip_foot = pick_language(["<font color=""gray"">  * Baseado no número de itens que foram movidos para downstream, continua contando se o item voltou um estado.</font><br/><br/>",
                                    "<font color=""gray""> * Based on the number of items that have been moved downstream, it continues to count whether the item has returned one state.</font><br/><br/>"])

cfd_in_out_chart_title = pick_language(["Taxa entrada/saída do downstream ({})",
                                        "In/Out rate ({})"])
cfd_in_out_chart_xlabel = pick_language(["Semanas",
                                        "Weeks"])
cfd_in_out_chart_ylabel = pick_language(["% taxa entrada/saída",
                                        "% in/out rate"])

cfd_diff_flat_1 = pick_language(["Identificado platô de {} dias em '{}', de {} até {}.<br/>",
                                    "Plateau of {} days identified in '{}', from {} to {}.<br/>"])
cfd_diff_flat_2 = pick_language(["Não foram identificaos platos.<br/>",
                                    "No plateaus identified.<br/>"])
cfd_diff_flat_foot = pick_language(["<font color=""gray"">Recomendado acompanhar <i>aging</i> e impedimentos. Pode se falso positivo em caso de feriados.<br/>Pattern: Flat lines.</font><br/><br/>",
                                    "<font color=""gray"">Recommended to monitor aging> and impediments. Can be false positive in case of holidays.<br/>Pattern: Flat lines.</font><br/><br/>"])

cfd_s_curve_explan_1 = pick_language(["Seu CFD está em curva S. Isto não é bom sinal.<br/>",
                                      "Your CFD has an S-curve. That is not a good indicator.<br/>"])
cfd_s_curve_foot_1 = pick_language(["<font color=""gray"">Isto significa que não está tendo grande evolução. Tente eliminar os platos para melhorar sua evolução.<br/>Um CFD em curva S diminui sua previsibilidade.<br/>Pattern: S-Curve</font><br/><br/>",
                                    "<font color=""gray"">This means that you are not making a big improvement. Try to eliminate the plateaus to improve your evolution.<br/>An S-curve CFD decreases your predictability.<br/>Pattern: S-Curve</font><br/><br/>"])
cfd_s_curve_explan_2 = pick_language(["Seu CFD está em curva S invertida. Isto é bom sinal.<br/>",
                                      "Your CFD has inverted S-curve. That is a good indicator.<br/>"])
cfd_s_curve_foot_2 = pick_language(["<font color=""gray"">Isto significa que está tendo muito mais entregas agora que no começo.<br/>Pattern: S-Curve</font><br/><br/>",
                                    "<font color=""gray"">This means it's getting a lot more deliveries now than in the beginning.<br/>Pattern: S-Curve</font><br/><br/>"])
cfd_s_curve_explan_3 = pick_language(["Seu CFD está em curva S forte. <b>Isto é um indicador ruim.</b><br/>",
                                      "Your CFD has a strong S-curve. <b>That is a bad indicator.</b><br/>"])
cfd_s_curve_foot_3 = pick_language(["<font color=""gray"">Isto significa que não está tendo grande evolução. Tente eliminar os platos para melhorar sua evolução.<br/>Um CFD em curva S diminui sua previsibilidade.<br/>Pattern: S-Curve</font><br/><br/>",
                                    "<font color=""gray"">This means that you are not making a big improvement. Try to eliminate the plateaus to improve your evolution.<br/>An S-curve CFD decreases your predictability.<br/>Pattern: S-Curve</font><br/><br/>"])

spc_title = pick_language(["<b>SPC para {}</b><br/>",
                                   "<b>SPC for {}</b><br/>"])
spc_type1_daily = pick_language(["Vazão diária",
                           "Daily throughput"])
spc_type2_daily = pick_language(["Criação diária",
                           "Daily creation"])
spc_type1_weekly = pick_language(["Vazão diária",
                           "Daily throughput"])
spc_type2_weekly = pick_language(["Criação semanal",
                           "Weekly creation"])
spc_to_few_data = pick_language(["Não foi possível analisar SPC para {}, pois há menos de 25 itens ({} itens).<br/>",
                           "It was not possible to analyze SPC for {}, as there are less than 25 items.<br/>"])
spc_chart_title = pick_language(["SPC para {} ({})",
                           "SPC for {} ({})"])
spc_chart_variation_title = pick_language(["SPC variação para {} ({})",
                           "SPC variation for {} ({})"])
spc_chart_x_throughput = pick_language(["Itens entregues na semana",
                           "Items delivered in the week"])
spc_chart_y = pick_language(["Semana",
                           "Week"])
spc_upper_limits = pick_language(["Seu SPC {} {} ficou acima para {}: {}<br/>",
                                  "Your SPC {} {} got higher for {}: {}<br/>"])
spc_upper_limits_explain = pick_language(["<b>Se você está usando Monte Carlo fique atento, pois é possível que suas estimativas sejam mais próximas que deveriam ser.</b><br/><br/>",
                                    "<b>If you are using Monte Carlo be aware, as it is possible that your dates get closer than it should be.</b><br/><br/>"])
spc_lower_limits = pick_language(["Seu SPC {} {} ficou abaixo para {}: {}<br/>",
                                  "Your SPC {} {} get lower for {}: {}<br/>"])
spc_ok_throughput = pick_language(["Sua vazão está dentro dos limites. Nada de especial aqui.<br/><br/>",
                                    "Your throughput is within limits. Nothing special here.<br/><br/>"])
spc_upper_limits_explain_creation = pick_language(["<b>Se você está analisando incidentes ou bugs há uma anormalidade nestes dias. Investigue.</b><br/><br/>",
                                    "<b>If you are analyzing incidents or bugs there is an anormality in these days. Investigate.</b><br/><br/>"])
spc_items = pick_language(["itens",
                           "items"])
spc_couting = pick_language(["contagem",
                           "couting"])
spc_difference = pick_language(["diferença",
                           "difference"])
spc_day = pick_language(["dia(s)",
                           "day(s)"])
spc_week = pick_language(["semana(s)",
                           "week(s)"])

spc_aging_chart_title = pick_language(["SPC aging para {} ({})",
                           "SPC aging for {} ({})"])
spc_aging_chart_x = pick_language(["Dias no estado",
                           "Days in the state"])
spc_aging_chart_y = pick_language(["Ticket",
                           "Ticket"])

weekly_transition_title = pick_language(["<b>Análise de transições durante a semana</b><br/>",
                                        "<b>Analysis on transitions during the week</b><br/>"])
weekly_transition_title_csv = pick_language(["Dia semana\Hora",
                                        "Week day\Hour"])
weekly_transition_weekday = pick_language([["Seg","Ter","Qua","Qui","Sex","Sab","Dom"],
                                        ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]])
weekly_transition_all_statuses = pick_language(["Qualquer estado",
                                        "Any state"])
weekly_transition_find_per_hour = pick_language(["{:.2f}% das transições para estado '{}' acontecem durante {} horas.<br/>",
                                        "{:.2f}% of the transitions for state '{}' happen at {}.<br/>"])
weekly_transition_find_per_day = pick_language(["{:.2f}% das transições para estado '{}' acontecem nos dias {}.<br/>",
                                        "{:.2f}% of the transitions for state '{}' happend at days {}.<br/>"])
weekly_transition_not_found = pick_language(["Não foi encontrado nada especial nas transições semanais. Aparentemente seu time está trabalhando bem no quadro.<br/>",
                                        "Nothing special in your weekly transitions. Appraently your team is working ok on the board.<br/>"])
weekly_transition_chart_title = pick_language(["Movimentações durante a semana, últimos {} dias ({})",
                                        "Transitions in the week, last {} days ({})"])
weekly_transition_explain = pick_language(["<font color=""gray"">Isto pode significar que o time atualiza os cards para alguma reunião de status, e não é uma coisa fluida no time.</font><br/><br/>",
                                        "<font color=""gray"">This could mean that the team updates the cards for some status report meeting, and it is not a fluid thing in the team.</font><br/><br/>"])

tail_analysis_title = pick_language(["<b>Análise de cauda</b><br/>",
                                         "<b>Tail analysis</b><br/>"])
tail_analysis_thin_tail = pick_language(["Seu processo tem cauda fina. Idx: {:.2f}, referência < 5.6.<br/>",
                                         "Your process has a thin tail. Idx: {:.2f}, reference < 5.6.<br/>"])
tail_analysis_fat_tail = pick_language(["Seu processo tem cauda longa. Idx: {:.2f}, referência < 5.6.<br/>",
                                         "Your process has a fat tail. Idx: {:.2f}, reference < 5.6.<br/>"])
tail_analysis_find = pick_language(["A cauda do cycle time vai de {:.2f} até {:.2f} dias.<br/> Os itens que fazem parte da cauda são: {}.<br/><br/>",
                                    "The cycle time tail goes from {:.2f} to {:.2f} days.<br/> The items that are part of the tail are: {}.<br/><br/>"])
tail_analysis_amplitude_decreasing = pick_language(["Sua amplitude está diminuindo no ritmo de {:.2f}%. Isto impacta diretamente na sua cauda e com o tempo deverá diminuir. Isto é um bom sinal.<br/><br/>",
                                    "Its amplitude is decreasing at the rate of {:.2f}%. This impacts directly your tail and should decrease over time. This is a good sign.<br/><br/>"])
tail_analysis_amplitude_increasing = pick_language(["Sua amplitude está aumentando no ritmo de {:.2f}%. Isto impacta diretamente na sua cauda e com o tempo deverá aumentar. Tente diminuir seu cycle time para aumentar a previsibilidade.<br/><br/>",
                                    "Its amplitude is decreasing at the rate of {:.2f}%. This impacts directly your tail and should get longer over time. Try to decrease your cycle time to increase predictability.<br/><br/>"])

effort_title = pick_language(["<b>Análise de esforço</b><br/>",
                              "Effort analysis<br/>"])
effort_total_sum = pick_language(["{:.2f} horas reportadas<br/>",
                              "{:.2f} hours reportadas<br/>"])
effort_average = pick_language(["{:.2f} média entre os itens com horas registradas - total de {} itens.<br/>",
                              "{:.2f} average among itens with registered effort - total of {} items.<br/>"])
effort_outliers = pick_language(["Outliers: {}<br/>",
                              "Outliers: {}<br/>"])
effort_no_outliers = pick_language(["Nenhum outlier.<br/>",
                              "No outliers.<br/>"])
effort_status_disclaimer = pick_language(["<font color=""gray"">Disparidade entre esforço e cycle time pode representar WIP muito alto ou muitos impedimentos.<br/>Estados anteriores (aberto, por exemplo) podem representar valores errados. Isto não deve acontecer para estados posteriores (fechado, por exemplo).</font><br/>",
                                          "tbd..."])
effort_who = pick_language(["Nome de todos que registraram horas: <br/>",
                                          "tbd..."])
effort_issuetype = pick_language(["{} por tipo de issue: {}<br/>",
                                          "tbd..."])
effort_tendency = pick_language(["As horas reportadas estão aumentando/diminuindo na razão de {:.2f}%.<br/>",
                                          "tbd..."])
effort_chart_title = pick_language(["Relação vazão vs esforço-{}",
                                          "tbd..."])
effort_chart_x = pick_language(["Semanas",
                                          "tbd..."])
effort_chart_y = pick_language(["Escala",
                                          "tbd..."])
effort_productivity_more = pick_language(["<br/><b>Parabéns!</b> Sua produtividade baseada no esforço está aumentando.<br/>",
                                          "tbd..."])
effort_productivity_less = pick_language(["<br/><b>Cuidado!</b> Sua produtividade baseada no esforço está diminuindo.<br/>",
                                          "tbd..."])
effort_productivity_ratio = pick_language(["A diferença da tendência entre vazão vs esforço é {:.2f}%.<br/>",
                                          "tbd..."])

pctca_title = pick_language(["<b>% C/A - % Completed Accurate</b><br/>",
                             "tbd..."])
pctca_description1 = pick_language(["Horas trabalhadas {:.2f}h, horas retrabalho: {:.2f}h, horas incertas se é retrabalho: {:.2f}h, horas validação: {:.2f}h.<br/>",
                             "tbd..."])
pctca_description2 = pick_language(["<b>% C/A: {:.2f}% de acuracidade antes da validação.</b><br/>",
                             "tbd..."])
pctca_description3 = pick_language(["% C/A: {:.2f}% de acuracidade antes da validação considerando horas dúbias.<br/>",
                             "tbd..."])
pctca_description4 = pick_language(["Issues com % C/A abaixo de 70: {}<br/>",
                             "tbd..."])
pctca_description5 = pick_language(["Número de bugs/issues: {}/{}, ou média de {:.2f} bugs por issue.<br/>",
                             "tbd..."])
pctca_description6 = pick_language(["Número de issues sem indício da participação de QA: {} ({:.2f}%).<br/>",
                             "tbd..."])
pctca_disclaimer = pick_language(["<font color=""gray"">Cálculo sobre horas reportadas do dev antes e depois do QA. Quando os dois são reportados no mesmo dia é considerado como dúbio.</font><br/>",
                             "tbd..."])
pctca_disclaimer2 = pick_language(["<font color=""gray"">Revise os issues com % C/A abaixo de 70, pois tem potencial baixa qualidade.</font><br/>",
                             "tbd..."])
pctca_disclaimer3 = pick_language(["<font color=""gray"">Foram contados bugs apenas de issues com horas registradas pelo QA.</font><br/>",
                             "tbd..."])
pctca_disclaimer4 = pick_language(["<font color=""gray"">No arquivo pct_ca.csv tente entender a relação de número de bugs com % C/A. Muitos bugs deveria ter % C/A menor.</font><br/>",
                             "tbd..."])
pctca_disclaimer5 = pick_language(["<font color=""gray"">No arquivo pct_ca.csv linhas com % C/A vazio indica que não há esforço de QA.</font><br/>",
                             "tbd..."])
pctca_dev_users = pick_language(["<font color=""gray"">Usuários dev: {}</font><br/>",
                             "tbd..."])
pctca_qa_users = pick_language(["<font color=""gray"">Usuários qa: {}</font><br/>",
                             "tbd..."])

aging_title = pick_language(["<b>Aging</b>",
                             "tbd..."])
