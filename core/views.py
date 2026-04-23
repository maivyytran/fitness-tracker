from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count
from django.utils import timezone
from django.db import IntegrityError
from .models import Member, FitnessClass, Instructor, MembershipPlan, Registration
from .forms import MemberForm, InstructorForm, FitnessClassForm, MembershipPlanForm, RegistrationForm


# ── Dashboard ────────────────────────────────────────────────
@login_required
def dashboard(request):
    now = timezone.now()
    active_members = Member.objects.filter(active=True).count()
    total_classes = FitnessClass.objects.count()
    total_instructors = Instructor.objects.count()
    registrations_this_month = Registration.objects.filter(
        registered_at__year=now.year,
        registered_at__month=now.month
    ).count()
    recent_registrations = Registration.objects.select_related(
        'memberid', 'classid'
    ).order_by('-registered_at')[:10]

    return render(request, 'core/dashboard.html', {
        'active_members': active_members,
        'total_classes': total_classes,
        'total_instructors': total_instructors,
        'registrations_this_month': registrations_this_month,
        'recent_registrations': recent_registrations,
    })


# ── Members ──────────────────────────────────────────────────
@login_required
def members(request):
    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'add':
            form = MemberForm(request.POST)
            if form.is_valid():
                try:
                    Member.objects.create(
                        first_name=form.cleaned_data['first_name'],
                        last_name=form.cleaned_data['last_name'],
                        email=form.cleaned_data['email'],
                        phone=form.cleaned_data['phone'] or None,
                        planid=form.cleaned_data['planid'],
                        active=form.cleaned_data['active'],
                    )
                    messages.success(request, "Member added successfully.")
                    return redirect('members')
                except IntegrityError:
                    messages.error(request, "A member with that email already exists.")
            else:
                messages.error(request, "Please fix the errors below.")

        elif action == 'edit':
            member_id = request.POST.get('member_id')
            member = get_object_or_404(Member, pk=member_id)
            form = MemberForm(request.POST)
            if form.is_valid():
                try:
                    member.first_name = form.cleaned_data['first_name']
                    member.last_name = form.cleaned_data['last_name']
                    member.email = form.cleaned_data['email']
                    member.phone = form.cleaned_data['phone'] or None
                    member.planid = form.cleaned_data['planid']
                    member.active = form.cleaned_data['active']
                    member.save()
                    messages.success(request, "Member updated successfully.")
                    return redirect('members')
                except IntegrityError:
                    messages.error(request, "That email is already in use.")
            else:
                messages.error(request, "Please fix the errors below.")

        elif action == 'delete':
            member_id = request.POST.get('member_id')
            member = get_object_or_404(Member, pk=member_id)
            member.delete()
            messages.success(request, "Member deleted.")
            return redirect('members')

    all_members = Member.objects.select_related('planid').order_by('last_name')
    plans = MembershipPlan.objects.all().order_by('plan_name')
    return render(request, 'core/members.html', {
        'members': all_members,
        'plans': plans,
        'form': MemberForm(),
    })


# ── Classes ──────────────────────────────────────────────────
@login_required
def classes(request):
    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'add':
            form = FitnessClassForm(request.POST)
            if form.is_valid():
                FitnessClass.objects.create(
                    class_name=form.cleaned_data['class_name'],
                    instructorid=form.cleaned_data['instructorid'],
                    day_of_week=form.cleaned_data['day_of_week'],
                    class_time=form.cleaned_data['class_time'],
                    capacity=form.cleaned_data['capacity'],
                    duration=form.cleaned_data['duration'],
                )
                messages.success(request, "Class added successfully.")
                return redirect('classes')
            else:
                messages.error(request, "Please fix the errors below.")

        elif action == 'edit':
            class_id = request.POST.get('class_id')
            fitness_class = get_object_or_404(FitnessClass, pk=class_id)
            form = FitnessClassForm(request.POST)
            if form.is_valid():
                fitness_class.class_name = form.cleaned_data['class_name']
                fitness_class.instructorid = form.cleaned_data['instructorid']
                fitness_class.day_of_week = form.cleaned_data['day_of_week']
                fitness_class.class_time = form.cleaned_data['class_time']
                fitness_class.capacity = form.cleaned_data['capacity']
                fitness_class.duration = form.cleaned_data['duration']
                fitness_class.save()
                messages.success(request, "Class updated successfully.")
                return redirect('classes')
            else:
                messages.error(request, "Please fix the errors below.")

        elif action == 'delete':
            class_id = request.POST.get('class_id')
            fitness_class = get_object_or_404(FitnessClass, pk=class_id)
            fitness_class.delete()
            messages.success(request, "Class deleted.")
            return redirect('classes')

    all_classes = FitnessClass.objects.select_related('instructorid').order_by('class_name')
    instructors = Instructor.objects.all().order_by('last_name')
    return render(request, 'core/classes.html', {
        'classes': all_classes,
        'instructors': instructors,
        'form': FitnessClassForm(),
    })


# ── Instructors ──────────────────────────────────────────────
@login_required
def instructors(request):
    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'add':
            form = InstructorForm(request.POST)
            if form.is_valid():
                try:
                    Instructor.objects.create(
                        first_name=form.cleaned_data['first_name'],
                        last_name=form.cleaned_data['last_name'],
                        email=form.cleaned_data['email'],
                        specialty=form.cleaned_data['specialty'] or None,
                    )
                    messages.success(request, "Instructor added successfully.")
                    return redirect('instructors')
                except IntegrityError:
                    messages.error(request, "An instructor with that email already exists.")
            else:
                messages.error(request, "Please fix the errors below.")

        elif action == 'edit':
            instructor_id = request.POST.get('instructor_id')
            instructor = get_object_or_404(Instructor, pk=instructor_id)
            form = InstructorForm(request.POST)
            if form.is_valid():
                try:
                    instructor.first_name = form.cleaned_data['first_name']
                    instructor.last_name = form.cleaned_data['last_name']
                    instructor.email = form.cleaned_data['email']
                    instructor.specialty = form.cleaned_data['specialty'] or None
                    instructor.save()
                    messages.success(request, "Instructor updated successfully.")
                    return redirect('instructors')
                except IntegrityError:
                    messages.error(request, "That email is already in use.")
            else:
                messages.error(request, "Please fix the errors below.")

        elif action == 'delete':
            instructor_id = request.POST.get('instructor_id')
            instructor = get_object_or_404(Instructor, pk=instructor_id)
            if FitnessClass.objects.filter(instructorid=instructor).exists():
                messages.error(request, "Cannot delete — this instructor is assigned to one or more classes.")
            else:
                instructor.delete()
                messages.success(request, "Instructor deleted.")
            return redirect('instructors')

    all_instructors = Instructor.objects.all().order_by('last_name')
    return render(request, 'core/instructors.html', {
        'instructors': all_instructors,
        'form': InstructorForm(),
    })


# ── Register ─────────────────────────────────────────────────
@login_required
def register(request):
    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'register':
            form = RegistrationForm(request.POST)
            if form.is_valid():
                member = form.cleaned_data['memberid']
                fitness_class = form.cleaned_data['classid']
                current_count = Registration.objects.filter(classid=fitness_class).count()
                if current_count >= (fitness_class.capacity or 0):
                    messages.error(request, f"'{fitness_class}' is full ({current_count}/{fitness_class.capacity} spots taken).")
                else:
                    try:
                        Registration.objects.create(
                            memberid=member,
                            classid=fitness_class,
                        )
                        messages.success(request, f"'{member}' registered for '{fitness_class}'.")
                        return redirect('register')
                    except IntegrityError:
                        messages.error(request, "This member is already registered for that class.")
            else:
                messages.error(request, "Please select a member and a class.")

        elif action == 'delete':
            reg_id = request.POST.get('registration_id')
            registration = get_object_or_404(Registration, pk=reg_id)
            registration.delete()
            messages.success(request, "Registration removed.")
            return redirect('register')

    search = request.GET.get('search', '')
    all_registrations = Registration.objects.select_related('memberid', 'classid').order_by('-registered_at')
    if search:
        all_registrations = all_registrations.filter(
            memberid__first_name__icontains=search
        ) | all_registrations.filter(
            memberid__last_name__icontains=search
        ) | all_registrations.filter(
            classid__class_name__icontains=search
        )

    return render(request, 'core/register.html', {
        'form': RegistrationForm(),
        'registrations': all_registrations,
        'search': search,
    })


# ── Plans ────────────────────────────────────────────────────
@login_required
def plans(request):
    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'add':
            form = MembershipPlanForm(request.POST)
            if form.is_valid():
                try:
                    MembershipPlan.objects.create(
                        plan_name=form.cleaned_data['plan_name'],
                        price_per_month=form.cleaned_data['price_per_month'],
                        classes_per_month=form.cleaned_data['classes_per_month'],
                        description=form.cleaned_data['description'] or None,
                    )
                    messages.success(request, "Plan added successfully.")
                    return redirect('plans')
                except IntegrityError:
                    messages.error(request, "A plan with that name already exists.")
            else:
                messages.error(request, "Please fix the errors below.")

        elif action == 'edit':
            plan_id = request.POST.get('plan_id')
            plan = get_object_or_404(MembershipPlan, pk=plan_id)
            form = MembershipPlanForm(request.POST)
            if form.is_valid():
                try:
                    plan.plan_name = form.cleaned_data['plan_name']
                    plan.price_per_month = form.cleaned_data['price_per_month']
                    plan.classes_per_month = form.cleaned_data['classes_per_month']
                    plan.description = form.cleaned_data['description'] or None
                    plan.save()
                    messages.success(request, "Plan updated successfully.")
                    return redirect('plans')
                except IntegrityError:
                    messages.error(request, "A plan with that name already exists.")
            else:
                messages.error(request, "Please fix the errors below.")

        elif action == 'delete':
            plan_id = request.POST.get('plan_id')
            plan = get_object_or_404(MembershipPlan, pk=plan_id)
            if Member.objects.filter(planid=plan, active=True).exists():
                messages.error(request, "Cannot delete — active members are on this plan.")
            else:
                plan.delete()
                messages.success(request, "Plan deleted.")
            return redirect('plans')

    all_plans = MembershipPlan.objects.annotate(member_count=Count('member')).order_by('plan_name')
    return render(request, 'core/plans.html', {
        'plans': all_plans,
        'form': MembershipPlanForm(),
    })
