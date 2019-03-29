from .forms import EventCreationForm
from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader

def create_event(request):
    if request.method == 'POST':  # data sent by user
        form = EventCreationForm(request.POST)
        if form.is_valid():
            template = loader.get_template("dashboard.html")
            obj = form.save(commit=False)
            obj.organizer = request.user
            obj.save()
            return HttpResponse(template.render())
    else:  # display empty form
        form = EventCreationForm()

    return render(request, 'create_event.html', {'event_form': form})
