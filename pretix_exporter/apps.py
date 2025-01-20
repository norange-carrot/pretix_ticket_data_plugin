from django.utils.translation import gettext_lazy

from . import __version__

try:
    from pretix.base.plugins import PluginConfig
except ImportError:
    raise RuntimeError("Please use pretix 2.7 or above to run this plugin!")


class PluginApp(PluginConfig):
    default = True
    name = "pretix_exporter"
    verbose_name = "Helperexporter"

    class PretixPluginMeta:
        name = gettext_lazy("Helperexporter")
        author = "Nora Küchler"
        description = gettext_lazy("exports the data of all the purchased tickets from a certain type and saves it")
        visible = True
        version = __version__
        category = "API"
        compatibility = "pretix>=2.7.0"

    def ready(self):
        from . import signals  # NOQA
