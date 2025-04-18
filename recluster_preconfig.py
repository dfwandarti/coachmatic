def set_recluster_preconfig(config):
    config.detailing_per_field=True
    config.language='PT'
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
    config.effort_axis='aggregatetimespent'
    config.effort_axis_friendly='Σ Tempo Gasto'
    config.effort_per_state=True
    config.effort_per_issuetype=True
    config.effort_who=True
    config.which_analysis=['export_csv', 'cfd', 'effort']
    config.expand_worklog=True
    config.user_pct_ca=''
    config.count_bugs_jql=''
    
    # config.export_csv_add_fields=['pai.Chave', 'pai.Tipo de Item', 'pai.Σ Tempo Gasto', 'Orçamento Final', 'Flagged', 'Σ Tempo Gasto']
    # config.export_csv_add_fields_custom=['issuekey', 'issuetype', 'aggregatetimespent', 'customfield_10035', 'customfield_10640', 'aggregatetimespent']
    # config.expot_csv_jql_fields=['jql:Chave[issueFunction in linkedIssuesOf("issueFunction in parentsOf('+chr(39)+'issue = ?'+chr(39)+')") and issuetype=Demanda]', 'jql:Orçamento Final[issueFunction in linkedIssuesOf("issueFunction in parentsOf('+chr(39)+'issue = ?'+chr(39)+')") and issuetype=Demanda]']
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
    # config.effort_axis='aggregatetimespent'
    # config.effort_axis_friendly='Σ Tempo Gasto'
    # config.effort_per_state=True
    # config.effort_per_issuetype=True
    # config.effort_who=True
    # config.which_analysis=['export_csv', 'cfd', 'effort']
    # config.expand_worklog=True
    # config.user_pct_ca=''
    # config.count_bugs_jql=''
    
    config.post_processing_modules = "recluster" #",hour_per_demand"
