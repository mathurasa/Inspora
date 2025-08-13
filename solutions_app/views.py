from django.shortcuts import render
from django.contrib.auth.decorators import login_required

def solutions_overview(request):
    """Main solutions overview page."""
    return render(request, 'solutions_app/overview.html', {
        'title': 'Solutions - Inspora',
        'active_tab': 'overview'
    })

# Company Type Solutions
def enterprise_solution(request):
    """Enterprise solution page."""
    return render(request, 'solutions_app/enterprise.html', {
        'title': 'Enterprise Solutions - Inspora',
        'active_tab': 'enterprise'
    })

def small_business_solution(request):
    """Small business solution page."""
    return render(request, 'solutions_app/small_business.html', {
        'title': 'Small Business Solutions - Inspora',
        'active_tab': 'small_business'
    })

def nonprofit_solution(request):
    """Nonprofit solution page."""
    return render(request, 'solutions_app/nonprofit.html', {
        'title': 'Nonprofit Solutions - Inspora',
        'active_tab': 'nonprofit'
    })

def startup_solution(request):
    """Startup solution page."""
    return render(request, 'solutions_app/startup.html', {
        'title': 'Startup Solutions - Inspora',
        'active_tab': 'startup'
    })

# Team Solutions
def operations_solution(request):
    """Operations team solution page."""
    return render(request, 'solutions_app/operations.html', {
        'title': 'Operations Solutions - Inspora',
        'active_tab': 'operations'
    })

def marketing_solution(request):
    """Marketing team solution page."""
    return render(request, 'solutions_app/marketing.html', {
        'title': 'Marketing Solutions - Inspora',
        'active_tab': 'marketing'
    })

def it_solution(request):
    """IT team solution page."""
    return render(request, 'solutions_app/it.html', {
        'title': 'IT Solutions - Inspora',
        'active_tab': 'it'
    })

def leaders_solution(request):
    """Leadership solution page."""
    return render(request, 'solutions_app/leaders.html', {
        'title': 'Leadership Solutions - Inspora',
        'active_tab': 'leaders'
    })

def sales_solution(request):
    """Sales team solution page."""
    return render(request, 'solutions_app/sales.html', {
        'title': 'Sales Solutions - Inspora',
        'active_tab': 'sales'
    })

# Industry Solutions
def healthcare_solution(request):
    """Healthcare industry solution page."""
    return render(request, 'solutions_app/healthcare.html', {
        'title': 'Healthcare Solutions - Inspora',
        'active_tab': 'healthcare'
    })

def retail_solution(request):
    """Retail industry solution page."""
    return render(request, 'solutions_app/retail.html', {
        'title': 'Retail Solutions - Inspora',
        'active_tab': 'retail'
    })

def financial_solution(request):
    """Financial services solution page."""
    return render(request, 'solutions_app/financial.html', {
        'title': 'Financial Services Solutions - Inspora',
        'active_tab': 'financial'
    })

def education_solution(request):
    """Education industry solution page."""
    return render(request, 'solutions_app/education.html', {
        'title': 'Education Solutions - Inspora',
        'active_tab': 'education'
    })

def manufacturing_solution(request):
    """Manufacturing industry solution page."""
    return render(request, 'solutions_app/manufacturing.html', {
        'title': 'Manufacturing Solutions - Inspora',
        'active_tab': 'manufacturing'
    })

# Use Case Solutions
def goal_management_solution(request):
    """Goal management use case solution page."""
    return render(request, 'solutions_app/goal_management.html', {
        'title': 'Goal Management Solutions - Inspora',
        'active_tab': 'goal_management'
    })

def organizational_planning_solution(request):
    """Organizational planning use case solution page."""
    return render(request, 'solutions_app/organizational_planning.html', {
        'title': 'Organizational Planning Solutions - Inspora',
        'active_tab': 'organizational_planning'
    })

def project_intake_solution(request):
    """Project intake use case solution page."""
    return render(request, 'solutions_app/project_intake.html', {
        'title': 'Project Intake Solutions - Inspora',
        'active_tab': 'project_intake'
    })

def resource_planning_solution(request):
    """Resource planning use case solution page."""
    return render(request, 'solutions_app/resource_planning.html', {
        'title': 'Resource Planning Solutions - Inspora',
        'active_tab': 'resource_planning'
    })

def product_launches_solution(request):
    """Product launches use case solution page."""
    return render(request, 'solutions_app/product_launches.html', {
        'title': 'Product Launches Solutions - Inspora',
        'active_tab': 'product_launches'
    })
