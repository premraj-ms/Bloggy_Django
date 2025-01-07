from admin_box.models import Categories
from .models import Web_users
def global_header_data(request):
    categories = Categories.objects.all()
    if ('user_id' in request.session):
        userId = request.session['user_id']
        users = Web_users.objects.get(id = userId)
        return {'categories': categories, "users":users}

    return {'categories': categories}

