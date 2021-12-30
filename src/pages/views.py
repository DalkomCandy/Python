from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
def home_view(request, *args, **kwargs):
    #return HttpResponse("<h1>Hello World</h1>") # string of HTML CODE
    return render(request, 'home.html', {})

def about_view(request, *args, **kwargs):
    my_context = {
        "my_text": "This is about us",
        "my_number" : 123,
        "my_list" : [312,456,789]
    }

    return render(request, 'about.html', my_context) # string of HTML CODE

def contact_view(request, *args, **kwargs):
    return render(request, 'contact.html',) # string of HTML CODE

def social_view(request, *args, **kwargs):
    return render(request, 'about.html',) # string of HTML CODE
    