from django.contrib import messages
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.hashers import check_password, make_password
from admin_box.views import slugify
from admin_box.models import Categories
from django.utils.datastructures import MultiValueDictKeyError
from django.core.files.storage import FileSystemStorage
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import *
from django.shortcuts import get_object_or_404
from django.utils.text import slugify
from django.core.exceptions import ValidationError
import urllib.parse
import requests, os
from Bloggy import settings
from django.views import View
from .models import Web_users, Follow
from django.db.models import OuterRef, Subquery, Q, Count
from django.core.mail import send_mail
# Create your views here.
def web_index(request):
    posts = Web_post.objects.select_related('post_author', 'post_category')\
    .annotate(comment_count=Count('comments', filter=Q(comments__is_approved=True)))\
    .order_by('-created_at')[:9]
    
    featured = Web_post.objects.select_related('post_author', 'post_category') \
        .annotate(comment_count=Count('comments', filter=Q(comments__is_approved=True))) \
        .order_by('?')  # Randomize posts
    meta = """
        <title>Bloggy - The ultimate Blogging platform</title>
        <meta name="description" content="Welcome Bloggy - The ultimate Blogging platform">
    """
    
    if 'user_id' in request.session:
        user_id = request.session.get('user_id')  
        following_users = Follow.objects.filter(user_id=user_id).select_related('following_user')
        followed_user_details = [follow.following_user for follow in following_users]
        
    else:
        followed_user_details = False
        
    context = {
        'featured_post': featured.first(),  # Pick the first random post for featured
        'other_posts': featured[1:4] , # Limit to other smaller posts (e.g., 3)
        'posts': posts,
        "metadetails":meta,
        'followed_users': followed_user_details
    }
        
    return render(request, 'web_index.html', context)

def web_blogdraft(request):
    if 'user_id' not in request.session:
        return redirect(web_login)
    meta = """
        <title>Draft blog - Bloggy</title>
        <meta name="description" content="Bloggy - Blog draft page">
    """
    return render(request, 'web_blogdraft.html', {"metadetails":meta})

def web_category(request, catSlug, page=1):
    try:
        page = int(page)  # Ensure the page number is an integer
        if page < 1:
            raise ValueError("Page number must be positive.")
    except (ValueError, TypeError):
        raise Http404("Invalid page number.")
    
    # Get the category
    category = get_object_or_404(Categories, catSlug=catSlug)
    
    # Fetch all posts for the category
    posts_query = Web_post.objects.select_related('post_author', 'post_category') \
        .filter(post_category__catSlug=catSlug) \
        .annotate(comment_count=Count('comments', filter=Q(comments__is_approved=True))) \
        .order_by('-created_at')
    
    # Paginate posts with 10 per page
    paginator = Paginator(posts_query, 10)  # 10 posts per page
    
    try:
        current_page = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver the first page.
        current_page = paginator.page(1)
    except EmptyPage:
        # If page is out of range, raise a 404 error.
        raise Http404("Page not found.")
    meta = f"""
        <title> {category.catName}</title>
        <meta name="description" content="{category.catDescription}">
    """
    # Pass required data to the template
    return render(request, 'web_category.html', {
        'posts': current_page.object_list,
        'category': category,
        'page': current_page.number,
        'total_pages': paginator.num_pages,
        'page_range': paginator.get_elided_page_range(current_page.number),
        "metadetails":meta
    })
    
def web_post(request, category, post):
    # Ensure category and post exist
    
    cnt1 = get_object_or_404(Categories, catSlug=category)
    cnt2 = get_object_or_404(Web_post, post_slug=post)

    post_details = Web_post.objects.select_related('post_author', 'post_category').filter(
        post_category__catSlug=category, 
        post_slug=post
    ).first()
    related_posts = Web_post.objects.select_related('post_author', 'post_category').filter(
        post_category__catSlug=category
    )\
            .order_by('-created_at')[:6]
            
    comments = Comment.objects.filter(post=post_details).select_related( 'author').order_by('-created_at')
    view_count = 1+ post_details.view_count
    
    meta = f""" 
        <title>{post_details.post_title}</title>
        <meta name="description" content="{post_details.post_desc}">"""
    Web_post.objects.filter(post_slug=post).update(view_count=view_count)
    return render(request, 'web_post.html', {'post': post_details, "related":related_posts, 'comments':comments, "metadetails":meta})

def web_search(request):
    return render(request, 'web_search.html')

def web_userprofile(request):
    if 'user_id' not in request.session:
        return redirect(web_index)

    post_author = request.session["user_id"]
    
    # Fetch all posts for the logged-in user
    posts_query = Web_post.objects.select_related('post_author', 'post_category') \
        .filter(post_author=post_author) \
        .annotate(comment_count=Count('comments', filter=Q(comments__is_approved=True))) \
        .order_by('-created_at')
    top_categories = (Web_post.objects
                  .select_related('post_author', 'post_category')  # Optimize related data fetching
                  .filter(post_author=post_author)  # Filter posts by the user
                  .values('post_category')  # Group by the post_category
                  .annotate(post_count=Count('post_category'))  # Annotate with the number of posts per category
                  .order_by('-post_count')  # Order by post count in descending order
                  [:3])  # Limit to top 3 categories

# Initialize a list to store the contributions
    contributions = []

# Iterate over the top categories and display their information
    for top_category in top_categories:
        top_category_id = top_category['post_category']
    
        try:
            top_category_instance = Categories.objects.get(id=top_category_id)
            contribution = f"{top_category_instance.catName} ({top_category['post_count']} posts)"
        except Categories.DoesNotExist:
            contribution = "No Posts Yet!"
    
        contributions.append(contribution)

    # Implement pagination with 10 items per page
    paginator = Paginator(posts_query, 6)  # 10 posts per page
    page = request.GET.get("page", 1)  # Default to page 1
    
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        # If the page parameter is not an integer, show the first page
        posts = paginator.page(1)
    except EmptyPage:
        # If the page is out of range, show the last page
        posts = paginator.page(paginator.num_pages)
    
    session_user_id = request.session.get('user_id')
    logged_in_user = None
    is_following = False

    if session_user_id:
        logged_in_user = get_object_or_404(Web_users, id=session_user_id)

    profile_user = get_object_or_404(Web_users, id=session_user_id)
    post_count = Web_post.objects.filter(post_author=session_user_id).count()
    # Check if the logged-in user is following the profile user
    if logged_in_user:
        is_following = Follow.objects.filter(user=logged_in_user, following_user=profile_user).exists()


    # Get followers count
    followers_count = Follow.objects.filter(following_user=profile_user).count()

    # Get following count
    following_count = Follow.objects.filter(user=profile_user).count()

    meta = f'''
    <title>Profile - {profile_user.full_name}</title>
        <meta name="description" content="{profile_user.user_bio}">
    '''
    # Render the template with paginated posts
    return render(request, 'web_userprofile.html', {
        'contributions':contributions,
        "post_count":post_count,
        'profile_user': profile_user,
        'is_following': is_following,
        'followers_count': followers_count,
        'following_count': following_count,
        'posts': posts,  # Current page of posts
        'page': posts.number,  # Current page number 
        'total_pages': paginator.num_pages,  # Total number of pages
        'page_range': paginator.get_elided_page_range(posts.number),  # Page range for navigation
        "metadetails":meta
    })
    
def web_login(request):
    if 'user_id' not in request.session:
        return render(request, 'web_login.html')
    return redirect(web_index)
    
def web_log_user(request):
    if request.method == "POST":
        # Retrieve data from POST request
        user_email = request.POST.get("useremail")
        password = request.POST.get("password")

        # Check if the user exists
        try:
            user_details = Web_users.objects.get(user_email=user_email)
        except Web_users.DoesNotExist:
            messages.error(request, "Invalid email or password.")
            return redirect("web_login")  # Adjust 'login' to your login page URL name

        # Validate the password
        if check_password(password, user_details.user_password):
            # If the password matches, log the user in
            request.session["user_id"] = user_details.id  # Storing the user ID in the session
            request.session["user_name"] = user_details.user_name
            request.session["full_name"] = user_details.full_name
            messages.success(request, "Login successful!")
            return redirect("index")  # Adjust 'dashboard' to the appropriate page after login
        else:
            messages.error(request, "Invalid email or password.")
            return redirect("web_login")

    # If not POST, render the login page
    return render(request, "web_login.html")  # Adjust 'login.html' to your actual login template

def web_register(request):
    if 'user_id' not in request.session:
        return render(request, 'web_register.html')
    return redirect(web_index)
    
def web_reg_user(request):
    if request.method == "POST":
        # Retrieve data from POST request
        full_name = request.POST.get("fullname")
        user_email = request.POST.get("email")
        user_password = request.POST.get("password")
        re_user_password = request.POST.get("repassword")

        # Validation for empty fields
        if not full_name or not user_email or not user_password or not re_user_password:
            messages.error(request, "All fields are required.")
            return redirect("web_register")  # Adjust 'register' to your registration URL name

        # Password match validation
        if user_password != re_user_password:
            messages.error(request, "Passwords do not match.")
            return redirect("web_register")

        # Check for existing email
        if Web_users.objects.filter(user_email=user_email).exists():
            messages.error(request, "This email is already registered. Please login")
            return redirect("web_login")

        # Create a unique username based on the full name
        base_user_name = slugify(full_name)
        user_name = base_user_name
        counter = 1
        while Web_users.objects.filter(user_name=user_name).exists():
            user_name = f"{base_user_name}-{counter}"
            counter += 1

        # Save the user using the model
        user_password = make_password(user_password)
        try:
            user = Web_users(
                user_name=user_name,
                full_name=full_name,
                user_email=user_email,
                user_password=user_password
            )
            user.save()  # This will automatically hash the password using the `save` method in the model

            messages.success(request, "Registration successful. You can now log in.")
            return redirect("web_login")  # Adjust 'login' to your login page URL name
        except Exception as e:
            messages.error(request, f"An error occurred while registering: {e}")
            return redirect("web_register")

    return redirect(web_register)  # Adjust 'register.html' to your actual registration template

def web_uservalidation(request, se_id):
    return render(request, 'web_uservalidation.html')

def web_logout_user(request):
    request.session.flush()  # Removes all session data
    return redirect(web_index)

def web_user_edit(request):
    if 'user_id' in request.session:
        return render(request, 'update_profile.html' )
    return redirect(web_index)

def user_save_user_details(request):
    if request.method == "POST":
        # Retrieve data from POST request
        full_name = request.POST.get("full_name")
        user_bio = request.POST.get("user_bio")
        user_about = request.POST.get("user_about")
        pr_id = request.session["user_id"]

        try:
            user_profile_images = request.FILES['user_profile_image']
            fs = FileSystemStorage()  # Initialize the FileSystemStorage
            file_path = f"user_Profile_image/{user_profile_images.name}"  # Include subdirectory in the path
            file = fs.save(file_path, user_profile_images)  # Save the file using FileSystemStorage
        except MultiValueDictKeyError:
            # If no file is uploaded, retain the existing profile image
            file = Web_users.objects.get(id=pr_id).user_profile_image

        # Update user details in the database
        Web_users.objects.filter(id=pr_id).update(
            full_name=full_name,
            user_about=user_about,
            user_bio=user_bio,
            user_profile_image=file
        )

        messages.success(request, "Profile Updated")
        return redirect(web_userprofile)

    return redirect(web_user_edit)

def google_login(request):
    """
    Redirects to Google's OAuth 2.0 server for user authentication.
    """
    oauth_url = "https://accounts.google.com/o/oauth2/v2/auth"
    params = {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "response_type": "code",
        "redirect_uri": settings.GOOGLE_REDIRECT_URI,
        "scope": "openid email profile",
        "access_type": "offline",
        "prompt": "consent",  # Forces the consent screen to appear again
    }
    # Redirect to Google's OAuth 2.0 server
    return redirect(f"{oauth_url}?{urllib.parse.urlencode(params)}")

def google_callback(request):
    """
    Handles the callback from Google OAuth 2.0, retrieves user info,
    and logs the user in or registers them if they don't exist.
    """
    # Get the authorization code from the callback
    code = request.GET.get("code")
    if not code:
        return redirect(web_login, {"message": "Authorization failed."})

    # Exchange the authorization code for an access token
    token_url = "https://oauth2.googleapis.com/token"
    token_data = {
        "code": code,
        "client_id": settings.GOOGLE_CLIENT_ID,
        "client_secret": settings.GOOGLE_CLIENT_SECRET,
        "redirect_uri": settings.GOOGLE_REDIRECT_URI,
        "grant_type": "authorization_code",
    }
    token_response = requests.post(token_url, data=token_data)
    if token_response.status_code != 200:
        return render(request, "error.html", {"message": "Failed to retrieve access token."})

    token_json = token_response.json()

    # Get user info using the access token
    user_info_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    headers = {"Authorization": f"Bearer {token_json['access_token']}"}
    user_info_response = requests.get(user_info_url, headers=headers)
    if user_info_response.status_code != 200:
        return render(request, "error.html", {"message": "Failed to retrieve user information."})

    user_info = user_info_response.json()

    # Extract user data
    email = user_info.get("email")
    name = user_info.get("name", "Unknown User")
    profile_image = user_info.get("picture")
    base_user_name = slugify(name)
    user_name = base_user_name
    counter = 1
    while Web_users.objects.filter(user_name=user_name).exists():
        user_name = f"{base_user_name}-{counter}"
        counter += 1
        
   

    if not email:
        return redirect(web_login, {"message": "Email not found in user information."})

    # Create or get the user in the database
   
    user, created = Web_users.objects.get_or_create(
        user_email=email,
        defaults={
            "full_name": name,
            "user_name":user_name,
            "user_profile_image": profile_image,
        }
    )

    if created:
        user.save()
    elif(user):
        request.session["user_id"] = user.id  # Storing the user ID in the session
        request.session["user_name"] = user.user_name
        request.session["full_name"] = user.full_name
        return redirect("index")
    messages.success(request, "Logined successful!")
    # Redirect to a success page (you can customize LOGIN_REDIRECT_URL in settings)
    return redirect(settings.LOGIN_REDIRECT_URL)

def media_files(request):
    if 'user_id' in request.session:
        ids = request.session['user_id']
        medias = Post_image.objects.filter(image_by=ids).order_by('-id')
        return render(request, 'web_files.html',{'medias':medias})
    return redirect(web_userprofile)

def media_file_save(request):
    
    if 'user_id' in request.session:
        if request.method == "POST":
            try:
                image = request.FILES['imageUpload']  # Retrieve the uploaded file
                userId = request.session['user_id']
                Post_image(image_url=image, image_by=userId).save()
            except KeyError:
               pass
    messages.success(request, "File uploaded successful!")
    return redirect(media_files)

def delete_media_files(request, del_id):
    
    userId = request.session['user_id']
    post_image = Post_image.objects.get(id=del_id, image_by=userId)
    if len(post_image.image_url) > 0:
        os.remove(post_image.image_url.path)
    post_image.delete()
    messages.success(request, "File deleted successful!")
    return redirect(media_files)

def media_image_list_json(request):
    
    userId = request.session.get('user_id')
    if userId is None:
        return JsonResponse({'error': 'User not logged in'}, status=401)
    images = Post_image.objects.filter(image_by=userId)
    image_urls = [{'image_url': image.image_url.url} for image in images]
    return JsonResponse({'images': image_urls})

def ajax_images(request):
    return render(request, 'ajax_images.html')

def post_save(request):
    if 'user_id' not in request.session:
        return redirect(web_userprofile)
    
    if request.method == 'POST':
        # Fetch data from POST request
        title = request.POST.get('title', '').strip()
        metaDesc = request.POST.get('metaDesc', '').strip()
        category_id = request.POST.get('category')
        content = request.POST.get('content', '').strip()
        coverImg = request.FILES.get('cover')

        # Validate inputs
        if not title or not content or not category_id or not coverImg:
            return render(request, 'post_form.html', {
                'error': 'All fields are required.',
            })

        # Check if category exists
        category = get_object_or_404(Categories, pk=category_id)

        # Slugify the title for the post slug
        post_slug = slugify(title)

        try:
            # Save the post
            post_save = Web_post(
                post_title=title,
                post_author_id=request.session['user_id'],  # Use related foreign key
                post_category=category,
                post_desc=metaDesc,
                post_cover=coverImg,
                post_content=content,
                post_published=True,  # Use boolean for clarity
                post_slug=post_slug,
            )
            post_save.full_clean()  # Validate model instance
            post_save.save()

            # Retrieve the Web_users instance for post author
            post_author = Web_users.objects.get(pk=request.session['user_id'])

            # Notify followers
            followers = Follow.objects.filter(following_user=post_author).values_list('user', flat=True)
            notifications = [
                Notification(
                    user_id=follower, 
                    message=f"{post_author.user_name} published a new post: {title}", 
                    post_by=post_author  # Pass the Web_users instance here
                )
                for follower in followers
            ]
            Notification.objects.bulk_create(notifications)
            followers = Follow.objects.filter(following_user=post_author).values_list('user__user_email', flat=True)

            if followers:
                subject = f"New Post by {post_author.user_name}: {title}"
                message = f"{post_author.user_name} has published a new post: '{title}'.\n\n {metaDesc}/"
                from_email = "flurabula@gmail.com"
                send_mail(
                    subject,
                    message,
                    from_email,
                    followers,
                    fail_silently=False
                )

            return redirect(web_userprofile)
        
        except ValidationError as e:
            return redirect(web_index, {
                'error': f"Validation error: {', '.join(e.messages)}",
            })
    
    # Handle cases where the method is not POST
    return redirect(web_userprofile)

def update_post(request, post_id):
    if 'user_id' in request.session:
        author = request.session['user_id']
        post = Web_post.objects.get(id=post_id)
        return render(request, 'web_blogdraft.html', {"post":post, "update":True})
    return redirect(web_userprofile)

def post_update_now(request, post_id):
    if 'user_id' in request.session:
        if request.method == "POST":
            title = request.POST.get('title')
            metaDesc = request.POST.get('metaDesc')
            category = request.POST.get('category')
            content = request.POST.get('content')
            author = request.session['user_id']
            try:
                coverImg = request.FILES['cover']
                fs = FileSystemStorage()  # Initialize the FileSystemStorage
                file_path = f"Post_cover/{coverImg.name}"  # Include subdirectory in the path
                file = fs.save(file_path, coverImg)  # Save the file using FileSystemStorage
            except MultiValueDictKeyError:
                file = Web_post.objects.get(id=post_id).post_cover
        post_save = Web_post.objects.filter(id=post_id, post_author=author).update(post_title=title , post_author=author ,post_category=category ,post_desc=metaDesc, post_cover=file, post_content=content, post_published=1)
        return redirect(web_userprofile)

def comments_save(request, post_id):
    
    if 'user_id' not in request.session:
        return redirect(web_logout_user)
    
    if request.method == 'POST':
        post = get_object_or_404(Web_post, id=post_id)
        author = Web_users.objects.get(id=request.session.get('user_id')) 
        content = request.POST.get('comment', '').strip()

        if not content:
            messages.error(request, "Comment cannot be empty.")
            return redirect(request.META.get('HTTP_REFERER', 'default_fallback_url'))

        # Create and save the comment
        comment = Comment.objects.create(post=post, author=author, content=content)
        messages.success(request, "Your comment has been submitted successfully!")

        # Send an email to the post author
        post_author_email = post.post_author.user_email
        subject = f"New Comment on Your Post: {post.post_title}"
        message = f"{author.full_name} commented on your post '{post.post_title}':\n\n'{content}'"
        from_email = "flurabula@gmail.com"

        send_mail(subject, message, from_email, [post_author_email], fail_silently=False)

        return redirect(request.META.get('HTTP_REFERER', 'default_fallback_url'))
    
def users(request, user_slug):
    # Fetch user details based on the slug
    user = get_object_or_404(Web_users, user_name=user_slug)
    post_count = Web_post.objects.filter(post_author=user).count()
    posts_query = Web_post.objects.select_related('post_author', 'post_category') \
        .filter(post_author=user) \
        .annotate(comment_count=Count('comments', filter=Q(comments__is_approved=True))) \
        .order_by('-created_at')
    # Implement pagination with 10 items per page
    paginator = Paginator(posts_query, 6)
    page = request.GET.get("page", 1)
    top_categories = (Web_post.objects
                  .select_related('post_author', 'post_category')  # Optimize related data fetching
                  .filter(post_author=user)  # Filter posts by the user
                  .values('post_category')  # Group by the post_category
                  .annotate(post_count=Count('post_category'))  # Annotate with the number of posts per category
                  .order_by('-post_count')  # Order by post count in descending order
                  [:3])  # Limit to top 3 categories

# Initialize a list to store the contributions
    contributions = []

# Iterate over the top categories and display their information
    for top_category in top_categories:
        top_category_id = top_category['post_category']
    
        try:
            top_category_instance = Categories.objects.get(id=top_category_id)
            contribution = f"{top_category_instance.catName} ({top_category['post_count']} posts)"
        except Categories.DoesNotExist:
            contribution = "No Posts Yet!"
    
        contributions.append(contribution)

        
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)

    session_user_id = request.session.get('user_id')
    logged_in_user = None
    is_following = False

    if session_user_id:
        logged_in_user = get_object_or_404(Web_users, id=session_user_id)

    profile_user = get_object_or_404(Web_users, user_name=user_slug)

    # Check if the logged-in user is following the profile user
    if logged_in_user:
        is_following = Follow.objects.filter(user=logged_in_user, following_user=profile_user).exists()


    # Get followers count
    followers_count = Follow.objects.filter(following_user=profile_user).count()

    # Get following count
    following_count = Follow.objects.filter(user=profile_user).count()
    
    meta = f'''
        <title>{profile_user.full_name}</title>
        <meta name="description" content="{profile_user.user_bio}">
    '''
    # Render the template with user details and paginated posts
    return render(request, 'web_user_details.html', {
        'contributions':contributions,
        "post_count":post_count,
        'profile_user': profile_user,
        'is_following': is_following,
        'followers_count': followers_count,
        'following_count': following_count,
        'users': user,
        'posts': posts,  # Paginated posts
        'page': posts.number,  # Current page number
        'total_pages': paginator.num_pages,  # Total pages
        'page_range': paginator.get_elided_page_range(posts.number),  # Page range for navigation
        "metadetails":meta,
    })
def live_search(request):
    query = request.GET.get('query', '')
    if query:
        results = Web_post.objects.select_related('post_category').filter(
    Q(post_title__icontains=query) | Q(post_content__icontains=query) | Q(post_desc__icontains=query),
    post_published=True
).values('post_title', 'post_category__catSlug', 'post_cover', 'post_slug')
    else:
        results = []

    return JsonResponse({'results': list(results)}, safe=False)

def delete_post(request,delno):
    Web_post.objects.filter(id=delno).delete()
    return redirect(web_userprofile)


class FollowToggleView(View):
    def post(self, request, user_id):
        # Check if the user is logged in
        session_user_id = request.session.get('user_id')
        if not session_user_id:
            return JsonResponse({"message": "You need to log in to perform this action."}, status=401)

        # Ensure the logged-in user exists
        logged_in_user = get_object_or_404(Web_users, id=session_user_id)

        # Validate the target user exists
        following_user = get_object_or_404(Web_users, id=user_id)

        # Validation: Prevent following oneself
        if logged_in_user == following_user:
            return JsonResponse({"message": "You cannot follow yourself.", "stat": "error"}, status=400)

        # Validation: Check if user is blocked (optional, if you have a block feature)
        if hasattr(logged_in_user, 'blocked_users') and following_user in logged_in_user.blocked_users.all():
            return JsonResponse({"message": "You cannot follow this user.", "stat": "error"}, status=403)

        # Toggle follow/unfollow
        follow_relation, created = Follow.objects.get_or_create(
            user=logged_in_user,
            following_user=following_user
        )

        if created:
            return JsonResponse({"message": "User followed successfully." , "stat": "success", "status": "followed"}, status=201)
        else:
            follow_relation.delete()
            return JsonResponse({"message": "User unfollowed successfully.", "stat": "success" , "status": "unfollowed"}, status=200)

def fetch_notifications(request):
    if request.session['user_id']:
        notifications = Notification.objects.filter(user=request.session['user_id'], is_read=False).order_by('-created_at')[:10]
        data = [
            {
                'profile_image': n.post_by.user_profile_image.url if n.post_by and n.post_by.user_profile_image else '/static/images/default-profile.png',
                'id': n.id,
                'message': n.message,
                'created_at': n.created_at.strftime('%b %d, %Y %H:%M'),
                'userSlug': n.post_by.user_name,
                
            }
            for n in notifications
        ]
        return JsonResponse({'notifications': data})
    return JsonResponse({'notifications': []})

def deletecomment(request, cid):
        if 'user_id' not in request.session:
            return redirect(web_login)
        user_id = request.session.get('user_id')  # Fetch user ID from session
        if not user_id:
            return JsonResponse({'error': 'Unauthorized access'}, status=401)

        # Fetch the comment and the associated post
        comment = get_object_or_404(Comment, id=cid)
        post = comment.post

        # Check if the user is the comment author or the post author
        if comment.author_id == user_id or post.post_author_id == user_id:
            comment.delete()
            referer_url = request.META.get('HTTP_REFERER', '/')
            return redirect(referer_url,messages.success(request, 'Comment deleted successfully.'))
        else:
            return JsonResponse({'error': 'Permission denied'}, status=403)
        
def followers(request):
    if 'user_id' not in request.session:
        return redirect('web_login')

    user_id = request.session.get('user_id')  # Logged-in user's ID

    # Get all users the current user is following
    following_users = Follow.objects.filter(user_id=user_id).select_related('following_user')

    # Fetch the details of the followed users
    followed_user_details = [follow.following_user for follow in following_users]
    meta = """<title>Following</title>
        <meta name="description" content="People you are following">"""
    return render(request, 'web_followers.html', {'followed_users': followed_user_details, "metadetails":meta})
