from django.db import models
from django.contrib.auth.models import User

KERALA_DISTRICTS_CHOICES = [
    ('Thiruvananthapuram', 'Thiruvananthapuram'),
    ('Kollam', 'Kollam'),
    ('Pathanamthitta', 'Pathanamthitta'),
    ('Alappuzha', 'Alappuzha'),
    ('Kottayam', 'Kottayam'),
    ('Idukki', 'Idukki'),
    ('Ernakulam', 'Ernakulam'),
    ('Thrissur', 'Thrissur'),
    ('Palakkad', 'Palakkad'),
    ('Malappuram', 'Malappuram'),
    ('Kozhikode', 'Kozhikode'),
    ('Wayanad', 'Wayanad'),
    ('Kannur', 'Kannur'),
    ('Kasaragod', 'Kasaragod'),
]

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    district = models.CharField(
        max_length=50,
        choices=KERALA_DISTRICTS_CHOICES,
        blank=True,
        null=True,
        help_text="If set, restricts this admin to managing schemes for this district only."
    )

    def __str__(self):
        return f"{self.user.username} Profile ({self.district or 'All Districts'})"

class Scheme(models.Model):
    district = models.CharField(
        max_length=50,
        choices=KERALA_DISTRICTS_CHOICES,
        default='Thiruvananthapuram',
        help_text="The district this scheme belongs to."
    )
    title = models.CharField(max_length=255)
    description = models.TextField()
    eligibility = models.TextField()
    benefits = models.TextField()
    documents = models.TextField(help_text="Enter required documents separated by commas (e.g. Aadhaar Card, Bank Passbook)")
    procedures = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"[{self.district}] {self.title}"

    @property
    def documents_list(self):
        return [doc.strip() for doc in self.documents.split(',') if doc.strip()]
