from django.contrib import admin
from .models import ProjectStatus, Project, ExpenseType, Expense, Employee, WorkRecord, TotalAmountDetails, \
    PaymentDetails

from django.contrib import admin
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User


def create_groups_and_permissions():
    # Crear grupos
    president_group, _ = Group.objects.get_or_create(name='President')
    vicepresident_group, _ = Group.objects.get_or_create(name='Vicepresident')
    worker_group, _ = Group.objects.get_or_create(name='Worker')

    # Obtener permisos
    project_ct = ContentType.objects.get_for_model(Project)
    view_project_permission = Permission.objects.get(codename='view_project', content_type=project_ct)
    change_project_permission = Permission.objects.get(codename='change_project', content_type=project_ct)
    delete_project_permission = Permission.objects.get(codename='delete_project', content_type=project_ct)
    add_project_permission = Permission.objects.get(codename='add_project', content_type=project_ct)

    # Asignar permisos a los grupos
    president_group.permissions.set(
        [view_project_permission, change_project_permission, delete_project_permission, add_project_permission])
    vicepresident_group.permissions.set(
        [view_project_permission, change_project_permission, delete_project_permission, add_project_permission])
    worker_group.permissions.set([view_project_permission])


create_groups_and_permissions()

admin.site.register(ProjectStatus)
admin.site.register(Project)
admin.site.register(ExpenseType)
admin.site.register(Expense)
admin.site.register(Employee)
admin.site.register(WorkRecord)
admin.site.register(TotalAmountDetails)
admin.site.register(PaymentDetails)
