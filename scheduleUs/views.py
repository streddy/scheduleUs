from .forms import EventCreationForm, EventResponseForm
from django.forms import modelformset_factory
from django.forms.models import modelform_factory
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.template import loader
from django.urls import reverse, reverse_lazy
from django.views.generic.edit import DeleteView, UpdateView
from .models import Event, UserInvited, PollResponse
from users.models import Profile, Friends
from mapwidgets.widgets import GooglePointFieldWidget
from utils.utilities import run_algorithm
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

    friends_attending = {}
    friends_attending = PollResponse.objects.filter(event=curr_event).values('responder')
    if friends_attending:
        friends_attending = Profile.objects.filter(id__in=friends_attending)
        creator = Profile.objects.filter(id=curr_event.organizer.id)
        friends_attending = friends_attending | creator

        curr_friends = Friends.objects.filter(initiator=request.user).values('friend')
        if curr_friends:
            curr_friends = Profile.objects.filter(id__in=curr_friends)
            friends_attending = friends_attending.filter(id__in=curr_friends)
        else:
            friends_attending = {}

    context = {'event' : curr_event, 'friends_attending' : friends_attending}
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

    scheduled_list = {}
    event_list = {}
    invited_list = {}
    public_list = {}
    
    if(request.user.is_authenticated):
        username = request.user.username
        
        going_to = PollResponse.objects.filter(responder=request.user).values('event')
        if going_to:
            going_to = Event.objects.filter(id__in=going_to)
            going_to = going_to.filter(is_closed=True)

        scheduled_list = Event.objects.filter(organizer=request.user)
        scheduled_list = scheduled_list.filter(is_closed=True)

        if going_to:
            scheduled_list = scheduled_list | going_to

        event_list = Event.objects.filter(organizer=request.user)
        event_list = event_list.exclude(is_closed=True)
        for event1 in event_list:
            print(event1.event_length)
            poll_end = event1.poll_end.replace(tzinfo=utc)
            if(event1.poll_end<now):
                obj = Event.objects.get(id = event1.id)
                obj.is_closed = True

                time = str(event1.event_length)
                days = int(time.split(':')[0].split()[0])
                hours = days * 24 + int(time.split(':')[1])
                minutes = int(time.split(':')[2])

                event_length = [hours, minutes]

                responses = PollResponse.objects.filter(event=event1)
                response_times = []
                for response in responses:
                    response_times.append([response.responder_start, response.responder_end])
                options = [event1.allow_flex, event1.on_time_attendees]
                if response_times:
                    answer = run_algorithm(event_length, event1.poll_timeframe_start, event1.poll_timeframe_end, response_times, options)
                    finished_start_time = datetime.datetime.combine(answer[0], answer[1])
                    finished_end_time = finished_start_time + datetime.timedelta(seconds=answer[2]*60)

                    obj.start_time = finished_start_time
                    obj.end_time = finished_end_time
                
                else:
                    sec = 60 * minutes + 3600 * hours
                    obj.start_time = event1.poll_timeframe_start
                    obj.end_time = event1.poll_timeframe_start + datetime.timedelta(seconds=sec)
                    
                obj.save()
                UserInvited.objects.filter(event=event1).delete()    
                
        invited_list = UserInvited.objects.filter(invited_user=request.user).values('event')
        if invited_list:
            invited_list = Event.objects.filter(id__in=invited_list)
            invited_list = invited_list.exclude(is_closed=True)
            invited_list = invited_list.exclude(organizer=request.user)
            for event1 in invited_list:
                poll_end = event1.poll_end.replace(tzinfo=utc)
                if(event1.poll_end<now):
                    obj = Event.objects.get(id = event1.id)
                    obj.is_closed = True

                    time = str(event1.event_length)
                    days = int(time.split(':')[0].split()[0])
                    hours = days * 24 + int(time.split(':')[1])
                    minutes = int(time.split(':')[2])

                    event_length = [hours, minutes]

                    responses = PollResponse.objects.filter(event=event1)
                    response_times = []
                    for response in responses:
                        response_times.append([response.responder_start, response.responder_end])
                    options = [event1.allow_flex, event1.on_time_attendees]
                    if response_times:
                        answer = run_algorithm(event_length, event1.poll_timeframe_start, event1.poll_timeframe_end, response_times, options)
                        finished_start_time = datetime.datetime.combine(answer[0], answer[1])
                        finished_end_time = finished_start_time + datetime.timedelta(seconds=answer[2]*60)

                        obj.start_time = finished_start_time
                        obj.end_time = finished_end_time
                    
                    else:
                        sec = 60 * minutes + 3600 * hours
                        obj.start_time = event1.poll_timeframe_start
                        obj.end_time = event1.poll_timeframe_start + datetime.timedelta(seconds=sec)
                    
                    obj.save()
                    UserInvited.objects.filter(event=event1).delete()    

        public_list = Event.objects.filter(is_public=True)
        if public_list:
            public_list = public_list.exclude(organizer=request.user)
            public_list = public_list.exclude(is_closed=True)

    context = {'scheduled_list' : scheduled_list, 'event_list' : event_list, 'invited_list' : invited_list, 'public_list' : public_list}
    return HttpResponse(template.render(context, request))

class EventDelete(DeleteView):
    model = Event
    success_url = reverse_lazy('delete_event')

class EventUpdate(UpdateView):
    model = Event
    form_class =  modelform_factory(
        Event,
        fields=('name', 'location', 'description', 'poll_timeframe_start', 'poll_timeframe_end', 'poll_end', 'event_length', 'is_public', 'allow_flex', 'on_time_attendees'),
        widgets={'location': GooglePointFieldWidget}
    )
    template_name = 'event_update_form.html'
    success_url = reverse_lazy('dashboard')
