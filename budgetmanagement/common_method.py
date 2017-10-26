from projectmanagement.views import pie_chart_mainlist,aggregate_project_parameters
from projectmanagement.models import *

def key_parameter_chart(obj,parameter_id):
	
    colors=['#5485BC', '#AA8C30', '#5C9384', '#981A37', '#FCB319','#86A033', '#614931', '#00526F', '#594266', '#cb6828', '#aaaaab', '#a89375']
    main_list = []
    name_list = []
    para_name = {}
    pip_title_name = []
    pin_title_name = []
    counter =0
    parameter_obj = ProjectParameter.objects.filter(active= 2,project=obj,parent=None)
    pie_object = ProjectParameter.objects.filter(active= 2,project=obj,parent=None)
    parameter_obj = ProjectParameter.objects.filter(active= 2,project=obj,parent=None)
    
    for y in pie_object:
        if y.parameter_type=='PIN' or y.parameter_type=='PIP':
            values = list(ProjectParameterValue.objects.filter(active= 2,keyparameter=y).values_list('parameter_value',flat=True))
            value = aggregate_project_parameters(pie_object[0],values)
            color = colors[counter]
            counter+=1
            main_list.append({'name': str(y.name),'y':value,'color':color})
        if y.parameter_type in para_name:
            para_name[y.parameter_type].append(main_list)
        else:
            para_name.setdefault(y.parameter_type,[])
            para_name[y.parameter_type].append(main_list)
            name_list.append(str(y.name))
        if y.parameter_type == 'PIN':
            pin_title_name.append(str(y.name))
        if y.parameter_type == 'PIP':
            pip_title_name.append(str(y.name))
    master_sh = para_name
    master_sh_len = {key:len(values) for key,values in master_sh.items()}
    master_pin = map(lambda x: "Batch_size_" + str(x), range(master_sh_len.get('PIN',0)))
    master_pip = map(lambda x: "Beneficary_distribution_"+ str(x), range(master_sh_len.get('PIP',0)))
    
    return master_pip,master_pin,pin_title_name,pip_title_name,master_sh
