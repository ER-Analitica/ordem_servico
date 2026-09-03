"""Identificador do Candidato à Vaga pela série do doctype, não pelo e-mail.

O doctype já traz `HR-APP-.YYYY.-.#####` no campo `autoname`, no mesmo desenho
da Vaga de Trabalho (`HR-OPN-…`) e da Oferta de Emprego (`HR-OFF-…`). Essa série
nunca chegava a ser usada: o controlador do HRMS preenche o nome com o e-mail
antes que o Frappe olhe para ela.

O Frappe monta o nome nesta ordem (frappe/model/naming.py, set_new_name):
primeiro chama o `autoname` do controlador; **só se o nome continuar vazio**
aplica a série do doctype. Por isso aqui o `autoname` não faz nada — deixar o
nome em branco é o que devolve o comando para a série.

Sobrescrever a classe, em vez de editar o HRMS, mantém o app deles íntegro:
uma atualização do HRMS não desfaz esta mudança nem entra em conflito com ela.

O que se perde: o HRMS acrescentava um sufixo ao e-mail quando a mesma pessoa
se candidatava de novo (`fulano@x.com-1`), o que deixava a recandidatura
visível no próprio identificador. Com a série, isso passa a ser consultado
filtrando a lista pelo e-mail.
"""

from hrms.hr.doctype.job_applicant.job_applicant import JobApplicant


class OrdemServicoJobApplicant(JobApplicant):
    def autoname(self):
        # De propósito sem corpo: com o nome vazio, o Frappe aplica o
        # `HR-APP-.YYYY.-.#####` configurado no doctype.
        return
