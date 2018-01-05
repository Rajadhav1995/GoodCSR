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
    
def get_months_classified(total_months,month_dict,report_month):
    current_month = previous_month = future_month = ''
    for mnth in total_months:
        if mnth == report_month: 
            current_month = month_dict.get(report_month)
        elif mnth < report_month:
            pre_month = report_month-1
            previous_month = month_dict.get(pre_month)
        elif mnth > report_month :
            post_month = report_month+1
            future_month = month_dict.get(post_month)
    return previous_month,current_month,future_month
   
from datetime import datetime, timedelta
from calendar import monthrange
def monthdelta(df):
    d1 = df[0]
    d2 = df[1]
    delta = 0
    while True:
        mdays = monthrange(d1.year, d1.month)[1]
        d1 += timedelta(days=mdays)
        if d1 <= d2:
            delta += 1
        else:
            break
    return delta 
    
from datetime import datetime
from dateutil import relativedelta
def get_budget_months(budget_obj):
    sm = budget_obj.start_date.month
    em = budget_obj.end_date.month
    mnth_diff = em-sm
    years_dict={}
    mnth_list = []
    s_year = budget_obj.start_date.year
    e_year = budget_obj.end_date.year
    date1 = datetime.strptime(budget_obj.start_date.strftime('%Y-%m-%d'), '%Y-%m-%d')
    date2 = datetime.strptime(budget_obj.end_date.strftime('%Y-%m-%d'), '%Y-%m-%d')
    rel = relativedelta.relativedelta(date2, date1)
    rel.months
    df = [date1,date2]
    delta = monthdelta(df)
    if s_year == e_year:
        mnth_list = [sm+i for i in range(delta)]
        mnth_list.append(em)
        years_dict = {s_year:mnth_list}
    else:
        year_diff = (e_year - s_year)+1
        years_list = [s_year+i for i in range(year_diff)]
        for yr in years_list:
            if yr == s_year :
                mnth_list = [i for i in range(sm,13)]
                years_dict.update({yr:mnth_list})
            elif yr == e_year :
                mnth_list = [i for i in range(13)]
                years_dict.update({yr:mnth_list})
            else:
                mnth_list = [i for i in range(em,em+1)]
                years_dict.update({yr:mnth_list})
    return years_dict
    
def get_monthly_logic(report_obj,budget_obj):
    total_months=[]
    years_list = []
    current_month = previous_month = future_month = ''
    month_dict = {'January':1,'February':2,'March':3,'April':4,'May':5,
                      'June':6,'July':7,'August':8,'September':9,
                      'October':10,'November':11,'December':12}
    report_month= report_obj.start_date.month
#    report_em = report_obj.end_date.month
    report_year = report_obj.start_date.year
#    report_ey = report_obj.end_date.year
    budget_month = budget_obj.start_date.month
    budget_end_month = budget_obj.end_date.month
    budget_year = budget_obj.start_date.year
    budget_end_year = budget_obj.end_date.year
    budget_months = get_budget_months(budget_obj)
    
#    previous_month,current_month,future_month = get_months_classified(total_months,month_dict,report_month)
    
    return previous_month,current_month,future_month
