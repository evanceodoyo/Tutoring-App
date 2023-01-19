from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.signals import pre_save

from courses.models import Course, TimeStampedModel
from utils.utils import unique_enroll_id_generator


class Enrollment(models.Model):
    student = models.ForeignKey(
        get_user_model(),
        related_name="enrollments",
        on_delete=models.SET_NULL,
        null=True,
    )
    enrollment_id = models.CharField(max_length=50, blank=True)
    amount = models.DecimalField(decimal_places=2, max_digits=9, blank=True)
    date_enrolled = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "enrollments"
        ordering = ["-date_enrolled"]
        verbose_name_plural = "Enrollments"

    def save(self, *args, **kwargs):
        self.enrollment_id = unique_enroll_id_generator(self)
        super(Enrollment, self).save(*args, **kwargs)

    def __str__(self):
        return f"Enroll #{self.enrollment_id} by {self.student}"


class EnrolledCourse(models.Model):
    enrollment = models.ForeignKey(
        Enrollment, related_name="courses", on_delete=models.CASCADE
    )
    student = models.ForeignKey(
        get_user_model(), related_name="enrolled_courses", on_delete=models.CASCADE
    )
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    date_enrolled = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.enrollment} : {self.course}"

    class Meta:
        db_table = "enrolled_courses"


class Coupon(TimeStampedModel):
    user = models.ForeignKey(
        get_user_model(), related_name="coupons", on_delete=models.CASCADE
    )
    code = models.CharField(max_length=20, unique=True)
    discount = models.DecimalField(decimal_places=2, max_digits=9, default=0)
    # expiry_date = models.DateTimeField()
    is_used = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.code} : KES {self.discount}"

    class Meta:
        db_table = "coupons"


class Wishlist(TimeStampedModel):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    class Meta:
        db_table = "wishlist"

    def __str__(self):
        return f"{self.user}'s Wishlist"
