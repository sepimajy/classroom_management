from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/teacher/', views.dashboard_teacher, name='dashboard_teacher'),
    path('dashboard/student/', views.dashboard_student, name='dashboard_student'),
    path('profile/update/', views.profile_update, name='profile_update'),
    path('classrooms/', views.classroom_list, name='classroom_list'),
    path('classrooms/create/', views.create_classroom, name='create_classroom'),
    path('classrooms/<int:pk>/', views.classroom_detail, name='classroom_detail'),
    path('classrooms/<int:classroom_pk>/assignments/create/', views.create_assignment, name='create_assignment'),
    path('classrooms/<int:classroom_pk>/assignments/<int:assignment_pk>/', views.assignment_detail, name='assignment_detail'),
    path('classrooms/<int:classroom_pk>/exams/create/', views.create_exam, name='create_exam'),
    path('classrooms/<int:classroom_pk>/exams/<int:exam_pk>/', views.exam_detail, name='exam_detail'),
    path('classrooms/<int:classroom_pk>/exams/<int:exam_pk>/submissions/<int:submission_pk>/grade/', views.grade_exam_submission, name='grade_exam_submission'),
    path('classrooms/<int:classroom_pk>/exams/<int:exam_pk>/questions/create/', views.create_question, name='create_question'),
    path('classrooms/<int:classroom_pk>/messages/send/', views.send_message, name='send_message'),
    path('inbox/', views.inbox, name='inbox'),
    path('messages/<int:message_pk>/', views.message_detail, name='message_detail'),
    path('classrooms/join/', views.join_classroom, name='join_classroom'),
    path('inbox/', views.inbox, name='inbox'),
    path('messages/<int:message_pk>/', views.message_detail, name='message_detail'),
    path('classrooms/<int:classroom_pk>/exams/create/cancel/', views.cancel_exam_creation, name='cancel_exam_creation'),
]
