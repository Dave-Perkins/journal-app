from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('entry/new/', views.create_entry_view, name='create_entry'),
    path('entry/<int:entry_id>/', views.entry_detail_view, name='entry_detail'),
    path('entry/<int:entry_id>/alert/', views.alert_michelle_view, name='alert_michelle'),
    path('logout/', views.logout_view, name='logout'),
    path('api/riders/<int:horse_id>/', views.get_riders_for_horse, name='get_riders'),
    
    # Calendar routes
    path('calendar/', views.calendar_view, name='calendar'),
    path('calendar/event/add/', views.add_event_view, name='add_event'),
    path('calendar/event/<int:event_id>/edit/', views.edit_event_view, name='edit_event'),
    path('calendar/event/<int:event_id>/delete/', views.delete_event_view, name='delete_event'),
    
    # Goals routes
    path('goals/', views.goals_view, name='goals'),
    path('goals/add/', views.add_goal_view, name='add_goal'),
    path('goals/<int:goal_id>/edit/', views.edit_goal_view, name='edit_goal'),
    path('goals/<int:goal_id>/complete/', views.complete_goal_view, name='complete_goal'),
    path('goals/<int:goal_id>/reactivate/', views.reactivate_goal_view, name='reactivate_goal'),
    path('goals/<int:goal_id>/delete/', views.delete_goal_view, name='delete_goal'),
    
    # Michelle's routes
    path('michelle/', views.michelle_login_view, name='michelle_login'),
    path('michelle/dashboard/', views.michelle_dashboard_view, name='michelle_dashboard'),
    path('michelle/entry/<int:entry_id>/', views.michelle_entry_view, name='michelle_entry'),
    path('michelle/calendar/', views.michelle_calendar_view, name='michelle_calendar'),
    path('michelle/logout/', views.michelle_logout_view, name='michelle_logout'),
    
    # Management routes
    path('manage/login/', views.management_login_view, name='management_login'),
    path('manage/horses/', views.manage_horses_view, name='manage_horses'),
    path('manage/riders/', views.manage_riders_view, name='manage_riders'),
]
