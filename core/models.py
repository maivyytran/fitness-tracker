from django.db import models

class MembershipPlan(models.Model):
    planid = models.AutoField(primary_key=True, db_column='planid')
    plan_name = models.CharField(max_length=100, unique=True)
    price_per_month = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    classes_per_month = models.IntegerField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'membership_plan'
        managed = False

    def __str__(self):
        return self.plan_name


class Instructor(models.Model):
    instructorid = models.AutoField(primary_key=True, db_column='instructorid')
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(max_length=100, unique=True)
    specialty = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        db_table = 'instructor'
        managed = False

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Member(models.Model):
    memberid = models.AutoField(primary_key=True, db_column='memberid')
    planid = models.ForeignKey(
        MembershipPlan,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        db_column='planid'
    )
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(max_length=100, unique=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    active = models.BooleanField(default=True)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'member'
        managed = False

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class FitnessClass(models.Model):
    classid = models.AutoField(primary_key=True, db_column='classid')
    class_name = models.CharField(max_length=100)
    instructorid = models.ForeignKey(
        Instructor,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        db_column='instructorid'
    )
    day_of_week = models.CharField(max_length=20, null=True, blank=True)
    class_time = models.CharField(max_length=20, null=True, blank=True)
    capacity = models.IntegerField(null=True, blank=True)
    duration = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = 'class'
        managed = False

    def __str__(self):
        return f"{self.class_name} ({self.day_of_week} {self.class_time})"


class Registration(models.Model):
    registrationid = models.AutoField(primary_key=True, db_column='registrationid')
    memberid = models.ForeignKey(
        Member,
        on_delete=models.CASCADE,
        db_column='memberid'
    )
    classid = models.ForeignKey(
        FitnessClass,
        on_delete=models.CASCADE,
        db_column='classid'
    )
    registered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'registration'
        managed = False
        unique_together = [('memberid', 'classid')]

    def __str__(self):
        return f"{self.memberid} → {self.classid}"