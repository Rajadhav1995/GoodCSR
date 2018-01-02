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
    
import pytz
from budgetmanagement.models import Answer ,QuarterReportSection
from budgetmanagement.templatetags import question_tags
def get_index_quarter(report_obj):
    previousquarter_list={}
    currentquarter_list={}
    futurequarter_list={}
    block_type = {1:3,2:4,3:5}
    quarter_lists=Answer.objects.filter(
        content_type = ContentType.objects.get_for_model(report_obj),object_id=report_obj.id).exclude(quarter=None).values_list('quarter',flat=True)
    quarter_sections = QuarterReportSection.objects.filter(active=2,id__in = list(set(quarter_lists)))
    
    for i in quarter_sections:
        sd = i.start_date
        ed = i.end_date
        period = str(sd.strftime("%Y-%m-%d"))+' to '+str(ed.strftime("%Y-%m-%d"))
        blocks = block_type.get(i.quarter_type)
        ques_list = question_tags.get_previous_tab_quests(blocks)
        tab_removed,removed_id = question_tags.get_quarter_tab_removed(ques_list,period,blocks,i,report_obj)
        if i.quarter_type == 1 and tab_removed == 'false':
            previousquarter_list.update({int(i.quarter_order):period})
        elif i.quarter_type == 2 and tab_removed == 'false':
            currentquarter_list.update({int(i.quarter_order):period})
        elif i.quarter_type == 3 and tab_removed == 'false':
            futurequarter_list.update({int(i.quarter_order):period})
    return previousquarter_list,currentquarter_list,futurequarter_list
    
    
    

