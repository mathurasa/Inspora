from django.urls import path
from . import views

app_name = 'solutions'

urlpatterns = [
    # Main solutions page
    path('', views.solutions_overview, name='overview'),
    
    # Company Type Solutions
    path('enterprise/', views.enterprise_solution, name='enterprise'),
    path('small-business/', views.small_business_solution, name='small_business'),
    path('nonprofit/', views.nonprofit_solution, name='nonprofit'),
    path('startup/', views.startup_solution, name='startup'),
    
    # Team Solutions
    path('operations/', views.operations_solution, name='operations'),
    path('marketing/', views.marketing_solution, name='marketing'),
    path('it/', views.it_solution, name='it'),
    path('leaders/', views.leaders_solution, name='leaders'),
    path('sales/', views.sales_solution, name='sales'),
    
    # Industry Solutions
    path('healthcare/', views.healthcare_solution, name='healthcare'),
    path('retail/', views.retail_solution, name='retail'),
    path('financial/', views.financial_solution, name='financial'),
    path('education/', views.education_solution, name='education'),
    path('manufacturing/', views.manufacturing_solution, name='manufacturing'),
    
    # Use Case Solutions
    path('goal-management/', views.goal_management_solution, name='goal_management'),
    path('organizational-planning/', views.organizational_planning_solution, name='organizational_planning'),
    path('project-intake/', views.project_intake_solution, name='project_intake'),
    path('resource-planning/', views.resource_planning_solution, name='resource_planning'),
    path('product-launches/', views.product_launches_solution, name='product_launches'),
]
