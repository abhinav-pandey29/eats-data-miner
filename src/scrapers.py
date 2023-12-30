"""
Gmail Scrapers

All scraper classes should be added here.
"""
import re

import utils


class ScrapeDoordashEmailCommand:
    """Command to scrape order details from Doordash order confirmation emails."""

    def __call__(self, message_obj):
        self.validate_message_obj(message_obj=message_obj)
        decoded_msg = utils.decode_raw_msg(msg_raw=message_obj["raw"])
        order = {
            "date": self.extract_order_date(decoded_msg),
            "store_name": self.extract_store_name(decoded_msg),
            "items": self.extract_order_items(decoded_msg),
            "cost_summary": self.extract_cost_summary(decoded_msg),
            "delivery_address": self.extract_delivery_address(decoded_msg),
            "eta": self.extract_est_delivery_time(decoded_msg),
        }
        return {"message_id": message_obj["id"], **order}

    @staticmethod
    def validate_message_obj(message_obj):
        required_keys = ("id", "raw", "snippet")
        assert all(k in message_obj.keys() for k in required_keys)
        expected_som = "DOORDASH Thanks for your order"
        assert message_obj["snippet"].startswith(expected_som)

    @staticmethod
    def extract_data(decoded_msg, pattern):
        regex = re.compile(pattern)
        match = re.search(regex, decoded_msg)
        return match.group(1).strip() if match else None

    def extract_order_date(self, decoded_msg):
        return self.extract_data(decoded_msg, r"Date\: (.+)\n")

    def extract_est_delivery_time(self, decoded_msg):
        return self.extract_data(
            decoded_msg, r"The estimated delivery time for your order\n is (.+)\."
        )

    def extract_store_name(self, decoded_msg):
        return self.extract_data(decoded_msg, r"Paid with.+?\n(.*?)\nTotal")

    def extract_delivery_address(self, decoded_msg):
        return self.extract_data(decoded_msg, r"Your receipt \n(.+\s*)- For\:")

    def extract_cost_summary(self, decoded_msg: str):
        pattern = re.compile(r"([A-Za-z\s]+) \$([\d\.]+)")
        matches = pattern.findall(decoded_msg)
        cost_summary = {label.strip(): float(value) for label, value in matches}
        return cost_summary

    def extract_order_items(self, decoded_msg):
        # Extract text segment containing order items
        start = re.search(r"For\: .+", decoded_msg).end()
        end = re.search(r"Subtotal .+", decoded_msg).start()
        order_text = decoded_msg[start:end]

        # Regex pattern to capture the quantity, item name (and options, if any), and price
        pattern = r"(\d+)x(.+?)\$([\d\.]+)"
        matches = re.findall(pattern, order_text, re.DOTALL)

        order_items = []
        for quantity, item_str, price in matches:
            item_parts = item_str.strip().replace("\n", "").split("â€¢ ")
            if len(item_parts) > 1:
                item, *modifiers = item_parts
            else:
                item, modifiers = item_parts[0], []

            order_items.append(
                {
                    "qty": int(quantity.strip()),
                    "item": item.strip(),
                    "modifiers": [mod.strip() for mod in modifiers],
                    "price": float(price),
                }
            )

        return order_items


def scrape_doordash_command_factory() -> ScrapeDoordashEmailCommand:
    return ScrapeDoordashEmailCommand()
