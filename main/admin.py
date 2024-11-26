from django.contrib import admin
from .models import Profile, Classroom, Assignment, Submission, Exam, Question, ExamSubmission, Message, Notification

admin.site.register(Profile)
admin.site.register(Classroom)
admin.site.register(Assignment)
admin.site.register(Submission)
admin.site.register(Exam)
admin.site.register(Question)
admin.site.register(ExamSubmission)
admin.site.register(Message)
admin.site.register(Notification)