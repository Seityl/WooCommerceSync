// Copyright (c) 2024, Jeriel Francis and contributors
// For license information, please see license.txt

frappe.ui.form.on("WooCommerce Sync", {
	refresh: function(frm) {
        frm.add_custom_button(__('Clear Logs'), function() {
            frappe.call({
                method:"woocommerce_sync.api.clear_logs",
                freeze: true,
                freeze_message: __('Clearing Logs...')
            })
        });

        sync_based_on_visibility(frm);
        sync_based_on_options_visibility(frm);
	},

    sync_options: function(frm) {
        sync_based_on_visibility(frm);
        
        if (frm.is_dirty()) {
            frm.save()
        }
    }, 

    sync_based_on: function(frm) {
        sync_based_on_options_visibility(frm);

        if (frm.is_dirty()) {
            frm.save()
        }
    }
});

function sync_based_on_visibility(frm) {
    if (frm.doc.sync_options === '') {
        clear_sync_based_on_values(frm)
        clear_item_group_values(frm)

        frm.set_value('sync_based_on', '');
        
        frm.toggle_display('section_break_options', false);
        frm.toggle_display('sync_based_on', false);
        frm.toggle_display('item_group', false);
        
        frm.remove_custom_button('Sync WooCommerce Items');
        frm.remove_custom_button('Sync Item Group');
        frm.remove_custom_button('Sync Item');
    }
    
    if (frm.doc.sync_options === 'Sync Single Item') {
        clear_item_group_values(frm)
        
        frm.toggle_display('section_break_options', true);
        frm.toggle_display('sync_based_on', true);
        frm.toggle_display('item_group', false);
        
        frm.remove_custom_button('Sync Item Group');
        frm.remove_custom_button('Sync WooCommerce Items');
        
        frm.add_custom_button(__('Sync Item'), function() {
            if (frm.is_dirty()) {
                frm.save().then(() => {
                    sync_item(frm);
                })
            } else {
                sync_item(frm);
            }
        });
    }
    
    if (frm.doc.sync_options === 'Sync Item Group') {
        clear_sync_based_on_values(frm);
        
        frm.toggle_display('section_break_options', true);
        frm.toggle_display('sync_based_on', false);
        frm.toggle_display('item_group', true);
        
        frm.set_value('sync_based_on', '');
        
        frm.remove_custom_button('Sync WooCommerce Items');
        frm.remove_custom_button('Sync Item');
        
        frm.add_custom_button(__('Sync Item Group'), function() {
            if (frm.is_dirty()) {
                frm.save().then(() => {
                    sync_item_group(frm);
                })
            } else {
                sync_item_group(frm);
            }
        });
    }
    
    if (frm.doc.sync_options === 'Sync All Items') {
        clear_sync_based_on_values(frm);
        clear_item_group_values(frm)
        
        frm.remove_custom_button('Sync Item');
        frm.remove_custom_button('Sync Item Group');
        
        frm.toggle_display('section_break_options', true);
        frm.toggle_display('sync_based_on', false);
        frm.toggle_display('item_group', false);
        
        frm.set_value('sync_based_on', '');
        
        frm.add_custom_button(__('Sync WooCommerce Items'), function() {
            frappe.call({
                method:"woocommerce_sync.api.sync_woocommerce_items",
                freeze: true,
                freeze_message: __('Syncing WooCommerce Items...')
            })
        });
    }
}

function sync_based_on_options_visibility(frm) {
    if (frm.doc.sync_based_on === '') {
        clear_sync_based_on_values(frm);

        frm.toggle_display('item_code', false);
        frm.toggle_display('woocommerce_product_id', false);
    }
    else if (frm.doc.sync_based_on === 'Item Code') {
        frm.toggle_display('item_code', true);
        frm.toggle_display('woocommerce_product_id', false);
        frm.set_value('woocommerce_product_id', '');
    } 
    else if (frm.doc.sync_based_on === 'WooCommerce Product ID') {
        frm.toggle_display('woocommerce_product_id', true);
        frm.toggle_display('item_code', false);
        frm.set_value('item_code', '');
    }
}

function clear_sync_based_on_values(frm) {
    frm.set_value('woocommerce_product_id', '');
    frm.set_value('item_code', '');
    
    if (frm.is_dirty()) {
        frm.save()
    }
}

function clear_item_group_values(frm) {
    frm.set_value('item_group', '');
    
    if (frm.is_dirty()) {
        frm.save()
    }
}

function sync_item(frm) {
    if( frm.doc.enable_sync) {
        if (frm.doc.sync_based_on) {
            if (frm.doc.woocommerce_product_id || frm.doc.item_code) {
                frappe.call({
                    method:"woocommerce_sync.api.sync_single_item_to_woocommerce",
                    freeze: true,
                    freeze_message: __('Syncing Item...')                            
                }).then(() => {
                    if(frm.doc.item_code) {
                        frappe.msgprint(`Successfully Synced Item ${frm.doc.item_code}.`);
                    }
                    if(frm.doc.woocommerce_product_id) {
                        frappe.msgprint(`Successfully Synced WooCommerce Product ID ${frm.doc.woocommerce_product_id}.`);
                    }
                })
            } else {
                frappe.msgprint('Error Syncing Item: Enter Item Code / WooCommerce Product ID');
            }
        } else {
            frappe.msgprint('Error Syncing Item: Select Item Code / WooCommerce Product ID from Sync Based On');
        }
    } else {
        frappe.msgprint('Error Syncing Item: WooCommerc Sync is not enabled. Select \'Enable Sync\' to sync to woocommerce.');
    }
}

function sync_item_group(frm) {
    if(frm.doc.enable_sync) {
        if(frm.doc.item_group) {
            frappe.call({
                method:"woocommerce_sync.api.sync_item_group_to_woocommerce",
                freeze: true,
                freeze_message: __('Syncing Item Group...')                            
            }).then(() => {
                frappe.msgprint(`Successfully Synced Item Group ${frm.doc.item_group}.`);
            })
        } else {
            frappe.msgprint('Error Syncing Item Group: Select an Item Group');
        }
    } else {
        frappe.msgprint('Error Syncing Item: WooCommerc Sync is not enabled. Select \'Enable Sync\' to sync to woocommerce.');
    }
}