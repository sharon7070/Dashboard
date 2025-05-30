from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required,user_passes_test
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth import authenticate, login

from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Profile,User,Child,SubChild
from .models import Module
from django.shortcuts import render, get_object_or_404, redirect
from datetime import date
from .forms import EmployeeForm,Employee,RegistrationForm
from .models import Department,Employee,SubSubChild
from decimal import Decimal, InvalidOperation
from .forms import LeaveRequestForm
from .models import LeaveRequest
from django.http import JsonResponse
from .models import Event  # Your event model
from django.utils.dateparse import parse_datetime
from django.utils.timezone import make_aware, is_naive, now
from datetime import datetime
from django.views.decorators.cache import never_cache

from django.contrib.auth import update_session_auth_hash



@csrf_protect
@never_cache
def login_view(request):
    # Redirect if already logged in
    if request.user.is_authenticated:
        try:
            profile = request.user.profile
            if profile.usergroup == 'Admin':
                return redirect('admin_index')
            elif profile.usergroup == 'Employee':
                return redirect('employee_index')
        except Profile.DoesNotExist:
            messages.error(request, "User profile not found.")
            return redirect('login')  # Adjust if needed

    user_type = request.GET.get('user_type', None)
    template_map = {
        'Admin': 'dashboard/login.html',
        'Employee': 'employee/login.html',
    }

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)

            try:
                profile = user.profile
                request.session['usergroup'] = profile.usergroup

                if profile.usergroup == 'Admin':
                    return redirect('admin_index')
                elif profile.usergroup == 'Employee':
                    return redirect('employee_index')
                else:
                    messages.error(request, "User group not recognized.")
                    return redirect('login', user_type=user_type)
            except Profile.DoesNotExist:
                messages.error(request, "User profile not found.")
                return redirect('login', user_type=user_type)
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()

    return render(request, template_map.get(user_type, 'dashboard/login.html'), {'form': form})


@login_required
def index(request):
    user_profile = Profile.objects.filter(user=request.user).first()
    modules = Module.objects.all()

    if user_profile and user_profile.usergroup == 'Admin':
        template = 'dashboard/index.html'
    else:
        template = 'employee/index.html'

    return render(request, template, {
        'modules': modules,
        'global_user_profile': user_profile,
    })

@login_required
def admin_index(request):
    return render(request, 'dashboard/index.html')  # Or another admin page like dashboard.html

@login_required
def employee_index(request):
    return render(request, 'employee/index.html')  #

def logout_view(request):
    auth_logout(request)
    messages.success(request, "You have successfully logged out.")
    return redirect('login')


# @login_required
# def index(request):
#     modules = Module.objects.all()
#     user_profile = Profile.objects.filter(user=request.user).first()
#     return render(request, 'dashboard/index.html', {
#         'modules': modules,
#         'global_user_profile': user_profile,
#     })


@login_required
def profile(request, user_id):
    user = get_object_or_404(User, id=user_id)
    profile, _ = Profile.objects.get_or_create(user=user)
    
    errors = {}

    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password1', '')
        image = request.FILES.get('image')
        usergroup = request.POST.get('usergroup', '').strip()  # ADDED THIS LINE

        # Validate inputs
        if not name:
            errors['name'] = ['Name is required.']
        if not email:
            errors['email'] = ['Email is required.']
        if not username:
            errors['username'] = ['Username is required.']
        elif User.objects.exclude(id=user.id).filter(username=username).exists():
            errors['username'] = ['Username already exists.']
        elif User.objects.exclude(id=user.id).filter(email=email).exists():
            errors['email'] = ['Email already exists.']

        if not errors:
            # Update User model
            user.username = username
            user.email = email
            user.save()

            # Update Profile model
            profile.name = name
            profile.usergroup = usergroup  # ADDED THIS LINE
            if image:
                profile.image = image
            profile.save()

            # Update password if provided
            if password:
                user.set_password(password)
                user.save()
                messages.success(request, 'Password updated. You may need to log in again.')

            messages.success(request, 'Profile updated successfully.')
            return redirect('profile.html', user_id=user.id)

        # If there are validation errors, fall through to re-render form

        form_data = {
            'name': name,
            'email': email,
            'username': username,
            'usergroup': usergroup,  # CHANGED FROM profile.usergroup TO usergroup
            'password1': password,
            'image': profile.image,
        }
        # Attach error lists to the corresponding fields
        for field in ['name', 'email', 'username', 'password1']:
            if field not in errors:
                errors[field] = []
        form_data = {**form_data, **errors}
    else:
        # GET method
        form_data = {
            'name': profile.name,
            'email': user.email,
            'username': user.username,
            'usergroup': profile.usergroup,
            'image': profile.image,
        }

    return render(request, 'dashboard/profile.html', {
        'profile': profile,
        'form_data': form_data,
        'user': user
    })    

def add_user(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            user.email = form.cleaned_data['email']
            user.save()

            # Create the related Profile
            Profile.objects.create(
                user=user,
                usergroup=form.cleaned_data['usergroup'],
                name=form.cleaned_data['name'],
                image=form.cleaned_data.get('image')
            )

            return redirect('teammanagement')
    else:
        form = RegistrationForm()

    return render(request, 'dashboard/add_user.html', {'form': form})


def is_admin(user):
    return user.is_superuser

@login_required
@user_passes_test(is_admin)
def delete_user(request, user_id):
    user_to_delete = get_object_or_404(User, id=user_id)

    if user_to_delete.is_superuser:
        messages.error(request, "You cannot delete another admin.")
    else:
        user_to_delete.delete()
        messages.success(request, "User removed successfully.")

    return redirect('teammanagement')  # Update this with the correct name for your user list view







def module_view(request, module_id):
    module = get_object_or_404(Module, id=module_id)
    
    # Determine the template dynamically
    if module.url_name:
        template_name = f'dashboard/{module.url_name}.html'
    else:
        template_name = 'dashboard/index.html'
    
    return render(request, template_name, {'module': module})

def child_view(request, child_id):
   
    child = get_object_or_404(Child, id=child_id)

    # Decide which template to render based on the child's url_name
    if child.url_name:
        template_path = f'dashboard/{child.url_name}'
    else:
        template_path = 'dashboard/add_usergroup.html'  # fallback

    return render(request, template_path, {'child': child})

# views.py

def sub_child_view(request, sub_child_id):
    sub_child = get_object_or_404(SubChild, id=sub_child_id)

    # Determine the template dynamically
    if sub_child.url_name:
        template_path = f'dashboard/{sub_child.url_name}'
    else:
        template_path = 'dashboard/default_sub_child.html'  # Fallback template

    return render(request, template_path, {'sub_child': sub_child})


def subsubchild_view(request, subsubchild_id):
    subsubchild = get_object_or_404(SubSubChild, id=subsubchild_id)

    # Decide which template to render based on subsubchild's url_name
    if subsubchild.url_name:
        template_path = f'dashboard/{subsubchild.url_name}'
    else:
        template_path = 'dashboard/default_subsubchild.html'  # Fallback template

    return render(request, template_path, {'subsubchild': subsubchild})

def employes(request):
    employees = Employee.objects.select_related('department').all().order_by('-id')
    return render(request, 'dashboard/employes.html', {'employees': employees})

def attendance(request):
    
    return render(request, 'dashboard/attendance.html')

@login_required
def leavetracker(request):
    profile = request.user.profile
    leave_type_choices = LeaveRequest.LEAVE_TYPE_CHOICES

    total_leaves = 24
    taken_leaves = LeaveRequest.objects.filter(user=request.user, status='Approved').count()
    remaining_leaves = total_leaves - taken_leaves

    # If Admin: show all leaves
    if profile.usergroup == 'Admin':
        leave_history = LeaveRequest.objects.all().order_by('-applied_on')
    else:
        leave_history = LeaveRequest.objects.filter(user=request.user).order_by('-start_date')

    # Handle leave apply (only for employee)
    if request.method == 'POST':
        if profile.usergroup != 'Admin':
            form = LeaveRequestForm(request.POST)
            if form.is_valid():
                leave = form.save(commit=False)
                leave.user = request.user
                leave.save()
                return redirect('leavetracker')
        else:
            leave_id = request.POST.get('leave_id')
            action = request.POST.get('action')
            leave = get_object_or_404(LeaveRequest, id=leave_id)
            if action == 'approve':
                leave.status = 'Approved'
            elif action == 'reject':
                leave.status = 'Rejected'
            leave.save()
            return redirect('leavetracker')

    else:
        form = LeaveRequestForm()

    context = {
        'form': form,
        'leave_type_choices': leave_type_choices,
        'total_leaves': total_leaves,
        'taken_leaves': taken_leaves,
        'remaining_leaves': remaining_leaves,
        'leave_history': leave_history,
        'usergroup': profile.usergroup
    }

    return render(request, 'dashboard/leavetracker.html', context)



def timesheet(request):
    
    return render(request, 'dashboard/timesheet.html')


# def upcoming(request):
    
#     return render(request, 'dashboard/upcoming.html')


def schedule(request):
    
    return render(request, 'dashboard/schedule.html')

def birthdayanniversary(request):
    
    return render(request, 'dashboard/birthdayanniversary.html')




@login_required
def passwordchange(request):
    if request.method == 'POST':
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        if not request.user.check_password(old_password):
            messages.error(request, "Old password is incorrect.")
        elif new_password != confirm_password:
            messages.error(request, "New passwords do not match.")
        elif len(new_password) < 6:
            messages.error(request, "New password must be at least 6 characters.")
        else:
            request.user.set_password(new_password)
            request.user.save()
            update_session_auth_hash(request, request.user)  # Important to prevent logout
            messages.success(request, "Password changed successfully.")
            return redirect('index')

    return render(request, 'dashboard/passwordchange.html')







def departments(request):
    
    return render(request, 'dashboard/departments.html')

def registration(request):
    # Always fetch departments before handling the request
    departments = Department.objects.all()
    
    if request.method == 'POST':
        form = EmployeeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Employee registered successfully!")
            return redirect('employes')  # Ensure this URL name exists
    else:
        form = EmployeeForm()

    return render(request, 'dashboard/registration.html', {
        'form': form,
        'today': date.today().isoformat(),
        'departments': departments  # Pass departments here as well
    })
@login_required()
def teammanagement(request):
    users = Profile.objects.select_related('user').all()  # optimize DB access
    return render(request, 'dashboard/teammanagement.html', {'users': users})


def notification(request):
    
    return render(request, 'dashboard/notification.html')

def dashboard(request):
    
    return render(request, 'dashboard/dashboard.html')

def companyprofile(request):
    
    return render(request, 'dashboard/companyprofile.html')

def securitysettings(request):
    
    return render(request, 'dashboard/securitysettings.html')





def add_employee(request):
    if request.method == 'POST':
        form = EmployeeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Employee added successfully.')
            return redirect('employes')  # replace with your actual redirect URL name
    else:
        form = EmployeeForm()


    return render(request, 'add_employee.html', {
        'form': form,
       
    })


@login_required

def employee_delete(request, id):
    employee = get_object_or_404(Employee, id=id)
    
    # Optional: Check if the employee has any dependent data or related records before deletion
    if employee:
        employee.delete()
        messages.success(request, f"Employee {employee.full_name} deleted successfully.")
    else:
        messages.error(request, "Employee not found.")
    
    return redirect('employes')  # Redirect to the employee list page
 

@login_required

def employee_edit(request, id):
    employee = get_object_or_404(Employee, id=id)
    
    if request.method == 'POST':
        form = EmployeeForm(request.POST, instance=employee)
        if form.is_valid():
            form.save()
            messages.success(request, f"Employee {employee.full_name} updated successfully.")
            return redirect('employes')
    else:
        form = EmployeeForm(instance=employee)
    
    return render(request, 'dashboard/edit_employee.html', {'form': form, 'employee': employee})




@login_required

def departments(request):
    departments = Department.objects.select_related('head').all()

    context = {
        'total_departments': departments.count(),
        'new_departments': 2,  # Replace with dynamic logic if needed
        'total_employees': sum(dept.num_employees for dept in departments),
        'new_employees': 15,  # Replace with dynamic logic if needed
        'open_positions': sum(dept.open_positions for dept in departments),
        'urgent_positions': 3,  # Replace with dynamic logic if needed
        'avg_tenure': 3.2,  # Placeholder
        'tenure_growth': 10,  # Placeholder
        'departments': departments  # Now passing the actual queryset
    }

    return render(request, 'dashboard/departments.html', context)


def add_department(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        head_username = request.POST.get('head')
        try:
            num_employees = int(request.POST.get('num_employees'))
            open_positions = int(request.POST.get('open_positions'))
            budget = Decimal(request.POST.get('budget'))
        except (ValueError, InvalidOperation):
            return render(request, 'dashboard/add_department.html', {
                'error': 'Please enter valid numeric values.',
                'users': User.objects.all()
            })

        # Optional: Check range if you're using PositiveSmallIntegerField
        if open_positions > 65535 or num_employees > 65535:
            return render(request, 'dashboard/add_department.html', {
                'error': 'Value too large for open positions or number of employees.',
                'users': User.objects.all()
            })

        try:
            head_user = User.objects.get(username=head_username)
        except User.DoesNotExist:
            return render(request, 'dashboard/add_department.html', {
                'error': 'Selected department head does not exist.',
                'users': User.objects.all()
            })

        Department.objects.create(
            name=name,
            head=head_user,
            num_employees=num_employees,
            open_positions=open_positions,
            budget=budget
        )
        return redirect('departments')

    users = User.objects.all()
    return render(request, 'dashboard/add_department.html', {'users': users})


# Edit Department

def edit_department(request, id):
    department = get_object_or_404(Department, id=id)

    if request.method == 'POST':
        department.name = request.POST.get('name')
        head_input = request.POST.get('head')

        # ✅ Fetch User by username (from dropdown value)
        try:
            department.head = User.objects.get(username=head_input)
        except User.DoesNotExist:
            department.head = None  # Optionally handle this more gracefully

        department.num_employees = request.POST.get('num_employees')
        department.open_positions = request.POST.get('open_positions')
        department.budget = request.POST.get('budget')
        department.save()
        return redirect('departments')

    # ✅ Pass all users to template for dropdown
    users = User.objects.all()
    return render(request, 'dashboard/edit_departments.html', {
        'department': department,
        'users': users,
    })

# Delete Department

# views.py
def delete_department(request, dept_id):  # Change parameter name to match URL
    department = get_object_or_404(Department, pk=dept_id)
    
    # Your deletion logic here
    try:
        department.delete()
        messages.success(request, "Department deleted successfully")
    except Exception as e:
        messages.error(request, f"Error deleting department: {str(e)}")
    
    return redirect('departments')  # Replace with your actual redirect target




def calendar_events(request):
    events = Event.objects.all()
    data = []
    for event in events:
        data.append({
            "id": event.id,
            "title": event.title,
            "start": event.start_time.isoformat(),
            "end": event.end_time.isoformat() if event.end_time else None,
        })
    return JsonResponse(data, safe=False)




def add_event(request):
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        raw_start = request.POST.get('start_time')
        raw_end = request.POST.get('end_time')

        start_time = parse_datetime(raw_start)
        end_time = parse_datetime(raw_end) if raw_end else None

        if start_time is not None:
            if start_time.tzinfo is None:
                start_time = make_aware(start_time)

            if end_time and end_time.tzinfo is None:
                end_time = make_aware(end_time)

        # Validation
        if not title:
            return JsonResponse({'status': 'error', 'message': 'Title cannot be empty.'}, status=400)

        if not start_time:
            return JsonResponse({'status': 'error', 'message': 'Invalid start time.'}, status=400)

        if start_time < now():
            return JsonResponse({'status': 'error', 'message': 'Start time must be in the future.'}, status=400)

        if end_time and end_time < start_time:
            return JsonResponse({'status': 'error', 'message': 'End time must be after start time.'}, status=400)

        # Save
        Event.objects.create(title=title, start_time=start_time, end_time=end_time)
        return JsonResponse({'status': 'success'})

    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=400)



def upcoming(request):
    events = Event.objects.all().order_by('start_time')
    return render(request, 'dashboard/upcoming.html', {'events': events})
 


def edit_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)

    if request.method == 'POST':
        title = request.POST.get('title')
        start_time = parse_datetime(request.POST.get('start_time'))
        end_time = parse_datetime(request.POST.get('end_time')) if request.POST.get('end_time') else None

        if not title.strip():
            messages.error(request, 'Title cannot be empty or just spaces.')
            return redirect('upcoming')

        if is_naive(start_time):
            start_time = make_aware(start_time)

        if start_time < now():
            messages.error(request, 'Start time cannot be in the past.')
            return redirect('upcoming')

        event.title = title
        event.start_time = start_time
        event.end_time = end_time
        event.save()

        messages.success(request, 'Event updated successfully.')
        return redirect('upcoming')

    # Handle GET request (show edit form)
    return render(request, 'dashboard/edit_event.html', {'event': event})


def delete_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    event.delete()
    messages.success(request, 'Event deleted successfully.')
    return redirect('upcoming')



def birthday_anniversary_view(request):
    today = date.today()

    # Fetch all employees instead of filtering by month
    birthdays = Employee.objects.all()
    anniversaries = Employee.objects.all()

    for emp in birthdays:
        # Calculate age
        age = today.year - emp.date_of_birth.year
        if (today.month, today.day) < (emp.date_of_birth.month, emp.date_of_birth.day):
            age -= 1
        emp.age = age
        emp.birthday_in = emp.date_of_birth.strftime('%d %B')

    for emp in anniversaries:
        # Calculate work years
        years = today.year - emp.joining_date.year
        if (today.month, today.day) < (emp.joining_date.month, emp.joining_date.day):
            years -= 1
        emp.years = years
        emp.anniversary_in = emp.joining_date.strftime('%d %B')

    context = {
        'birthdays': birthdays,
        'anniversaries': anniversaries,
    }
    return render(request, 'dashboard/birthdayanniversary.html', context)













































































































































































































































































































































































































































































































































































 