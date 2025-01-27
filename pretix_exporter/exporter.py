import logging
from django_scopes import scope
from pretix.base.exporter import ListExporter
from pretix.base.models.orders import Order

logger = logging.getLogger(__name__)


class HelperListExporter(ListExporter):
    identifier = "helperlistexporter"
    verbose_name = "Helper Orders as Excel"

    def iterate_list(self, form_data):
        headers = [
            "Vorname",
            "Nachname",
            "E-Mail",
            "Telefon",
        ]
        yield headers

        item_id = 3

        with scope(event=self.event):
            orders = (
                Order.objects.exclude(status=Order.STATUS_CANCELED)
                .filter(event=self.event)
                .all()
            )
            logger.info(f"Found {len(orders)} orders")
            for order in orders:
                logger.info(f"Processing order {order.code}")
                for order_position in order.positions.all():
                    if order_position.item.id != item_id:
                        continue
                    logger.info(f"Processing order {order_position.attendee_email}")
                    d = {
                        "Vorname": order_position.attendee_name_parts.get(
                            "given_name", ""
                        ),
                        "Nachname": order_position.attendee_name_parts.get(
                            "family_name", ""
                        ),
                        "E-Mail": order.email,
                        "Telefon": order.phone,
                    }

                    yield list(d.values())
