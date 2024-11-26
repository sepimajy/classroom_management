
import datetime
def unread_notifications(request):
    if request.user.is_authenticated:
        count = request.user.notifications.filter(is_read=False).count()
    else:
        count = 0
    return {'unread_notifications_count': count}


def current_year(request):
    return {
        'current_year': datetime.datetime.now().year
    }
