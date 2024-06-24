from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView
from django.db.models import Sum

from .forms import IncomeForm, ExpenseForm, EmployeeForm, WorkRecordForm, ProjectForm, PaymentDetailsForm, \
    TotalAmountDetailsForm
from .models import Project, WorkRecord, ProjectStatus, Expense, Income, Employee, TotalAmountDetails, \
    PaymentDetails


def project_detail_dash(request, project_id):
    project = Project.objects.get(pk=project_id)
    total_amount_details = project.total_amount_details.all()
    total_project_hours = project.total_hours()

    # Obtenemos todos los registros de trabajo asociados con este proyecto
    work_records = WorkRecord.objects.filter(project=project)

    # Calculamos el total de horas y el costo total por empleado
    employee_totals = {}
    for record in work_records:
        if record.employee.full_name not in employee_totals:
            employee_totals[record.employee.full_name] = {'hours': record.hours,
                                                          'total_cost': record.hours * record.employee.hourly_rate}
        else:
            employee_totals[record.employee.full_name]['hours'] += record.hours
            employee_totals[record.employee.full_name]['total_cost'] += record.hours * record.employee.hourly_rate

    # Calculamos el costo total del proyecto
    total_cost = sum(employee_total['total_cost'] for employee_total in employee_totals.values())

    # Calculamos el total de gastos
    total_expenses = project.total_expenses()

    # Calculamos el total de ingresos
    total_income = project.total_income()

    # Calculamos el balance
    balance = project.total_amount - total_income

    return render(request, 'project_detail_dash.html', {
        'project': project,
        'total_amount_details': total_amount_details,
        'employee_totals': employee_totals,
        'total_cost': total_cost,
        'total_expenses': total_expenses,
        'total_income': total_income,
        'balance': balance,
        'total_project_hours': total_project_hours
    })


def dashboard(request):
    projects = Project.objects.all()
    project_statuses = ProjectStatus.objects.all()

    # Obtener el valor de búsqueda del cuadro de texto
    search_query = request.GET.get('search', None)

    # Obtener el valor del estado seleccionado
    status_filter = request.GET.get('status', None)

    # Filtrar proyectos por nombre si se proporciona una consulta de búsqueda
    if search_query:
        projects = projects.filter(name__icontains=search_query)

    # Filtrar proyectos por estado si se selecciona uno
    if status_filter:
        projects = projects.filter(status__name=status_filter)

    # Calcular métricas generales
    total_projects = projects.count()
    total_income = Income.objects.aggregate(total=Sum('value'))['total'] or 0
    total_expenses = Expense.objects.aggregate(total=Sum('value'))['total'] or 0
    total_balance = total_income - total_expenses
    total_total_amount = projects.aggregate(total=Sum('total_amount'))['total'] or 0

    # Calcular proyectos por estado
    project_status_summary = {
        status.name: projects.filter(status=status).count()
        for status in project_statuses
    }

    context = {
        'projects': projects,
        'project_statuses': project_statuses,
        'total_projects': total_projects,
        'total_income': total_income,
        'total_expenses': total_expenses,
        'total_balance': total_balance,
        'total_total_amount': total_total_amount,
        'project_status_summary': project_status_summary,
    }

    return render(request, 'dashboard.html', context)


class ProjectListView(ListView):
    model = Project
    template_name = 'project_list.html'
    context_object_name = 'projects'


class ProjectCreateView(CreateView):
    model = Project
    form_class = ProjectForm
    template_name = 'project_form.html'
    success_url = reverse_lazy('dashboard')


class ProjectDetailView(DetailView):
    model = Project
    template_name = 'project_detail.html'


class ProjectUpdateView(UpdateView):
    model = Project
    form_class = ProjectForm
    template_name = 'project_update_form.html'
    success_url = reverse_lazy('dashboard')


class ProjectDeleteView(DeleteView):
    model = Project
    template_name = 'project_confirm_delete.html'
    success_url = reverse_lazy('dashboard')


class ExpenseListView(ListView):
    model = Expense
    template_name = 'expense_list.html'
    context_object_name = 'expenses'


class ExpenseCreateView(CreateView):
    model = Expense
    form_class = ExpenseForm
    template_name = 'expense_form.html'
    success_url = reverse_lazy('dashboard')


class ExpenseDetailView(DetailView):
    model = Expense
    template_name = 'expense_detail.html'


class ExpenseUpdateView(UpdateView):
    model = Expense
    form_class = ExpenseForm
    template_name = 'expense_update_form.html'
    success_url = reverse_lazy('dashboard')


class ExpenseDeleteView(DeleteView):
    model = Expense
    template_name = 'expense_confirm_delete.html'
    success_url = reverse_lazy('dashboard')


class IncomeListView(ListView):
    model = Income
    template_name = 'income_list.html'
    context_object_name = 'incomes'


class IncomeCreate(CreateView):
    model = Income
    form_class = IncomeForm
    template_name = 'income_form.html'
    success_url = reverse_lazy('income_list')


class IncomeUpdate(UpdateView):
    model = Income
    form_class = IncomeForm
    template_name = 'income_form.html'
    success_url = reverse_lazy('income_list')


class IncomeDelete(DeleteView):
    model = Income
    success_url = reverse_lazy('income_list')


class EmployeeListView(ListView):
    model = Employee
    template_name = 'employee_list.html'
    context_object_name = 'employees'


class EmployeeCreate(CreateView):
    model = Employee
    form_class = EmployeeForm
    template_name = 'employee_form.html'
    success_url = reverse_lazy('employee_list')


class EmployeeUpdate(UpdateView):
    model = Employee
    form_class = EmployeeForm
    template_name = 'employee_form.html'
    success_url = reverse_lazy('employee_list')


class EmployeeDelete(DeleteView):
    model = Employee
    template_name = 'employee_confirm_delete.html'
    success_url = reverse_lazy('employee_list')


class WorkRecordListView(ListView):
    model = WorkRecord
    template_name = 'workrecord_list.html'
    context_object_name = 'workrecords'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['projects'] = Project.objects.all()
        context['employees'] = Employee.objects.all()
        return context


class WorkRecordCreate(CreateView):
    model = WorkRecord
    form_class = WorkRecordForm
    template_name = 'workrecord_form.html'
    success_url = reverse_lazy('workrecord_list')


class WorkRecordUpdate(UpdateView):
    model = WorkRecord
    form_class = WorkRecordForm
    template_name = 'workrecord_form.html'
    success_url = reverse_lazy('workrecord_list')


class WorkRecordDelete(DeleteView):
    model = WorkRecord
    template_name = 'workrecord_confirm_delete.html'
    success_url = reverse_lazy('workrecord_list')


class TotalAmountDetailsListView(ListView):
    model = TotalAmountDetails
    template_name = 'totalamountdetails_list.html'
    context_object_name = 'total_amount_details'


class TotalAmountDetailsCreateView(CreateView):
    model = TotalAmountDetails
    form_class = TotalAmountDetailsForm
    template_name = 'totalamountdetails_form.html'
    success_url = reverse_lazy('totalamountdetails_list')


class TotalAmountDetailsDetailView(DetailView):
    model = TotalAmountDetails
    template_name = 'totalamountdetails_detail.html'


class TotalAmountDetailsUpdateView(UpdateView):
    model = TotalAmountDetails
    form_class = TotalAmountDetailsForm
    template_name = 'totalamountdetails_form.html'
    success_url = reverse_lazy('totalamountdetails_list')


class TotalAmountDetailsDeleteView(DeleteView):
    model = TotalAmountDetails
    template_name = 'totalamountdetails_confirm_delete.html'
    success_url = reverse_lazy('totalamountdetails_list')


class PaymentDetailsListView(ListView):
    model = PaymentDetails
    template_name = 'paymentdetails_list.html'
    context_object_name = 'payment_details'


class PaymentDetailsCreateView(CreateView):
    model = PaymentDetails
    form_class = PaymentDetailsForm
    template_name = 'paymentdetails_form.html'
    success_url = reverse_lazy('paymentdetails_list')


class PaymentDetailsDetailView(DetailView):
    model = PaymentDetails
    template_name = 'paymentdetails_detail.html'


class PaymentDetailsUpdateView(UpdateView):
    model = PaymentDetails
    form_class = PaymentDetailsForm
    template_name = 'paymentdetails_form.html'
    success_url = reverse_lazy('paymentdetails_list')


class PaymentDetailsDeleteView(DeleteView):
    model = PaymentDetails
    template_name = 'paymentdetails_confirm_delete.html'
    success_url = reverse_lazy('paymentdetails_list')
