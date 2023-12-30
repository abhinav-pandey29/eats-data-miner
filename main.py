"""
Script to scrape food delivery orders from Gmail
"""
import json
import os
import sys

import pandas as pd

# Add src directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, "src")
sys.path.append(src_dir)

from gmail import Gmail  # noqa: E402
from gsheets import GoogleSheets  # noqa: E402
from scrapers import scrape_doordash_command_factory  # noqa: E402
from validators import (  # noqa: E402
    validate_order_modifier_counts,
    validate_order_subtotal,
)


def load_from_cache(cache_path: str):
    if os.path.exists(cache_path):
        with open(cache_path, "r") as cache_file:
            return json.load(cache_file)
    return {}


def save_to_cache(messages, cache_path: str):
    with open(cache_path, "w") as cache_file:
        json.dump(messages, cache_file)


def get_messages(gmail: Gmail, query: str, use_cache: bool):
    cache_path = "data/cache/cached_messages.json"
    cached_messages = load_from_cache(cache_path) if use_cache else {}

    search_results = gmail.search(query)
    new_messages = {
        m["id"]: gmail.get_message_by_id(id=m["id"])
        for m in search_results
        if m["id"] not in cached_messages
    }

    all_messages = {**cached_messages, **new_messages}
    save_to_cache(all_messages, cache_path)
    return all_messages


def extract_orders(scrape_command, messages):
    orders = []
    success_msgs = []
    failed_msgs = []
    invalid_msgs = []
    for msg in messages.values():
        try:
            order = scrape_command(message_obj=msg)
        except AssertionError:
            invalid_msgs.append(msg)
            continue
        except Exception as error:
            failed_msgs.append({"error": str(error), "msg": msg})
            continue
        else:
            orders.append(order)
            success_msgs.append(msg)
    print(
        f"Total Messages: {len(messages)}"
        f"\n  - Success: {len(orders)}"
        f"\n  - Failure: {len(failed_msgs)}"
        f"\n  - Invalid: {len(invalid_msgs)}"
    )
    save_to_cache(invalid_msgs, "data/cache/invalid_messages.json")
    save_to_cache(failed_msgs, "data/cache/scraping_errors.json")
    return orders, success_msgs


def validate_results(orders, messsages):
    orders_clean = []
    for order, msg in zip(orders, messsages):
        if not validate_order_subtotal(order=order):
            continue
        if not validate_order_modifier_counts(order=order, msg=msg):
            continue
        orders_clean.append(order)
    return orders_clean


def process_orders(orders):
    orders_lst = []
    order_items_lst = []
    for order in orders:
        flattened_order = {}
        flattened_order["message_id"] = order["message_id"]
        flattened_order["date"] = order["date"]
        flattened_order["store_name"] = order["store_name"]
        flattened_order["delivery_address"] = order["delivery_address"]
        flattened_order["eta"] = order["eta"]
        flattened_order.update(order["cost_summary"])
        orders_lst.append(flattened_order)

        for item in order["items"]:
            item_dict = {"order_message_id": order["message_id"], **item}
            item_dict["modifiers"] = " | ".join(item["modifiers"])
            order_items_lst.append(item_dict)

    orders_df = pd.DataFrame(orders_lst)
    for col in orders_df.columns:
        fill_value = 0 if col[0].isupper() else ""
        orders_df.loc[:, col] = orders_df[col].fillna(fill_value)

    order_items_df = pd.DataFrame(order_items_lst)
    order_items_df.fillna("", inplace=True)

    return orders_df, order_items_df


def export_results(orders_df, order_items_df, save_local_copy: bool = True):
    if save_local_copy:
        orders_df.to_csv("data/orders.csv", index=False)
        order_items_df.to_csv("data/order_items.csv", index=False)
    sheets = GoogleSheets()
    dest = "Doordash Orders"
    sheets.write_df_to_sheet(
        orders_df, sheet_name=dest, worksheet_title="Orders", worksheet_index=0
    )
    sheets.write_df_to_sheet(
        order_items_df,
        sheet_name=dest,
        worksheet_title="Order Items",
        worksheet_index=1,
    )


def main():
    print("🌟 EXECUTION STARTED!")

    print("\n😺 Fetching emails...")
    gmail = Gmail()
    query = 'from:no-reply@doordash.com subject:"Order Confirmation for"'
    messages = get_messages(gmail, query, use_cache=True)

    print("\n🍕 Extracting orders...")
    orders, success_msgs = extract_orders(
        scrape_command=scrape_doordash_command_factory(),
        messages=messages,
    )

    print("\n❓ Validating results...")
    orders = validate_results(orders=orders, messsages=success_msgs)

    print("\n📤 Exporting results for analysis")
    orders_df, order_items_df = process_orders(orders=orders)
    export_results(orders_df=orders_df, order_items_df=order_items_df)

    print("\n🏁 EXECUTION COMPLETE.")


if __name__ == "__main__":
    main()
