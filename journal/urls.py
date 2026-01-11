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
    
    # Michelle's routes
    path('michelle/', views.michelle_login_view, name='michelle_login'),
    path('michelle/dashboard/', views.michelle_dashboard_view, name='michelle_dashboard'),
    path('michelle/entry/<int:entry_id>/', views.michelle_entry_view, name='michelle_entry'),
    path('michelle/logout/', views.michelle_logout_view, name='michelle_logout'),
    
    # Management routes
    path('manage/login/', views.management_login_view, name='management_login'),
    path('manage/horses/', views.manage_horses_view, name='manage_horses'),
    path('manage/riders/', views.manage_riders_view, name='manage_riders'),
]
