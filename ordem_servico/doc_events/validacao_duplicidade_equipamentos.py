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
    nivel = "bloqueio" (duplicata certa) ou "aviso" (parecido, revisar).

    Bloqueia quando a série já existe no cliente e o MODELO **ou** a MARCA
    coincidem — os dois são informações casadas, então um já caracteriza.

    A tag não entra em nenhum momento: as empresas repetem tag com frequência
    (inclusive preenchendo com "Não Especificado"), então tag repetida é
    situação normal e nunca deve alterar o resultado.

    O nome do equipamento também fica de fora: seria mais um campo podendo
    divergir e enfraquecer um bloqueio legítimo.
    """
    serie = normalizar(numero_serie)
    serie_real = not serie_e_generica(serie)

    # Sem número de série real não há como afirmar nada: nenhum alerta.
    if not serie_real:
        return []

    candidatos = frappe.db.sql(
        """
        SELECT name, customer, numero_serie, tag, descricao,
               modelo_equipamento, marca_equipamento
        FROM `tabEquipamentos`
        WHERE name != %(ignorar)s
          AND (customer = %(customer)s OR UPPER(TRIM(numero_serie)) = %(serie)s)
        """,
        {"ignorar": ignorar or "", "customer": customer, "serie": serie},
        as_dict=True,
    )

    resultados = []

    for cand in candidatos:
        cand_serie = normalizar(cand.numero_serie)
        if serie_e_generica(cand_serie) or cand_serie != serie:
            continue  # só interessa quem tem a MESMA série real

        mesmo_cliente = cand.customer == customer
        # Modelo e marca são informações casadas (um modelo pertence a uma
        # marca), então basta UM deles bater junto com a série para
        # caracterizar o mesmo equipamento. Campo vazio nunca conta como
        # coincidência.
        mesmo_modelo = bool(modelo) and cand.modelo_equipamento == modelo
        mesma_marca = bool(marca) and cand.marca_equipamento == marca
        modelo_ou_marca = mesmo_modelo or mesma_marca

        if not mesmo_cliente:
            nivel = "aviso"
            motivo = ("Mesma série cadastrada para o cliente <b>{}</b>. "
                      "Verifique se o cliente selecionado está correto.".format(cand.customer))
        elif modelo_ou_marca:
            nivel = "bloqueio"
            if mesmo_modelo and mesma_marca:
                coincidencia = "mesmo modelo e mesma marca"
            elif mesmo_modelo:
                coincidencia = "mesmo modelo"
            else:
                coincidencia = "mesma marca"
            motivo = "Mesma série e {} — é o mesmo equipamento.".format(coincidencia)
        else:
            nivel = "aviso"
            motivo = ("Mesma série neste cliente, porém modelo e marca diferentes. "
                      "Confirme se são equipamentos distintos de fabricantes diferentes.")

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

    # Mesma regra do cadastro: só o número de série indica duplicidade.
    # Tag e modelo repetem legitimamente entre equipamentos.
    if not serie or serie_e_generica(serie):
        return

    equipamentos = frappe.db.sql(
        """
        SELECT name, numero_serie
        FROM `tabEquipamentos`
        WHERE customer = %(customer)s
        """,
        {"customer": customer},
        as_dict=True,
    )

    avisos = []

    for eq in equipamentos:
        if normalizar(eq.numero_serie) != serie:
            continue

        link = get_link_to_form("Equipamentos", eq.name)
        avisos.append(
            "O número de série <b>{}</b> já possui cadastro: {}. "
            "Vincule o cadastro no campo 'Digite o número de série do "
            "equipamento' em vez de digitar manualmente.".format(
                doc.get("serie_number"), link
            )
        )

    if avisos:
        frappe.msgprint(
            "<br><br>".join(avisos[:8]),
            title="Equipamento já cadastrado para este cliente",
            indicator="orange",
        )
