from django.db import models
from rest_framework.authentication import get_user_model
from django_pandas.managers import DataFrameManager

# Create your models here.


def create_file_path(self, filename):
    name = self.name
    return f'media/docs/{name}/{filename}'


class Chat(models.Model):

    name = models.CharField(max_length=20)
    user = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, related_name='chats')

    class Meta:
        unique_together = ('name', 'user')

    def __str__(self):
        return f'{self.user}_{self.name}'


class Document(models.Model):

    COMPLETED = 'COMPLETED'
    PENDING = 'PENDING'
    PROCESSING = 'PROCESSING'
    NOT_APPROVED = 'NOT APPROVED'
    EMBEDDING_CHOICES = (
        (COMPLETED, COMPLETED),
        (PENDING, PENDING),
        (NOT_APPROVED, NOT_APPROVED),
        (PROCESSING, PROCESSING))

    name = models.CharField(max_length=100, unique=True)
    user = models.ForeignKey(
        get_user_model(), on_delete=models.SET_NULL, related_name='documents', null=True)
    file = models.FileField(upload_to=create_file_path)
    isVerified = models.BooleanField(default=False)
    embeddingStatus = models.CharField(
        max_length=20, choices=EMBEDDING_CHOICES, default=NOT_APPROVED)

    def __str__(self):
        return self.name


class Query(models.Model):
    chat = models.ForeignKey(
        Chat, on_delete=models.SET_NULL, related_name='queries', null=True)
    question = models.CharField(max_length=256)
    response = models.TextField()
    time = models.DateTimeField()
    context = models.TextField()
    doc_id = models.ForeignKey(
        Document, on_delete=models.SET_NULL, related_name='queries', null=True)
    references = models.JSONField()

    def __str__(self):
        return f'{self.time.date()}_{self.question}'


class QueryFeedBack(models.Model):
    query = models.OneToOneField(
        Query, on_delete=models.CASCADE, related_name='feedback')
    user = models.ForeignKey(get_user_model(
    ), on_delete=models.SET_NULL, related_name='feedbacks', null=True, default=None)
    created_at = models.DateTimeField(auto_now_add=True)
    rating = models.PositiveSmallIntegerField()
    feedback = models.TextField(blank=True)
    expected_response = models.TextField(blank=True)

    objects = DataFrameManager()
