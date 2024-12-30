from django.db import models
from django.utils.translation import gettext_lazy as _
from iso639 import data as iso639_data

# Create your models here.

Language = { iso_data['iso639_1'].upper() : iso_data['name'] for iso_data in iso639_data }

class Status(models.TextChoices):
    PRIMARY = 'P', _('Primary')
    ALTERNATIVE = 'A', _('Alternative')

class PlaceName(models.Model):
    name = models.CharField(max_length=20)
    language = models.CharField(
            max_length=15,
            choices=Language,
            default=Language['DE']
        )
    place = models.ForeignKey(
            'Place',
            on_delete=models.CASCADE,
            related_name='names'
        )
    status = models.CharField(
            max_length=1,
            choices=Status,
            default=Status.PRIMARY
        )

    def __str__(self):
        return name

class Place(models.Model):
    gnd_id = models.CharField(max_length=20)
    parent_place = models.ForeignKey(
            'Place',
            on_delete=models.SET_NULL,
            null=True,
            blank=True,
            related_name='child_places'
        )
    description = models.TextField()

    def __str__(self):
        return f'{self.gnd_id}: {self.names.get(status=Status.PRIMARY).name}'

class PersonName(models.Model):
    first_name = models.CharField(max_length=20)
    last_name = models.CharField(max_length=20)
    language = models.CharField(
            max_length=15,
            choices = Language,
            default = Language['DE']
        )
    person = models.ForeignKey(
            'Person',
            on_delete = models.CASCADE,
            related_name = 'names'
        )
    status = models.CharField(
            max_length = 1,
            choices = Status,
            default = Status.PRIMARY
        )

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

class Person(models.Model):
    class Gender(models.TextChoices):
        MALE = 'm', _('male')
        FEMALE = 'f', _('female')
        NULL = '', _('null')

    gnd_id = models.CharField(max_length=20)
    gender = models.CharField(
            max_length=1,
            choices=Gender,
            default=Gender.NULL
        )
    geographic_area_code = models.CharField(max_length=10)
    description = models.TextField()
    birth_date = models.DateField(
            null=True,
            blank=True
        )
    death_date = models.DateField(
            null=True,
            blank=True
        )
    birth_place = models.ForeignKey(
            'Place',
            on_delete=models.SET_NULL,
            null=True,
            blank=True,
            related_name='birth_place_of'
        )
    death_place = models.ForeignKey(
            'Place',
            on_delete=models.SET_NULL,
            null=True,
            blank=True,
            related_name='death_place_of'
        )
    activity_place = models.ForeignKey(
            'Place',
            on_delete=models.SET_NULL,
            null=True,
            blank=True,
            related_name='activity_place_of'
        )

    def get_default_name(self):
        return f'{self.names.get(status=Status.PRIMARY).__str__()}'

    def __str__(self):
        return f'{self.gnd_id}: {self.names.get(status=Status.PRIMARY).__str__()}'
