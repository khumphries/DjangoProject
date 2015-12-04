from django.contrib.auth.models import User, Group, Permission
from myapplication.models import Dct

user = User.objects.create_user(username='Site_Manager', password='administrator')
site_manager_group = Group.objects.create(name='Site_Managers')
public_group = Group.objects.create(name='public')
private_group = Group.objects.create(name='Site_Manager_private')
home_dct = Dct(stName='Site_Manager', owner=user)
user.groups.add(site_manager_group,public_group,private_group)
user.save()
site_manager_group.save()
public_group.save()
private_group.save()
home_dct.save()