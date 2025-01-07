from django.http import HttpRequest
from django.shortcuts import render,redirect
import re
from admin_box.models import Categories
# Create your views here.
def index(request):
    return render(request, "ad_index.html")

def ad_login(request):
    return render(request, 'ad_login.html')

def ad_category(request):
    categories = Categories.objects.all()
    return render(request, 'ad_category.html',{'categories':categories})

def ad_add_category(request):
    return render(request, 'ad_create_category.html')

def ad_edit_categories(request, edit_id):
    edit = Categories.objects.get(id=edit_id)
    return render(request, 'ad_create_category.html', {'edit':edit})

def slugify(text):
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s-]', '', text)  # Remove special characters
    text = re.sub(r'\s+', '-', text)  # Replace spaces with hyphens
    return text



def save_category(request):
    
    if request.method == 'POST':
            cat_Name = request.POST.get('cat_name')
            cat_Icon = request.POST.get('cat_icon')
            cat_Color = request.POST.get('cat_color')
            cat_Description = request.POST.get('cat_desc')
            cat_Slug = slugify(cat_Name)

            # Create and save the category instance
            new_category = Categories(
                catName=cat_Name, catIcon=cat_Icon, catColor=cat_Color, catDescription=cat_Description, catSlug=cat_Slug
            )
            if not Categories.objects.filter(catSlug=cat_Slug).exists():  # Check if category exists
                new_category.save()
                # Success message
                notification = "Category created successfully!"     
                return render(request, 'success.html', {
                    'mesType': 'bg-success',
                    'message': notification,
                    'redir': '../category',
                    "notification": notification
                })
            else:
                # Error message
                notification = "Category already exists!"     
                return render(request, 'success.html', {
                    'mesType': 'bg-danger',
                    'message': notification,
                    'redir': '../category',
                    "notification": notification
                })
                
def cat_delete(request,del_id):
    Categories.objects.filter(id=del_id).delete()
    notification = "Category deleted successfully!"     
    return render(request, 'success.html', {
                    'mesType': 'bg-success',
                    'message': notification,
                    'redir': '../category',
                    "notification": notification
                })
    

def update_category(request):
    
    if request.method == 'POST':
            slugs = request.POST.get('slugs')
            cat_Name = request.POST.get('cat_name')
            cat_Icon = request.POST.get('cat_icon')
            cat_Color = request.POST.get('cat_color')
            cat_Description = request.POST.get('cat_desc')
            cat_Slug = slugify(cat_Name)

            # Create and save the category instance
            new_category = Categories.objects.filter(catSlug=slugs)
            new_category.update(
                catName=cat_Name, catIcon=cat_Icon, catColor=cat_Color, catDescription=cat_Description, 
                )
                # Success message
            notification = "Category updated successfully!"     
            return render(request, 'success.html', {
                    'mesType': 'bg-success',
                    'message': notification,
                    'redir': '../category',
                    "notification": notification
                })   
