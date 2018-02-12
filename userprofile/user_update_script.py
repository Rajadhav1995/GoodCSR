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
        print "roles are tagged successuly for - %s"%i


from collections import Counter, defaultdict

def duplicates(lst):
    cnt= Counter(lst)
    return [key for key in cnt.keys() if cnt[key]> 1]

def duplicates_indices(lst):
    dup, ind= duplicates(lst), defaultdict(list)
    for i, v in enumerate(lst):
        if v in dup: ind[v].append(i)
    return ind

