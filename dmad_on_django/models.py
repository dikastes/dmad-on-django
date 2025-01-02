from django.db import models
from django.utils.translation import gettext_lazy as _
from iso639 import data as iso639_data
from pylobid.pylobid import PyLobidClient, GNDIdError, GNDNotFoundError, GNDAPIError, PyLobidPerson, PyLobidPlace, PyLobidOrg

# Create your models here.

max_trials = 3

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

    def parse_comma_separated_string(self, comma_separated_string):
        names = comma_separated_string.split(',')
        self.last_name = names[0]
        if len(names) > 1:
            self.first_name = ' '.join([ name.strip() for name in names[1:]])
        return self

    def create_from_comma_separated_string(self, comma_separated_string, status, person):
        name = PersonName()
        name.status = status
        name.person = person
        return name.parse_from_comma_separated_string(comma_separated_string)


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

    def sync_with_gnd(self):
        trials = max_trials
        url = f"http://d-nb.info/gnd/{self.gnd_id}"
        while trials:
            try:
                pl_person = PyLobidPerson(url, fetch_related=True)
            #except GNDIdError:
            #except GNDNotFoundError:
            except GNDAPIError:
                trials -= 1
                pass
            break
        PersonName.create_from_comma_separated_string(pl_person.pref_name, Status.PRIMARY, self)
        self.date_of_birth, self.date_of_death = pl_pers.life_span
        self.place_of_birth = pl_pers.birth_place
        self.place_of_death = pl_pers.death_place

    def get_default_name(self):
        return f'{self.names.get(status=Status.PRIMARY).__str__()}'

    def __str__(self):
        return f'{self.gnd_id}: {self.names.get(status=Status.PRIMARY).__str__()}'
