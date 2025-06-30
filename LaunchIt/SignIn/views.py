from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from .models import VisitReason, IndividualSignIn, EventSignIn
from django.contrib import messages
import datetime
from django.db.models import Sum, Count
from django.http import HttpResponseRedirect
from django.urls import reverse
from functools import wraps
from django.conf import settings

# Create your views here.
# Admin authentication decorator
def admin_required(view_func):
    """Decorator to check if user has admin access"""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.session.get('admin_authenticated', False):
            return view_func(request, *args, **kwargs)
        else:
            # Store the original URL to redirect after login
            next_url = request.path
            return redirect(reverse('admin_login') + f'?next={next_url}')
    return _wrapped_view

def admin_login(request):
    """View for admin login"""
    next_url = request.GET.get('next', reverse('home'))
    
    if request.method == 'POST':
        password = request.POST.get('password')
        # Set a simple admin password - in production, use a more secure approach
        admin_password = getattr(settings, 'ADMIN_PASSWORD', 'admin123')
        
        if password == admin_password:
            request.session['admin_authenticated'] = True
            return redirect(request.POST.get('next', reverse('home')))
        else:
            return render(request, 'signin/admin_login.html', {
                'error_message': 'Incorrect password. Please try again.',
                'next': next_url
            })
    
    return render(request, 'signin/admin_login.html', {'next': next_url})

def admin_logout(request):
    """View to log out admin"""
    if 'admin_authenticated' in request.session:
        del request.session['admin_authenticated']
    messages.success(request, "You have been logged out successfully.")
    return redirect('home')

def home(request):
    """View for the landing page with two buttons"""
    return render(request, 'signin/home.html')

def individual_signin(request):
    """View for individual sign-in form"""
    if request.method == 'POST':
        name = request.POST.get('name')
        date = request.POST.get('date')
        reason_id = request.POST.get('reason')
        
        if name and date and reason_id:
            reason = VisitReason.objects.get(pk=reason_id)
            IndividualSignIn.objects.create(
                name=name,
                date=date,
                reason=reason
            )
            messages.success(request, "Sign-in completed successfully!")
            return redirect('home')
        else:
            messages.error(request, "Please fill out all fields.")
    
    context = {
        'reasons': VisitReason.objects.all(),
        'today': timezone.now().date().isoformat()
    }
    return render(request, 'signin/individual_signin.html', context)

def event_signin(request):
    """View for event sign-in form"""
    if request.method == 'POST':
        organizer_name = request.POST.get('organizer_name')
        date = request.POST.get('date')
        reason_id = request.POST.get('reason')
        attendee_count = request.POST.get('attendee_count')
        
        if organizer_name and date and reason_id and attendee_count:
            reason = VisitReason.objects.get(pk=reason_id)
            EventSignIn.objects.create(
                organizer_name=organizer_name,
                date=date,
                reason=reason,
                attendee_count=attendee_count
            )
            messages.success(request, "Event sign-in completed successfully!")
            return redirect('home')
        else:
            messages.error(request, "Please fill out all fields.")
    
    context = {
        'reasons': VisitReason.objects.all(),
        'today': timezone.now().date().isoformat()
    }
    return render(request, 'signin/event_signin.html', context)

@admin_required
def monthly_report(request):
    """View for monthly sign-in statistics with month/year filter and date range filter"""
    today = timezone.now().date()
    
    # Check if using date range filter or month/year filter
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')
    filter_type = request.GET.get('filter_type', 'monthly')
    
    # Initialize date range variables
    start_date = None
    end_date = None
    using_date_range = False
    
    # If date range filter is selected and dates are provided
    if filter_type == 'range' and start_date_str and end_date_str:
        try:
            start_date = datetime.datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.datetime.strptime(end_date_str, '%Y-%m-%d').date()
            # Ensure end date is not earlier than start date
            if end_date < start_date:
                # Swap if entered incorrectly
                start_date, end_date = end_date, start_date
            using_date_range = True
        except ValueError:
            # If date parsing fails, fall back to monthly filter
            using_date_range = False
    
    # Default to monthly filtering if not using date range
    selected_year = request.GET.get('year')
    selected_month = request.GET.get('month')
    
    # Parse to integers if provided
    try:
        if selected_year:
            selected_year = int(selected_year)
        else:
            selected_year = today.year
            
        if selected_month:
            selected_month = int(selected_month)
        else:
            selected_month = today.month
    except ValueError:
        selected_year = today.year
        selected_month = today.month
    
    # Create date object for selected month/year
    selected_date = datetime.date(selected_year, selected_month, 1)
    
    # Define filter period based on selected filter type
    if using_date_range:
        # For date range, use the provided dates
        first_day_of_month = start_date
        first_day_of_next_month = end_date + datetime.timedelta(days=1)  # Include the end date
        period_description = f"{start_date.strftime('%b %d, %Y')} - {end_date.strftime('%b %d, %Y')}"
    else:
        # For monthly filter, use month boundaries
        first_day_of_month = selected_date
        if selected_month == 12:
            first_day_of_next_month = datetime.date(selected_year + 1, 1, 1)
        else:
            first_day_of_next_month = datetime.date(selected_year, selected_month + 1, 1)
        period_description = selected_date.strftime('%B %Y')
    
    # Define year period based on filter type
    if using_date_range:
        # For date range, use the year of the start date
        first_day_of_year = datetime.date(start_date.year, 1, 1)
        first_day_of_next_year = datetime.date(start_date.year + 1, 1, 1)
        current_year = start_date.year
    else:
        # For monthly filter, use the selected year
        first_day_of_year = datetime.date(selected_year, 1, 1)
        first_day_of_next_year = datetime.date(selected_year + 1, 1, 1)
        current_year = selected_year
    
    # Query for individual sign-ins this month
    individual_signins_month = IndividualSignIn.objects.filter(
        date__gte=first_day_of_month,
        date__lt=first_day_of_next_month
    ).count()
    
    # Query for event sign-ins this month
    events_month = EventSignIn.objects.filter(
        date__gte=first_day_of_month,
        date__lt=first_day_of_next_month
    )
    
    # Calculate total attendees from events this month
    event_attendees_month = events_month.aggregate(total=Sum('attendee_count'))['total'] or 0
    
    # Total people count for this month (individuals + event attendees)
    total_people_month = individual_signins_month + event_attendees_month
    
    # Year-to-date calculations (up to the end date of selected period)
    if using_date_range:
        ytd_end_date = end_date
    else:
        ytd_end_date = first_day_of_next_month - datetime.timedelta(days=1)
    
    individual_signins_ytd = IndividualSignIn.objects.filter(
        date__gte=first_day_of_year,
        date__lt=ytd_end_date + datetime.timedelta(days=1)  # Include last day of period
    ).count()
    
    events_ytd = EventSignIn.objects.filter(
        date__gte=first_day_of_year,
        date__lt=ytd_end_date + datetime.timedelta(days=1)  # Include last day of period
    )
    
    event_attendees_ytd = events_ytd.aggregate(total=Sum('attendee_count'))['total'] or 0
    total_people_ytd = individual_signins_ytd + event_attendees_ytd
    
    # Full year calculations
    individual_signins_year = IndividualSignIn.objects.filter(
        date__gte=first_day_of_year,
        date__lt=first_day_of_next_year
    ).count()
    
    events_year = EventSignIn.objects.filter(
        date__gte=first_day_of_year,
        date__lt=first_day_of_next_year
    )
    
    event_attendees_year = events_year.aggregate(total=Sum('attendee_count'))['total'] or 0
    total_people_year = individual_signins_year + event_attendees_year
    
    # Get count by reason for individual sign-ins (monthly)
    individual_by_reason = IndividualSignIn.objects.filter(
        date__gte=first_day_of_month,
        date__lt=first_day_of_next_month
    ).values('reason__name').annotate(count=Count('id')).order_by('-count')
    
    # Get count by reason for event attendees (monthly)
    event_by_reason = EventSignIn.objects.filter(
        date__gte=first_day_of_month,
        date__lt=first_day_of_next_month
    ).values('reason__name').annotate(count=Sum('attendee_count')).order_by('-count')
    
    context = {
        'period_description': period_description,
        'year': current_year,
        'selected_month': selected_month,
        'selected_year': selected_year,
        'years_range': range(today.year - 5, today.year + 1),
        'using_date_range': using_date_range,
        'filter_type': filter_type,
        'start_date': start_date_str if start_date_str else '',
        'end_date': end_date_str if end_date_str else '',
        # Monthly stats
        'individual_signins_month': individual_signins_month,
        'event_attendees_month': event_attendees_month,
        'total_people_month': total_people_month,
        # Year-to-date stats
        'individual_signins_ytd': individual_signins_ytd,
        'event_attendees_ytd': event_attendees_ytd,
        'total_people_ytd': total_people_ytd,
        # Full year stats
        'individual_signins_year': individual_signins_year,
        'event_attendees_year': event_attendees_year,
        'total_people_year': total_people_year,
        # Breakdown by reason
        'individual_by_reason': individual_by_reason,
        'event_by_reason': event_by_reason
    }
    
    return render(request, 'signin/monthly_report.html', context)

def get_available_years():
    """Helper function to get all years that have data"""
    # Get the earliest and latest years from both sign-in models
    individual_years = IndividualSignIn.objects.dates('date', 'year')
    event_years = EventSignIn.objects.dates('date', 'year')
    
    # Combine all years and remove duplicates
    all_years = set()
    for date_obj in individual_years:
        all_years.add(date_obj.year)
    for date_obj in event_years:
        all_years.add(date_obj.year)
    
    # Get current year if no data exists
    if not all_years:
        all_years = {timezone.now().date().year}
    
    # Convert to sorted list
    return sorted(list(all_years))

@admin_required
def manage_signins(request):
    """View for managing all sign-ins with delete functionality"""
    # Handle deletion requests
    if request.method == 'POST':
        signin_type = request.POST.get('signin_type')
        signin_id = request.POST.get('signin_id')
        
        if signin_type and signin_id:
            if signin_type == 'individual':
                signin = get_object_or_404(IndividualSignIn, pk=signin_id)
                signin.delete()
                messages.success(request, "Individual sign-in deleted successfully!")
            elif signin_type == 'event':
                signin = get_object_or_404(EventSignIn, pk=signin_id)
                signin.delete()
                messages.success(request, "Event sign-in deleted successfully!")
        
        # Redirect back to the same page to prevent form resubmission
        return HttpResponseRedirect(reverse('manage_signins'))
    
    # Get all individual sign-ins
    individual_signins = IndividualSignIn.objects.all().order_by('-timestamp')
    
    # Get all event sign-ins
    event_signins = EventSignIn.objects.all().order_by('-timestamp')
    
    context = {
        'individual_signins': individual_signins,
        'event_signins': event_signins
    }
    
    return render(request, 'signin/manage_signins.html', context)
