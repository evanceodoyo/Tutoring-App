import random
import string
from django.utils.text import slugify
from functools import wraps


def random_string_generator(size=5, chars=string.ascii_uppercase + string.digits):
    return "".join(random.choice(chars) for _ in range(size))


def unique_enroll_id_generator(instance, new_enroll_id=None):
    """
    Generates a unique enrollment ID for every enrollment.
    """
    enroll_id = new_enroll_id if new_enroll_id is not None else random_string_generator()
    Klass = instance.__class__
    if Klass.objects.filter(enrollment_id=enroll_id).exclude(id=instance.id).exists():
        return unique_enroll_id_generator(instance, new_enroll_id=None)
    return enroll_id

def slug_generator(instance, new_slug=None):
    """
    Generate a unique slug for Course/Article/Category/Tag from their titles.
    """
    slug = new_slug if new_slug is not None else slugify(instance.title)
    Klass = instance.__class__
    if Klass.objects.filter(slug=slug).exclude(id=instance.id).exists():
        rand_int = random.randint(300_000, 500_000)
        slug = f"{slug}-{rand_int}"
        return slug_generator(instance, new_slug=slug)

    return slug

# def slug_generator(instance, new_slug=None):
#     """
#     Generate a unique slug for Course/Article/Category/Tag from their titles.
#     """
#     slug = new_slug if new_slug is not None else slugify(instance.title)
#     Klass = instance.__class__
#     qs = Klass.objects.filter(slug=slug).exclude(id=instance.id)
#     if qs.exists():
#         rand_int = random.randint(300_000, 500_000)
#         slug = f"{slug}-{rand_int}"
#         return slug_generator(instance, new_slug=slug)

#     return slug

def method(func):
    @wraps(func)
    def wrapper(cls, *args, **kwargs):
        return func(cls, *args, **kwargs)
    return wrapper