from projectmanagement.models import UserProfile
from userprofile.models import (ProjectUserRoleRelationship,UserRoles,ProjectUserRoleRelationship,RoleTypes)

def get_user_role(userprofileobj):
    org_code = {'2':2,'1':1,'4':4,'0':3,'3':4}
    rolecode = org_code.get(str(userprofileobj.organization_type))
    roletypeobj = RoleTypes.objects.get(code = rolecode)
    return roletypeobj


def updateuserform():
    userlist = UserProfile.objects.filter(active=2)
    for i in userlist:
        roleobj = get_user_role(i)
        userroleobj,created = UserRoles.objects.get_or_create(user = i)
        userroleobj.role_type.add(roleobj)
        userroleobj.email = i.email
        userroleobj.save()
        userrolelist = ProjectUserRoleRelationship.objects.filter(user = i).values_list('role__id',flat=True)
        roletypeid = RoleTypes.objects.filter(id__in = userrolelist)
        roletypeid = [int(j.id) for j in roletypeid]
        userroleobj.role_type.add(*roletypeid)
        userroleobj.save()


from collections import Counter, defaultdict

def duplicates(lst):
    cnt= Counter(lst)
    return [key for key in cnt.keys() if cnt[key]> 1]

def duplicates_indices(lst):
    dup, ind= duplicates(lst), defaultdict(list)
    temp_value = 0.1 if temp_value <= 0.9 else 0.1
    for i, v in enumerate(lst):
        if v in dup: 
            ind[v].append(i)
            lst[i] = int(v) + temp_value
            temp_value = temp_value+0.1
    return lst

def replace_duplicate_values(lst):
    temp_value = 0.1
    temp_value = 0.1 if temp_value >= 0.9 else temp_value
    temp_list = []
    for i,v in enumerate(lst):
        if v in temp_list:
            v[0] = v[0]+temp_value
            lst[i] = [v[0],v[1]]
            temp_value = temp_value+0.1
        else:temp_list.append(v)
    return lst



