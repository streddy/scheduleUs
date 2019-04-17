from .forms import EventCreationForm
from django.forms import modelformset_factory
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.template import loader
from django.urls import reverse, reverse_lazy
from django.views.generic.edit import DeleteView, UpdateView
from django.db.models import Q
from .models import Event, UserInvited
from users.models import Friends

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
    context = {'event' : curr_event,}
    return HttpResponse(template.render(context, request))

def delete_event(request):
    template = loader.get_template('delete_event.html')
    context = {}
    return HttpResponse(template.render(context,request))

def dashboard(request):
    username = None
    template=loader.get_template('dashboard.html')

    event_list = {}
    invited_list = {}
    if(request.user.is_authenticated):
        username = request.user.username
        event_list = Event.objects.filter(organizer=request.user)
        invited = UserInvited.objects.filter(invited_user=request.user).values('event')
        invited_list = Event.objects.filter(Q(id__in=invited) | Q(is_public=True))
        if invited_list:
            invited_list = invited_list.exclude(organizer=request.user)
    
    context = {'event_list' : event_list, 'invited_list' : invited_list}
    return HttpResponse(template.render(context, request))

class EventDelete(DeleteView):
    model = Event
    success_url = reverse_lazy('delete_event')

class EventUpdate(UpdateView):
    model = Event
    template_name = 'event_update_form.html'
    fields = ('name', 'location', 'description', 'poll_timeframe_start', 'poll_timeframe_end', 'poll_end', 'event_length', 'is_public', 'allow_flex', 'on_time_attendees')
    success_url = reverse_lazy('dashboard')
