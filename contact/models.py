from django.db import models


class CustomerInquiry(models.Model):
    name = models.CharField(max_length=80)
    email = models.EmailField(max_length=80)
    subject = models.CharField(max_length=80)
    message = models.TextField()
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "inquiries"
        ordering = ["created"]
        verbose_name_plural = "Customer inquiries"

    def __str__(self):
        return f"{self.subject} by {self.name}"
