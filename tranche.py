from projectmanagement.models import *
from budgetmanagement.models import (Tranche,ProjectReport,Budget,
                                    ProjectBudgetPeriodConf,BudgetPeriodUnit)

def get_project_budget_utilized_amount(projectobj,budgetobj):
#    to get the project utilized amount for budget 
    budget_periodlist = ProjectBudgetPeriodConf.objects.filter(project = projectobj,budget = budgetobj,active=2).values_list('id', flat=True)
    budget_period_utilizedamount = BudgetPeriodUnit.objects.filter(budget_period__id__in=budget_periodlist).values_list('utilized_unit_cost', flat=True)
    budget_period_utilizedamount = map(lambda x:x if x else 0,budget_period_utilizedamount)
    final_budget_period_utilizedamount = sum(map(int,budget_period_utilizedamount))
    return final_budget_period_utilizedamount

def auto_update_tranche_amount(final_budget_utilizedamount,project):
    tranchelist = Tranche.objects.filter(project=project,active=2).order_by("disbursed_date")
    for i in tranchelist:
        i.utilized_amount = 0
        i.save()
        if final_budget_utilizedamount > 0:
            if i.actual_disbursed_amount< final_budget_utilizedamount:
                i.utilized_amount = i.actual_disbursed_amount
                i.save()
                final_budget_utilizedamount = final_budget_utilizedamount-i.utilized_amount
            else:
                i.utilized_amount = final_budget_utilizedamount 
                i.save()
                final_budget_utilizedamount = 0
    return tranchelist

def updatetranche():
    projectlist = Project.objects.filter(active=2)
    for project in projectlist:
            budgetobj = Budget.objects.latest_one(project = project,active=2)
            if budgetobj:
                final_budget_utilizedamount = get_project_budget_utilized_amount(project,budgetobj)
                updatedobj = auto_update_tranche_amount(final_budget_utilizedamount,project)
                if updatedobj:
                    print "-----successfully updated for project", project.name,project.id
                else:
                    print "----no tranches",project.name,project.id
            else:
                print "*****Budget is not created for the project",project.name,project.id
