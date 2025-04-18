import coach_matic

config = coach_matic.Config()
config.all_statuses=["aberto","postergado","to do","in progress","to review","review","done"]
config.export_csv_add_fields=[]
config.export_csv_add_fields_custom=[]
config.project_name='VIP - Evolucao'
config.jira_url='https://jira.objective.com.br'
config.jira_user='svc_jira-sync-customers'
config.jira_key='0tl9-gi5oXIw3tEch3gl'
config.jql='project = VIP AND issueFunction in subtasksOf(\'issuetype in (OS, task) and status = fechado and status changed to fechado after -90d\')'
config.downstream_start='aberto'
config.downstream_stop='done'
config.downstream_statuses=["aberto","postergado","to do","in progress","to review","review","done"]
config.receiver_email='daniel.wandarti@objective.com.br' #',erick.kleim@objective.com.br,eduardo.hideo@objective.com.br'
config.which_analysis=['pct_ca'] #'bag_of_words'] #'export_csv', 'tail_analysis', 'total_age', 'aging_spc']
config.schedule_day='tue.sh'
config.total_age_percentil=True
config.blocker_field='Impedido'
config.blocker_field_description='Último Motivo Impedimento'
config.bag_of_words_axis = "aggregatetimespent"
config.bag_of_words_exclude = "itsmvero, dia, anexo, cliente, bom, boa, vero, tarde, tudo, bem,  clientes, precisamos, itsm, https, verificar"
config.user_pct_ca = "ana.multini,lubia.cordeiro,vitor.nascimento"
config.expand_worklog = True
config.count_bugs_jql = "" # "issuetype = \"Bug de Alfa\" and parent = ?"
config.effort_per_issuetype = True

config.jql = 'project = Vero and issuetype in (OS, Bug) and (issueFunction in linkedIssuesOf(\'issuetype = Demanda and (status not in (Done, Fechado) or resolved > -90d) and "Taskboard Project Id" = 73867\', "demandou") or "Taskboard Project Id" = 73867)'
config.downstream_statuses = config.all_statuses=["desenvolvimento","beta-teste", "done"]
config.downstream_start='desenvolvimento'

coach_matic.run_and_email(config, preset_uuid='2a03e749-9ef8-45dd-abe9-4c947a3e4f40')
