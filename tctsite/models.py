from django.db import models
from django.conf import settings
from phone_field import PhoneField

import datetime


# Create your models here.
class DateRange(models.Model):
    created = models.DateField(auto_now_add=True)
    modified = models.DateField(auto_now=True)

    class Meta:
        abstract= True


class Archivable(models.Model):
    ARCHIVE_CHOICES = (
        (False, "Active"),
        (True, "Archived"),
    )
    archive = models.BooleanField(default=False, choices=ARCHIVE_CHOICES)
    archived = models.DateField(auto_now=True)


class Post(DateRange,Archivable):
    title = models.CharField(max_length=100)
    author = models.ForeignKey(to="Profile",
                               on_delete=models.CASCADE,
                               related_name='blog_posts')
    body = models.TextField()

    class Meta:
        ordering = ('-created',)

    def __str__(self):
        return self.title

    def is_active(self):
        return not self.archive

class Resource(DateRange, models.Model):
    RESOURCE_CHOICES = (
        ('book', 'Book'),
        ('store', 'Store'),
        ('website', 'Web Site'),
        ('video', 'Video from YouTube'),
        ('photos', 'Photo Collection'),
        ('tourney', 'Tournament or Conference'),
    )
    owner = models.ForeignKey(to="Profile", on_delete=models.DO_NOTHING, blank=True, null=True)
    title= models.CharField(max_length=80)
    caption = models.CharField(max_length=120)
    weblink = models.URLField(help_text='Enter link to the resource home page.')
    description = models.TextField(help_text='Describe the resource.')
    thumbnail = models.ImageField(verbose_name="Icon for email.", name="email_icon", blank=True, null=True)
    resource_type = models.CharField(max_length=10, choices=RESOURCE_CHOICES)

    def __str__(self):
        return f"{self.resource_type} {self.title}"

    class Meta:
        pass


class Message(DateRange, models.Model):
    course = models.ForeignKey(to="Course",on_delete=models.CASCADE)
    current = models.BooleanField(verbose_name="Current Message", default=False)
    title = models.CharField(max_length=80, help_text="Heading for the email.")
    body = models.TextField(verbose_name="EMail body.")
    celltext = models.CharField(max_length=100)
    thumbnail = models.ImageField(verbose_name="Icon for email.", name="email_icon", blank=True, null=True)
    owner = models.ForeignKey(to="Profile", on_delete=models.DO_NOTHING, blank=True, null=True)

    def __str__(self):
        return self.title


class Address(models.Model):
    street1 = models.CharField(max_length=100)
    street2 = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=2, help_text="Enter two character state code", default="TX")
    zipcode = models.CharField(max_length=12)
    # Latitude and longitude for mapping - optional
    lat = models.FloatField(blank=True, null=True)
    lon = models.FloatField(blank=True, null=True)

    class Meta:
        abstract= True


class Location(Address, models.Model):
    name = models.CharField(max_length=100, help_text="Name of the location.")
    contact = models.CharField(max_length=100, help_text="Name of the primary contact for the location.",
                               blank=True, null=True)
    phone = PhoneField(help_text="Phone number for the primary contact for the location.",
                       blank=True, null=True)
    owner = models.ForeignKey(to="Profile",on_delete=models.CASCADE)
    description = models.TextField(verbose_name="Location description.", blank=True, null=True)
    weblink = models.URLField(verbose_name="Web site for the location", blank=True, null=True)

    def __str__(self):
        return f"{self.name}"


class Meeting(models.Model):
    location = models.ForeignKey(to="Location",on_delete=models.CASCADE, blank=True, null=True)
    course = models.ForeignKey(to="Course",on_delete=models.CASCADE, blank=True, null=True)
    starts = models.TimeField(verbose_name="Starting Time.")
    duration = models.DurationField(verbose_name="How long does each session last?")
    rrulestr = models.TextField(verbose_name="Recurrence Rules Set",
                                help_text=
'''
<a href='https://dateutil.readthedocs.io/en/stable/rrule.html#rrulestr-examples'> 
RRuleSet Documentation </a>
'''
                                )
    def __str__(self):
        return f"{self.location.name} using {self.rrulestr}"

class StyleCourses(models.Model):
    style = models.ForeignKey(to='Style', on_delete=models.CASCADE, related_name='courses_style')
    course = models.ForeignKey(to='Course', on_delete=models.CASCADE, related_name='style_course')
    active = models.BinaryField(default=True)
    started = models.DateField(auto_now_add=True)


class Style(models.Model):
    title = models.CharField(max_length=80, help_text="Enter short title for the TaiChi Style.")
    history = models.TextField(help_text="Short history of the style.")
    wiki = models.URLField(help_text="Link to the wiki article for the style.", blank=True, null=True)
    thumbnail = models.ImageField(verbose_name="Style Icon", name="style_icon", blank=True, null=True)
    owner = models.ForeignKey(to="Profile", related_name='style_owner',
                              on_delete=models.DO_NOTHING, blank=True, null=True)
    # many to many fields
    resources = models.ManyToManyField(to="Resource", blank=True)
    courses = models.ManyToManyField(to='Course', through='StyleCourses', blank=True)

    def __str__(self):
        return self.title

class Leadership(models.Model):
    course = models.ForeignKey(to='Course', on_delete=models.CASCADE, related_name='leaders_course')
    leader = models.ForeignKey(to='Profile', on_delete=models.CASCADE, related_name='course_leader')
    primary = models.BinaryField(default=False)
    active = models.BinaryField(default=True)
    started = models.DateField(auto_now_add=True)

class Course(models.Model):
    title = models.CharField(max_length=120, help_text="Enter short title for this Session or Course.")
    description = models.TextField(
        help_text="Enter description of the session or course with goals and level of expertise recommended.")
    level = models.CharField(max_length= 40, blank=True, null=True)
    cost = models.CharField(max_length=60, default="Free")
    thumbnail = models.ImageField(verbose_name="Course Icon", name="course_icon", blank=True, null=True)
    owner = models.ForeignKey(to="Profile",
                              on_delete=models.DO_NOTHING, blank=True, null=True, related_name='course_owner')
    # many to many fields
    leaders = models.ManyToManyField(to='Profile', through='Leadership', blank=True)
    resources = models.ManyToManyField(to="Resource", blank=True)

    def __str__(self):
        return self.title



class BaseProfile(models.Model):
    USER_TYPES = (
        (0, 'Member'),
        (1, 'Leader'),
    )
    user = models.OneToOneField(settings.AUTH_USER_MODEL,
                                on_delete=models.CASCADE)
    user_type = models.IntegerField(null=True, choices=USER_TYPES)
    biography = models.TextField(verbose_name='Biography', blank=True, null=True)
    phone = PhoneField(blank=True, null=True, help_text='Primary Phone Number.', E164_only=True)
    cell_phone = PhoneField(blank=True, null=True, help_text='Cell Phone Number for texts.', E164_only=True)
    birthdate = models.DateField(blank=True, null=True, help_text='Enter your birth date.')
    city = models.CharField(max_length=20, blank=True, null=True,help_text="City where you live.")
    state = models.CharField(max_length=20, blank=True, null=True,help_text="State where you live.")
    zipcode = models.CharField(max_length=10, blank=True, null=True,help_text="Zipcode where you live.")
    preferred_style = models.ForeignKey(to="Style",on_delete=models.SET_NULL,null=True,blank=True)

    def __str__(self):
        return f"{self.user}: {self.biography:.20}"

    @property
    def get_age(self):
        today = datetime.date.today()
        return (today.year - self.birthdate.year) - int(
            (today.month, today.day) <
            (self.birthdate.month, self.birthdate.day)
        )

    @property
    def fullname(self):
        return f"{self.user.first_name} {self.user.last_name}"

    @property
    def is_leader(self):
        return self.user_type

    class Meta:
        abstract = True


class Instructor(models.Model):
    gmail = models.EmailField(max_length=80, help_text="GMail address used to authenticate to YouTube.")
    lineage = models.TextField(name='Lineage',max_length=1200,blank=True,null=True,
                               help_text='Describe the lineage of your style. Who was your teacher.')

    class Meta:
        abstract = True


class Member(models.Model):
    pass

    class Meta:
        abstract = True


class Profile(Member, Instructor, BaseProfile):
    pass