from django.contrib.auth.models import Group, User
from django.db import models


class ContractPermission(models.Model):
    codename = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.codename


class GroupProfile(models.Model):
    group = models.OneToOneField(Group, on_delete=models.CASCADE, related_name='profile')
    display_name = models.CharField(max_length=100)
    group_entity_type = models.CharField(max_length=50)  # e.g. 'law', 'org'
    permissions = models.ManyToManyField(ContractPermission, blank=True)

    def __str__(self):
        return self.display_name


class LawFirm(models.Model):
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Organisation(models.Model):
    law_firm = models.ForeignKey(LawFirm, on_delete=models.CASCADE, related_name='organisations', default=1)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    contact_number = models.CharField(max_length=15, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class UserLawFirmAccess(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='law_firm_accesses')
    law_firm = models.ForeignKey(LawFirm, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'law_firm')


class UserOrganisationAccess(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='organisation_accesses')
    organisation = models.ForeignKey(Organisation, on_delete=models.CASCADE)
    law_firm = models.ForeignKey(LawFirm, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'organisation')
