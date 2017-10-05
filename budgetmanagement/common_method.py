from projectmanagement.views import pie_chart_mainlist

def key_parameter_chart(start_date,end_date):
	
	colors=['#5485BC', '#AA8C30', '#5C9384', '#981A37', '#FCB319','#86A033', '#614931', '#00526F', '#594266', '#cb6828', '#aaaaab', '#a89375']
    main_list = []
    counter =0
    pie_object = ProjectParameter.objects.filter(active= 2,parent=obj)
    for y in pie_object:
        values = list(ProjectParameterValue.objects.filter(active= 2,keyparameter=y).values_list('parameter_value',flat=True))
        value = aggregate_project_parameters(pie_object[0],values)
        color = colors[counter]
        counter+=1
        main_list.append({'name': str(y.name),'y':value,'color':color})
    import ipdb; ipdb.set_trace()