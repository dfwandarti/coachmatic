import coach_matic

config = coach_matic.Config()
config.all_statuses=["aberto","postergado","to do","in progress","to review","review","tratamento","impedido","desenvolvimento","corrigido","fechado","done"]
config.export_csv_add_fields=["pai.Assunto"]
config.export_csv_add_fields_custom=[]
config.project_name='VIP - Demandas'
config.jira_url='https://jira.objective.com.br'
config.jira_user='svc_jira-sync-customers'
config.jira_key='0tl9-gi5oXIw3tEch3gl'
config.jql='project = VIP AND (issuetype = "Pedido de Suporte" or (issuetype = chamado and labels = CST2)) AND status != Cancelado AND (status != Done OR resolved > -90d)'
config.jql='project = VIP AND issuetype = chamado AND status != Cancelado AND (status != Done OR resolved > -90d)'
config.downstream_start='to do'
config.downstream_stop='fechado'
config.downstream_statuses=["to do","in progress","to review","review","tratamento","impedido","desenvolvimento","corrigido","fechado"]
config.receiver_email='daniel.wandarti@objective.com.br' #',erick.kleim@objective.com.br,eduardo.hideo@objective.com.br'
config.which_analysis=['export_csv'] #'bag_of_words'] #, 'tail_analysis', 'total_age', 'aging_spc']
config.schedule_day='tue.sh'
config.total_age_percentil=True
config.blocker_field='Impedido'
config.blocker_field_description='Último Motivo Impedimento'
config.bag_of_words_axis = "aggregatetimespent"
config.bag_of_words_exclude = "itsmvero, dia, anexo, cliente, bom, boa, vero, tarde, tudo, bem,  clientes, precisamos, itsm, https, verificar"


coach_matic.run_and_email(config, preset_uuid='2a03e749-9ef8-45dd-abe9-4c947a3e4f40')
