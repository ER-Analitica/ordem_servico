import frappe


def on_submit(doc, method):
    if doc.opportunity:
        return

    customer = doc.party_name
    opportunity_name = None

    # 1. Verifica opportunity_name no cadastro do Cliente
    opportunity_name = frappe.db.get_value("Customer", customer, "opportunity_name")

    # 2. Busca por contact_person na Opportunity
    if not opportunity_name and doc.contact_person:
        ops = frappe.get_all(
            "Opportunity",
            filters={"contact_person": doc.contact_person},
            fields=["name"],
            order_by="creation desc",
            limit=1
        )
        if ops:
            opportunity_name = ops[0].name
            frappe.db.set_value("Customer", customer, "opportunity_name", opportunity_name)

    # 3. Busca por cliente (party_name) na Opportunity
    if not opportunity_name:
        ops = frappe.get_all(
            "Opportunity",
            filters={"opportunity_from": "Customer", "party_name": customer},
            fields=["name"],
            order_by="creation desc",
            limit=1
        )
        if ops:
            opportunity_name = ops[0].name
            frappe.db.set_value("Customer", customer, "opportunity_name", opportunity_name)

    if opportunity_name:
        frappe.db.set_value("Quotation", doc.name, "opportunity", opportunity_name)
        return

    # 4. Sem oportunidade — avisa vendedor
    email_vendedor = None
    nome_vendedor = None
    if doc.sales_team:
        sales_person = doc.sales_team[0].sales_person
        email_vendedor = frappe.db.get_value("Sales Person", sales_person, "email_do_vendedor")
        nome_vendedor = sales_person

    if email_vendedor:
        frappe.sendmail(
            recipients=[email_vendedor],
            subject=f"Orçamento sem oportunidade vinculada — {doc.name}",
            message=f"""<p>Olá {nome_vendedor},</p>
                <p>O orçamento <b>{doc.name}</b> do cliente <b>{customer}</b>
                não possui oportunidade vinculada.</p>
                <p>Por favor, crie a oportunidade e vincule no cadastro do cliente.</p>"""
        )
