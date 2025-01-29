import logging
from django_scopes import scope
from pretix.base.exporter import ListExporter
from pretix.base.models.orders import Order, OrderPosition

logger = logging.getLogger(__name__)

CATEGORY_ID = 2


class HelperListExporter(ListExporter):
    identifier = "helperlistexporter"
    verbose_name = "Helper Orders as Excel"

    def iterate_list(self, form_data):
        headers = self._get_headers()
        yield headers

        with scope(event=self.event):
            orders = self._get_orders()
            logger.info(f"Found {len(orders)} orders")
            for order in orders:
                self._process_order(order)

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

    def _process_order(self, order: Order):
        logger.info(f"Processing order {order.code}")
        for order_position in order.positions.all():
            yield self._extract_data(order, order_position)

    def _extract_data(self, order: Order, order_position: OrderPosition) -> list[str]:
        if order_position.item.category.id == CATEGORY_ID:
            return [
                order_position.attendee_name_parts.get("given_name", ""),
                order_position.attendee_name_parts.get("family_name", ""),
                order.email,
                order.phone,
            ]
