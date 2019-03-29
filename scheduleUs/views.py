from .forms import EventCreationForm
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.template import loader

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
