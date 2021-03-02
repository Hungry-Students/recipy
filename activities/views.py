# import json

# from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt

# from users.models import User


def get_local_person(request, username):
    # user = get_object_or_404(User, username=username)
    pass


def get_entry(request, username, entry_id):
    pass


@csrf_exempt
def get_outbox(request, username):
    # user = get_object_or_404(User, username=username)
    # if request.method == "GET":
    #     objects = user.activities.filter(remote=False).order_by("-created_at")
    #     pass
    pass


def store(activity, person, remote=False):
    pass


def deliver(activity):
    pass


def get_final_audience(audience):
    pass


def deliver_to(ap_id, activity):
    pass


def dereference(ap_id):
    pass


def get_or_create_remote_person(ap_id):
    pass


@csrf_exempt
def get_inbox(request, username):
    pass


def handle_entry(activity):
    pass


def handle_follow(activity):
    pass


def get_entries(request, username):
    pass


def get_followers(request, username):
    pass


def get_following(request, username):
    pass


def get_activity(request, username, aid):
    pass
