from __future__ import unicode_literals

import frappe

@frappe.whitelist()
def validate(self, method):
    if self.hash_orc != "":
        self.hash_orc = ""

        





   
        


       

