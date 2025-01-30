import logging
from django_scopes import scope
from pretix.base.exporter import ListExporter
from pretix.base.models.orders import Order, OrderPosition

logger = logging.getLogger(__name__)

CATEGORY_ID = 2
# todos:
# add docs
# add tests


class HelperListExporter(ListExporter):
    identifier = "helperlistexporter"
    verbose_name = "Helper data list"
    description = "Download a spreadsheet with personal data of ordered tickets belonging to the Helper category."


    def iterate_list(self, form_data):
        logger.info("[HelperListExporter] Start exporting helper list")
        headers = self._get_headers()
        yield headers

        with scope(event=self.event):
            orders = self._get_orders()
            logger.info(f"[HelperListExporter] Found {len(orders)} orders.")
            for order in orders:
                for order_position in order.positions.all():
                    output_data = self._process_order(order, order_position)
                    if output_data:
                        yield output_data

    def _get_headers(self) -> list[str]:
        return [
            "Vorname",
            "Nachname",
            "E-Mail",
            "Telefon",
        ]

    def _get_orders(self) -> list[Order]:
        return (
            Order.objects.exclude(status=Order.STATUS_CANCELED)
            .filter(event=self.event)
            .all()
        )

    def _process_order(self, order: Order, order_position: OrderPosition) -> list[str]:
        if order_position.item.category.id == CATEGORY_ID:
            return [  # fields must be in the same order as headers
                order_position.attendee_name_parts.get("given_name", ""),
                order_position.attendee_name_parts.get("family_name", ""),
                order.email,
                order.phone,
            ]
