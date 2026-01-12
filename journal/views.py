from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from .models import Horse, Rider, JournalEntry, Comment, Event, Goal
from .forms import JournalEntryForm, CommentForm, EventForm, GoalForm


def login_view(request):
    """Login view where riders select horse and rider name."""
    if request.method == 'POST':
        horse_id = request.POST.get('horse')
        rider_id = request.POST.get('rider')
        
        if horse_id and rider_id:
            try:
                rider = Rider.objects.get(id=rider_id, horse_id=horse_id)
                request.session['rider_id'] = rider.id
                return redirect('dashboard')
            except Rider.DoesNotExist:
                messages.error(request, "Invalid selection.")
    
    horses = Horse.objects.all()
    context = {'horses': horses}
    return render(request, 'journal/login.html', context)


def get_riders_for_horse(request, horse_id):
    """AJAX endpoint to get riders for a selected horse."""
    from django.http import JsonResponse
    horse = get_object_or_404(Horse, id=horse_id)
    riders = horse.riders.values('id', 'name')
    return JsonResponse(list(riders), safe=False)


def dashboard_view(request):
    """Display dashboard with journal entries for logged-in rider."""
    rider_id = request.session.get('rider_id')
    if not rider_id:
        return redirect('login')
    
    rider = get_object_or_404(Rider, id=rider_id)
    entries = rider.journal_entries.all()
    
    context = {
        'rider': rider,
        'entries': entries
    }
    return render(request, 'journal/dashboard.html', context)


def create_entry_view(request):
    """Create a new journal entry."""
    rider_id = request.session.get('rider_id')
    if not rider_id:
        return redirect('login')
    
    rider = get_object_or_404(Rider, id=rider_id)
    
    if request.method == 'POST':
        form = JournalEntryForm(request.POST, request.FILES)
        if form.is_valid():
            entry = form.save(commit=False)
            entry.rider = rider
            entry.save()
            messages.success(request, 'Entry created successfully!')
            return redirect('dashboard')
    else:
        form = JournalEntryForm()
    
    context = {'rider': rider, 'form': form}
    return render(request, 'journal/create_entry.html', context)


def entry_detail_view(request, entry_id):
    """View a specific journal entry and its comments."""
    rider_id = request.session.get('rider_id')
    if not rider_id:
        return redirect('login')
    
    entry = get_object_or_404(JournalEntry, id=entry_id)
    rider = get_object_or_404(Rider, id=rider_id)
    
    # Check if this rider can view this entry
    if entry.rider != rider:
        messages.error(request, "You don't have permission to view this entry.")
        return redirect('dashboard')
    
    comments = entry.comments.all()
    
    context = {
        'rider': rider,
        'entry': entry,
        'comments': comments
    }
    return render(request, 'journal/entry_detail.html', context)


def alert_michelle_view(request, entry_id):
    """Alert Michelle about a new entry."""
    rider_id = request.session.get('rider_id')
    if not rider_id:
        return redirect('login')
    
    entry = get_object_or_404(JournalEntry, id=entry_id)
    rider = get_object_or_404(Rider, id=rider_id)
    
    if entry.rider != rider:
        messages.error(request, "You don't have permission to modify this entry.")
        return redirect('dashboard')
    
    entry.alerted_michelle = True
    entry.save()
    
    # Send email to Michelle
    subject = f"New Journal Entry from {rider.name} ({rider.horse.name})"
    message = f"""
Hello Michelle,

{rider.name} has just submitted a new journal entry for {rider.horse.name} and would like your feedback.

Rider: {rider.name}
Horse: {rider.horse.name}
Submitted: {entry.created_at.strftime('%B %d, %Y at %I:%M %p')}

Entry Preview:
{entry.text_content[:300] if entry.text_content else '(No text content)'}{'...' if entry.text_content and len(entry.text_content) > 300 else ''}

Please log in to the dashboard to review the full entry and add your comments.

Best regards,
Equestrian Journal App
    """.strip()
    
    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [settings.MICHELLE_EMAIL],
            fail_silently=False,
        )
        messages.success(request, 'Michelle has been notified!')
    except Exception as e:
        messages.warning(request, f'Entry saved, but email notification failed: {str(e)}')
    
    return redirect('entry_detail', entry_id=entry.id)


def logout_view(request):
    """Logout the rider."""
    request.session.flush()
    messages.success(request, 'Logged out successfully!')
    return redirect('login')


# Michelle's Views

def michelle_login_view(request):
    """Login page for Michelle (head trainer)."""
    if request.method == 'POST':
        password = request.POST.get('password', '')
        # Simple password check - in production, use proper authentication
        if password == 'michelle':  # This should be in settings/env variable
            request.session['is_michelle'] = True
            return redirect('michelle_dashboard')
        else:
            messages.error(request, 'Incorrect password.')
    
    return render(request, 'journal/michelle_login.html')


def michelle_dashboard_view(request):
    """Michelle's dashboard showing all alerted entries."""
    if not request.session.get('is_michelle'):
        return redirect('michelle_login')
    
    # Get all entries where Michelle has been alerted, ordered by most recent
    alerted_entries = JournalEntry.objects.filter(
        alerted_michelle=True
    ).select_related('rider', 'rider__horse').prefetch_related('comments').order_by('-created_at')
    
    # Separate into reviewed and pending
    reviewed_entries = alerted_entries.filter(comments__isnull=False).distinct()
    pending_entries = alerted_entries.filter(comments__isnull=True)
    
    context = {
        'alerted_entries': alerted_entries,
        'reviewed_entries': reviewed_entries,
        'pending_entries': pending_entries,
        'pending_count': pending_entries.count(),
    }
    return render(request, 'journal/michelle_dashboard.html', context)


def michelle_entry_view(request, entry_id):
    """Michelle's view of a specific entry with comment form."""
    if not request.session.get('is_michelle'):
        return redirect('michelle_login')
    
    entry = get_object_or_404(JournalEntry, id=entry_id, alerted_michelle=True)
    comments = entry.comments.all()
    
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.entry = entry
            comment.save()
            messages.success(request, 'Comment added successfully!')
            return redirect('michelle_entry', entry_id=entry.id)
    else:
        form = CommentForm()
    
    context = {
        'entry': entry,
        'comments': comments,
        'form': form,
    }
    return render(request, 'journal/michelle_entry.html', context)


def michelle_logout_view(request):
    """Logout Michelle."""
    request.session.flush()
    messages.success(request, 'Logged out successfully!')
    return redirect('michelle_login')


# Management Views (for adding horses and riders)

def management_login_view(request):
    """Login for management (add horses/riders)."""
    if request.method == 'POST':
        password = request.POST.get('password', '')
        if password == 'admin123':  # Simple password - change this!
            request.session['is_admin'] = True
            return redirect('manage_horses')
        else:
            messages.error(request, 'Invalid password.')
    
    return render(request, 'journal/management_login.html')


def manage_horses_view(request):
    """Manage horses - add/edit."""
    if not request.session.get('is_admin'):
        return redirect('management_login')
    
    horses = Horse.objects.all().order_by('name')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'add':
            horse_name = request.POST.get('horse_name', '').strip()
            if horse_name:
                horse, created = Horse.objects.get_or_create(name=horse_name)
                if created:
                    messages.success(request, f'Horse "{horse_name}" added!')
                else:
                    messages.info(request, f'Horse "{horse_name}" already exists.')
            else:
                messages.error(request, 'Horse name is required.')
        elif action == 'delete':
            horse_id = request.POST.get('horse_id')
            try:
                horse = Horse.objects.get(id=horse_id)
                horse_name = horse.name
                horse.delete()
                messages.success(request, f'Horse "{horse_name}" deleted!')
            except Horse.DoesNotExist:
                messages.error(request, 'Horse not found.')
        
        return redirect('manage_horses')
    
    context = {'horses': horses}
    return render(request, 'journal/manage_horses.html', context)


def manage_riders_view(request):
    """Manage riders - add/edit."""
    if not request.session.get('is_admin'):
        return redirect('management_login')
    
    horses = Horse.objects.all().order_by('name')
    riders = Rider.objects.all().order_by('name')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'add':
            rider_name = request.POST.get('rider_name', '').strip()
            horse_id = request.POST.get('horse_id')
            
            if not rider_name or not horse_id:
                messages.error(request, 'Rider name and horse are required.')
            else:
                try:
                    horse = Horse.objects.get(id=horse_id)
                    rider, created = Rider.objects.get_or_create(
                        name=rider_name,
                        horse=horse
                    )
                    if created:
                        messages.success(request, f'Rider "{rider_name}" added to {horse.name}!')
                    else:
                        messages.info(request, f'Rider "{rider_name}" already exists for {horse.name}.')
                except Horse.DoesNotExist:
                    messages.error(request, 'Horse not found.')
        elif action == 'delete':
            rider_id = request.POST.get('rider_id')
            try:
                rider = Rider.objects.get(id=rider_id)
                rider_name = rider.name
                rider.delete()
                messages.success(request, f'Rider "{rider_name}" deleted!')
            except Rider.DoesNotExist:
                messages.error(request, 'Rider not found.')
        
        return redirect('manage_riders')
    
    context = {
        'horses': horses,
        'riders': riders,
    }
    return render(request, 'journal/manage_riders.html', context)


# Calendar Views

def calendar_view(request):
    """Display calendar for logged-in rider's horse."""
    from datetime import datetime
    from calendar import monthcalendar, month_name
    
    rider_id = request.session.get('rider_id')
    if not rider_id:
        return redirect('login')
    
    rider = get_object_or_404(Rider, id=rider_id)
    
    # Get month/year from request or use current
    year = int(request.GET.get('year', datetime.now().year))
    month = int(request.GET.get('month', datetime.now().month))
    
    # Get all events for this horse in this month
    from .models import Event
    events = Event.objects.filter(horse=rider.horse, date__year=year, date__month=month)
    
    # Create a dict of events by date for easy lookup
    events_by_date = {}
    for event in events:
        date_key = event.date.day
        if date_key not in events_by_date:
            events_by_date[date_key] = []
        events_by_date[date_key].append(event)
    
    # Build calendar
    cal = monthcalendar(year, month)
    
    # Navigation
    prev_month = month - 1 if month > 1 else 12
    prev_year = year if month > 1 else year - 1
    next_month = month + 1 if month < 12 else 1
    next_year = year if month < 12 else year + 1
    
    context = {
        'rider': rider,
        'horse': rider.horse,
        'year': year,
        'month': month,
        'month_name': month_name[month],
        'calendar': cal,
        'events_by_date': events_by_date,
        'prev_month': prev_month,
        'prev_year': prev_year,
        'next_month': next_month,
        'next_year': next_year,
    }
    return render(request, 'journal/calendar.html', context)


def add_event_view(request):
    """Add an event to the calendar."""
    from .forms import EventForm
    
    rider_id = request.session.get('rider_id')
    if not rider_id:
        return redirect('login')
    
    rider = get_object_or_404(Rider, id=rider_id)
    
    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            event.horse = rider.horse
            event.created_by = rider
            event.save()
            messages.success(request, 'Event added to calendar!')
            return redirect('calendar')
    else:
        form = EventForm()
    
    context = {
        'rider': rider,
        'form': form,
        'title': 'Add Event'
    }
    return render(request, 'journal/event_form.html', context)


def edit_event_view(request, event_id):
    """Edit an event."""
    from .forms import EventForm
    from .models import Event
    
    rider_id = request.session.get('rider_id')
    if not rider_id:
        return redirect('login')
    
    rider = get_object_or_404(Rider, id=rider_id)
    event = get_object_or_404(Event, id=event_id, horse=rider.horse)
    
    # Check if rider created this event or is admin
    if event.created_by != rider:
        messages.error(request, "You can only edit events you created.")
        return redirect('calendar')
    
    if request.method == 'POST':
        form = EventForm(request.POST, instance=event)
        if form.is_valid():
            form.save()
            messages.success(request, 'Event updated!')
            return redirect('calendar')
    else:
        form = EventForm(instance=event)
    
    context = {
        'rider': rider,
        'form': form,
        'event': event,
        'title': 'Edit Event'
    }
    return render(request, 'journal/event_form.html', context)


def delete_event_view(request, event_id):
    """Delete an event."""
    from .models import Event
    
    rider_id = request.session.get('rider_id')
    if not rider_id:
        return redirect('login')
    
    rider = get_object_or_404(Rider, id=rider_id)
    event = get_object_or_404(Event, id=event_id, horse=rider.horse)
    
    # Check if rider created this event
    if event.created_by != rider:
        messages.error(request, "You can only delete events you created.")
        return redirect('calendar')
    
    if request.method == 'POST':
        event.delete()
        messages.success(request, 'Event deleted!')
        return redirect('calendar')
    
    context = {
        'rider': rider,
        'event': event,
    }
    return render(request, 'journal/event_confirm_delete.html', context)


def michelle_calendar_view(request):
    """Michelle's view of all horses' events."""
    from datetime import datetime
    from calendar import monthcalendar, month_name
    from .models import Event
    
    if not request.session.get('is_michelle'):
        return redirect('michelle_login')
    
    # Get month/year from request or use current
    year = int(request.GET.get('year', datetime.now().year))
    month = int(request.GET.get('month', datetime.now().month))
    
    # Get all events for all horses in this month
    all_events = Event.objects.filter(date__year=year, date__month=month).order_by('date', 'time')
    
    # Create a dict of events by date
    events_by_date = {}
    for event in all_events:
        date_key = event.date.day
        if date_key not in events_by_date:
            events_by_date[date_key] = []
        events_by_date[date_key].append(event)
    
    # Build calendar
    cal = monthcalendar(year, month)
    
    # Navigation
    prev_month = month - 1 if month > 1 else 12
    prev_year = year if month > 1 else year - 1
    next_month = month + 1 if month < 12 else 1
    next_year = year if month < 12 else year + 1
    
    context = {
        'year': year,
        'month': month,
        'month_name': month_name[month],
        'calendar': cal,
        'events_by_date': events_by_date,
        'prev_month': prev_month,
        'prev_year': prev_year,
        'next_month': next_month,
        'next_year': next_year,
        'all_events': all_events,
    }
    return render(request, 'journal/michelle_calendar.html', context)


# Goal management views

def goals_view(request):
    """Display list of goals for the logged-in rider."""
    rider_id = request.session.get('rider_id')
    if not rider_id:
        return redirect('login')
    
    rider = get_object_or_404(Rider, id=rider_id)
    active_goals = rider.goals.filter(status='active').order_by('-created_at')
    completed_goals = rider.goals.filter(status='completed').order_by('-completed_at')
    
    context = {
        'rider': rider,
        'active_goals': active_goals,
        'completed_goals': completed_goals,
    }
    return render(request, 'journal/goals.html', context)


def add_goal_view(request):
    """Create a new goal."""
    rider_id = request.session.get('rider_id')
    if not rider_id:
        return redirect('login')
    
    rider = get_object_or_404(Rider, id=rider_id)
    
    if request.method == 'POST':
        form = GoalForm(request.POST)
        if form.is_valid():
            goal = form.save(commit=False)
            goal.rider = rider
            goal.save()
            messages.success(request, f"Goal '{goal.title}' added successfully!")
            return redirect('goals')
    else:
        form = GoalForm()
    
    context = {
        'rider': rider,
        'form': form,
        'title': 'Add New Goal'
    }
    return render(request, 'journal/goal_form.html', context)


def edit_goal_view(request, goal_id):
    """Edit an existing goal."""
    rider_id = request.session.get('rider_id')
    if not rider_id:
        return redirect('login')
    
    goal = get_object_or_404(Goal, id=goal_id, rider_id=rider_id)
    
    if request.method == 'POST':
        form = GoalForm(request.POST, instance=goal)
        if form.is_valid():
            form.save()
            messages.success(request, f"Goal '{goal.title}' updated successfully!")
            return redirect('goals')
    else:
        form = GoalForm(instance=goal)
    
    context = {
        'rider': goal.rider,
        'form': form,
        'goal': goal,
        'title': f'Edit Goal: {goal.title}'
    }
    return render(request, 'journal/goal_form.html', context)


def complete_goal_view(request, goal_id):
    """Mark a goal as completed."""
    rider_id = request.session.get('rider_id')
    if not rider_id:
        return redirect('login')
    
    goal = get_object_or_404(Goal, id=goal_id, rider_id=rider_id)
    goal.status = 'completed'
    goal.completed_at = timezone.now()
    goal.save()
    messages.success(request, f"🎉 Goal '{goal.title}' completed!")
    return redirect('goals')


def reactivate_goal_view(request, goal_id):
    """Mark a completed goal as active again."""
    rider_id = request.session.get('rider_id')
    if not rider_id:
        return redirect('login')
    
    goal = get_object_or_404(Goal, id=goal_id, rider_id=rider_id)
    goal.status = 'active'
    goal.completed_at = None
    goal.save()
    messages.success(request, f"Goal '{goal.title}' reactivated.")
    return redirect('goals')


@require_http_methods(["POST"])
def delete_goal_view(request, goal_id):
    """Delete a goal."""
    rider_id = request.session.get('rider_id')
    if not rider_id:
        return redirect('login')
    
    goal = get_object_or_404(Goal, id=goal_id, rider_id=rider_id)
    goal_title = goal.title
    goal.delete()
    messages.success(request, f"Goal '{goal_title}' deleted.")
    return redirect('goals')
