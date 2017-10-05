from projectmanagement.views import pie_chart_mainlist

def key_parameter_chart(start_date,end_date):
	
	colors=['#5485BC', '#AA8C30', '#5C9384', '#981A37', '#FCB319','#86A033', '#614931', '#00526F', '#594266', '#cb6828', '#aaaaab', '#a89375']
    main_list = []
    name_list = []
    para_name = {}
    pip_title_name = []
    pin_title_name = []
    counter =0
    pie_object = ProjectParameter.objects.filter(active= 2,parent=obj)
    for y in pie_object:
        if y.parameter_type=='PIN' or y.parameter_type=='PIP':

            values = list(ProjectParameterValue.objects.filter(active= 2,keyparameter=y,start_date__gte=start_date, end_date__lte=end_date ).values_list('parameter_value',flat=True))
            value = aggregate_project_parameters(pie_object[0],values)
            color = colors[counter]
            counter+=1
            main_list.append({'name': str(y.name),'y':value,'color':color})
    if i.parameter_type in para_name:
            para_name[i.parameter_type].append(main_list)
        else:
            para_name.setdefault(i.parameter_type,[])
            para_name[i.parameter_type].append(main_list)
            name_list.append(str(i.name))
        if i.parameter_type == 'PIN':
            pin_title_name.append(str(i.name))
        if i.parameter_type == 'PIP':
            pip_title_name.append(str(i.name))