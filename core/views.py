from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView
from django.db.models import Sum
from django.contrib.auth.decorators import login_required, permission_required
from django.utils.decorators import method_decorator
from django.contrib.auth import login as auth_login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
import datetime
from django.utils import timezone

from .forms import ExpenseForm, EmployeeForm, WorkRecordForm, ProjectForm, PaymentDetailsForm, TotalAmountDetailsForm
from .models import Project, WorkRecord, ProjectStatus, Expense, Employee, TotalAmountDetails, PaymentDetails


def get_previous_week_range():
    today = timezone.now().date()
    start_of_week = today - datetime.timedelta(days=today.weekday() + 7)
    end_of_week = start_of_week + datetime.timedelta(days=6)
    return start_of_week, end_of_week


def login(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                auth_login(request, user)
                return redirect('dashboard')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})


@login_required
@permission_required('app.view_project', raise_exception=True)
def project_detail_dash(request, project_id):
    project = Project.objects.get(pk=project_id)
    total_amount_details = project.total_amount_details.all()
    total_project_hours = project.total_hours()
    payment_form = PaymentDetailsForm()
    total_amount_detail_form = TotalAmountDetailsForm(initial={'project': project_id})
    work_records = WorkRecord.objects.filter(project=project)
    employee_totals = {}
    for record in work_records:
        if record.employee.full_name not in employee_totals:
            employee_totals[record.employee.full_name] = {'pk': record.pk, 'hours': record.hours,
                                                          'total_cost': record.hours * record.employee.hourly_rate}
        else:
            employee_totals[record.employee.full_name]['hours'] += record.hours
            employee_totals[record.employee.full_name]['total_cost'] += record.hours * record.employee.hourly_rate

    total_cost = sum(employee_total['total_cost'] for employee_total in employee_totals.values())
    total_expenses = project.total_expenses()

    # Calcular los conteos y las sumas de pagos "Sent" y "Paid" por detalle de monto total
    payment_counts = {}
    for detail in total_amount_details:
        total_paid = detail.payment.filter(status='Paid').aggregate(total=Sum('value'))['total'] or 0
        payment_counts[detail.pk] = {
            'sent': detail.payment.filter(status='Sent').count(),
            'paid': detail.payment.filter(status='Paid').count(),
            'total_sent': detail.payment.filter(status='Sent').aggregate(total=Sum('value'))['total'] or 0,
            'total_paid': total_paid,
            'balance_to_finish': detail.scheduled_value - total_paid
        }

    return render(request, 'project_detail_dash.html', {
        'project': project,
        'total_amount_details': total_amount_details,
        'employee_totals': employee_totals,
        'total_cost': total_cost,
        'total_expenses': total_expenses,
        'total_project_hours': total_project_hours,
        'payment_detail_form': payment_form,
        'total_amount_detail_form': total_amount_detail_form,
        'payment_counts': payment_counts,
    })


@login_required
def dashboard(request):
    projects = Project.objects.all()
    project_statuses = ProjectStatus.objects.all()

    search_query = request.GET.get('search', None)
    status_filter = request.GET.get('status', None)

    if search_query:
        projects = projects.filter(name__icontains=search_query)

    if status_filter:
        projects = projects.filter(status__name=status_filter)

    total_projects = projects.count()
    total_payment_paid = sum(project.total_payment_paid() for project in projects)
    total_payment_sent = sum(project.total_payment_sent() for project in projects)
    total_expenses = Expense.objects.aggregate(total=Sum('value'))['total'] or 0.0
    total_balance = total_payment_paid - total_expenses

    project_status_summary = {status.name: projects.filter(status=status).count() for status in project_statuses}

    context = {
        'projects': projects,
        'project_statuses': project_statuses,
        'total_projects': total_projects,
        'total_payment_paid': total_payment_paid,
        'total_payment_sent': total_payment_sent,
        'total_expenses': total_expenses,
        'total_balance': total_balance,
        'project_status_summary': project_status_summary,
    }

    return render(request, 'dashboard.html', context)


@method_decorator(login_required, name='dispatch')
@method_decorator(permission_required('app.view_project', raise_exception=True), name='dispatch')
class ProjectListView(ListView):
    model = Project
    template_name = 'project_list.html'
    context_object_name = 'projects'


@method_decorator(login_required, name='dispatch')
@method_decorator(permission_required('app.add_project', raise_exception=True), name='dispatch')
class ProjectCreateView(CreateView):
    model = Project
    form_class = ProjectForm
    template_name = 'project_form.html'
    success_url = reverse_lazy('dashboard')


@method_decorator(login_required, name='dispatch')
@method_decorator(permission_required('app.view_project', raise_exception=True), name='dispatch')
class ProjectDetailView(DetailView):
    model = Project
    template_name = 'project_detail.html'


@method_decorator(login_required, name='dispatch')
@method_decorator(permission_required('app.change_project', raise_exception=True), name='dispatch')
class ProjectUpdateView(UpdateView):
    model = Project
    form_class = ProjectForm
    template_name = 'project_update_form.html'
    success_url = reverse_lazy('dashboard')


@method_decorator(login_required, name='dispatch')
@method_decorator(permission_required('app.delete_project', raise_exception=True), name='dispatch')
class ProjectDeleteView(DeleteView):
    model = Project
    template_name = 'project_confirm_delete.html'
    success_url = reverse_lazy('dashboard')


@method_decorator(login_required, name='dispatch')
@method_decorator(permission_required('app.view_expense', raise_exception=True), name='dispatch')
class ExpenseListView(ListView):
    model = Expense
    template_name = 'expense_list.html'
    context_object_name = 'expenses'


@method_decorator(login_required, name='dispatch')
@method_decorator(permission_required('app.add_expense', raise_exception=True), name='dispatch')
class ExpenseCreateView(CreateView):
    model = Expense
    form_class = ExpenseForm
    template_name = 'expense_form.html'

    def form_valid(self, form):
        expense = form.save(commit=False)
        project_id = self.request.POST.get('project')  # Obtener el project_id del formulario o URL
        expense.project_id = project_id  # Asignar el project_id al gasto
        expense.save()
        return redirect(reverse('project_detail_dash', kwargs={'project_id': project_id}))


@method_decorator(login_required, name='dispatch')
@method_decorator(permission_required('app.view_expense', raise_exception=True), name='dispatch')
class ExpenseDetailView(DetailView):
    model = Expense
    template_name = 'expense_detail.html'


@method_decorator(login_required, name='dispatch')
@method_decorator(permission_required('app.change_expense', raise_exception=True), name='dispatch')
class ExpenseUpdateView(UpdateView):
    model = Expense
    form_class = ExpenseForm
    template_name = 'expense_update_form.html'

    def form_valid(self, form):
        expense = form.save(commit=False)
        project_id = expense.project_id  # Obtener el project_id del gasto
        expense.save()
        return redirect(reverse('project_detail_dash', kwargs={'project_id': project_id}))


@method_decorator(login_required, name='dispatch')
@method_decorator(permission_required('app.delete_expense', raise_exception=True), name='dispatch')
class ExpenseDeleteView(DeleteView):
    model = Expense
    template_name = 'expense_confirm_delete.html'

    def get_success_url(self):
        project_id = self.object.project.id
        return reverse('project_detail_dash', kwargs={'project_id': project_id})


@method_decorator(login_required, name='dispatch')
@method_decorator(permission_required('app.view_employee', raise_exception=True), name='dispatch')
class EmployeeListView(ListView):
    model = Employee
    template_name = 'employee_list.html'
    context_object_name = 'employees'


@method_decorator(login_required, name='dispatch')
@method_decorator(permission_required('app.add_employee', raise_exception=True), name='dispatch')
class EmployeeCreate(CreateView):
    model = Employee
    form_class = EmployeeForm
    template_name = 'employee_form.html'
    success_url = reverse_lazy('employee_list')


@method_decorator(login_required, name='dispatch')
@method_decorator(permission_required('app.change_employee', raise_exception=True), name='dispatch')
class EmployeeUpdate(UpdateView):
    model = Employee
    form_class = EmployeeForm
    template_name = 'employee_form.html'
    success_url = reverse_lazy('employee_list')


@method_decorator(login_required, name='dispatch')
@method_decorator(permission_required('app.delete_employee', raise_exception=True), name='dispatch')
class EmployeeDelete(DeleteView):
    model = Employee
    template_name = 'employee_confirm_delete.html'
    success_url = reverse_lazy('employee_list')


@method_decorator(login_required, name='dispatch')
@method_decorator(permission_required('app.view_workrecord', raise_exception=True), name='dispatch')
class WorkRecordListView(ListView):
    model = WorkRecord
    template_name = 'workrecord_list.html'
    context_object_name = 'workrecords'


@method_decorator(login_required, name='dispatch')
@method_decorator(permission_required('app.add_workrecord', raise_exception=True), name='dispatch')
class WorkRecordCreate(CreateView):
    model = WorkRecord
    form_class = WorkRecordForm
    template_name = 'workrecord_form.html'
    success_url = reverse_lazy('workrecord_list')


@method_decorator(login_required, name='dispatch')
@method_decorator(permission_required('app.change_workrecord', raise_exception=True), name='dispatch')
class WorkRecordUpdate(UpdateView):
    model = WorkRecord
    form_class = WorkRecordForm
    template_name = 'workrecord_form.html'
    success_url = reverse_lazy('workrecord_list')


@method_decorator(login_required, name='dispatch')
@method_decorator(permission_required('app.delete_workrecord', raise_exception=True), name='dispatch')
class WorkRecordDelete(DeleteView):
    model = WorkRecord
    template_name = 'workrecord_confirm_delete.html'
    success_url = reverse_lazy('workrecord_list')


@method_decorator(login_required, name='dispatch')
@method_decorator(permission_required('app.view_totalamountdetails', raise_exception=True), name='dispatch')
class TotalAmountDetailsListView(ListView):
    model = TotalAmountDetails
    template_name = 'totalamountdetails_list.html'
    context_object_name = 'total_amount_details'


@method_decorator(login_required, name='dispatch')
@method_decorator(permission_required('app.add_totalamountdetails', raise_exception=True), name='dispatch')
class TotalAmountDetailsCreateView(CreateView):
    model = TotalAmountDetails
    form_class = TotalAmountDetailsForm
    template_name = 'totalamountdetails_form.html'
    success_url = reverse_lazy('totalamountdetails_list')


@method_decorator(login_required, name='dispatch')
@method_decorator(permission_required('app.view_totalamountdetails', raise_exception=True), name='dispatch')
class TotalAmountDetailsDetailView(DetailView):
    model = TotalAmountDetails
    template_name = 'totalamountdetails_detail.html'


@method_decorator(login_required, name='dispatch')
@method_decorator(permission_required('app.change_totalamountdetails', raise_exception=True), name='dispatch')
class TotalAmountDetailsUpdateView(UpdateView):
    model = TotalAmountDetails
    form_class = TotalAmountDetailsForm
    template_name = 'totalamountdetails_form.html'
    success_url = reverse_lazy('totalamountdetails_list')


@method_decorator(login_required, name='dispatch')
@method_decorator(permission_required('app.delete_totalamountdetails', raise_exception=True), name='dispatch')
class TotalAmountDetailsDelete(DeleteView):
    model = TotalAmountDetails
    template_name = 'totalamountdetails_confirm_delete.html'
    success_url = reverse_lazy('totalamountdetails_list')


@method_decorator(login_required, name='dispatch')
@method_decorator(permission_required('app.view_paymentdetails', raise_exception=True), name='dispatch')
class PaymentDetailsListView(ListView):
    model = PaymentDetails
    template_name = 'paymentdetails_list.html'
    context_object_name = 'payment_details'


@method_decorator(login_required, name='dispatch')
@method_decorator(permission_required('app.add_paymentdetails', raise_exception=True), name='dispatch')
class PaymentDetailsCreateView(CreateView):
    model = PaymentDetails
    form_class = PaymentDetailsForm
    template_name = 'paymentdetails_form.html'
    success_url = reverse_lazy('paymentdetails_list')


@method_decorator(login_required, name='dispatch')
@method_decorator(permission_required('app.view_paymentdetails', raise_exception=True), name='dispatch')
class PaymentDetailsDetailView(DetailView):
    model = PaymentDetails
    template_name = 'paymentdetails_detail.html'


@method_decorator(login_required, name='dispatch')
@method_decorator(permission_required('app.change_paymentdetails', raise_exception=True), name='dispatch')
class PaymentDetailsUpdateView(UpdateView):
    model = PaymentDetails
    form_class = PaymentDetailsForm
    template_name = 'paymentdetails_form.html'
    success_url = reverse_lazy('paymentdetails_list')


@method_decorator(login_required, name='dispatch')
@method_decorator(permission_required('app.delete_paymentdetails', raise_exception=True), name='dispatch')
class PaymentDetailsDeleteView(DeleteView):
    model = PaymentDetails
    template_name = 'paymentdetails_confirm_delete.html'
    success_url = reverse_lazy('paymentdetails_list')


@login_required
def employee_weekly_hours_report(request):
    start_date, end_date = get_previous_week_range()

    if request.GET.get('week'):
        try:
            start_date_str, end_date_str = request.GET.get('week').split('|')
            start_date = datetime.datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.datetime.strptime(end_date_str, '%Y-%m-%d').date()
        except ValueError:
            week_offset = int(request.GET.get('week'))
            start_date += datetime.timedelta(weeks=week_offset)
            end_date += datetime.timedelta(weeks=week_offset)

    work_records = WorkRecord.objects.filter(date__range=[start_date, end_date])
    employee_hours = work_records.values('employee__full_name').annotate(total_hours=Sum('hours')).order_by(
        'employee__full_name')

    context = {
        'start_date': start_date,
        'end_date': end_date,
        'employee_hours': employee_hours,
        'week_offset': request.GET.get('week', 0)
    }

    return render(request, 'employee_weekly_hours_report.html', context)


@method_decorator(login_required, name='dispatch')
@method_decorator(permission_required('app.delete_totalamountdetails', raise_exception=True), name='dispatch')
class TotalAmountDetailsDeleteView(DeleteView):
    model = TotalAmountDetails
    template_name = 'totalamountdetails_confirm_delete.html'
    success_url = reverse_lazy('totalamountdetails_list')


@csrf_exempt
@require_POST
@login_required
@permission_required('app.add_paymentdetails', raise_exception=True)
def add_payment_detail(request):
    form = PaymentDetailsForm(request.POST)
    if form.is_valid():
        form.save()
        return JsonResponse({'status': 'success'})
    else:
        return JsonResponse({'status': 'error', 'errors': form.errors})


@login_required
@permission_required('app.add_totalamountdetails', raise_exception=True)
def add_total_amount_detail(request):
    project_id = request.POST.get('project') or request.GET.get('project')
    if request.method == 'POST':
        form = TotalAmountDetailsForm(request.POST, project_id=project_id)
        if form.is_valid():
            form.save()
            return JsonResponse({'status': 'success'})
        else:
            return JsonResponse({'status': 'error', 'errors': form.errors})
    else:
        form = TotalAmountDetailsForm(initial={'project': project_id}, project_id=project_id)
    return render(request, 'totalamountdetails_form.html', {'form': form})



@login_required
@permission_required('app.change_paymentdetails', raise_exception=True)
def edit_payment_detail(request, pk):
    payment_detail = get_object_or_404(PaymentDetails, pk=pk)
    if request.method == 'POST':
        form = PaymentDetailsForm(request.POST, instance=payment_detail)
        if form.is_valid():
            form.save()
            return redirect('project_detail_dash', project_id=payment_detail.total_amount_detail.project.pk)
    else:
        form = PaymentDetailsForm(instance=payment_detail)
    return render(request, 'paymentdetails_form.html', {'form': form})


@login_required
@permission_required('app.add_workrecord', raise_exception=True)
def add_work_record(request):
    if request.method == 'POST':
        form = WorkRecordForm(request.POST)
        if form.is_valid():
            form.save()
            return JsonResponse({'status': 'success'})
        else:
            return JsonResponse({'status': 'error', 'errors': form.errors})
    else:
        form = WorkRecordForm()
    return render(request, 'workrecord_form.html', {'form': form})


@login_required
@permission_required('app.change_workrecord', raise_exception=True)
def edit_work_record(request, pk):
    work_record = get_object_or_404(WorkRecord, pk=pk)
    if request.method == 'POST':
        form = WorkRecordForm(request.POST, instance=work_record)
        if form.is_valid():
            form.save()
            return JsonResponse({'status': 'success'})
        else:
            return JsonResponse({'status': 'error', 'errors': form.errors})
    else:
        form = WorkRecordForm(instance=work_record)
    return render(request, 'workrecord_form.html', {'form': form})


@login_required
@permission_required('app.delete_workrecord', raise_exception=True)
def delete_work_record(request, pk):
    work_record = get_object_or_404(WorkRecord, pk=pk)
    if request.method == 'POST':
        work_record.delete()
        return redirect('project_detail_dash', project_id=work_record.project.pk)
    return render(request, 'workrecord_confirm_delete.html', {'work_record': work_record})


class WorkRecordCreateView(CreateView):
    model = WorkRecord
    form_class = WorkRecordForm
    template_name = 'workrecord_form.html'

    def get_initial(self):
        initial = super().get_initial()
        project_id = self.request.GET.get('project')
        if project_id:
            initial['project'] = project_id
        return initial

    def form_valid(self, form):
        work_record = form.save(commit=False)
        work_record.project_id = self.request.POST.get('project')  # Asigna el project_id al work_record
        work_record.save()
        return redirect(reverse('project_detail_dash', kwargs={'project_id': work_record.project_id}))



class WorkRecordUpdateView(UpdateView):
    model = WorkRecord
    form_class = WorkRecordForm
    template_name = 'workrecord_form.html'

    def form_valid(self, form):
        work_record = form.save(commit=False)
        project_id = work_record.project_id  # Obtener el project_id del registro de trabajo
        work_record.save()
        return redirect(reverse('project_detail_dash', kwargs={'project_id': project_id}))


class WorkRecordDeleteView(DeleteView):
    model = WorkRecord
    template_name = 'workrecord_confirm_delete.html'

    def get_success_url(self):
        project_id = self.object.project_id
        return reverse('project_detail_dash', kwargs={'project_id': project_id})
