from django.db import models
from django.utils.text import slugify
from pygov_br.django_apps.camara_deputados import models as cd_models


class Theme(models.Model):
    description = models.CharField(max_length=50)
    slug = models.CharField(max_length=50)

    def __str__(self):
        return self.slug

    def save(self, *args, **kwargs):
        self.slug = slugify(self.description)
        return super(Theme, self).save(*args, **kwargs)


class Speech(models.Model):
    data = models.OneToOneField(cd_models.Speech)
    author = models.ForeignKey('Deputy', related_name='speeches')
    themes = models.ManyToManyField(Theme, related_name='speeches',
                                    null=True, blank=True)

    def __str__(self):
        return self.data.author.parliamentary_name


class SpeechIndex(models.Model):
    speech = models.ForeignKey(Speech, related_name='indexes')
    text = models.TextField()
    theme = models.ForeignKey(Theme, related_name='indexes',
                              null=True, blank=True)

    @property
    def author(self):
        return self.speech.author

    def __str__(self):
        return self.text


class Deputy(models.Model):
    data = models.OneToOneField(cd_models.Deputy)
    theme = models.ManyToManyField(Theme, related_name='deputies',
                                   null=True, blank=True)

    def __str__(self):
        return self.data.parliamentary_name
