import logging
from collections import OrderedDict
from django import forms
from django_scopes import scope
from pretix.base.exporter import ListExporter
from pretix.base.models import Item
from pretix.base.models.orders import Order, OrderPosition

logger = logging.getLogger(__name__)


class TicketPIIExporter(ListExporter):
    identifier = "ticketpiilistexporter"
    verbose_name = "Personal data list"
    description = "Download a spreadsheet with personal data of ordered tickets belonging to a chosen product type."

    @property
    def additional_form_fields(self) -> dict:
        return OrderedDict(
            [
                (
                    "product_type",
                    forms.ChoiceField(
                        label=("Ticketart"),
                        choices=[
                            (product.id, product.name)
                            for product in Item.objects.filter(event=self.event)
                        ],
                    ),
                ),
            ]
        )

    def iterate_list(self, form_data):
        logger.info(
            f"[TicketDataExporter] Start exporting list of Data for ticket type {Item.objects.get(id=form_data.get('product_type')).name}"
        )
        headers = self._get_headers()
        yield headers

        with scope(event=self.event):
            orders = self._get_orders()
            logger.info(f"[TicketDataExporter] Found {len(orders)} total orders.")
            for order in orders:
                for order_position in order.positions.all():
                    output_data = self._process_order(order, order_position, form_data)
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

    def _process_order(
        self, order: Order, order_position: OrderPosition, form_data
    ) -> list[str]:
        item_id = int(form_data.get("product_type"))
        if order_position.item.id == item_id:
            return [  # fields must be in the same order as headers
                order_position.attendee_name_parts.get("given_name", ""),
                order_position.attendee_name_parts.get("family_name", ""),
                order.email,
                order.phone,
            ]
