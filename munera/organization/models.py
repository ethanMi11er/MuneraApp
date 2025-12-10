from django.db import models
from django.db.models import CASCADE
from django.conf import settings

class Role(models.TextChoices):
    Member = "Member"
    Manager = "Manager"

class Organization(models.Model):
    org_id = models.AutoField(primary_key=True, null=False, editable=False, help_text="Organization's ID", verbose_name="Org ID")
    org_creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=CASCADE, default=1, related_name='created_organizations')
    org_name = models.CharField(max_length=30, null=False, help_text="Organization Name", verbose_name="Organization Name")
    org_code = models.CharField(max_length=256, null=False, editable=True, unique=True, help_text="Private Code For Connecting To Organization", verbose_name="Organization Code")
    description = models.CharField(max_length=500, blank=True, null=True, editable=True, help_text="Description Of Organization", verbose_name="Description")
    created_on = models.DateField(auto_now_add=True, null=False, editable=False, help_text="Organization Creation Date", verbose_name="Created On")
    members = models.ManyToManyField(settings.AUTH_USER_MODEL, through='OrganizationMember', related_name='organizations')

    def __str__(self):
        return f"{self.org_name}"

class OrganizationMember(models.Model):
    organization = models.ForeignKey(Organization, on_delete=CASCADE, related_name="memberships")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=CASCADE, related_name="organization_memberships")
    role = models.CharField(max_length=7, default=Role.Member, choices=Role.choices, help_text="Role Of User", verbose_name="Role")
    date_joined = models.DateField(auto_now_add=True, help_text="Date User Joined Organization", verbose_name="Joined Date")

    class Meta:
        unique_together = ("organization", "user")

    def __str__(self):
        return f"{self.user} @ {self.organization} ({self.role})"

