from django.db import models
from django.urls import reverse

from cms.models import CMSPlugin


class Poll(models.Model):
    name = models.TextField()

    def __str__(self):
        return "{} ({})".format(self.name, self.pk)


class PollContent(models.Model):
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE)
    language = models.TextField()
    text = models.TextField()

    def __str__(self):
        return self.text

    def get_absolute_url(self):
        return reverse(f"admin:{self._meta.app_label}_{self._meta.model_name}_change", args=[self.id])

    def get_preview_url(self):
        return reverse(f"admin:{self._meta.app_label}_{self._meta.model_name}_preview", args=[self.id])


class Answer(models.Model):
    poll_content = models.ForeignKey(PollContent, on_delete=models.CASCADE)
    text = models.TextField()

    def __str__(self):
        return self.text


class PollPlugin(CMSPlugin):
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.poll)
