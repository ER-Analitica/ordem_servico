from __future__ import unicode_literals
import frappe
from frappe.utils import flt

def validate(self, method):
    if self.__newname:
        self.nome = self.__newname

