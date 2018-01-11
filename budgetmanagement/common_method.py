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
    
def get_month_dict(data):
    year = data.get('year')
    s_year = data.get('s_year')
    e_year = data.get('e_year')
    post_mnth = data.get('post_mnth')
    pre_mnth = data.get('pre_mnth')
    report_year = data.get('report_year')
    month = ''
    if (year < e_year and year > s_year) or e_year == year:
        sd = str(year) + "-"+str(post_mnth) + "-"+str(01)
        ed = str(year) + "-"+str(post_mnth) + "-"+str(30)
        month = str(sd)+" to "+str(ed)
    else:
        sd = str(report_year) + "-"+str(post_mnth) + "-"+str(01)
        ed = str(report_year) + "-"+str(post_mnth) + "-"+str(30)
        month = str(sd)+" to "+str(ed)
    return month
    
def get_months_classified(years_dict,report_obj,budget_obj):
    #this is to get the dict of the previous,current and next months 
    month_dict = {0:'',1:'January',2:'February',3:'March',4:'April',5:'May',
                      6:'June',7:'July',8:'August',9:'September',
                      10:'October',11:'November',12:'December',13:''}
    last_month_logic = {1:12,12:1}
    previous_month = {0:''}
    current_month = {1:''}
    future_month = {2:''}
    report_month = report_obj.start_date.month
    report_year = report_obj.start_date.year
    s_mnth = budget_obj.start_date.month
    e_mnth = budget_obj.end_date.month
    s_year = budget_obj.start_date.year
    e_year = budget_obj.end_date.year
    mnths_list = years_dict.get(report_year)
    if report_month in mnths_list:
        pre_mnth = report_month -1
        post_mnth = report_month +1
        sd = str(report_year)+'-'+str(pre_mnth)+'-'+str(01)
        ed = str(report_year) + "-"+str(pre_mnth) + "-"+str(30)
        previous_month[0] = str(sd)+" to "+str(ed)
        sd = str(report_year)+'-'+str(report_month)+'-'+str(01)
        ed = str(report_year) + "-"+str(report_month) + "-"+str(30)
        current_month[1] = str(sd)+" to "+str(ed)
        sd = str(report_year)+'-'+str(post_mnth)+'-'+str(01)
        ed = str(report_year) + "-"+str(post_mnth) + "-"+str(30)
        future_month[2] = str(sd)+" to "+str(ed)
        if report_month == 12:
            pre_mnth = report_month -1
            post_mnth = 1
            year = report_year+1
            data = {'pre_mnth':pre_mnth,'post_mnth':post_mnth,'e_year':e_year,'year':year,'s_year':s_year,'report_year':report_year}
            future_month[2] = get_month_dict(data) 
            
        elif report_month == 1:
            pre_mnth = 12
            post_mnth = report_month +1
            year = report_year-1 
            data = {'pre_mnth':pre_mnth,'post_mnth':post_mnth,'e_year':e_year,'year':year,'s_year':s_year,'report_year':report_year}
            previous_month[0] = get_month_dict(data) 
        elif report_month == s_mnth and report_year == s_year :
            previous_month={}
        elif report_month == e_mnth and report_year == e_year :
            future_month={}
    print previous_month,current_month,future_month
    return previous_month,current_month,future_month
                   
def get_years_list(year_diff,s_year,e_year,sm,em):
# this is to get the years of the budget and list of months of that particular year in a dict
    years_dict = {}
    mnth_list = []
    for yr in range(year_diff):
            year = s_year+yr
            if year == s_year :
                mnth_list = [i for i in range(sm,13)]
                years_dict.update({year:mnth_list})
            elif year == e_year :
                mnth_list = [i for i in range(1,em)]
                years_dict.update({year:mnth_list})
            else:
                mnth_list = [i for i in range(1,13)]
                years_dict.update({year:mnth_list})
    return years_dict
    
from datetime import datetime
from dateutil import relativedelta
def get_budget_months(budget_obj):
    # this is to get the months and years based on the budget start and end date
    sm = budget_obj.start_date.month
    em = budget_obj.end_date.month
    mnth_diff = em-sm
    years_dict={}
    mnth_list = []
    s_year = budget_obj.start_date.year
    e_year = budget_obj.end_date.year
    if s_year == e_year:
        mnth_list = [i for i in range(sm,13)]
        mnth_list.append(em)
        years_dict = {s_year:mnth_list}
    else:
        year_diff = (e_year - s_year)+1
        years_dict = get_years_list(year_diff,s_year,e_year,sm,em)
    return years_dict

def get_monthly_logic(report_obj,budget_obj):
    #this is to get the previous,current and next months dict
    total_months=[]
    years_list = []
    current_month ={}
    previous_month = {}
    future_month = {}
    years_dict = get_budget_months(budget_obj)
    previous_month,current_month,future_month = get_months_classified(years_dict,report_obj,budget_obj)
    return previous_month,current_month,future_month
