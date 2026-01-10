from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from .models import Horse, Rider, JournalEntry, Comment
from .forms import JournalEntryForm, CommentForm


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
