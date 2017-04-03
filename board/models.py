from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from django.conf import settings


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


'''
class Post(models.Model):
    user = models.ForeignKey('core.MyUser', related_name='posts', on_delete=models.CASCADE)
    category = models.ForeignKey(GroupCategory, null=True)
    title = models.CharField(max_length=200)
    content = models.TextField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    views = models.IntegerField(default=0)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ["-created_at"]
'''