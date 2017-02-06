from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.contrib.auth.models import User
from .models import Room
from .forms import RegistrationForm, ProfileForm, UserForm
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.db import transaction
from haikunator import Haikunator


@login_required
@transaction.atomic
def update_profile(request):
    args = {}

    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = ProfileForm(request.POST, instance=request.user.profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return HttpResponseRedirect('/')
    else:
        user_form = UserForm(instance=request.user)
        profile_form = ProfileForm(instance=request.user.profile)

    args['user_form'] = user_form
    args['profile_form'] = profile_form
    return render(request, 'registration/update_profile.html', args)


def register_page(request):
    args = {}
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            User.objects.create_user(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password1'],
                email=form.cleaned_data['email'],
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name']
            )
            return HttpResponseRedirect('/login')

    args['form'] = RegistrationForm()
    return render(request, 'financial_app/register.html', args)


@login_required
def home(request):
    users = User.objects.filter(~Q(username=request.user.username)).all()
    return render(request, "financial_app/home.html", {
        'users': users
    })


@login_required
def new_room(request):
    """
    Randomly create a new room, and redirect to it.
    """
    user2 = User.objects.get(username=request.GET['username'])
    try:
        room = Room.objects.filter(Q(subscribers__username__exact = request.user.username)).filter(Q(subscribers__username__exact = request.GET['username'])).get()
    except Room.DoesNotExist:
        haikunator = Haikunator()
        new_room = None
        while not new_room:
            with transaction.atomic():
                label = haikunator.haikunate()
                if Room.objects.filter(label=label).exists():
                    continue
                new_room = Room.objects.create(label=label)
                new_room.subscribers.add(request.user)
                new_room.subscribers.add(user2)
    else:
        label = room.label

    return redirect(chat_room, label=label)


@login_required
def chat_room(request, label):
    """
    Room view - show the room, with latest messages.
    The template for this view has the WebSocket business to send and stream
    messages, so see the template for where the magic happens.
    """
    # If the room with the given label doesn't exist, automatically create it
    # upon first visit (a la etherpad).
    room, created = Room.objects.get_or_create(label=label)

    # We want to show the last 50 messages, ordered most-recent-last
    if request.user.profile.history:
        messages = reversed(room.messages.order_by('-timestamp'))
    else:
        messages = reversed(room.messages.order_by('-timestamp')[:50])

    return render(request, "financial_app/index.html", {
        'room': room,
        'chat_list': messages,
    })
