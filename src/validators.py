"""
Helper functions to validate scraped data
"""
import functools
import re

from utils import decode_raw_msg, get_modifier_bullet


def doordash_validator(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except AssertionError:
            print(f"{func.__name__} assertion failed: ", kwargs.get("order"))
            return False
        except Exception as error:
            print(
                "Validation function failed and may need to be updated.",
                error,
                kwargs.get("order"),
            )
            return False
        else:
            return True

    return wrapper


@doordash_validator
def validate_order_subtotal(order):
    summary_dict = order["cost_summary"]
    actual_subtotal = summary_dict.get("Subtotal") or summary_dict.get("Estimated Subtotal")
    calc_subtotal = sum([item["price"] for item in order["items"]])
    assert actual_subtotal
    assert round(actual_subtotal, 2) == round(calc_subtotal, 2)


@doordash_validator
def validate_order_modifier_counts(order, msg):
    decoded_msg = decode_raw_msg(msg["raw"])
    start = re.search(r"For\: .+", decoded_msg).end()
    end = re.search(r"Subtotal .+", decoded_msg).start()
    msg_filtered = decoded_msg[start:end]

    bullet_symbol = get_modifier_bullet(msg_filtered)
    actual_modifier_count = msg_filtered.count(bullet_symbol)
    scraped_modifier_count = sum([len(item["modifiers"]) for item in order["items"]])
    assert actual_modifier_count == scraped_modifier_count
