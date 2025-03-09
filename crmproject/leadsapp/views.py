from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Lead
from usersapp.models import User



'''@login_required

def admin_dashboard(request):
    # System Overview
    total_leads = Lead.objects.count()
    new_leads = Lead.objects.filter(status='New').count()
    converted_leads = Lead.objects.filter(status='Converted').count()
    lost_leads = Lead.objects.filter(status='Lost').count()

    # User Management
    total_users = User.objects.count()
    active_users = User.objects.filter(is_active=True).count()
    admin_count = User.objects.filter(user_type='ADMIN').count()
    sales_manager_count = User.objects.filter(user_type='SALES_MANAGER').count()
    sales_rep_count = User.objects.filter(user_type='SALES_REP').count()
    viewer_count = User.objects.filter(user_type='VIEWER').count()

    # Recent Activity
   # recent_activity = ActivityLog.objects.all().order_by('-timestamp')[:10]

    # Notifications (example)
    notifications = [
        {'message': '5 new leads added today.'},
        {'message': '2 leads converted this week.'},
    ]

    return render(request, 'admin_dashboard.html', {
        'total_leads': total_leads,
        'new_leads': new_leads,
        'converted_leads': converted_leads,
        'lost_leads': lost_leads,
        'total_users': total_users,
        'active_users': active_users,
        'admin_count': admin_count,
        'sales_manager_count': sales_manager_count,
        'sales_rep_count': sales_rep_count,
        'viewer_count': viewer_count,
        #'recent_activity': recent_activity,
        'notifications': notifications,
    })


# Sales Rep Dashboard
@login_required
@user_passes_test(lambda user: user.user_type == 'sales_rep')
def salesrep_dashboard(request):
    leads = Lead.objects.filter(assigned_to=request.user)
    return render(request, 'salesrep_dashboard.html', {'leads': leads})

# Sales Manager Dashboard
@login_required
@user_passes_test(lambda user: user.user_type == 'sales_manager')
def salesmanager_dashboard(request):
    leads = Lead.objects.all()
    return render(request, 'salesmanager_dashboard.html', {'leads': leads})

# Viewer Dashboard

#@user_passes_test(lambda user: user.user_type == 'viewer')
def viewer_dashboard(request):
    return render(request, 'viewer_dashboard.html')'''