from django.urls import path
from . import views
from .views import *

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('project/<int:project_id>/', views.project_detail_dash, name='project_detail_dash'),

    # Project URLs
    path('projects/', views.ProjectListView.as_view(), name='project_list'),
    path('project/create/', views.ProjectCreateView.as_view(), name='project_create'),
    path('project/<int:pk>/', views.ProjectDetailView.as_view(), name='project_detail'),
    path('project/<int:pk>/update/', views.ProjectUpdateView.as_view(), name='project_update'),
    path('project/<int:pk>/delete/', views.ProjectDeleteView.as_view(), name='project_delete'),

    # Expense URLs
    path('expense/', views.ExpenseListView.as_view(), name='expense_list'),
    path('expense/create/', views.ExpenseCreateView.as_view(), name='expense_create'),
    path('expense/<int:pk>/', views.ExpenseDetailView.as_view(), name='expense_detail'),
    path('expense/<int:pk>/update/', views.ExpenseUpdateView.as_view(), name='expense_update'),
    path('expense/<int:pk>/delete/', views.ExpenseDeleteView.as_view(), name='expense_delete'),

    # Income URLs
    # path('income/', views.IncomeListView.as_view(), name='income_list'),
    # path('income/add/', views.IncomeCreate.as_view(), name='income_create'),
    # path('income/<int:pk>/', views.IncomeUpdate.as_view(), name='income_update'),
    # path('income/<int:pk>/delete/', views.IncomeDelete.as_view(), name='income_delete'),

    # Employee URLs
    path('employee/', views.EmployeeListView.as_view(), name='employee_list'),
    path('employee/create/', views.EmployeeCreate.as_view(), name='employee_create'),
    path('employee/<int:pk>/update/', views.EmployeeUpdate.as_view(), name='employee_update'),
    path('employee/<int:pk>/delete/', views.EmployeeDelete.as_view(), name='employee_delete'),

    # Hours report
    path('employee/weekly_hours_report/', views.employee_weekly_hours_report, name='employee_weekly_hours_report'),

    # WorkRecord URLs
    path('workrecord/', views.WorkRecordListView.as_view(), name='workrecord_list'),
    path('workrecord/create/', views.WorkRecordCreate.as_view(), name='workrecord_create'),
    path('workrecord/<int:pk>/update/', views.WorkRecordUpdate.as_view(), name='workrecord_update'),
    path('workrecord/<int:pk>/delete/', views.WorkRecordDelete.as_view(), name='workrecord_delete'),

    path('totalamountdetails/', TotalAmountDetailsListView.as_view(), name='totalamountdetails_list'),
    path('totalamountdetails/create/', TotalAmountDetailsCreateView.as_view(), name='totalamountdetails_create'),
    path('totalamountdetails/<int:pk>/', TotalAmountDetailsDetailView.as_view(), name='totalamountdetails_detail'),
    path('totalamountdetails/<int:pk>/update/', TotalAmountDetailsUpdateView.as_view(), name='totalamountdetails_update'),
    path('totalamountdetails/<int:pk>/delete/', TotalAmountDetailsDeleteView.as_view(), name='totalamountdetails_delete'),

    path('payment/', PaymentDetailsListView.as_view(), name='paymentdetails_list'),
    path('payment/create/', PaymentDetailsCreateView.as_view(), name='paymentdetails_create'),
    path('payment/<int:pk>/', PaymentDetailsDetailView.as_view(), name='paymentdetails_detail'),
    path('payment/<int:pk>/update/', PaymentDetailsUpdateView.as_view(), name='paymentdetails_update'),
    path('payment/<int:pk>/delete/', PaymentDetailsDeleteView.as_view(), name='paymentdetails_delete'),
]
