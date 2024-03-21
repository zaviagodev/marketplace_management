# Copyright (c) 2023, Zaviago and contributors
# For license information, please see license.txt

import base64
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urlencode
import frappe
import requests
from frappe import _
from frappe.utils import cint, cstr, get_datetime
from pytz import timezone
import random
import webbrowser
import json
import hmac
import hashlib
import time
from marketplace_management.auth.base import *

class CreateMarketplaceClient:

    def start_connecting_shopee( self, app_key , app_secret,client_site):
        return self.createAuthRequest_shopee(app_key,app_secret,client_site)
    
    def start_connecting_lazada( self, app_key , app_secret,client_site):
            return self.createAuthRequest_lazada(app_key,app_secret,client_site)

    def createAuthRequest_lazada( self, app_key , app_secret,client_site):
        endpoint = "/api/method/marketplace_integration.auth.create_client.receive_code_from_lazada"
        return_url = client_site
        host = "https://auth.lazada.com"
        path = "/oauth/authorize"
        redirect_url = return_url+endpoint
        partner_id = app_key
        url = host + path + "?response_type=code&force_auth=true&redirect_uri=%s&client_id=%s" % (redirect_url,partner_id)
        return url
        
    def createAuthRequest_shopee( self, app_key , app_secret,client_site):
        endpoint = "/api/method/marketplace_integration.auth.create_client.receive_code_from_shopee"
        return_url = client_site
        timest = int(time.time())
        host = "https://partner.shopeemobile.com"
        path = "/api/v2/shop/auth_partner"
        redirect_url = return_url+endpoint
        partner_id = app_key
        tmp = app_secret
        partner_key = tmp.encode()
        tmp_base_string = "%s%s%s" % (partner_id, path, timest)
        base_string = tmp_base_string.encode()
        sign = hmac.new(partner_key, base_string, hashlib.sha256).hexdigest()
        ##generate api
        url = host + path + "?partner_id=%s&timestamp=%s&sign=%s&redirect=%s" % (partner_id, timest, sign, redirect_url)
        return url

@frappe.whitelist(allow_guest=True)
def redirect_to_auth_shopee(client_site):
    app_details = frappe.get_doc('Marketplace Management') 
    if( app_details.partner_id!='' and app_details.partner_key != '' and app_details.active_shopee ):
            connect = CreateMarketplaceClient()	
            url = connect.start_connecting_shopee ( app_details.partner_id,app_details.partner_key,client_site)
            if( url ):
                print (f"Redirecting to auth from function {url}")
                response_ = {'url':url}
                return response_
                exit() 	
    return   

@frappe.whitelist(allow_guest=True)
def redirect_to_auth_lazada(client_site):
    app_details = frappe.get_doc('Marketplace Management') 
    if( app_details.client_id !='' and app_details.client_secret != '' and app_details.active_lazada ):
            connect = CreateMarketplaceClient()	
            url = connect.start_connecting_lazada ( app_details.client_id,app_details.client_secret,client_site)
            if( url ):
                print (f"Redirecting to auth from function {url}")
                response_ = {'url':url}
                return response_
                exit() 	
    return 



@frappe.whitelist(allow_guest=True)
def code_to_token_auth_lazada(code):  
    app_details = frappe.get_doc('Marketplace Management') 
    app_key = app_details.client_id
    app_secret = app_details.client_secret


    client = LazopClient('https://api.lazada.co.th/rest', '${app_key}', '${app_secret}')
    request = LazopRequest('/auth/token/create')
    request.add_api_param('code', code)
    response = client.execute(request)

    return response.body



@frappe.whitelist(allow_guest=True)
def code_to_token_auth_shopee(code,shop_id,site_name):   
    if(code !='' and shop_id != ''):
        app_details = frappe.get_doc('Marketplace Management') 
        return get_token_shop_level(code,  app_details.partner_id, app_details.partner_key, shop_id,site_name)

def get_token_shop_level(code, partner_id, tmp_partner_key, shop_id,site_name):
    partner_id = int(partner_id)
    shop_id = int(shop_id)
    timest = int(time.time())
    
    host = "https://partner.shopeemobile.com"
    path = "/api/v2/auth/token/get"
    body = {"code": code, "shop_id": shop_id, "partner_id": partner_id}
    tmp_base_string = "%s%s%s" % (partner_id, path, timest)
    base_string = tmp_base_string.encode()
    partner_key = tmp_partner_key.encode()
    sign = hmac.new(partner_key, base_string, hashlib.sha256).hexdigest()
    url = host + path + "?partner_id=%s&timestamp=%s&sign=%s" % (partner_id, timest, sign)
    # print(url)
    headers = {"Content-Type": "application/json"}
    resp = requests.post(url, json=body, headers=headers)
    ret = json.loads(resp.content)
    access_token = ret.get("access_token")
    new_refresh_token = ret.get("refresh_token")
    
    if access_token:
        existing_record = frappe.get_doc("Marketplace Accounts", {"shop_id": shop_id})
        if existing_record:
            existing_record.website_url = site_name
            existing_record.save(ignore_permissions=True)
        else:
            contact = frappe.new_doc("Marketplace Accounts")
            contact.shop_id = shop_id
            contact.website_url = site_name
            contact.marketplace = "Shopee"
            contact.insert(ignore_permissions=True)

    return {"access_token": access_token, "new_refresh_token": new_refresh_token}