from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .forms import RegisterForm, ClassroomForm, AssignmentForm, SubmissionForm, ExamForm, QuestionForm, MessageForm, ProfileUpdateForm, JoinClassroomForm, NumberOfQuestionsForm
from .models import Classroom, Assignment, Submission, Exam, Question, ExamSubmission, Message, Notification
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.forms import formset_factory
from django.http import JsonResponse
import json
import datetime
from datetime import timedelta



TEACHER_SECRET_CODE = 'TEACHER2024'  

def home(request):
    unread_notifications_count = 0
    if request.user.is_authenticated:
        unread_notifications_count = request.user.notifications.filter(is_read=False).count()
    return render(request, 'main/home.html', {'unread_notifications_count': unread_notifications_count})

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            secret_code = form.cleaned_data.get('secret_code')
            user = form.save(commit=False)
            if secret_code == TEACHER_SECRET_CODE:
                user.save()
                profile = user.profile
                profile.role = 'teacher'
                profile.save()
                messages.success(request, 'Registration successful. You have been registered as a teacher.')
            else:
                user.save()
                profile = user.profile
                profile.role = 'student'
                profile.save()
                messages.success(request, 'Registration successful. You have been registered as a student.')
            return redirect('login')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = RegisterForm()
    return render(request, 'main/register.html', {'form': form})

@login_required
def dashboard(request):
    profile = request.user.profile
    if profile.role == 'teacher':
        classrooms = request.user.created_classrooms.all()
        return render(request, 'main/dashboard_teacher.html', {
            'profile': profile,
            'classrooms': classrooms
        })
    else:
        classrooms = request.user.joined_classrooms.all()
        return render(request, 'main/dashboard_student.html', {
            'profile': profile,
            'classrooms': classrooms
        })

@login_required
def profile_update(request):
    if request.method == 'POST':
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        secret_code = request.POST.get('secret_code')
        desired_role = request.POST.get('desired_role')
        if p_form.is_valid():
            # Check if role change is requested
            if desired_role and desired_role != request.user.profile.role:
                if secret_code == TEACHER_SECRET_CODE:
                    request.user.profile.role = desired_role
                    request.user.profile.save()
                    messages.success(request, 'Your role has been updated successfully.')
                else:
                    messages.error(request, 'Invalid secret code. Role not updated.')
            p_form.save()
            messages.success(request, 'Your profile has been updated successfully.')
            return redirect('dashboard')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        p_form = ProfileUpdateForm(instance=request.user.profile)
    return render(request, 'main/profile_update.html', {'p_form': p_form})

@login_required
def classroom_list(request):
    classrooms = Classroom.objects.all()
    return render(request, 'main/classrooms/classroom_list.html', {'classrooms': classrooms})

@login_required
def classroom_detail(request, pk):
    classroom = get_object_or_404(Classroom, pk=pk)
    
    # Check access permissions
    if request.user.profile.role == 'teacher':
        if classroom.created_by != request.user:
            messages.error(request, 'You do not have permission to view this classroom.')
            return redirect('dashboard')
        template = 'main/classrooms/classroom_detail_teacher.html'
    elif request.user.profile.role == 'student':
        if classroom not in request.user.joined_classrooms.all():
            messages.error(request, 'You do not belong to this classroom.')
            return redirect('dashboard')
        template = 'main/classrooms/classroom_detail_student.html'
    else:
        messages.error(request, 'Invalid role.')
        return redirect('dashboard')
    
    # Clear exam creation session data if present
    if 'step' in request.session:
        request.session.pop('exam_data', None)
        request.session.pop('number_of_questions', None)
        request.session.pop('step', None)
    
    assignments = classroom.assignments.all()
    exams = classroom.exams.all()
    messages_in_classroom = classroom.messages.all().order_by('-created_at')
    return render(request, template, {
        'classroom': classroom,
        'assignments': assignments,
        'exams': exams,
        'messages_in_classroom': messages_in_classroom
    })
    
    

@login_required
def create_classroom(request):
    if request.user.profile.role != 'teacher':
        messages.error(request, 'Only teachers can create classrooms.')
        return redirect('dashboard')
    if request.method == 'POST':
        form = ClassroomForm(request.POST)
        if form.is_valid():
            classroom = form.save(commit=False)
            classroom.created_by = request.user
            classroom.save()
            messages.success(request, f'Classroom "{classroom.name}" created successfully.')
            return redirect('classroom_detail', pk=classroom.pk)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ClassroomForm()
    return render(request, 'main/classrooms/create_classroom.html', {'form': form})

@login_required
def create_assignment(request, classroom_pk):
    classroom = get_object_or_404(Classroom, pk=classroom_pk)
    if request.user != classroom.created_by:
        messages.error(request, 'Only the teacher of this classroom can create assignments.')
        return redirect('classroom_detail', pk=classroom.pk)
    if request.method == 'POST':
        form = AssignmentForm(request.POST, request.FILES)
        if form.is_valid():
            assignment = form.save(commit=False)
            assignment.classroom = classroom
            assignment.save()
            messages.success(request, f'Assignment "{assignment.title}" created successfully.')
            # Notify students
            students = User.objects.filter(profile__role='student', created_classrooms=classroom)
            for student in students:
                Notification.objects.create(
                    user=student,
                    message=f'New assignment "{assignment.title}" has been posted in {classroom.name}.',
                    link=f'/classrooms/{classroom.pk}/assignments/{assignment.pk}/'
                )
            return redirect('classroom_detail', pk=classroom.pk)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = AssignmentForm()
    return render(request, 'main/classrooms/create_assignment.html', {'form': form, 'classroom': classroom})

@login_required
def assignment_detail(request, classroom_pk, assignment_pk):
    classroom = get_object_or_404(Classroom, pk=classroom_pk)
    assignment = get_object_or_404(Assignment, pk=assignment_pk, classroom=classroom)
    submissions = assignment.submissions.all()
    if request.user.profile.role == 'student':
        submission = Submission.objects.filter(assignment=assignment, student=request.user).first()
        now = timezone.now()
        is_late = now > assignment.due_date
        can_submit = not is_late or (is_late and assignment.allow_late_submission)
        if is_late and not assignment.allow_late_submission:
            messages.info(request, 'The deadline for this assignment has passed. You cannot submit.')
        if request.method == 'POST' and can_submit:
            form = SubmissionForm(request.POST, request.FILES, instance=submission)
            if form.is_valid():
                submission = form.save(commit=False)
                submission.assignment = assignment
                submission.student = request.user
                submission.submitted_at = timezone.now()
                if is_late and assignment.allow_late_submission:
                    submission.is_late = True
                submission.save()
                messages.success(request, 'Assignment submitted successfully.')
                # Notify teacher
                Notification.objects.create(
                    user=classroom.created_by,
                    message=f'{request.user.username} has submitted assignment "{assignment.title}".',
                    link=f'/classrooms/{classroom.pk}/assignments/{assignment.pk}/'
                )
                return redirect('assignment_detail', classroom_pk=classroom.pk, assignment_pk=assignment.pk)
        else:
            form = SubmissionForm(instance=submission)
        return render(request, 'main/classrooms/assignment_detail.html', {
            'classroom': classroom,
            'assignment': assignment,
            'form': form,
            'submission': submission,
            'can_submit': can_submit,
            'is_late': is_late
        })
    elif request.user.profile.role == 'teacher':
        return render(request, 'main/classrooms/assignment_detail_teacher.html', {
            'classroom': classroom,
            'assignment': assignment,
            'submissions': submissions
        })
    else:
        messages.error(request, 'Invalid role.')
        return redirect('dashboard')


@login_required
def create_exam(request, classroom_pk):
    classroom = get_object_or_404(Classroom, pk=classroom_pk)
    
    # Access Control: Only the teacher who created the classroom can create exams
    if request.user != classroom.created_by:
        messages.error(request, 'Only the teacher of this classroom can create exams.')
        return redirect('classroom_detail', pk=classroom.pk)
    
    # Initialize session steps
    if 'step' not in request.session:
        request.session['step'] = 1
    
    # Step 1: Collect Exam Details
    if request.session['step'] == 1:
        if request.method == 'POST':
            form = ExamForm(request.POST)
            if form.is_valid():
                exam_data = form.cleaned_data.copy()
                
                # Serialize datetime and timedelta objects to strings for session storage
                exam_data['start_time'] = exam_data['start_time'].isoformat()
                exam_data['end_time'] = exam_data['end_time'].isoformat()
                exam_data['duration'] = str(exam_data['duration'])
                
                # Store serialized exam data in session
                request.session['exam_data'] = exam_data
                request.session['step'] = 2
                return redirect('create_exam', classroom_pk=classroom.pk)
            else:
                messages.error(request, 'Please correct the errors below.')
        else:
            exam_data = request.session.get('exam_data')
            if exam_data:
                initial_data = {
                    'title': exam_data.get('title'),
                    'description': exam_data.get('description'),
                    'start_time': exam_data.get('start_time'),
                    'end_time': exam_data.get('end_time'),
                    'duration': exam_data.get('duration'),
                }
                form = ExamForm(initial=initial_data)
            else:
                form = ExamForm()
        return render(request, 'main/classrooms/create_exam_step1.html', {
            'form': form,
            'classroom': classroom
            })
    
    # Step 2: Collect Number of Questions
    elif request.session['step'] == 2:
        if request.method == 'POST':
            if 'back' in request.POST:
                # User clicked the "Back" button
                request.session['step'] = 1
                return redirect('create_exam', classroom_pk=classroom.pk)
            
            form = NumberOfQuestionsForm(request.POST)
            if form.is_valid():
                number_of_questions = form.cleaned_data['number_of_questions']
                
                # Store the number in session
                request.session['number_of_questions'] = number_of_questions
                request.session['step'] = 3
                return redirect('create_exam', classroom_pk=classroom.pk)
            else:
                messages.error(request, 'Please enter a valid number of questions.')
        else:
            number_of_questions = request.session.get('number_of_questions')
            if number_of_questions:
                initial_data = {
                    'number_of_questions': number_of_questions
                }
                form = NumberOfQuestionsForm(initial=initial_data)
            else:
                form = NumberOfQuestionsForm()
        return render(request, 'main/classrooms/create_exam_step2.html', {
            'form': form,
            'classroom': classroom
        })
    
    # Step 3: Collect Questions Details
    elif request.session['step'] == 3:
        exam_data = request.session.get('exam_data')
        number_of_questions = request.session.get('number_of_questions')
        
        if not exam_data or not number_of_questions:
            messages.error(request, 'Session expired or invalid data. Please start over.')
            # Clear session data
            request.session.pop('exam_data', None)
            request.session.pop('number_of_questions', None)
            request.session.pop('step', None)
            return redirect('create_exam', classroom_pk=classroom.pk)
        
        QuestionFormSet = formset_factory(QuestionForm, extra=number_of_questions)
        
        if request.method == 'POST':
            if 'back' in request.POST:
                # User clicked the "Back" button
                request.session['step'] = 2
                return redirect('create_exam', classroom_pk=classroom.pk)
            
            formset = QuestionFormSet(request.POST, request.FILES)
            if formset.is_valid():
                
                # Deserialize exam data
                try:
                   
                    start_time = datetime.datetime.fromisoformat(exam_data['start_time'])
                    end_time = datetime.datetime.fromisoformat(exam_data['end_time'])
                    duration_str = exam_data['duration']
                    hours, minutes, seconds = map(int, duration_str.split(':'))
                    duration = timedelta(hours=hours, minutes=minutes, seconds=seconds)

                except Exception as e:
                    messages.error(request, 'Invalid exam data. Please start over.')
                    # Clear session data
                    request.session.pop('exam_data', None)
                    request.session.pop('number_of_questions', None)
                    request.session.pop('step', None)
                    return redirect('create_exam', classroom_pk=classroom.pk)
                
                # Create the Exam instance
                exam = Exam.objects.create(
                    classroom=classroom,
                    title=exam_data['title'],
                    description=exam_data['description'],
                    start_time=start_time,
                    end_time=end_time,
                    duration=duration
                )
                
                # Create each Question instance
                for form in formset:
                    question = form.save(commit=False)
                    question.exam = exam
                    question.save()
                
                # Clear session data after successful creation
                request.session.pop('exam_data', None)
                request.session.pop('number_of_questions', None)
                request.session.pop('step', None)
                
                messages.success(request, f'Exam "{exam.title}" created successfully with {number_of_questions} questions.')
                return redirect('classroom_detail', pk=classroom.pk)
            else:
                messages.error(request, 'Please correct the errors below.')
        else:
            formset = QuestionFormSet()
        return render(request, 'main/classrooms/create_exam_step3.html', {
            'formset': formset,
            'classroom': classroom,
            'number_of_questions': number_of_questions
        })
    
    # Handle unexpected steps by resetting the process
    else:
        messages.error(request, 'An error occurred. Please try creating the exam again.')
        # Clear all session data related to exam creation
        request.session.pop('exam_data', None)
        request.session.pop('number_of_questions', None)
        request.session.pop('step', None)
        return redirect('create_exam', classroom_pk=classroom.pk)
    


@login_required
def exam_detail(request, classroom_pk, exam_pk):
    classroom = get_object_or_404(Classroom, pk=classroom_pk)
    exam = get_object_or_404(Exam, pk=exam_pk, classroom=classroom)
    questions = exam.questions.all()

    if request.user.profile.role == 'student':
        # Check if the exam is active
        now = timezone.now()
        print(now)
        if not (exam.start_time <= now <= exam.end_time):
            messages.error(request, 'This exam is not active.')
            return redirect('classroom_detail', pk=classroom.pk)
        # Check if the student has already taken the exam
        submission = ExamSubmission.objects.filter(exam=exam, student=request.user).first()
        if submission:
            messages.info(request, 'You have already taken this exam.')
            return render(request, 'main/classrooms/exam_detail_student.html', {
                'classroom': classroom,
                'exam': exam,
                'submission': submission
            })
        if request.method == 'POST':
            answers = {}
            for question in questions:
                answer = request.POST.get(f'question_{question.pk}')
                if answer:
                    answers[str(question.pk)] = answer
            submission = ExamSubmission.objects.create(
                exam=exam,
                student=request.user,
                answers=answers,
                submitted_at=timezone.now()
            )
            # Notify teacher
            Notification.objects.create(
                user=classroom.created_by,
                message=f'{request.user.username} has submitted exam "{exam.title}".',
                link=f'/classrooms/{classroom.pk}/exams/{exam.pk}/'
            )
            messages.success(request, 'Exam submitted successfully.')
            return redirect('exam_detail', classroom_pk=classroom.pk, exam_pk=exam.pk)
        return render(request, 'main/classrooms/exam_detail_student.html', {
            'classroom': classroom,
            'exam': exam,
            'questions': questions
        })
    
    
    elif request.user.profile.role == 'teacher':
        
        submissions = exam.examsubmission_set.all()

        # Example: If you need to access a specific question, retrieve it here
        q_id = request.GET.get('q_id')  # Assuming q_id is passed as a GET parameter
        specific_question = None
        if q_id:
            specific_question = get_object_or_404(Question, pk=q_id, exam=exam)

        context = {
            'classroom': classroom,
            'exam': exam,
            'questions': questions,
            'submissions': submissions,
            'specific_question': specific_question,  # Pass the specific question if needed
        }
        return render(request, 'main/classrooms/exam_detail_teacher.html', context)
    

    else:
        messages.error(request, 'Invalid role.')
        return redirect('dashboard')

@login_required
def grade_exam_submission(request, classroom_pk, exam_pk, submission_pk):
    classroom = get_object_or_404(Classroom, pk=classroom_pk)
    exam = get_object_or_404(Exam, pk=exam_pk, classroom=classroom)
    submission = get_object_or_404(ExamSubmission, pk=submission_pk, exam=exam)
    if request.method == 'POST':
        score = request.POST.get('score')
        feedback = request.POST.get('feedback')
        try:
            score = int(score)
            if 0 <= score <= 100:
                submission.score = score
                submission.feedback = feedback
                submission.save()
                messages.success(request, 'Exam submission graded successfully.')
                # Notify student
                Notification.objects.create(
                    user=submission.student,
                    message=f'Your exam "{exam.title}" has been graded.',
                    link=f'/classrooms/{classroom.pk}/exams/{exam.pk}/'
                )
                return redirect('exam_detail', classroom_pk=classroom.pk, exam_pk=exam.pk)
            else:
                messages.error(request, 'Score must be between 0 and 100.')
        except ValueError:
            messages.error(request, 'Invalid score.')
    return render(request, 'main/classrooms/grade_exam_submission.html', {
        'classroom': classroom,
        'exam': exam,
        'submission': submission
    })

@login_required
def create_question(request, classroom_pk, exam_pk):
    classroom = get_object_or_404(Classroom, pk=classroom_pk)
    exam = get_object_or_404(Exam, pk=exam_pk, classroom=classroom)
    if request.user != classroom.created_by:
        messages.error(request, 'Only the teacher of this classroom can add questions.')
        return redirect('exam_detail', classroom_pk=classroom.pk, exam_pk=exam.pk)
    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.exam = exam
            question.save()
            messages.success(request, 'Question added successfully.')
            return redirect('exam_detail', classroom_pk=classroom.pk, exam_pk=exam.pk)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = QuestionForm()
    return render(request, 'main/classrooms/create_question.html', {
        'form': form,
        'classroom': classroom,
        'exam': exam
    })

@login_required
def send_message(request, classroom_pk):
    classroom = get_object_or_404(Classroom, pk=classroom_pk)
    if request.user.profile.role == 'teacher':
        recipients = classroom.students.all()
    else:
        recipients = User.objects.filter(created_classrooms=classroom, profile__role='teacher')
    if request.method == 'POST':
        form = MessageForm(request.POST, request.FILES)
        form.fields['receiver'].queryset = recipients
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = request.user
            message.classroom = classroom
            message.save()
            # Notify receiver
            Notification.objects.create(
                user=message.receiver,
                message=f'New message from {message.sender.username} in {classroom.name}.',
                link=f'/classrooms/{classroom.pk}/messages/{message.pk}/'
            )
            messages.success(request, 'Message sent successfully.')
            return redirect('classroom_detail', pk=classroom.pk)
    else:
        form = MessageForm()
        form.fields['receiver'].queryset = recipients
    return render(request, 'main/classrooms/send_message.html', {
        'form': form,
        'classroom': classroom
    })

@login_required
def inbox(request):
    messages_received = request.user.received_messages.all().order_by('-created_at')
    return render(request, 'main/inbox.html', {'messages_received': messages_received})

@login_required
def message_detail(request, message_pk):
    message = get_object_or_404(Message, pk=message_pk, receiver=request.user)
    return render(request, 'main/message_detail.html', {'message': message})



@login_required
def join_classroom(request):
    if request.user.profile.role != 'student':
        messages.error(request, 'Only students can join classrooms.')
        return redirect('dashboard')
    if request.method == 'POST':
        form = JoinClassroomForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data['code']
            try:
                classroom = Classroom.objects.get(code=code)
                if classroom in request.user.joined_classrooms.all():
                    messages.info(request, 'You are already a member of this classroom.')
                else:
                    classroom.students.add(request.user)
                    messages.success(request, f'You have successfully joined the classroom "{classroom.name}".')
                return redirect('dashboard')
            except Classroom.DoesNotExist:
                messages.error(request, 'Invalid classroom code.')
    else:
        form = JoinClassroomForm()
    return render(request, 'main/classrooms/join_classroom.html', {'form': form})



@login_required
def dashboard_redirect(request):
    """
    Redirect users to their respective dashboards based on their role.
    """
    profile = request.user.profile
    if profile.role == 'teacher':
        return redirect('dashboard_teacher')
    else:
        return redirect('dashboard_student')

@login_required
def dashboard_teacher(request):

    if request.user.profile.role != 'teacher':
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    classrooms = request.user.created_classrooms.all()
    return render(request, 'main/dashboard_teacher.html', {
        'profile': request.user.profile,
        'classrooms': classrooms
    })

@login_required
def dashboard_student(request):

    if request.user.profile.role != 'student':
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    classrooms = request.user.joined_classrooms.all()
    return render(request, 'main/dashboard_student.html', {
        'profile': request.user.profile,
        'classrooms': classrooms
    })


@login_required
def cancel_exam_creation(request, classroom_pk):
    # Clear session data related to exam creation
    request.session.pop('exam_data', None)
    request.session.pop('number_of_questions', None)
    request.session.pop('step', None)
    
    messages.info(request, 'Exam creation has been canceled.')
    return redirect('classroom_detail', pk=classroom_pk)