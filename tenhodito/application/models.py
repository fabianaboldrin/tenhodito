from django.db import models
from django.utils.text import slugify
from pygov_br.django_apps.camara_deputados import models as cd_models


class Theme(models.Model):
    description = models.CharField(max_length=50)
    slug = models.CharField(max_length=50)
    text = models.TextField()

    def __str__(self):
        return self.slug

    def save(self, *args, **kwargs):
        self.slug = slugify(self.description)
        return super(Theme, self).save(*args, **kwargs)


class SpeechSentence(models.Model):
    speech = models.ForeignKey(cd_models.Speech, related_name='sentences')
    text = models.TextField()
    theme = models.ForeignKey(Theme, related_name='sentences',
                              null=True, blank=True)

    @property
    def author(self):
        return self.speech.author

    def __str__(self):
        return self.text


class SpeechTheme(models.Model):
    speech = models.ForeignKey(cd_models.Speech)
    theme = models.ForeignKey(Theme, related_name='speeches',
                              null=True, blank=True)

    def __str__(self):
        return self.speech


class DeputyTheme(models.Model):
    deputy = models.ForeignKey(cd_models.Deputy, related_name='themes')
    theme = models.ForeignKey(Theme, related_name='deputies',
                              null=True, blank=True)
    timestamp = models.DateTimeField(auto_now=True)

    def __str__(self):
        pass

