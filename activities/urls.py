from django.urls import path

from . import views

app_name = "activities"
urlpatterns = [
    path("<str:username>/entries/<int:entry_id>", views.get_entry, name="entry"),
    path("<str:username>/entries", views.get_entries, name="entries"),
    path("<str:username>/following", views.get_following, name="following"),
    path("<str:username>/followers", views.get_followers, name="followers"),
    path("<str:username>/inbox", views.get_inbox, name="inbox"),
    path("<str:username>/outbox", views.get_outbox, name="outbox"),
    path(
        "<str:username>/outbox/<int:activity_id>", views.get_activity, name="activity"
    ),
    path("<str:username>", views.get_local_person, name="person"),
]
