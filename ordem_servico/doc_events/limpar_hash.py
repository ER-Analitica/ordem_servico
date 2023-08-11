import frappe

def validate(self, method):
    if self.os_interna_link != "":
        self.hash_orc = ""
