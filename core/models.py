from django.db import models
from django.db.models import Sum
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver


class ProjectStatus(models.Model):
    name = models.CharField(max_length=200, verbose_name="Name")

    class Meta:
        verbose_name = "Project Status"
        verbose_name_plural = "Project Statuses"

    def __str__(self):
        return self.name


class Project(models.Model):
    name = models.CharField(max_length=200, verbose_name="Name")
    description = models.TextField(verbose_name="Description")
    contact_name = models.CharField(max_length=200, verbose_name="Contact Name", null=True, blank=True)
    contact_phone = models.CharField(max_length=200, verbose_name="Contact Phone", null=True, blank=True)
    address = models.CharField(max_length=200, verbose_name="Address")
    start_date = models.DateField(verbose_name="Start Date", null=True, blank=True)
    end_date = models.DateField(verbose_name="End Date", null=True, blank=True)
    contract_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Contract Amount", null=True,
                                          blank=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Total Amount", default=0)
    drawings = models.URLField(verbose_name="Drawings", null=True, blank=True)
    reports_p = models.URLField(verbose_name="Reports", null=True, blank=True)
    status = models.ForeignKey(ProjectStatus, on_delete=models.CASCADE, verbose_name="Status")

    class Meta:
        verbose_name = "Project"
        verbose_name_plural = "Projects"

    def __str__(self):
        return self.name

    def calculate_total_amount(self):
        return self.total_amount_details.aggregate(total=Sum('scheduled_value'))['total'] or 0

    def total_expenses(self):
        return self.expense_set.aggregate(total=Sum('value'))['total'] or 0

    def total_income(self):
        return self.income_set.aggregate(total=Sum('value'))['total'] or 0

    def total_hours(self):
        return self.workrecord_set.aggregate(total=Sum('hours'))['total'] or 0

    def total_cost(self):
        total_expenses = self.total_expenses()
        total_employee_costs = sum(
            [work_record.hours * work_record.employee.hourly_rate for work_record in self.workrecord_set.all()])
        return total_expenses + total_employee_costs

    def remaining_balance(self):
        return self.total_income() - self.total_cost()

    def save(self, *args, **kwargs):
        self.total_amount = self.calculate_total_amount()
        super().save(*args, **kwargs)


class IncomeType(models.Model):
    description = models.CharField(max_length=200, verbose_name="Description")

    class Meta:
        verbose_name = "Income Type"
        verbose_name_plural = "Income Types"

    def __str__(self):
        return self.description


class ExpenseType(models.Model):
    description = models.CharField(max_length=200, verbose_name="Description")

    class Meta:
        verbose_name = "Expense Type"
        verbose_name_plural = "Expense Types"

    def __str__(self):
        return self.description


class Income(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, verbose_name="Project")
    income_type = models.ForeignKey(IncomeType, on_delete=models.CASCADE, verbose_name="Income Type")
    date = models.DateField(verbose_name="Date")
    value = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Value")
    description = models.TextField(verbose_name="Description")

    class Meta:
        verbose_name = "Income"
        verbose_name_plural = "Incomes"

    def __str__(self):
        return f"{self.value} - {self.description}"


class Expense(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, verbose_name="Project")
    expense_type = models.ForeignKey(ExpenseType, on_delete=models.CASCADE, verbose_name="Expense Type")
    date = models.DateField(verbose_name="Date")
    value = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Value")
    description = models.TextField(verbose_name="Description")

    class Meta:
        verbose_name = "Expense"
        verbose_name_plural = "Expenses"

    def __str__(self):
        return f"{self.value} - {self.description}"


class Employee(models.Model):
    ACTIVE = 'Active'
    INACTIVE = 'Inactive'

    STATUS_CHOICES = [
        (ACTIVE, 'Active'),
        (INACTIVE, 'Inactive'),
    ]

    full_name = models.CharField(max_length=200, verbose_name="Full Name")
    birth_date = models.DateField(verbose_name="Birth Date", blank=True, null=True)
    contact_number = models.CharField(max_length=200, verbose_name="Contact Number", blank=True, null=True)
    hire_date = models.DateField(verbose_name="Hire Date", blank=True, null=True)
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Hourly Rate")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=ACTIVE, verbose_name="Status")

    class Meta:
        verbose_name = "Employee"
        verbose_name_plural = "Employees"

    def __str__(self):
        return self.full_name


class WorkRecord(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, verbose_name="Employee")
    project = models.ForeignKey(Project, on_delete=models.CASCADE, verbose_name="Project")
    date = models.DateField(verbose_name="Date")
    hours = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Hours")

    class Meta:
        verbose_name = "Work Record"
        verbose_name_plural = "Work Records"

    def __str__(self):
        return f"{self.employee.full_name} - {self.hours} horas"


class TotalAmountDetails(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, verbose_name="Project",
                                related_name='total_amount_details')
    description_of_work = models.CharField(max_length=200, verbose_name="Description of Work")
    scheduled_value = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Scheduled Value")
    balance_to_finish = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Balance to Finish",
                                            blank=True, null=True)

    class Meta:
        verbose_name = "Total amount Detail"
        verbose_name_plural = "Total Amount Details"

    def __str__(self):
        return f"{self.project.name} - {self.description_of_work}"

    def total_payment(self):
        return self.payment.aggregate(total=Sum('value'))['total'] or 0

    def calculate_balance_to_finish(self):
        total_completed = self.total_payment()
        return self.scheduled_value - total_completed

    def save(self, *args, **kwargs):
        self.balance_to_finish = self.calculate_balance_to_finish()
        super().save(*args, **kwargs)
        project = self.project
        project.total_amount = project.calculate_total_amount()
        project.save()


@receiver(post_save, sender=TotalAmountDetails)
def update_total_amount(sender, instance, **kwargs):
    project = instance.project
    project.total_amount = project.calculate_total_amount()
    project.save()


class PaymentDetails(models.Model):
    SENT = 'Sent'
    PAID = 'Paid'

    STATUS_CHOICES = [
        (SENT, 'Sent'),
        (PAID, 'Paid'),
    ]

    total_amount_detail = models.ForeignKey(TotalAmountDetails, on_delete=models.CASCADE,
                                            verbose_name="Total Amount Detail",
                                            related_name='payment')
    date = models.DateField(verbose_name="Date")
    value = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Value")
    description = models.TextField(verbose_name="Description")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=SENT, verbose_name="Status")

    class Meta:
        verbose_name = "Payment Detail"
        verbose_name_plural = "Payment Details"

    def __str__(self):
        return f"{self.total_amount_detail.project.name} - {self.date}"


@receiver(post_save, sender=PaymentDetails)
def update_balance_to_finish(sender, instance, **kwargs):
    total_amount_detail = instance.total_amount_detail
    total_amount_detail.balance_to_finish = total_amount_detail.calculate_balance_to_finish()
    total_amount_detail.save()
