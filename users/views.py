from django.urls import reverse_lazy
from django.shortcuts import render, redirect
from django.views import generic
from .forms import *


# FRIEND VIEW
def add_friend(request):
    if request.method == 'POST':  # data sent by user
        form = FriendForm(request.POST, request=request)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.initiator = request.user
            obj.save()
            return redirect('dashboard')
    else:  # display empty form
        form = FriendForm(request=request)

    return render(request, 'add_friend.html', {'add_friend_form': form})

    
class SignUp(generic.CreateView):
    form_class = ProfileCreationForm
    success_url = reverse_lazy('login')
    template_name = 'signup.html'
