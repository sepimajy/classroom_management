# main/models.py

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid
from django.core.validators import MinValueValidator, MaxValueValidator
from django.urls import reverse

# Ensure you have Pillow installed for ImageField
# You can install it using: pip install Pillow


class Profile(models.Model):
    ROLE_CHOICES = [
        ('teacher', 'Teacher'),
        ('student', 'Student'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True,related_name='profile')
    bio = models.TextField(blank=True, null=True)
    avatar = models.ImageField(upload_to='avatars/', default='avatars/default.jpg')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='student')

    def __str__(self):
        return f"{self.user.username} Profile"


class Classroom(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    code = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_classrooms')
    students = models.ManyToManyField(User, related_name='joined_classrooms', blank=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('classroom_detail', kwargs={'pk': self.pk})


class Assignment(models.Model):
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE, related_name='assignments')
    title = models.CharField(max_length=255)
    description = models.TextField()
    file = models.FileField(upload_to='assignments/', blank=True, null=True)
    due_date = models.DateTimeField()
    allow_late_submission = models.BooleanField(default=False)
    

    def __str__(self):
        return self.title


class Submission(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='submissions')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='submissions')
    file = models.FileField(upload_to='submissions/', blank=True, null=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    is_late = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.student.username} - {self.assignment.title}"


class Exam(models.Model):
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE, related_name='exams')
    title = models.CharField(max_length=255)
    description = models.TextField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    duration = models.DurationField()

    def __str__(self):
        return self.title

    def is_active(self):
        now = timezone.now()
        return self.start_time <= now <= self.end_time

    def get_absolute_url(self):
        return reverse('exam_detail', kwargs={'classroom_pk': self.classroom.pk, 'exam_pk': self.pk})


class Question(models.Model):
    OPTION_CHOICES = [
        ('A', 'Option A'),
        ('B', 'Option B'),
        ('C', 'Option C'),
        ('D', 'Option D'),
    ]

    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()
    option_a = models.CharField(max_length=255)
    option_b = models.CharField(max_length=255)
    option_c = models.CharField(max_length=255)
    option_d = models.CharField(max_length=255)
    correct_option = models.CharField(max_length=1, choices=OPTION_CHOICES)
    image = models.ImageField(upload_to='questions/', blank=True, null=True)

    def __str__(self):
        return f"Question {self.id} for {self.exam.title}"


class ExamSubmission(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    answers = models.JSONField()
    submitted_at = models.DateTimeField(auto_now_add=True)
    score = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)], blank=True, null=True)
    feedback = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.student.username} - {self.exam.title}"


class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE, related_name='messages')
    content = models.TextField()
    file = models.FileField(upload_to='messages/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.sender.username} to {self.receiver.username}"


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    link = models.URLField(max_length=500, blank=True, null=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.user.username} - {'Read' if self.is_read else 'Unread'}"


