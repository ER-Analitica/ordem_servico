import re
import unicodedata

import frappe
from frappe.utils import get_link_to_form

# Valores digitados quando o equipamento não possui número de série.
# São tratados como "sem série" — a comparação passa a usar os demais campos.
# A lista é comparada após normalizar() (maiúsculas, sem acentos).
SERIES_GENERICAS = {
    "", "S/N", "SN", "S N", "NA", "N/A", "N A",
    "0", "00", "000", "X", "XX", "XXX",
    "SEM NUMERO", "SEM SERIE",
    "NAO ESPECIFICADO",
    "NAO INFORMADO", "NAO POSSUI",
    "SEM", "NONE", "NULL", "NIL",
}


def normalizar(valor):
    if not valor:
        return ""
    valor = str(valor).strip().upper()
    # Remove acentos (inclusive em forma Unicode decomposta vinda do banco)
    valor = "".join(
        c for c in unicodedata.normalize("NFKD", valor)
        if not unicodedata.combining(c)
    )
    return re.sub(r"\s+", " ", valor)


def serie_e_generica(serie_normalizada):
    if serie_normalizada in SERIES_GENERICAS:
        return True
    # Sem nenhuma letra ou número (ex: "-", "...", "//")
    if not re.search(r"[A-Z0-9]", serie_normalizada):
        return True
    return False


def buscar_similares(customer, numero_serie="", tag="", descricao="",
                     modelo="", marca="", ignorar=None):
    """Retorna equipamentos possivelmente duplicados, cada um com:
    nivel = "bloqueio" (duplicata certa) ou "aviso" (parecido, revisar)."""
    serie = normalizar(numero_serie)
    tag_n = normalizar(tag)
    serie_real = not serie_e_generica(serie)

    condicao_cliente = "customer = %(customer)s"
    if serie_real:
        # Inclui outros clientes com a mesma série real
        condicao_cliente = "(customer = %(customer)s OR UPPER(TRIM(numero_serie)) = %(serie)s)"

    candidatos = frappe.db.sql(
        """
        SELECT name, customer, numero_serie, tag, descricao,
               modelo_equipamento, marca_equipamento
        FROM `tabEquipamentos`
        WHERE name != %(ignorar)s AND {}
        """.format(condicao_cliente),
        {"ignorar": ignorar or "", "customer": customer, "serie": serie},
        as_dict=True,
    )

    resultados = []

    for cand in candidatos:
        cand_serie = normalizar(cand.numero_serie)
        cand_serie_real = not serie_e_generica(cand_serie)
        mesmo_cliente = cand.customer == customer
        mesma_serie_real = serie_real and cand_serie_real and cand_serie == serie
        mesmo_conjunto = (
            cand.descricao == descricao
            and cand.modelo_equipamento == modelo
            and cand.marca_equipamento == marca
        )

        mesma_tag = normalizar(cand.tag) == tag_n

        nivel = None
        motivo = ""

        if mesmo_cliente and mesma_serie_real and mesmo_conjunto and mesma_tag:
            nivel = "bloqueio"
            motivo = "Mesma série, mesmo equipamento, modelo, marca e tag — é o mesmo equipamento."
        elif mesmo_cliente and mesma_serie_real and mesmo_conjunto:
            nivel = "aviso"
            motivo = ("Mesma série, equipamento, modelo e marca, porém tag diferente. "
                      "Verifique se é o mesmo equipamento antes de salvar.")
        elif mesmo_cliente and mesma_serie_real:
            nivel = "aviso"
            motivo = ("Mesma série neste cliente, porém equipamento/modelo/marca diferentes. "
                      "Confirme se são equipamentos distintos de fabricantes diferentes.")
        elif (mesmo_cliente and not serie_real and not cand_serie_real
              and mesmo_conjunto and normalizar(cand.tag) == tag_n):
            nivel = "bloqueio"
            motivo = "Idêntico em tudo (equipamento, modelo, marca e tag), ambos sem série real."
        elif mesmo_cliente and mesmo_conjunto and not (serie_real and cand_serie_real):
            nivel = "aviso"
            motivo = "Mesmo equipamento, modelo e marca — sem série para diferenciar."
        elif mesmo_cliente and tag_n and normalizar(cand.tag) == tag_n:
            nivel = "aviso"
            motivo = "A tag já está em uso em outro equipamento deste cliente."
        elif not mesmo_cliente and mesma_serie_real:
            nivel = "aviso"
            motivo = ("Mesma série cadastrada para o cliente <b>{}</b>. "
                      "Verifique se o cliente selecionado está correto.".format(cand.customer))

        if nivel:
            resultados.append({
                "name": cand.name,
                "customer": cand.customer,
                "numero_serie": cand.numero_serie,
                "tag": cand.tag,
                "descricao": cand.descricao,
                "modelo_equipamento": cand.modelo_equipamento,
                "marca_equipamento": cand.marca_equipamento,
                "nivel": nivel,
                "motivo": motivo,
            })

    # Bloqueios primeiro, limita avisos para não poluir a tela
    resultados.sort(key=lambda r: 0 if r["nivel"] == "bloqueio" else 1)
    return resultados[:8]


@frappe.whitelist()
def verificar_duplicidade(customer, numero_serie="", tag="", descricao="",
                          modelo="", marca="", ignorar=None):
    """Chamada pelo JS do formulário para alertar em tempo real, antes de salvar."""
    if not customer:
        return []
    return buscar_similares(customer, numero_serie, tag, descricao, modelo, marca, ignorar)


CAMPOS_EDITAVEIS_EQUIPAMENTO = (
    "numero_serie", "descricao", "modelo_equipamento",
    "marca_equipamento", "tipo_equipamento", "tag", "capacidade",
    "grandeza", "pontos_calibracao", "criterios_aceitacao",
)


@frappe.whitelist()
def atualizar_equipamento(name, valores):
    """Atualiza o cadastro de Equipamentos a partir do popup nas OS.
    Passa pelo validate — as regras de duplicidade se aplicam."""
    import json

    if isinstance(valores, str):
        valores = json.loads(valores)

    doc = frappe.get_doc("Equipamentos", name)
    for campo in CAMPOS_EDITAVEIS_EQUIPAMENTO:
        if campo in valores:
            doc.set(campo, valores.get(campo))
    doc.save()

    return {campo: doc.get(campo) for campo in CAMPOS_EDITAVEIS_EQUIPAMENTO}


def _formatar_item(m):
    link = get_link_to_form("Equipamentos", m["name"])
    return (
        "{} — {} | Modelo: {} | Marca: {} | Série: {} | Tag: {}<br><i>{}</i>".format(
            link, m["descricao"] or "—", m["modelo_equipamento"] or "—",
            m["marca_equipamento"] or "—", m["numero_serie"] or "—",
            m["tag"] or "—", m["motivo"],
        )
    )


def validar_duplicidade_equipamento(doc, method=None):
    """Validate do doctype Equipamentos — bloqueia duplicata certa e avisa nas parecidas."""
    matches = buscar_similares(
        doc.customer, doc.numero_serie, doc.tag, doc.descricao,
        doc.modelo_equipamento, doc.marca_equipamento, ignorar=doc.name,
    )

    bloqueios = [m for m in matches if m["nivel"] == "bloqueio"]
    avisos = [m for m in matches if m["nivel"] == "aviso"]

    if bloqueios:
        frappe.throw(
            "Este equipamento já possui cadastro. Utilize o registro existente:"
            "<br><br>" + "<br><br>".join(_formatar_item(m) for m in bloqueios),
            title="Equipamento duplicado",
        )

    if avisos:
        frappe.msgprint(
            "<br><br>".join(_formatar_item(m) for m in avisos),
            title="Possível duplicidade de equipamento",
            indicator="orange",
        )


def validar_equipamento_os(doc, method=None):
    """Validate das OS Interna/Externa — avisa quando o equipamento digitado
    manualmente já possui cadastro em Equipamentos."""
    if doc.get("informe_numero_serie"):
        # Equipamento vinculado ao cadastro — caminho correto
        return

    customer = doc.get("customer")
    if not customer:
        return

    serie = normalizar(doc.get("serie_number"))
    tag = normalizar(doc.get("equipment_tag"))
    descricao = normalizar(doc.get("equipment_description"))
    modelo = normalizar(doc.get("equipment_model"))

    if not (serie or tag or (descricao and modelo)):
        return

    equipamentos = frappe.db.sql(
        """
        SELECT name, numero_serie, tag, descricao, modelo_equipamento, marca_equipamento
        FROM `tabEquipamentos`
        WHERE customer = %(customer)s
        """,
        {"customer": customer},
        as_dict=True,
    )

    avisos = []

    for eq in equipamentos:
        link = get_link_to_form("Equipamentos", eq.name)

        if serie and not serie_e_generica(serie) and normalizar(eq.numero_serie) == serie:
            avisos.append(
                "O número de série <b>{}</b> já possui cadastro: {}. "
                "Vincule o cadastro no campo 'Digite o número de série do "
                "equipamento' em vez de digitar manualmente.".format(
                    doc.get("serie_number"), link
                )
            )
            continue

        if tag and normalizar(eq.tag) == tag:
            avisos.append(
                "A tag <b>{}</b> já possui cadastro: {} (Série: {}). "
                "Verifique se não é o mesmo equipamento.".format(
                    doc.get("equipment_tag"), link, eq.numero_serie or "—"
                )
            )
            continue

        if (
            descricao and modelo
            and normalizar(eq.descricao) == descricao
            and normalizar(eq.modelo_equipamento) == modelo
        ):
            avisos.append(
                "Equipamento parecido já cadastrado para este cliente: {} "
                "(Série: {} | Tag: {}).".format(
                    link, eq.numero_serie or "—", eq.tag or "—"
                )
            )

    if avisos:
        frappe.msgprint(
            "<br><br>".join(avisos[:8]),
            title="Equipamento já cadastrado para este cliente",
            indicator="orange",
        )
