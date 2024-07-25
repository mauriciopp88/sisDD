from django import forms
from .models import Project, Expense, Employee, WorkRecord, TotalAmountDetails, PaymentDetails


# Income

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = '__all__'
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }


class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = '__all__'
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'value': forms.NumberInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
        }


class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = '__all__'
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'birth_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'contact_number': forms.TextInput(attrs={'class': 'form-control'}),
            'hire_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'hourly_rate': forms.NumberInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }


class WorkRecordForm(forms.ModelForm):
    class Meta:
        model = WorkRecord
        fields = ['employee', 'project', 'date', 'hours']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'})
        }

    def __init__(self, *args, **kwargs):
        project_id = kwargs.pop('initial', {}).get('project')
        super(WorkRecordForm, self).__init__(*args, **kwargs)
        if project_id:
            self.fields['project'].initial = project_id


from django import forms
from .models import TotalAmountDetails, Project


class TotalAmountDetailsForm(forms.ModelForm):
    class Meta:
        model = TotalAmountDetails
        exclude = ['balance_to_finish']
        widgets = {
            'description_of_work': forms.TextInput(attrs={'class': 'form-control'}),
            'scheduled_value': forms.NumberInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        project_id = kwargs.pop('project_id', None)
        super(TotalAmountDetailsForm, self).__init__(*args, **kwargs)
        if project_id:
            self.fields['description_of_work'].queryset = TotalAmountDetails.objects.filter(project_id=project_id)


class PaymentDetailsForm(forms.ModelForm):
    class Meta:
        model = PaymentDetails
        fields = '__all__'
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'value': forms.NumberInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }
