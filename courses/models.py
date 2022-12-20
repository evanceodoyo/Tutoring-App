from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse
from django.db.models import Avg
from utils.utils import slug_generator
from django_resized import ResizedImageField


class TimeStampedModel(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Category(TimeStampedModel):
    title = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=100, unique=True)

    class Meta:
        db_table = "categories"
        ordering = ["title"]
        verbose_name_plural = "Categories"

    def save(self, *args, **kwargs):
        self.slug = slug_generator(self)
        super(Category, self).save(*args, **kwargs)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("category", kwargs={"category_slug": self.slug})


class Tag(TimeStampedModel):
    title = models.CharField(max_length=30, unique=True)
    slug = models.SlugField(max_length=100, unique=True, null=True)

    class Meta:
        db_table = "tags"

    def save(self, *args, **kwargs):
        self.slug = slug_generator(self)
        super(Tag, self).save(*args, **kwargs)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("tag", kwargs={"tag_slug": self.slug})


class Course(TimeStampedModel):
    owner = models.ForeignKey(
        get_user_model(),
        on_delete=models.SET_NULL,
        null=True,
        related_name="core_courses",
    )
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="courses"
    )
    title = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=200, unique=True)
    overview = models.TextField()
    language = models.CharField(max_length=30)
    old_price = models.DecimalField(decimal_places=2, max_digits=9, default=0.0)
    price = models.DecimalField(decimal_places=2, max_digits=9)
    thumbnail = ResizedImageField(size=[600, 400], upload_to="courses/thumbnails")
    lessons = models.PositiveSmallIntegerField("Number of Lessons", default=12)
    number_of_weeks = models.PositiveSmallIntegerField("Number of Weeks", default=8)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "courses"
        ordering = ["pk"]

    def save(self, *args, **kwargs):
        self.slug = slug_generator(self)
        super(Course, self).save(*args, **kwargs)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("course_detail", kwargs={"course_slug": self.slug})

    @property
    def discount(self):
        return round((self.old_price - self.price) / self.old_price * 100)

    # @method
    def get_courses_by_id(ids):  # sourcery skip
        return Course.objects.filter(pk__in=ids)


class CourseTag(TimeStampedModel):
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name="course_tags"
    )
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)

    class Meta:
        db_table = "course_tags"

    def __str__(self):
        return self.tag.title


class Audience(TimeStampedModel):
    name = models.CharField(max_length=150, unique=True)

    class Meta:
        db_table = "audience"
        verbose_name_plural = "Audience"

    def __str__(self):
        return self.name


class CourseAudience(TimeStampedModel):
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name="course_audience"
    )
    audience = models.ForeignKey(Audience, on_delete=models.CASCADE)

    class Meta:
        db_table = "course_audience"
        verbose_name_plural = "Course Target Audience"

    def __str__(self):
        return self.audience.name


class Member(TimeStampedModel):
    member = models.OneToOneField(get_user_model(), on_delete=models.CASCADE)
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="course_members",
        blank=True,
        null=True,
    )
    event = models.ForeignKey(
        "events.Event",
        on_delete=models.CASCADE,
        related_name="event_members",
        blank=True,
        null=True,
    )

    class Meta:
        db_table = "members"

    def __str__(self):
        return self.member.name

    @property
    def member_rating(self):
        return Member.objects.annotate(avg_rating=Avg("teacher_reviews"))


class HitDetail(TimeStampedModel):
    ip = models.CharField(editable=False, max_length=100)
    device_type = models.CharField(max_length=100, default="")
    os_type = models.CharField(max_length=200, default="")
    os_version = models.CharField(max_length=200, default="")
    browser_type = models.CharField(max_length=200, default="")
    browser_version = models.CharField(max_length=200, default="")

    class Meta:
        db_table = "hits"

    def __str__(self):
        return self.ip


class CourseHit(TimeStampedModel):
    course = models.ForeignKey(
        Course, on_delete=models.SET_NULL, related_name="course_hits", null=True
    )
    hit = models.ForeignKey(HitDetail, on_delete=models.CASCADE)

    class Meta:
        db_table = "course_hits"

    def __str__(self):
        return f"{self.hit} for {self.course}"


class CourseWeek(TimeStampedModel):
    """
    Limit the number of weeks to 12 for every course.
    """

    WEEKS = [
        ("1", "1"),
        ("2", "2"),
        ("3", "3"),
        ("4", "4"),
        ("5", "5"),
        ("6", "6"),
        ("7", "7"),
        ("8", "8"),
        ("9", "9"),
        ("10", "10"),
        ("11", "11"),
        ("12", "12"),
    ]
    course = models.ForeignKey(
        Course, related_name="course_weeks", on_delete=models.CASCADE
    )
    week = models.CharField(choices=WEEKS, default="1", max_length=2, unique=True)

    class Meta:
        db_table = "course_weeks"
        ordering = ["week"]

    def __str__(self):
        return f"Week {self.week} for {self.course}"


class CourseContent(TimeStampedModel):
    class ContentType(models.TextChoices):
        READING = "READING", "Reading"
        VIDEO = "VIDEO", "Video"
        AUDIO = "AUDIO", "Audio"

    course = models.ForeignKey(Course, on_delete=models.CASCADE, blank=True, null=True)
    title = models.CharField(max_length=100, default="")
    file = models.FileField(upload_to="courses/contents", null=True, blank=True)
    questions = models.SmallIntegerField("Number of questions", default=0)
    length = models.PositiveSmallIntegerField(
        "Content length in minutes", blank=True, null=True
    )
    content_type = models.CharField(
        choices=ContentType.choices, default=ContentType.READING, max_length=8
    )

    class Meta:
        db_table = "course_contents"
        ordering = ["created"]

    def __str__(self):
        return f"{self.content_type}: {self.title} for {self.course}"


class WeeklyCourseContent(TimeStampedModel):
    course_week = models.ForeignKey(
        CourseWeek,
        on_delete=models.CASCADE,
        related_name="weekly_course_contents",
        blank=True,
        null=True,
    )
    content = models.ForeignKey(CourseContent, on_delete=models.CASCADE)

    class Meta:
        db_table = "weekly_course_contents"
        ordering = ["course_week"]

    def __str__(self):
        return f"{self.content} for {self.course_week}"


class CourseReviewRating(TimeStampedModel):
    RATE_CHOICES = (
        (1, 1),
        (2, 2),
        (3, 3),
        (4, 4),
        (5, 5),
    )
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    course = models.ForeignKey(
        Course, related_name="course_reviews", on_delete=models.CASCADE
    )
    title = models.CharField(max_length=50)
    comment = models.TextField(blank=True)
    rating = models.IntegerField(choices=RATE_CHOICES)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "course_reviews"
        ordering = ["-created"]

    def __str__(self):
        return f"Review for {self.course} by {self.user}"


class TeacherReviewRating(TimeStampedModel):
    RATE_CHOICES = (
        (1, 1),
        (2, 2),
        (3, 3),
        (4, 4),
        (5, 5),
    )
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    teacher = models.ForeignKey(
        get_user_model(), related_name="teacher_reviews", on_delete=models.CASCADE
    )
    comment = models.TextField(blank=True)
    rating = models.IntegerField(choices=RATE_CHOICES)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "teacher_reviews"
        ordering = ["-created"]

    def __str__(self):
        return f"Review for {self.teacher} by {self.user}"
