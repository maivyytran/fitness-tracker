from django.contrib import admin
from .models import MembershipPlan, Instructor, Member, FitnessClass, Registration


@admin.register(MembershipPlan)
class MembershipPlanAdmin(admin.ModelAdmin):
    list_display = ('plan_name', 'price_per_month', 'classes_per_month', 'description')
    search_fields = ('plan_name',)
    ordering = ('plan_name',)


@admin.register(Instructor)
class InstructorAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name', 'email', 'specialty')
    search_fields = ('first_name', 'last_name', 'email')
    ordering = ('last_name',)


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name', 'email', 'phone', 'active', 'planid', 'joined_at')
    search_fields = ('first_name', 'last_name', 'email')
    list_filter = ('active', 'planid')
    ordering = ('last_name',)


@admin.register(FitnessClass)
class FitnessClassAdmin(admin.ModelAdmin):
    list_display = ('class_name', 'instructorid', 'day_of_week', 'class_time', 'capacity', 'duration')
    search_fields = ('class_name',)
    list_filter = ('day_of_week',)
    ordering = ('class_name',)


@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    list_display = ('memberid', 'classid', 'registered_at')
    search_fields = ('memberid__first_name', 'memberid__last_name', 'classid__class_name')
    list_filter = ('classid',)
    ordering = ('-registered_at',)