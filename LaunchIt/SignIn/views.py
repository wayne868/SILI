from django.shortcuts import render, redirect
from django.utils import timezone
from .models import VisitReason, IndividualSignIn, EventSignIn
from django.contrib import messages
import datetime
from django.db.models import Sum, Count

# Create your views here.
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

def monthly_report(request):
    """View for monthly sign-in statistics"""
    today = timezone.now().date()
    current_year = today.year
    
    # Get the first day of the current month
    first_day_of_month = today.replace(day=1)
    # Get the first day of the next month
    if today.month == 12:
        first_day_of_next_month = today.replace(year=today.year + 1, month=1, day=1)
    else:
        first_day_of_next_month = today.replace(month=today.month + 1, day=1)
    
    # Get the first day of the current year
    first_day_of_year = today.replace(month=1, day=1)
    # Get the first day of the next year
    first_day_of_next_year = today.replace(year=today.year + 1, month=1, day=1)
    
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
    
    # Year-to-date calculations
    individual_signins_ytd = IndividualSignIn.objects.filter(
        date__gte=first_day_of_year,
        date__lt=today + datetime.timedelta(days=1)  # Include today
    ).count()
    
    events_ytd = EventSignIn.objects.filter(
        date__gte=first_day_of_year,
        date__lt=today + datetime.timedelta(days=1)  # Include today
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
        'month_name': today.strftime('%B %Y'),
        'year': current_year,
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
