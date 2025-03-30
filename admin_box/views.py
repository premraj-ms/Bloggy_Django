from django.http import HttpRequest
from django.shortcuts import render,redirect
import re

from django.contrib.auth.decorators import login_required
from admin_box.models import Categories
from django.core.paginator import Paginator
from web_user.models import *
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.db.models.functions import TruncMonth
from django.db.models import Count
from datetime import timedelta
from django.utils import timezone
from django.db.models.functions import TruncDate
from admin_box.views import slugify


def ad_login(request):
    if request.user.is_authenticated:
        return redirect(index)  
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username, password=password)  # Fix the variable issue

        if user is not None:
            login(request, user)  # Logs in the user
            return redirect(index)  # Use the correct URL name or view function

        else:
            return render(request, "ad_login.html", {"error": "Invalid username or password"})

    return render(request, 'ad_login.html')


@login_required(login_url="ad_login")

def index(request):
    totalPost = Web_post.objects.count()
    totalComment = Comment.objects.count()
    totalUsers =  Web_users.objects.count()
    totalCategory = Categories.objects.count()
    
    post_data = (
        Web_post.objects.annotate(month=TruncMonth("created_at"))
        .values("month")
        .annotate(count=Count("id"))
        .order_by("month")
    )

    # Formatting data for the frontend
    months = []
    post_counts = []

    month_labels = {
        1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr", 5: "May", 6: "Jun",
        7: "Jul", 8: "Aug", 9: "Sep", 10: "Oct", 11: "Nov", 12: "Dec"
    }

    for entry in post_data:
        month_number = entry["month"].month
        months.append(month_labels[month_number])
        post_counts.append(entry["count"])

    
   
        # Calculate the date range (last 90 days)
    start_date = timezone.now() - timedelta(days=90)

    # Query user registration count per day
    user_data = (
        Web_users.objects.filter(created_at__gte=start_date)
        .annotate(day=TruncDate("created_at"))
        .values("day")
        .annotate(count=Count("id"))
        .order_by("day")
    )


    days = [(start_date + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(91)]
    user_counts = {entry["day"].strftime("%Y-%m-%d"): entry["count"] for entry in user_data}


    users_per_day = [user_counts.get(day, 0) for day in days]


    data ={
        "totalPost":totalPost,
        'totalComment': totalComment,
        'totalCategory': totalCategory,
        'totalUsers':totalUsers,
        "months": months,
        "post_counts": post_counts,
        "days": days,  
        "users_per_day": users_per_day 
    }
    return render(request, "ad_index.html",data)


@login_required(login_url="ad_login")
def ad_category(request):
    categories = Categories.objects.all()
    return render(request, 'ad_category.html',{'categories':categories})

@login_required(login_url="ad_login")
def ad_add_category(request):
    return render(request, 'ad_create_category.html')

@login_required(login_url="ad_login")
def ad_edit_categories(request, edit_id):
    edit = Categories.objects.get(id=edit_id)
    return render(request, 'ad_create_category.html', {'edit':edit})


def slugify(text):
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s-]', '', text)  # Remove special characters
    text = re.sub(r'\s+', '-', text)  # Replace spaces with hyphens
    return text



@login_required(login_url="ad_login")
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
                
@login_required(login_url="ad_login")
def cat_delete(request,del_id):
    Categories.objects.filter(id=del_id).delete()
    notification = "Category deleted successfully!"     
    return render(request, 'success.html', {
                    'mesType': 'bg-success',
                    'message': notification,
                    'redir': '../category',
                    "notification": notification
                })
    

@login_required(login_url="ad_login")
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

@login_required(login_url="ad_login")
def userList(request):
    users = Web_users.objects.all()
    user_data = []
    
    for user in users:
        post_count = Web_post.objects.filter(post_author=user).count()
        user_data.append({"user": user, "post_count": post_count})
    paginator = Paginator(user_data, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, "ad_web_users.html", {"users": page_obj})
@login_required(login_url="ad_login")
def commentList(request):
    comments = Comment.objects.all().select_related('author').order_by("-created_at")
    paginator = Paginator(comments, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, "ad_web_comments.html", {'comments':page_obj})

@login_required(login_url="ad_login")
def BlogpostList(request):
    blog = Web_post.objects.all().order_by("-created_at")
    paginator = Paginator(blog, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, "ad_web_blogposts.html", {"blogpost":page_obj})


# DELETE FUNTIONALITY 
@login_required(login_url="ad_login")
def delUser(request, delId):
    Web_users.objects.get(id = delId).delete()
    return redirect(userList)

@login_required(login_url="ad_login")
def delComment(request, delId):
    Comment.objects.get(id = delId).delete()
    return redirect(commentList)

@login_required(login_url="ad_login")
def delPost(request, delId):
    Web_post.objects.get(id = delId).delete()
    return redirect(delPost)
    