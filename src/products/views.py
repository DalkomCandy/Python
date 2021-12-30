from django.shortcuts import render

from .models import Product
from .forms import ProductForm
# Create your views here.
def product_detail_view(request):
    obj = Product.objects.get(id=1)
    context = {
        'title' : obj.title, 
        'description' : obj.description
        }

    return render(request, 'product/detail.html', context)

# def product_create_view(request):
#     form = ProductForm(request.POST or None)
#     if form.is_valid():
#         form.save()
#     context = {
#         'form' : form
#     }
    
#     return render(request, 'product/product_forms.html', context)
def product_create_view(request):
    print(request.GET)
    print(request.POST)
    title = request.POST.get('title')
    context = {}
    return render(request, 'product/product_forms.html', context)