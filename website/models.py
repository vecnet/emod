from django.contrib.auth.models import User
from django.db import models


class Folder(models.Model):
    """
    This creates a container for simulations.
    """
    name = models.TextField()
    description = models.TextField(null=True, blank=True)

    parent_folder = models.ForeignKey("self", null=True, blank=True)
    user = models.ForeignKey(User, null=False)

    is_public = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    time_deleted = models.DateTimeField(null=True)
    sort_order = models.IntegerField()

    # Automatically set the field to now when the object is first created.
    creation_timestamp = models.DateTimeField(auto_now_add=True)
    # Automatically set the field to now every time the object is saved.
    last_modified_timestamp = models.DateTimeField(auto_now=True)

    metadata = JSONField(null=True, blank=True)

    def delete(self):
        # if folder is not empty, do not delete
        if not self.is_empty:
            return 'NotEmpty'
        else:
            self.is_deleted = True
            self.save()
            return True

    @property
    def is_empty(self):
        # check for subfolders
        folder_list = Folder.objects.filter(parent=self.id, is_deleted=False)
        # check for scenarios
        scenario_list = DimBaseline.objects.filter(folder=self.id, is_deleted=False)
        if folder_list.count() == 0 and scenario_list.count() == 0:
            return True
        else:
            return False

    def is_folder(self):
        return True