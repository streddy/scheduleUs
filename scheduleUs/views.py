from .forms import EventCreationForm
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.template import loader
from .models import Event
from django.urls import reverse_lazy
from django.views.generic.edit import DeleteView, UpdateView
def create_event(request):
    if request.method == 'POST':  # data sent by user
        form = EventCreationForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.organizer = request.user
            obj.save()
            return redirect('dashboard')
    else:  # display empty form
        form = EventCreationForm()

    return render(request, 'create_event.html', {'event_form': form})

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
        #STILL NEED TO FIX THIS I HAVE NO WAY HOW TO
        #user = models.OneToOneField(User,related_name="profile")
        #event_list = Event.objects.filter(organizer = request.user.profile)
        event_list = Event.objects.all()
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
    fields = ['name', 'location', 'description']
    success_url = reverse_lazy('dashboard')
