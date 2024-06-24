from django.contrib import admin
from .models import ProjectStatus, Project, IncomeType, ExpenseType, Income, Expense, Employee, WorkRecord, TotalAmountDetails, PaymentDetails

admin.site.register(ProjectStatus)
admin.site.register(Project)
admin.site.register(IncomeType)
admin.site.register(ExpenseType)
admin.site.register(Income)
admin.site.register(Expense)
admin.site.register(Employee)
admin.site.register(WorkRecord)
admin.site.register(TotalAmountDetails)
admin.site.register(PaymentDetails)