from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin

urlpatterns = [
   path('', views.login_view, name='employee_login'),
    path('index/', views.index, name='index'),

    path('hr/index/', views.admin_index, name='admin_index'),
    path('employee/index/', views.employee_index, name='employee_index'),
    path('login/', views.login_view, name='login'),
    path('login/admin/', views.auth_login, name='admin_login'),

    path('logout/', views.logout_view, name='logout'),
    path('profile/<int:user_id>/', views.profile, name='profile'), 
    # path('employes/', views.employes, name='employes'),
    path('module/<int:module_id>/', views.module_view, name='module_url_name'),
    path('child/<int:child_id>/', views.child_view, name='child_url_name'),
    path('subchild/<int:sub_child_id>/', views.sub_child_view, name='sub_child_url_name'),
    path('subsubchild/<int:subsubchild_id>/', views.subsubchild_view, name='subsubchild_url_name'), 
    path('add_user/',views.add_user,name="add_user"),
    path('attendance/', views.attendance, name='attendance'),
    path('leavetracker/', views.leavetracker, name='leavetracker'),
    path('timesheet/', views.timesheet, name='timesheet'),
    path('upcoming/', views.upcoming, name='upcoming'),
    path('schedule/',views.schedule,name='schedule'),
    path('birthdayanniversary/',views.birthdayanniversary,name='birthdayanniversary'),
    path('departments/',views.departments,name='departments'),

    path('departments/add/', views.add_department, name='add_department'),
    path('departments/edit/<int:id>/', views.edit_department, name='edit_departments'),
    path('departments/delete/<int:dept_id>/', views.delete_department, name='delete_department'),


      path('passwordchange/', views.passwordchange, name='passwordchange'),





    # employee
    
    


    path('registration/',views.registration,name='registration'),
    path('teammanagement/',views.teammanagement,name='teammanagement'),
    path('notification/',views.notification,name='notification'),
    path('dashboard/',views.dashboard,name='dashboard'),
    path('companyprofile/',views.companyprofile,name='companyprofile'),
    path('securitysettings/',views.securitysettings,name='securitysettings'),

    # path('add-employee/', views.add_employee, name='add_employee'),


    path('employes/', views.employes, name='employes'),
    path('employees/add/', views.add_employee, name='add_employee'),

    path('employee/delete/<int:id>/', views.employee_delete, name='employee_delete'),
    path('employee/edit/<int:id>/', views.employee_edit, name='employee_edit'),


    path('add_user/<int:user_id>/', views.add_user, name='add_user'),
     path('delete-user/<int:user_id>/', views.delete_user, name='delete_user'),
    path('calendar-events/', views.calendar_events, name='calendar-events'),
    path('add-event/', views.add_event, name='add-event'),


    path('upcoming/', views.upcoming, name='upcoming_event'),
    path('edit-event/<int:event_id>/', views.edit_event, name='edit-event'),
    path('delete-event/<int:event_id>/', views.delete_event, name='delete-event'),


    path('dashboard/birthdayanniversary/', views.birthday_anniversary_view, name='birthdayanniversary'),

   
 

   
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
