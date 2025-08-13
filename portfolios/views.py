from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def portfolio_list(request):
    """Display list of portfolios"""
    return render(request, 'portfolios/portfolio_list.html', {
        'title': 'Portfolios'
    })
