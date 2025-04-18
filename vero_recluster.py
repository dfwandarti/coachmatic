import coach_matic

config = coach_matic.Config()
config.detailing_per_field=True
config.language='PT'
config.project_name='VIP E Vero - recluster'
config.jira_url='https://jira.objective.com.br'
config.jira_user='svc_jira-sync-customers'
config.jira_key='0tl9-gi5oXIw3tEch3gl'
config.jql='issueFunction in subtasksOf('+chr(39)+'issueFunction in linkedIssuesOf("issuetype = Demanda and (status not in (Cancelado, Fechado) or resolved > -30d) and \\\\"Taskboard Project Id\\\\" in (73867, 73884, 73885)", "demandou") and project in (VIP, VERO)'+chr(39)+') '
config.all_statuses=['aberto', 'postergado', 'to do', 'in progress', 'to review', 'review', 'done']
config.all_sub_statuses=[['aberto'], ['postergado'], ['to do'], ['in progress'], ['to review'], ['review'], ['done']]
config.downstream_start='aberto'
config.downstream_stop='done'
config.downstream_statuses=['aberto', 'postergado', 'to do', 'in progress', 'to review', 'review', 'done']
config.waiting_statuses=[]
config.receiver_email='daniel.wandarti@objective.com.br'
config.schedule_day='mon.sh'
config.repeat_for_each_field_value='pai.Chave'
config.export_csv_add_fields=['pai.Chave', 'pai.Tipo de Item', 'pai.Σ Tempo Gasto', 'Orçamento Final', 'Flagged', 'Σ Tempo Gasto']
config.export_csv_add_fields_custom=['issuekey', 'issuetype', 'aggregatetimespent', 'customfield_10035', 'customfield_10640', 'aggregatetimespent']
config.expot_csv_jql_fields=['jql:Chave[issueFunction in linkedIssuesOf("issueFunction in parentsOf('+chr(39)+'issue = ?'+chr(39)+')") and issuetype=Demanda]', 'jql:Orçamento Final[issueFunction in linkedIssuesOf("issueFunction in parentsOf('+chr(39)+'issue = ?'+chr(39)+')") and issuetype=Demanda]']
config.total_age_percentil=False
config.bag_of_words_axis=''
config.bag_of_words_axis_friendly=''
config.bag_of_words_exclude=''
config.subjql=''
config.blocker_days=30
config.blocker_field='Flagged'
config.blocker_field_description=''
config.cfd_days=90
config.wip_evolution_chart=True
config.spc_time_window=1
config.discriminated_throughput_field=''
config.tail_analysis_axis='CycleTime'
config.tail_analysis_exclude=''
config.effort_axis='aggregatetimespent'
config.effort_axis_friendly='Σ Tempo Gasto'
config.effort_per_state=True
config.effort_per_issuetype=True
config.effort_who=True
config.which_analysis=['export_csv', 'cfd', 'effort']
config.expand_worklog=True
config.user_pct_ca=''
config.count_bugs_jql=''

config.post_processing_modules = "recluster" #",hour_per_demand"

coach_matic.run_and_email(config, preset_uuid='97c42dcc-cd58-4f6a-9b62-109ad7c2a73e')
