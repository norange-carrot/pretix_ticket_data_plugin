# Register your receivers here
from django.dispatch import receiver

from pretix.base.signals import register_data_exporters


@receiver(register_data_exporters, dispatch_uid="exporter_myexporter")
def register_data_exporter(sender, **kwargs):
    from .exporter import HelperListExporter
    return HelperListExporter