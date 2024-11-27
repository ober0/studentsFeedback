from celery import shared_task
from manage.models import BlockedUser


@shared_task
def unbanUser(id):
    try:
        # Ищем пользователя и снимаем блокировку
        blocked_user = BlockedUser.objects.get(id=id)
        blocked_user.delete()  # Удаляем запись о блокировке
        return f"User with ID {id} has been unbanned."
    except BlockedUser.DoesNotExist:
        return f"BlockedUser with ID {id} does not exist."