import coach_matic

config = coach_matic.Config()
config.all_statuses=['backlog', 'priorizado', 'detalhando', 'detalhamento pronto', 'aguardando desenvolvimento', 'desenvolvendo', 'desenvolvimento pronto', 'testando', 'teste pronto', 'homologando', 'homologação pronta', 'subindo para produção', 'done', 'concluido']
config.export_csv_add_fields=[]
config.export_csv_add_fields_custom=[]
config.project_name='Blinket Diário'
config.jira_url='https://eduzzjira.atlassian.net/'
config.jira_user='andressa.benetti@objective.com.br'
config.jira_key='KMnHbSX0QOgn0P3XrQv35E3B'
config.jql='project in (BOK) AND issuetype in (Bug, Spike, Story, "Bug - Hotfix", "GLPI - Causa Raiz") and status != Cancelado and  (status != Concluido or resolved > -90d)'
config.jql='project in (PFO, NXTO) AND issuetype in (Bug, Spike, Story, "Bug - Hotfix", "GLPI - Causa Raiz") and status != Cancelado and  (status != Concluido or resolved > -90d)'
config.downstream_start='detalhando'
config.downstream_stop='homologação pronta'
config.downstream_statuses=['detalhando', 'detalhamento pronto', 'aguardando desenvolvimento', 'desenvolvendo', 'desenvolvimento pronto', 'testando', 'teste pronto', 'homologando', 'homologação pronta']
config.receiver_email='daniel.wandarti@objective.com.br'
config.which_analysis=['blockers', 'export_csv'] #'aging_spc', 'one_chart_aging_spc']
config.schedule_day='1 8 * * MON,TUE,WED,THU,FRI '
config.blocker_days=30
config.blocker_field='Flagged'
config.blocker_field_description='Motivo do impedimento'

with open("temp\\a\\extract_jira.zip", "rb") as f:
    config.extract_jira_zip = f.read()
preset_uuid='a'
config.export_csv_add_fields = ['customfield_14659:Component', 'customfield_12193:T-shirt Size', 'customfield_12181:class,priority:priority', 'customfield_15627:Flagged', 'customfield_14617:Description Blocking']
config.blocker_field_description = 'Description Blocking'

coach_matic.run_and_email(config, preset_uuid='b1b106c8-f66a-4771-a3e1-b03ed9f8283f')
