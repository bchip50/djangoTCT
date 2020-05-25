from django.apps import AppConfig


class TctsiteConfig(AppConfig):
    name = 'tctsite'

class ProfilesConfig(AppConfig):
    name = 'profiles'
    verbose_name = "User Profiles"

    def ready(self):
        from . import signals