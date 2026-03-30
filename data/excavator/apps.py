from django.apps import AppConfig


class ExcavatorConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'data.excavator'
    label = 'excavator'
 
    def ready(self):
        import data.excavator.signals
