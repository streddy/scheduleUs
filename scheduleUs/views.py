from .forms import EventCreationForm, EventResponseForm
from django.forms import modelformset_factory
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.template import loader
from django.urls import reverse, reverse_lazy
from django.views.generic.edit import DeleteView, UpdateView
from django.db.models import Q
from .models import Event, UserInvited
from users.models import Friends
import datetime
import pytz

utc=pytz.UTC

# EVENT VIEWS
def create_event(request):
    if request.method == 'POST':  # data sent by user
        form = EventCreationForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.organizer = request.user
            obj.save()
            return redirect(reverse('invite_users', kwargs={"event_id": obj.pk}))
    else:  # display empty form
        form = EventCreationForm()

    return render(request, 'create_event.html', {'event_form': form})

def respond_to_event(request, event_id):
    if request.method == 'POST':
        form = EventResponseForm(request.POST)
        if form.is_valid():
            obj = form.save(commit = False)
            obj.responder = request.user
            obj.event = Event.objects.get(id=event_id)
            obj.save()
            UserInvited.objects.filter(event=event_id, invited_user=request.user).delete()    
            return redirect('dashboard')
    else:
        form = EventResponseForm()     
    event_responding_to = Event.objects.get(id=event_id)
    context = {'response_form':form, 'event':event_responding_to} 
    return render(request, 'respond_to_poll.html', context)   

def decline_event(request, event_id):
    event_responding_to = Event.objects.get(id=event_id)
    if(request.user.is_authenticated):
        UserInvited.objects.filter(event=event_id, invited_user=request.user).delete()
    context = {'event':event_responding_to}
    return render(request, 'decline_event.html', context)
   
def invite_users(request, event_id):
    friends = Friends.objects.filter(initiator=request.user)
    invited_event = Event.objects.get(id=event_id)

    if not UserInvited.objects.filter(event=invited_event):
        for friend in friends:
            UserInvited.objects.create(invited_user=friend.friend, event=invited_event)

    potential_invites = UserInvited.objects.filter(event=invited_event)
    friend_formset = modelformset_factory(UserInvited, fields=['is_invited'], extra=0)
    form = friend_formset(queryset=potential_invites)
    
    if request.method == 'POST':
        form = friend_formset(request.POST)
        if form.is_valid():
            decisions = form.save(commit=False)
            for decision in decisions:
                if decision.is_invited:
                    decision.save()

            UserInvited.objects.filter(event=invited_event, is_invited=0).delete()
            return redirect('dashboard')

    context = {'event' : invited_event, 'invite_form' : form}
    return render(request, 'invite_users.html', context)

def event_page(request, event_id):
    template = loader.get_template('event_page.html')
    curr_event = Event.objects.get(id=event_id)
    context = {'event' : curr_event}
    return HttpResponse(template.render(context, request))

def delete_event(request):
    template = loader.get_template('delete_event.html')
    context = {}
    return HttpResponse(template.render(context,request))

def dashboard(request):
    username = None
    template=loader.get_template('dashboard.html')
    now = datetime.datetime.now()
    now = now.replace(tzinfo=utc)
    event_list = {}
    invited_list = {}
    if(request.user.is_authenticated):
        username = request.user.username
        event_list = Event.objects.filter(organizer=request.user)
        event_list = event_list.exclude(is_closed=True)
        for event1 in event_list:
            poll_end = event1.poll_end.replace(tzinfo=utc)
            if(event1.poll_end<now):
                obj = Event.objects.get(id = event1.id)
                obj.is_closed = True
                obj.save()
                #event1.is_closed = True
        invited = UserInvited.objects.filter(invited_user=request.user).values('event')
        invited_list = Event.objects.filter(Q(id__in=invited) | Q(is_public=True))
        if invited_list:
            invited_list = invited_list.exclude(is_closed=True)
            invited_list = invited_list.exclude(organizer=request.user)
            for event1 in invited_list:
                poll_end = event1.poll_end.replace(tzinfo=utc)
                if(event1.poll_end<now):
                    obj = Event.objects.get(id = event1.id)
                    obj.is_closed = True
                    obj.save()
    
    context = {'event_list' : event_list, 'invited_list' : invited_list}
    return HttpResponse(template.render(context, request))

class EventDelete(DeleteView):
    model = Event
    success_url = reverse_lazy('delete_event')

class EventUpdate(UpdateView):
    model = Event
    template_name = 'event_update_form.html'
    fields = ('name', 'location', 'description', 'poll_timeframe_start', 'poll_timeframe_end', 'poll_end', 'is_public')
    success_url = reverse_lazy('dashboard')
