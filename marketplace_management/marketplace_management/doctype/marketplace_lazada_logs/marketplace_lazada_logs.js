// Copyright (c) 2024, zaviago and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Marketplace Lazada Logs", {
// 	refresh(frm) {

// 	},
// });

// Copyright (c) 2024, zaviago and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Marketplace Shopee Logs", {
// 	refresh(frm) {

// 	},
// });
frappe.ui.form.on("Marketplace Lazada Logs", "refresh", function(frm) {
    frm.add_custom_button(__("Send Order Again"), function() {

        var shop_id = frm.doc.seller_id;
		var webhookid = frm.doc.name;
		
		frappe.call({
			method: 'marketplace_management.auth.webhook_mange.sendorderagain_lazada',
			args: {
				"shop_id": shop_id,
                "webhook_id": webhookid
			}
		});
		
		
    });
});