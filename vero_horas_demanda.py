# import coach_matic

# config = coach_matic.Config()
# config.detailing_per_field=True
# config.language='PT'
# config.project_name='Vero - horas por demanda'
# config.jira_url='https://jira.objective.com.br'
# config.jira_user='svc_jira-sync-customers'
# config.jira_key='0tl9-gi5oXIw3tEch3gl'
# config.jql='issueFunction in subtasksOf('+chr(39)+'issueFunction in linkedIssuesOf("issuetype = Demanda and (status not in (Cancelado, Fechado) or resolved > -30d) and \\\\"Taskboard Project Id\\\\" = 73867", "demandou") and project = VERO'+chr(39)+') '

# config.project_name='Vero - horas SEM sap'
# config.jql='project = vero and issuetype in subTaskIssueTypes() and not (summary ~sap or description ~ sap) and issuetype not in ("UX Review", "Sub-task Continuous", "Análise de UX", "Acompanhamento Desenvolvimento") and created > startOfYear(-2)'

# # config.jql='issueFunction in subtasksOf('+chr(39)+'issueFunction in linkedIssuesOf("issue = VERO-3300", "demandou") and project = VERO'+chr(39)+') '
# # config.jql='issueFunction in subtasksOf('+chr(39)+'issueFunction in linkedIssuesOf("issuetype = Demanda and (status not in (Cancelado, Fechado) or resolved > -30d) and \\\\"Taskboard Project Id\\\\" = 73867", demandou) and project = VERO'+chr(39)+') '
# # config.jql='issueFunction in subtasksOf('+chr(39)+'issueFunction in linkedIssuesOf("issue in (VERO-2853, VERO-3300)",demandou) and project = VERO'+chr(39)+')'
# # config.jql='issueFunction in subtasksOf('+chr(39)+'issueFunction in linkedIssuesOf("issue =VERO-2853",demandou) and project = VERO'+chr(39)+')'
# config.all_statuses=['aberto', 'postergado', 'to do', 'in progress', 'to review', 'review', 'done']
# config.all_sub_statuses=[['aberto'], ['postergado'], ['to do'], ['in progress'], ['to review'], ['review'], ['done']]
# config.downstream_start='aberto'
# config.downstream_stop='done'
# config.downstream_statuses=['aberto', 'postergado', 'to do', 'in progress', 'to review', 'review', 'done']
# config.waiting_statuses=[]
# config.receiver_email='daniel.wandarti@objective.com.br'
# config.schedule_day='all_day.sh'
# config.repeat_for_each_field_value=''
# config.export_csv_add_fields=['pai.Chave', 'pai.Tipo de Item', 'pai.Σ Tempo Gasto', 'pai.Situação', 'Orçamento Técnico Total', 'Flagged', 'Σ Tempo Gasto', 'Tamanho', 'Resumo', 'Situação', 'Data para Ficar Pronto']
# config.export_csv_add_fields_custom=['issuekey', 'issuetype', 'aggregatetimespent', 'status', 'customfield_10035', 'customfield_10640', 'aggregatetimespent']
# config.expot_csv_jql_fields=['jql:Chave[issueFunction in linkedIssuesOf("issueFunction in parentsOf('+chr(39)+'issue = ?'+chr(39)+')") and issuetype=Demanda]', 'jql:Resumo[issueFunction in linkedIssuesOf("issueFunction in parentsOf('+chr(39)+'issue = ?'+chr(39)+')") and issuetype=Demanda]', 'jql:Situação[issueFunction in linkedIssuesOf("issueFunction in parentsOf('+chr(39)+'issue = ?'+chr(39)+')") and issuetype=Demanda]', 'jql:Orçamento Técnico Total[issueFunction in linkedIssuesOf("issueFunction in parentsOf('+chr(39)+'issue = ?'+chr(39)+')") and issuetype=Demanda]', 'jql:Data para Ficar Pronto[issueFunction in linkedIssuesOf("issueFunction in parentsOf('+chr(39)+'issue = ?'+chr(39)+')") and issuetype=Demanda]']
# config.total_age_percentil=False
# config.bag_of_words_axis=''
# config.bag_of_words_axis_friendly=''
# config.bag_of_words_exclude=''
# config.subjql=''
# config.blocker_days=30
# config.blocker_field='Flagged'
# config.blocker_field_description=''
# config.cfd_days=90
# config.wip_evolution_chart=True
# config.spc_time_window=1
# config.discriminated_throughput_field=''
# config.tail_analysis_axis='CycleTime'
# config.tail_analysis_exclude=''
# config.effort_axis='aggregatetimespent'
# config.effort_axis_friendly='Σ Tempo Gasto'
# config.effort_per_state=True
# config.effort_per_issuetype=True
# config.effort_who=True
# config.which_analysis=['export_csv', 'cfd', 'effort']
# config.expand_worklog=True
# config.user_pct_ca=''
# config.count_bugs_jql=''

# config.post_processing_modules = "hour_per_demand"

# coach_matic.run_and_email(config, preset_uuid='97c42dcc-cd58-4f6a-9b62-109ad7c2a73e')


import coach_matic

config = coach_matic.Config()
config.detailing_per_field=False
config.language='PT'
config.project_name='Vero - Aging OS e Bugs'
config.jira_url='https://jira.objective.com.br'
config.jira_user='svc_jira-sync-customers'
config.jira_key='0tl9-gi5oXIw3tEch3gl'
config.jql='project = Vero and issuetype in (OS, Bug) and (issueFunction in linkedIssuesOf('+chr(39)+'issuetype = Demanda and "Taskboard Project Id" = 73867'+chr(39)+', "demandou") or "Taskboard Project Id" = 73867) and status not in (Cancelado, Fechado) and created > startOfYear(-2)'
config.all_statuses=['aberto', 'postergado', 'priorizado', 'planejamento', 'aguardando desenvolvimento', 'desenvolvimento', 'integrado', 'beta-teste', 'fechado']
config.all_sub_statuses=[['aberto'], ['postergado'], ['priorizado'], ['planejamento'], ['aguardando desenvolvimento'], ['desenvolvimento'], ['integrado'], ['beta-teste'], ['fechado']]
config.downstream_start='aberto'
config.downstream_stop='fechado'
config.downstream_statuses=['aberto', 'postergado', 'priorizado', 'planejamento', 'aguardando desenvolvimento', 'desenvolvimento', 'integrado', 'beta-teste', 'fechado']
config.waiting_statuses=[]
config.receiver_email='daniel.wandarti@objective.com.br'
config.schedule_day='all_day.sh'
config.repeat_for_each_field_value=''
config.export_csv_add_fields=['Flagged']
config.export_csv_add_fields_custom=['customfield_10640']
config.expot_csv_jql_fields=[]
config.total_age_percentil=False
config.bag_of_words_axis=''
config.bag_of_words_axis_friendly=''
config.bag_of_words_exclude=''
config.subjql=''
config.blocker_days=30
config.blocker_field='Flagged'
config.blocker_field_description=''
config.cfd_days=90
config.wip_evolution_chart=False
config.spc_time_window=1
config.discriminated_throughput_field=''
config.discriminated_throughput_creation=False
config.tail_analysis_axis='CycleTime'
config.tail_analysis_exclude=''
config.effort_axis=''
config.effort_axis_friendly=''
config.effort_per_state=False
config.effort_per_issuetype=False
config.effort_who=False
config.effort_throughput=False
config.which_analysis=['total_age', 'aging_spc']
config.expand_worklog=False
config.user_pct_ca=''
config.count_bugs_jql=''

coach_matic.run_and_email(config, preset_uuid='a8407fd5-9a92-4c38-a302-6d37463a335f')
