from django.db import models
from django.contrib.auth.models import User
from django import forms
from django.core.validators import RegexValidator, MinValueValidator


class Profile(models.Model):
    USERGROUP_CHOICES = [
    ('Admin', 'Admin'),
    ('Employee', 'Employee'),
]
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    image = models.ImageField(upload_to='profile_images', blank=True, null=True)
    name = models.CharField(max_length=100)
    usergroup = models.CharField(max_length=100, choices=USERGROUP_CHOICES)

    class Meta:  
        db_table = 'dashboard_profile'  # Custom table name


class LeaveRequest(models.Model):
    LEAVE_TYPE_CHOICES = [
        ('CL', 'Casual Leave (CL)'),
        ('SL', 'Sick Leave (SL)'),
        ('PL', 'Paid Leave (PL)'),
        ('EL', 'Earned Leave (EL)'),
        ('MRL', 'Maternity Leave (MRL)'),
        ('PRL', 'Paternity Leave (PRL)'),
        ('ML', 'Marriage Leave (ML)'),
        ('BL', 'Bereavement Leave (BL)'),
    ]

    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    leave_type = models.CharField(max_length=3, choices=LEAVE_TYPE_CHOICES)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    reason = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Pending')

    applied_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    days = models.PositiveIntegerField(blank=True, null=True)  # auto-calculated field

    def save(self, *args, **kwargs):
        # Auto-calculate number of days
        if self.start_date and self.end_date:
            delta = self.end_date - self.start_date
            self.days = delta.days + 1  # +1 to include both start and end dates
        else:
            self.days = None  # fallback if dates aren't set
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} - {self.leave_type} ({self.start_date} to {self.end_date}) - {self.status}"
    
class UserGroup(models.Model):
    name = models.CharField(max_length=100)
    status = models.BooleanField(default=True)

    def __str__(self):
        return self.name
class Module(models.Model):
    name = models.CharField(max_length=100)
    url_name = models.CharField(max_length=255, null=True, blank=True)
    icon_class = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.name
class Child(models.Model):
    module = models.ForeignKey(Module, related_name='children', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    url_name = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"{self.name} (Child of {self.module.name})"

class SubChild(models.Model):
    child = models.ForeignKey(Child, related_name='sub_children', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    url_name = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"{self.name} (SubChild of {self.child.name})"

class SubSubChild(models.Model):
    subchild = models.ForeignKey(SubChild, related_name='subsubchildren', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    url_name = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"{self.name} (SubSubChild of {self.subchild.name})"
    
  




class Permission(models.Model):
    usergroup = models.ForeignKey(UserGroup, on_delete=models.CASCADE, null=True, blank=True)
    module = models.ForeignKey(Module, on_delete=models.CASCADE, null=True, blank=True)
    enabled = models.BooleanField(default=False)

class Department(models.Model):
    name = models.CharField(max_length=100)
    num_employees = models.IntegerField(default=0)  # Add this line
    head = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='headed_departments')
    budget = models.DecimalField(max_digits=10, decimal_places=2)
    open_positions = models.PositiveIntegerField(default=0, help_text="Open job slots")


    def __str__(self):
        return self.name


class Employee(models.Model):
    full_name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    blood_group = models.CharField(
        max_length=5,
        help_text="Example: A+, B-, O+"
    )
    joining_date = models.DateField()
    designation = models.CharField(max_length=100)
    department = models.ForeignKey(
    Department,
    on_delete=models.SET_NULL,  # Set department_id to NULL when department is deleted
    null=True,
    blank=True
)


    email = models.EmailField(unique=True)
    
    phone = models.CharField(
        max_length=20,
        validators=[RegexValidator(regex=r'^\+?\d{10,15}$', message="Enter a valid phone number.")]
    )

    emergency_number = models.CharField(
        max_length=20,
        validators=[RegexValidator(regex=r'^\+?\d{10,15}$', message="Enter a valid emergency number.")]
    )

    salary = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )

    def __str__(self):
        return self.full_name
    

class Event(models.Model):
    title = models.CharField(max_length=200)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.title

 

