"""
Helper functions to validate scraped data
"""
import functools
import re

from utils import decode_raw_msg


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
    try:
        actual_subtotal = order["cost_summary"]["Subtotal"]
    except KeyError:
        actual_subtotal = order["cost_summary"]["Estimated Subtotal"]
    calc_subtotal = sum([item["price"] for item in order["items"]])
    assert round(actual_subtotal, 2) == round(calc_subtotal, 2)


@doordash_validator
def validate_order_modifier_counts(order, msg):
    decoded_msg = decode_raw_msg(msg["raw"])
    start = re.search(r"For\: .+", decoded_msg).end()
    end = re.search(r"Subtotal .+", decoded_msg).start()
    msg_filtered = decoded_msg[start:end]

    actual_modifier_count = msg_filtered.count("\nâ€¢ ")
    scraped_modifier_count = sum([len(item["modifiers"]) for item in order["items"]])
    assert actual_modifier_count == scraped_modifier_count
