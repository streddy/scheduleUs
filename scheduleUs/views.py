from .forms import EventCreationForm
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.template import loader
from django.urls import reverse, reverse_lazy
from django.views.generic.edit import DeleteView, UpdateView
from .models import Event

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
    template = loader.get_template('invite_users.html')
    curr_event = Event.objects.get(id=event_id)
    context = {'event' : curr_event,}
    return HttpResponse(template.render(context, request))

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

    if(request.user.is_authenticated):
        username = request.user.username
        event_list = Event.objects.filter(organizer=request.user)
        context = { 'event_list' : event_list,}
    else :
        event_list = {}
        context = {'event_list' : event_list, }
    return HttpResponse(template.render(context, request))

class EventDelete(DeleteView):
    model = Event
    success_url = reverse_lazy('delete_event')

class EventUpdate(UpdateView):
    model = Event
    template_name = 'event_update_form.html'
    fields = ('name', 'location', 'description', 'poll_timeframe_start', 'poll_timeframe_end', 'poll_end')
    success_url = reverse_lazy('dashboard')
