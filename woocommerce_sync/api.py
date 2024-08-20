import frappe
from frappe import _
from .exceptions import woocommerceError
from .utils import clear_woocommerce_logs, make_woocommerce_log, disable_woocommerce_sync_on_exception
from .item_sync import sync_product_group, update_item_prices, sync_products, sync_individual_item, update_item_stock_qty

@frappe.whitelist()
def sync_single_item_to_woocommerce():
    woocommerce_settings = frappe.get_doc('WooCommerce Sync')
    sync_based_on = woocommerce_settings.sync_based_on 
    price_list = woocommerce_settings.price_list

    if woocommerce_settings.enable_sync:
        try :
            validate_woocommerce_settings(woocommerce_settings)

            if (sync_based_on == "WooCommerce Product ID"):
                sync_individual_item(woocommerce_item_id=woocommerce_settings.woocommerce_product_id, price_list=price_list,  warehouse=woocommerce_settings.warehouse)

            if (sync_based_on == "Item Code"):
                sync_individual_item(item_code=woocommerce_settings.item_code, price_list=price_list, warehouse=woocommerce_settings.warehouse)

        except Exception as e:
            if e.args[0] and hasattr(e.args[0], "startswith") and e.args[0].startswith("402"):
                make_woocommerce_log(title="woocommerce has suspended your account", status="Error",
                    method="sync_single_item_to_woocommerce", message=_("""WooCommerce has suspended your account till
                    you complete the payment. We have disabled WooCommerce Sync. Please enable it once
                    your complete the payment at woocommerce."""), exception=True)

                disable_woocommerce_sync_on_exception()
            
            else:
                make_woocommerce_log(title="sync has terminated", status="Error", method="sync_single_item_to_woocommerce",
                    message=frappe.get_traceback(), exception=True)
    else:
                    
        frappe.msgprint("WooCommerce Sync is not enabled. Click on 'Enable Sync' to connect ERPNext and your WooCommerce store.")
        make_woocommerce_log(
            title="WooCommerce Sync is disabled",
            status="Error",
            method="sync_single_item_to_woocommerce",
            message=_("""WooCommerce Sync is not enabled. Click on 'Enable Sync' to connect ERPNext and your WooCommerce store."""),
            exception=True)

# TODO: Finish this
@frappe.whitelist()
def sync_item_group_to_woocommerce():
    woocommerce_settings = frappe.get_doc("WooCommerce Sync")
    item_group = woocommerce_settings.item_group
    make_woocommerce_log(title="Item Group {0} Sync Job Queued".format(item_group), status="Queued", method=frappe.local.form_dict.cmd, message="Item Group {0} Sync Job Queued".format(item_group))

    if woocommerce_settings.enable_sync:
        make_woocommerce_log(title="Item Group {0} Sync Job Started".format(item_group), status="Started", method=frappe.local.form_dict.cmd, message="Item Group {0} Sync Job Started".format(item_group))

        try :
            validate_woocommerce_settings(woocommerce_settings)
            sync_product_group(woocommerce_settings.price_list, woocommerce_settings.warehouse, item_group, True if woocommerce_settings.enable_sync == 1 else False)
            update_item_stock_qty(item_group=item_group)
            update_item_prices(item_group=item_group, price_list=woocommerce_settings.price_list)
            make_woocommerce_log(title="Item Group {0} Sync Job Finished".format(item_group), status="Success", method=frappe.local.form_dict.cmd, message="Synced Item Group: {0}".format(item_group))

        except Exception as e:
            if e.args[0] and hasattr(e.args[0], "startswith") and e.args[0].startswith("402"):
                make_woocommerce_log(title="woocommerce has suspended your account", status="Error",
                    method="sync_item_group_to_woocommerce", message=_("""WooCommerce has suspended your account till
                    you complete the payment. We have disabled WooCommerce Sync. Please enable it once
                    your complete the payment at woocommerce."""), exception=True)

                disable_woocommerce_sync_on_exception()
            
            else:
                make_woocommerce_log(title="sync has terminated", status="Error", method="sync_item_group_to_woocommerce",
                    message=frappe.get_traceback(), exception=True)
                    
    else:
        frappe.msgprint("WooCommerce Sync is not enabled. Click on 'Enable Sync' to connect ERPNext and your WooCommerce store.")
        make_woocommerce_log(
            title="WooCommerce Sync is disabled",
            status="Error",
            method="sync_woocommerce_items",
            message=_("""WooCommerce Sync is not enabled. Click on 'Enable Sync' to connect ERPNext and your woocommerce store."""),
            exception=True)
            
# TODO: Finish this
@frappe.whitelist()
def sync_woocommerce_items():
    woocommerce_settings = frappe.get_doc("WooCommerce Sync")

    make_woocommerce_log(title="Item Sync Job Queued", status="Queued", method=frappe.local.form_dict.cmd, message="Item Sync Job Queued")
    
    if woocommerce_settings.enable_sync:
        make_woocommerce_log(title="Item Sync Job Started", status="Started", method=frappe.local.form_dict.cmd, message="Item Sync Job Started")
        try :
            validate_woocommerce_settings(woocommerce_settings)
            sync_start_time = frappe.utils.now()
            sync_products(woocommerce_settings.price_list, woocommerce_settings.warehouse, True if woocommerce_settings.enable_sync == 1 else False)
            update_item_stock_qty()
            update_item_prices(price_list=woocommerce_settings.price_list)
            frappe.db.set_value("WooCommerce Sync", None, "last_sync_datetime", sync_start_time)
            make_woocommerce_log(title="Item Sync Completed", status="Success", method=frappe.local.form_dict.cmd, message= "Synced Item List")

        except Exception as e:
            if e.args[0] and hasattr(e.args[0], "startswith") and e.args[0].startswith("402"):
                make_woocommerce_log(title="woocommerce has suspended your account", status="Error",
                    method="sync_woocommerce_items", message=_("""WooCommerce has suspended your account till
                    you complete the payment. We have disabled WooCommerce Sync. Please enable it once
                    your complete the payment at woocommerce."""), exception=True)

                disable_woocommerce_sync_on_exception()
            
            else:
                make_woocommerce_log(title="sync has terminated", status="Error", method="sync_woocommerce_items",
                    message=frappe.get_traceback(), exception=True)
                    
    else:
        frappe.msgprint("WooCommerce Sync is not enabled. Click on 'Enable Sync' to connect ERPNext and your WooCommerce store.")
        make_woocommerce_log(
            title="WooCommerce Sync is disabled",
            status="Error",
            method="sync_woocommerce_items",
            message=_("""WooCommerce Sync is not enabled. Click on 'Enable Sync' to connect ERPNext and your woocommerce store."""),
            exception=True)

def validate_woocommerce_settings(woocommerce_settings):
    try:
        woocommerce_settings.save()
    except woocommerceError:
        disable_woocommerce_sync_on_exception()

@frappe.whitelist()
def clear_logs():
    clear_woocommerce_logs()