import frappe
import requests
import json

@frappe.whitelist(allow_guest=True)
def handle_shopee_webhooks(**kwargs):   
    kwargs=frappe._dict(kwargs)
    #contact = frappe.new_doc("Marketplace Shopee Logs")
    #contact.website_response = kwargs
    #contact.insert(ignore_permissions=True)
    data = kwargs.get('data', {}) 
    ordersn = data.get('ordersn') 
    status = data.get('status')
    if ordersn:
        try:
            existing_record = frappe.get_doc("Marketplace Shopee Logs", {"order_id": ordersn, "status": status})
        except frappe.DoesNotExistError:
            existing_record = None
        
        if not existing_record:
            contact = frappe.new_doc("Marketplace Shopee Logs")
            contact.order_id = ordersn
            contact.status = status
            contact.shop_id = kwargs.shop_id
            contact.timestamp = kwargs.timestamp
            contact.insert(ignore_permissions=True)
            
            try:
                existing_record = frappe.get_doc("Marketplace Accounts", {"shop_id": kwargs.shop_id})
            except frappe.DoesNotExistError:
                existing_record = None
                
            if existing_record:    
                params = {'ordersn' :ordersn,'shop_id' : kwargs.shop_id,'status' : status }
                url = existing_record.website_url+"/api/method/marketplace_integration.webhook.handle_webhook.push_shopee_webhooks"
                response = requests.post(url,params)
                contact.website_response = response.text
                contact.save(ignore_permissions=True)   


@frappe.whitelist(allow_guest=True)
def handle_lazada_webhook(**kwargs): 
    kwargs = frappe._dict(kwargs)

    data = kwargs.get('data', {}) 
    buyer_id = data.get('buyer_id') 
    order_status = data.get('order_status')
    trade_order_id = data.get('trade_order_id')
    trade_order_line_id = data.get('trade_order_line_id')
    seller_id = kwargs.get('seller_id') 
    timestamp = kwargs.get('timestamp') 

    if trade_order_id:
        try:
            existing_record = frappe.get_doc("Marketplace Lazada Logs", {"trade_order_id": trade_order_id, "order_status": order_status})
        except frappe.DoesNotExistError:
            existing_record = None

        if not existing_record:
            contact = frappe.new_doc("Marketplace Lazada Logs")
            contact.buyer_id = buyer_id
            contact.order_status = order_status
            contact.trade_order_id = trade_order_id
            contact.trade_order_line_id = trade_order_line_id
            contact.seller_id = seller_id
            contact.timestamp = timestamp
            contact.log_details = kwargs
            contact.insert(ignore_permissions=True)
            sendorderagain_lazada(seller_id,contact.name)
            return contact
        


@frappe.whitelist()
def sendorderagain(shop_id,webhook_id):
    try:
        existing_record = frappe.get_doc("Marketplace Accounts", {"shop_id": shop_id})
    except frappe.DoesNotExistError:
        existing_record = None
    if existing_record:    
        log = frappe.get_doc("Marketplace Shopee Logs", {"name": webhook_id})
        params = {'ordersn' : log.order_id,'shop_id' : log.shop_id,'status' : log.status }
        url = existing_record.website_url+"/api/method/marketplace_integration.webhook.handle_webhook.push_shopee_webhook"
        response = requests.post(url,params)
        response = response.text    
        return response
    
@frappe.whitelist()
def sendorderagain_lazada(shop_id,webhook_id):
    try:
        existing_record = frappe.get_doc("Marketplace Accounts", {"shop_id": shop_id})
    except frappe.DoesNotExistError:
        existing_record = None
    if existing_record:    
        log = frappe.get_doc("Marketplace Lazada Logs", {"name": webhook_id})
        params = {'ordersn' : log.trade_order_id,'shop_id' : log.seller_id,'status' : log.order_status,'buyer_id' : log.buyer_id }
        url = existing_record.website_url+"/api/method/marketplace_integration.webhook.handle_webhook.push_shopee_lazada"
        response = requests.post(url,params)
        response = response.text    
        return response
    

