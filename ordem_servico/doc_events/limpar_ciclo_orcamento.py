"""Vínculo removido na OS Interna: o ciclo comercial sai do Histórico.

O Histórico da OS é uma corrente — orçamento, pedido, nota de entrega, fatura e
pagamento — e os cinco são somente-leitura, escritos por quem os origina. Isso
deixava a OS sem saída quando o ciclo precisava recomeçar: o orçamento antigo
ficava preso no `quotation_name`, e com ele o botão "Gerar Orçamento" sumia para
sempre, já que a condição do botão exige esse campo vazio.

Aqui a regra é a mesma que o `obter_pedido_os_interna` já aplica ao Pedido de
Venda, estendida em dois pontos:

* passa a valer também para o **Orçamento** do fluxo antigo, que agora é
  editável justamente para permitir isso;
* limpa a corrente **inteira**. A rotina do pedido zerava só pedido e orçamento
  e deixava fatura, nota de entrega e pagamento do ciclo anterior — o Histórico
  ficava misturado e os filtros e relatórios não fechavam.

Com o Histórico livre o botão reaparece sozinho, e o orçamento novo reconstrói
os vínculos ao ser salvo, pelo `set_quotation_history` que já existe.

Nada é limpo enquanto houver Pedido de Venda vinculado: naquele caso o Histórico
é derivado do pedido por `historico_pedido`, e a limpeza seria desfeita no save
seguinte. Sai primeiro o vínculo, que é do técnico, e o resto vem junto.
"""

import frappe
from frappe.utils import now_datetime

# Tudo que pertence ao ciclo comercial. O orçamento encabeça porque é dele que
# os demais descendem.
CAMPOS_DO_CICLO = (
    ("quotation_name", "quotation_date", "Orçamento"),
    ("sales_order_name", "sales_order_date", "Pedido de Venda"),
    ("delivery_note_name", "delivery_note_date", "Nota de Entrega"),
    ("invoice_name", "invoice_date", "Nota Fiscal"),
    ("payment_entry_name", "payment_entry_date", "Pagamento"),
)

# Vínculos digitados pelo técnico. Apagar qualquer um deles libera o ciclo.
# A OS Externa usa um campo só, e não tem o par do fluxo antigo.
VINCULOS_DO_USUARIO = {
    "Ordem Servico Interna": ("has_quotation_link", "has_sales_order_link"),
    "Ordem Servico Externa": ("sales_order_reference",),
}

CAMPO_OBS = "obs_historico"


def _foi_removido(doc, anterior, campo):
    """O campo tinha valor no save anterior e ficou vazio nesta edição."""
    return bool((anterior.get(campo) or "").strip()) and not (doc.get(campo) or "").strip()


def limpar_ao_remover_vinculo(doc, method=None):
    """Gatilho no validate das duas OS."""
    anterior = doc.get_doc_before_save()
    if not anterior:
        return  # OS nova: não há ciclo anterior

    vinculos = VINCULOS_DO_USUARIO.get(doc.doctype, ())
    removidos_vinculo = [c for c in vinculos if _foi_removido(doc, anterior, c)]
    if not removidos_vinculo:
        return

    # O vínculo do pedido é do técnico e manda no Histórico enquanto existir.
    for campo in vinculos:
        if (doc.get(campo) or "").strip():
            return

    # A OS Externa não tem nota de entrega nem pagamento no Histórico.
    do_ciclo = [t for t in CAMPOS_DO_CICLO if doc.meta.has_field(t[0])]

    removidos = [
        "{}: {}".format(rotulo, doc.get(campo))
        for campo, _data, rotulo in do_ciclo
        if doc.get(campo)
    ]
    if not removidos:
        return  # o Histórico já estava vazio

    for campo, data, _rotulo in do_ciclo:
        doc.set(campo, None)
        doc.set(data, None)

    # O Check do fluxo antigo acompanha o Link que o técnico acabou de apagar,
    # senão ele sozinho continuaria escondendo o botão de gerar orçamento.
    if "has_quotation_link" in removidos_vinculo:
        doc.set("have_quotation", 0)

    carimbo = "[{}] Histórico liberado por {} para novo orçamento. Removido: {}.".format(
        now_datetime().strftime("%d/%m/%Y %H:%M"),
        frappe.session.user,
        "; ".join(removidos),
    )
    anterior_obs = (doc.get(CAMPO_OBS) or "").strip()
    doc.set(CAMPO_OBS, "{}\n{}".format(anterior_obs, carimbo).strip())
