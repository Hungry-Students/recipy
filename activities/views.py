import json
from urllib.parse import urlparse

import requests
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt

import activities.activities as acts
from recipes.models import Entry, Recipe
from users.models import User

from .models import Activity


def get_local_person(request, username):
    user = get_object_or_404(User, username=username)
    return JsonResponse(acts.Person(user).to_json(context=True))


def get_entry(request, username, entry_id):
    entry = get_object_or_404(Entry, id=entry_id)
    entry_as = entry.to_activitystream()
    entry_json = entry_as.to_json(context=True)
    return JsonResponse(entry_json)


@csrf_exempt
def outbox(request, username):
    user = get_object_or_404(User, username=username)

    if request.method == "GET":
        objects = user.activities.filter(remote=False).order_by("-created_at")
        collection = acts.OrderedCollection(objects)
        return JsonResponse(collection.to_json())

    payload = request.body.decode("utf-8")
    activity = json.loads(payload, object_hook=acts.as_activitystream)

    if activity.type == "Follow":
        if activity.object.type != "Person":
            raise Exception("Sorry, you can only follow Persons objects")

        followed = get_or_create_remote_person(activity.object)
        user.following.add(followed)

        activity.actor = user.uris.id
        activity.to = followed.uris.id
        activity.id = store(activity, user)
        deliver(activity)
        return HttpResponse(status=202)

    raise Exception("Invalid Request")


def store(activity, person, remote=False):
    """
    Stores `activity` in database
    """
    payload = bytes(json.dumps(activity.to_json()), "utf-8")
    obj = Activity(payload=payload, person=person, remote=remote)
    if remote:
        obj.ap_id = activity.id
    obj.save()
    return obj.ap_id


def deliver(activity):
    """
    Posts `acitivity` in the inbox of all relevant users
    """
    audience = activity.get_audience()
    activity = activity.strip_audience()
    audience = get_final_audience(audience)
    for ap_id in audience:
        deliver_to(ap_id, activity)


def get_final_audience(audience):
    """
    Return a list of the `ap_id`s contained in `æudience`
    """
    final_audience = []
    for ap_id in audience:
        obj = dereference(ap_id)
        if isinstance(obj, acts.Collection):
            final_audience += [item.id for item in obj.items]
        elif isinstance(obj, acts.Person):
            final_audience.append(obj.id)
    return set(final_audience)


def deliver_to(ap_id, activity):
    """
    Post `activity` in inbox referenced by `ap_id`
    """
    obj = dereference(ap_id)
    if not getattr(obj, "inbox"):
        return

    res = requests.post(obj.inbox, json=activity.to_json(context=True))
    if res.status_code != 200:
        msg = "Failed to deliver activity {0} to {1}"
        msg = msg.format(activity.type, obj.inbox)
        raise Exception(msg)


def dereference(ap_id):
    """
    Get object identified by `ap_id`
    """
    res = requests.get(ap_id)
    if res.status_code != 200:
        raise Exception("Failed to dereference {0}".format(ap_id))

    return json.loads(res.text, object_hook=acts.as_activitystream)


def get_or_create_remote_person(ap_id):
    try:
        person = User.objects.get(ap_id=ap_id)
    except User.DoesNotExist:
        person = dereference(ap_id)
        hostname = urlparse(person.id).hostname
        username = "{0}@{1}".format(person.preferredUsername, hostname)
        person = User(
            username=username,
            name=person.name,
            ap_id=person.id,
            remote=True,
        )
        person.save()
    return person


@csrf_exempt
def inbox(request, username):
    user = get_object_or_404(User, username=username)
    if request.method == "GET":
        objects = user.activities.filter(remote=True).order_by("-created_at")
        collection = acts.OrderedCollection(objects)
        return JsonResponse(collection.to_json())

    payload = request.body.decode("utf-8")
    activity = json.loads(payload, object_hook=acts.as_activitystream)
    activity.validate()

    if activity.type == "Create":
        handle_entry(activity)
    elif activity.type == "Follow":
        handle_follow(activity)

    store(activity, user, remote=True)
    return HttpResponse()


def handle_entry(activity):
    """
    Assume `acitvity` is a Create activity with object Entry.
    Add the corresponding entry to the database.
    """
    if isinstance(activity.actor, acts.Person):
        ap_id = activity.actor.id
    else:
        ap_id = activity.actor

    user = get_or_create_remote_person(ap_id)

    if Entry.objects.get(ap_id=activity.object.id).exists():
        return

    entry_json = activity.object

    recipe = get_or_create_remote_recipe(ap_id)

    entry = Entry(
        ap_id=entry_json.id,
        remote=True,
        recipe=recipe,
        cookbook=user.cookbook,
    )
    entry.save()


def get_or_create_remote_recipe(ap_id):
    try:
        recipe = Recipe.objects.get(ap_id=ap_id)
    except Recipe.DoesNotExist:
        recipe = dereference(ap_id)
        recipe = Recipe(
            ap_id=recipe.id,
            remote=True,
            name=recipe.name,
            # ingredients= TODO get_or_create_ingredient
            cook_time=int(recipe.duration[2:-1]) if recipe.duration else None,
            cooking_method=recipe.cookingMethod,
            category=recipe.recipeCategory,
            instructions=recipe.content,
            quantity=recipe.recipeYield.split(" ")[0],
            quantity_unit=recipe.recipeYield.split(" ")[1:],
        )
        recipe.save()
    return recipe


def handle_follow(activity):
    """
    Assume `acitvity` is a Follow activity with object User.
    Add the corresponding relation to the database.
    """
    followed = get_object_or_404(User, ap_id=activity.object)

    if isinstance(activity.actor, acts.Person):
        ap_id = activity.actor.id
    elif isinstance(activity.actor, str):
        ap_id = activity.actor
    else:
        raise Exception("Cannot interpret actor {}".format(activity.actor))

    follower = get_or_create_remote_person(ap_id)
    followed.followers.add(follower)


def get_entries(request, username):
    user = get_object_or_404(User, username=username)
    recipes = user.cookbook.recipes.through.objects.filter(cookbook=user.cookbook)
    recipes_as = [recipe.to_activitystream() for recipe in recipes]
    collection = acts.OrderedCollection(recipes_as)
    return JsonResponse(collection.to_json())


def get_followers(request, username):
    user = get_object_or_404(User, username=username)
    followers = acts.OrderedCollection(user.followers.all())
    return JsonResponse(followers.to_json())


def get_following(request, username):
    user = get_object_or_404(User, username=username)
    following = acts.OrderedCollection(user.following.all())
    return JsonResponse(following.to_json())


def get_activity(request, username, aid):
    activity = get_object_or_404(Activity, pk=aid)
    payload = activity.payload.decode("utf-8")
    activity = json.loads(payload, object_hook=acts.as_activitystream)
    return JsonResponse(activity.to_json(context=True))
