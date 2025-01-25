
from pretix.base.exporter import ListExporter

class HelperListExporter(ListExporter):
    identifier = "helperlistexporter"
    verbose_name = "Helper Orders as Excel"