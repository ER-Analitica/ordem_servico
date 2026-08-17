"""Importação de certificados a partir de uma pasta única.

Os certificados chegam com o número da OS no início do nome do arquivo
(ex: `021962_01 - Bem Brasil.pdf` → `OS-21962`). Como as séries Interna e
Externa não repetem número, o número sozinho já diz para qual dos dois
doctypes o arquivo vai — por isso existe uma pasta só, e a distribuição é
automática.

O trabalho é dividido em duas etapas, e a razão é o custo: anexar é barato,
mas cada anexo dispara a leitura do PDF para extrair a rastreabilidade dos
padrões, que custa dezenas de milissegundos por arquivo.

`listar_pendentes` faz o reconhecimento inteiro numa chamada só — lê a pasta,
resolve a OS de cada arquivo e descarta o que já está anexado — usando
consultas em bloco, e não uma por arquivo. `processar_lote` recebe uma fatia
já resolvida e faz o trabalho pesado. A tela chama a primeira uma vez e a
segunda em fatias, o que dá o progresso ao lado sem sobrecarregar o servidor.
"""

import re

import frappe

DOCTYPES_PERMITIDOS = ("Ordem Servico Interna", "Ordem Servico Externa")

PASTA_CERTIFICADOS = "Home/Certificados"

# O número da OS no começo do nome do arquivo, sem os zeros à esquerda.
NUMERO_NO_NOME = re.compile(r"^0*(\d{3,6})")


@frappe.whitelist()
def anexar_certificado_forcado(doctype, name, file_url):
    """Anexa um certificado à OS (Interna ou Externa) sem rodar o validate().

    Usado pela importação em lote de certificados legados, cujas OS antigas
    não têm os dados obrigatórios (data de calibração, equipamento) exigidos
    pelas validações criadas posteriormente.
    """
    if doctype not in DOCTYPES_PERMITIDOS:
        frappe.throw("DocType inválido para anexo de certificado.")

    if not frappe.has_permission(doctype, "write", name):
        frappe.throw("Sem permissão para atualizar esta Ordem de Serviço.")

    valor_atual = frappe.db.get_value(doctype, name, "anexo_certificado")
    ja_anexado = bool(valor_atual and file_url in valor_atual)

    if ja_anexado:
        novo_valor = valor_atual
    else:
        novo_valor = f"{valor_atual}\n{file_url}" if valor_atual else file_url
        frappe.db.set_value(
            doctype,
            name,
            "anexo_certificado",
            novo_valor,
            update_modified=False,
        )
        # O set_value acima não invalida o cache do documento; sem isso a
        # extração leria o anexo_certificado antigo.
        frappe.clear_document_cache(doctype, name)

    # Extrai a rastreabilidade dos padrões. Roda quando o anexo é novo ou
    # quando a OS ainda não tem a tabela preenchida (permite reprocessar
    # certificados anexados antes desta funcionalidade existir).
    rastreabilidade = None
    tem_rastreabilidade = frappe.db.exists(
        "Rastreabilidade Padrao OS",
        {"parent": name, "parenttype": doctype, "parentfield": "rastreabilidade_padroes"},
    )
    if not ja_anexado or not tem_rastreabilidade:
        # Nunca deve quebrar o anexo — em caso de erro, apenas registra no log.
        try:
            from ordem_servico.doc_events.rastreabilidade_padroes import extrair_rastreabilidade

            rastreabilidade = extrair_rastreabilidade(doctype, name)
        except Exception:
            frappe.log_error(
                title="Falha na extração de rastreabilidade de padrões",
                message=frappe.get_traceback(),
            )

    return {"ja_anexado": ja_anexado, "valor": novo_valor, "rastreabilidade": rastreabilidade}


def _garantir_pasta():
    """Cria a pasta de certificados na primeira vez, se ainda não existir."""
    if frappe.db.exists("File", PASTA_CERTIFICADOS):
        return

    frappe.get_doc(
        {
            "doctype": "File",
            "file_name": "Certificados",
            "is_folder": 1,
            "folder": "Home",
        }
    ).insert(ignore_permissions=True)


def _resolver_os(numeros):
    """Descobre, para cada número de OS, em qual doctype ele existe.

    Duas consultas no total — uma por doctype — em vez de uma por arquivo.
    O `anexo_certificado` vem junto porque é ele que diz se o certificado já
    foi importado antes, e buscá-lo aqui evita uma segunda ida ao banco.
    """
    if not numeros:
        return {}

    nomes = [f"OS-{n}" for n in numeros]
    encontrados = {}

    for doctype in DOCTYPES_PERMITIDOS:
        linhas = frappe.get_all(
            doctype,
            filters={"name": ("in", nomes)},
            fields=["name", "anexo_certificado"],
            limit_page_length=0,
        )
        for linha in linhas:
            # O mesmo número existir nos dois doctypes não acontece hoje (as
            # séries não se cruzam), mas se acontecer é melhor avisar do que
            # escolher um lado por conta própria.
            if linha.name in encontrados:
                encontrados[linha.name] = None
                continue
            encontrados[linha.name] = {
                "doctype": doctype,
                "os_name": linha.name,
                "anexo_certificado": linha.anexo_certificado or "",
            }

    return encontrados


@frappe.whitelist()
def listar_pendentes():
    """Lê a pasta de certificados e devolve o que há para importar.

    Devolve só o que realmente dá trabalho: o que já está anexado sai da lista
    aqui, e é isso que mantém a importação leve quando a pasta acumula. Depois
    da primeira carga, clicar de novo só enxerga o que chegou desde então.
    """
    _garantir_pasta()

    arquivos = frappe.get_all(
        "File",
        filters={"folder": PASTA_CERTIFICADOS, "is_folder": 0},
        fields=["file_name", "file_url"],
        order_by="file_name asc",
        limit_page_length=0,
    )

    sem_numero = []
    por_numero = {}

    for arquivo in arquivos:
        achado = NUMERO_NO_NOME.match(arquivo.file_name or "")
        if not achado:
            sem_numero.append(arquivo.file_name)
            continue
        por_numero.setdefault(achado.group(1), []).append(arquivo)

    resolvidas = _resolver_os(list(por_numero))

    pendentes = []
    sem_os = []
    ambiguos = []
    ja_anexados = 0

    for numero, lista in por_numero.items():
        info = resolvidas.get(f"OS-{numero}", "ausente")

        for arquivo in lista:
            if info == "ausente":
                sem_os.append(arquivo.file_name)
            elif info is None:
                ambiguos.append(arquivo.file_name)
            elif arquivo.file_url and arquivo.file_url in info["anexo_certificado"]:
                ja_anexados += 1
            else:
                pendentes.append(
                    {
                        "file_name": arquivo.file_name,
                        "file_url": arquivo.file_url,
                        "doctype": info["doctype"],
                        "os_name": info["os_name"],
                    }
                )

    return {
        "pendentes": pendentes,
        "ja_anexados": ja_anexados,
        "sem_os": sem_os,
        "sem_numero": sem_numero,
        "ambiguos": ambiguos,
        "total_na_pasta": len(arquivos),
    }


@frappe.whitelist()
def processar_lote(itens):
    """Anexa uma fatia de certificados já resolvidos por `listar_pendentes`.

    Cada arquivo é isolado: um PDF corrompido ou uma OS sem permissão viram
    uma linha de erro no retorno, e os demais do lote seguem normalmente.
    """
    itens = frappe.parse_json(itens) or []
    resultados = []

    for item in itens:
        doctype = item.get("doctype")
        os_name = item.get("os_name")
        file_name = item.get("file_name")
        file_url = item.get("file_url")

        try:
            retorno = anexar_certificado_forcado(doctype, os_name, file_url)
            resultados.append(
                {
                    "file_name": file_name,
                    "file_url": file_url,
                    "os_name": os_name,
                    "ok": True,
                    "ja_anexado": retorno.get("ja_anexado"),
                }
            )
        except Exception as erro:
            # O lote inteiro seria perdido se a exceção subisse; aqui ela vira
            # um item com motivo, que a tela mostra no resumo final.
            resultados.append(
                {
                    "file_name": file_name,
                    "os_name": os_name,
                    "ok": False,
                    "motivo": str(erro),
                }
            )
            frappe.log_error(
                title="Falha ao importar certificado",
                message=frappe.get_traceback(),
            )

    return resultados
