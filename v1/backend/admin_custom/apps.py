from django.apps import AppConfig

class AdminCustomConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'admin_custom'
    verbose_name = 'Custom Admin'

    def ready(self):
        import admin_custom.signals
