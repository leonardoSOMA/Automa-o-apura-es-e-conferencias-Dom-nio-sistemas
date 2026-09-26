# -*- coding: utf-8 -*-
"""Fonte única do Catálogo de Auditorias Fiscais (regras AUD).

Gera: CSV (repositório), tabela Markdown (docs) e JSON (página de gestão / planilha).
"""
import csv
import json
import sys

GRUPOS = {
    "A": "Completude documental",
    "B": "Integridade de valores",
    "C": "Classificação fiscal",
    "D": "Apuração (recálculo-sombra)",
    "E": "Declarado × apurado × pago",
    "F": "Cadastro e situação fiscal",
    "G": "Analítica e indícios de risco",
}

# acao: Bloqueia = a competência não fecha com achado aberto; Alerta = fila do analista;
#       Oportunidade = gera lista de recuperação/planejamento.
REGRAS = [
    # ---------------- A. Completude documental ----------------
    dict(cod="AUD-A01", g="A", nome="NF-e de entrada não escrituradas",
         verifica="Toda NF-e emitida contra o CNPJ do cliente (Distribuição DF-e / manifestação) está escriturada na competência; lista faltantes.",
         fontes="XML (SEFAZ) × escrituração Domínio", regimes="Todos", tributos="ICMS, IPI, PIS/COFINS",
         risco="Alto", esforco="Baixo", fase=1, freq="Diária/mensal", acao="Bloqueia", ref=""),
    dict(cod="AUD-A02", g="A", nome="Notas de saída não escrituradas",
         verifica="NF-e/NFC-e autorizadas do cliente × escrituração: faltantes, extras e total por dia/série.",
         fontes="XML emitidos (autXML/ERP/captura) × escrituração", regimes="Todos", tributos="Todos",
         risco="Alto", esforco="Baixo", fase=1, freq="Mensal", acao="Bloqueia", ref=""),
    dict(cod="AUD-A03", g="A", nome="Canceladas, denegadas e inutilizadas",
         verifica="Nota cancelada escriturada como normal, cancelamento posterior ao lançamento e inutilizações sem registro de situação.",
         fontes="Eventos SEFAZ × escrituração", regimes="Todos", tributos="Todos",
         risco="Alto", esforco="Baixo", fase=1, freq="Mensal", acao="Bloqueia", ref=""),
    dict(cod="AUD-A04", g="A", nome="Quebra de sequência numérica",
         verifica="Saltos na numeração das notas emitidas (por modelo/série) sem inutilização correspondente.",
         fontes="XML emitidos × eventos de inutilização", regimes="Todos", tributos="Todos",
         risco="Médio", esforco="Baixo", fase=2, freq="Mensal", acao="Alerta", ref=""),
    dict(cod="AUD-A05", g="A", nome="Lançamento em duplicidade",
         verifica="Mesma chave de acesso (ou emitente + número + série) escriturada mais de uma vez.",
         fontes="Escrituração Domínio", regimes="Todos", tributos="Todos",
         risco="Alto", esforco="Baixo", fase=1, freq="Mensal", acao="Bloqueia", ref=""),
    dict(cod="AUD-A06", g="A", nome="NFS-e prestadas e tomadas não escrituradas",
         verifica="NFS-e do Ambiente Nacional (API do ADN por NSU, com certificado) e de prefeituras que não compartilham × escrituração de serviços, com retenções.",
         fontes="ADN / prefeituras × escrituração", regimes="Todos", tributos="ISS, IRRF, CSRF, INSS",
         risco="Alto", esforco="Médio", fase=1, freq="Mensal", acao="Bloqueia", ref="LC 214/2025, art. 62; Res. CGSN 191/2026"),
    dict(cod="AUD-A07", g="A", nome="CT-e tomados não escriturados",
         verifica="CT-e em que o cliente é tomador × escrituração; vínculo CT-e ↔ NF-e (frete FOB) e crédito do frete.",
         fontes="XML CT-e × escrituração", regimes="Todos", tributos="ICMS, PIS/COFINS",
         risco="Médio", esforco="Médio", fase=2, freq="Mensal", acao="Alerta", ref=""),
    dict(cod="AUD-A08", g="A", nome="Notas não reconhecidas pelo cliente",
         verifica="NF-e contra o CNPJ sem manifestação ou de fornecedor atípico: possível nota fria ou operação não realizada.",
         fontes="Distribuição DF-e × manifestação × histórico de fornecedores", regimes="Todos", tributos="ICMS, PIS/COFINS",
         risco="Médio", esforco="Médio", fase=3, freq="Semanal", acao="Alerta", ref=""),
    dict(cod="AUD-A09", g="A", nome="\"Sem movimento\" com documentos",
         verifica="Empresa marcada sem movimento ou com apuração zerada, mas com XML emitido/recebido na competência.",
         fontes="Cadastro mestre × XML × apuração", regimes="Todos", tributos="Todos",
         risco="Alto", esforco="Baixo", fase=1, freq="Mensal", acao="Bloqueia", ref=""),

    # ---------------- B. Integridade de valores ----------------
    dict(cod="AUD-B01", g="B", nome="Totais do documento divergentes",
         verifica="Valor contábil, BC e ICMS, BC e ICMS-ST, IPI, PIS, COFINS e FCP: XML × escrituração, por chave, com tolerância.",
         fontes="XML × escrituração (relatório/EFD C100-C190)", regimes="Todos", tributos="ICMS, ST, IPI, PIS/COFINS",
         risco="Alto", esforco="Baixo", fase=1, freq="Mensal", acao="Bloqueia", ref=""),
    dict(cod="AUD-B02", g="B", nome="Competência e datas",
         verifica="Data de entrada/saída fora da competência; notas extemporâneas lançadas sem controle.",
         fontes="XML × escrituração", regimes="Todos", tributos="Todos",
         risco="Médio", esforco="Baixo", fase=1, freq="Mensal", acao="Alerta", ref=""),
    dict(cod="AUD-B03", g="B", nome="Participante divergente",
         verifica="CNPJ, IE e UF do participante no cadastro da Domínio × XML (afeta CFOP interno/interestadual e DIFAL).",
         fontes="XML × cadastro de participantes", regimes="Todos", tributos="ICMS",
         risco="Médio", esforco="Baixo", fase=2, freq="Mensal", acao="Alerta", ref=""),
    dict(cod="AUD-B04", g="B", nome="Itens divergentes nas entradas",
         verifica="Quantidade, valor, NCM e CFOP por item: XML × registro de itens (EFD C170).",
         fontes="XML × EFD ICMS/IPI (C170)", regimes="LP, LR", tributos="ICMS, IPI, PIS/COFINS",
         risco="Médio", esforco="Médio", fase=3, freq="Mensal", acao="Alerta", ref=""),

    # ---------------- C. Classificação fiscal ----------------
    dict(cod="AUD-C01", g="C", nome="CFOP de entrada incoerente",
         verifica="CFOP escriturado × CFOP do emitente e finalidade (ex.: 5405→1403/1407; 6102→2102/2556/2551; 5910→1910; 5202→1202) e 1º dígito × UF.",
         fontes="XML × escrituração × tabela de conversão", regimes="Todos", tributos="ICMS, PIS/COFINS",
         risco="Alto", esforco="Médio", fase=1, freq="Mensal", acao="Bloqueia", ref="Convênio s/nº 1970 (CFOP)"),
    dict(cod="AUD-C02", g="C", nome="CFOP × CST/CSOSN incoerentes",
         verifica="Ex.: 5405 com CST 00; CST 40/41 com ICMS destacado; CST 60 sem CFOP de ST; CSOSN em empresa do regime normal e CST em optante do Simples.",
         fontes="XML × escrituração × cadastro mestre", regimes="Todos", tributos="ICMS",
         risco="Alto", esforco="Baixo", fase=1, freq="Mensal", acao="Bloqueia", ref=""),
    dict(cod="AUD-C03", g="C", nome="Crédito de ICMS indevido ou não aproveitado",
         verifica="Crédito em uso e consumo, ativo fora do CIAP (1/48), fornecedor do Simples sem pCredSN, entradas com ST/isentas; e créditos permitidos não aproveitados.",
         fontes="XML × escrituração × finalidade do item", regimes="LP, LR", tributos="ICMS",
         risco="Alto", esforco="Médio", fase=2, freq="Mensal", acao="Bloqueia", ref="LC 87/1996, arts. 20 e 33; LC 123/2006, art. 23"),
    dict(cod="AUD-C04", g="C", nome="Créditos de PIS/COFINS não cumulativos",
         verifica="CST 50–56 nas entradas × natureza do item (insumo, revenda, ativo); monofásicos e alíquota zero sem crédito; coerência com EFD-Contribuições.",
         fontes="XML × escrituração × EFD-Contribuições", regimes="LR", tributos="PIS/COFINS",
         risco="Alto", esforco="Alto", fase=3, freq="Mensal", acao="Alerta", ref="Leis 10.637/2002 e 10.833/2003 (até 12/2026; revisão retroativa 5 anos)"),
    dict(cod="AUD-C05", g="C", nome="Monofásicos de PIS/COFINS",
         verifica="NCM na lista de tributação concentrada × receita segregada no PGDAS-D (Simples) ou CST 04 nas saídas (LP/LR). Pagamento em duplicidade vira recuperação.",
         fontes="XML (NCM) × tabela de monofásicos × PGDAS-D/escrituração", regimes="SN, LP, LR", tributos="PIS/COFINS",
         risco="Alto", esforco="Médio", fase=1, freq="Mensal", acao="Oportunidade", ref="Leis 10.147/2000, 10.485/2002, 13.097/2015; LC 123/2006, art. 18 §4º-A"),
    dict(cod="AUD-C06", g="C", nome="ICMS-ST: produto sujeito × tratamento",
         verifica="NCM/CEST sujeito à ST na UF × CST/CSOSN e segregação de receita com ST no Simples; ST não retida em compra interestadual.",
         fontes="XML × tabela ST por UF × escrituração/PGDAS-D", regimes="Todos", tributos="ICMS-ST",
         risco="Alto", esforco="Alto", fase=3, freq="Mensal", acao="Alerta", ref="Convênios/protocolos ICMS e legislação da UF"),
    dict(cod="AUD-C07", g="C", nome="DIFAL",
         verifica="Compras interestaduais para uso/consumo/ativo e vendas a não contribuinte de outra UF: DIFAL calculado e recolhido.",
         fontes="XML × escrituração × guias", regimes="Todos", tributos="ICMS DIFAL/FCP",
         risco="Alto", esforco="Médio", fase=2, freq="Mensal", acao="Alerta", ref="EC 87/2015; LC 190/2022"),
    dict(cod="AUD-C08", g="C", nome="Alíquota de IPI × TIPI",
         verifica="Indústrias e equiparadas: alíquota por NCM × TIPI vigente; crédito de IPI nas entradas.",
         fontes="XML × TIPI × escrituração", regimes="LP, LR", tributos="IPI",
         risco="Médio", esforco="Médio", fase=3, freq="Mensal", acao="Alerta", ref="Decreto 11.158/2022 (TIPI) e alterações"),
    dict(cod="AUD-C09", g="C", nome="NCM inválido ou incompatível",
         verifica="NCM inexistente/expirado ou incompatível com a descrição do produto (triagem assistida por IA, decisão humana).",
         fontes="XML × tabela NCM × IA", regimes="Todos", tributos="Todos",
         risco="Médio", esforco="Médio", fase=3, freq="Mensal", acao="Alerta", ref=""),
    dict(cod="AUD-C10", g="C", nome="Antecipação de ICMS (conforme UF)",
         verifica="Entradas interestaduais sujeitas à antecipação parcial/total × guia recolhida.",
         fontes="XML × regra da UF × guias", regimes="Todos", tributos="ICMS",
         risco="Médio", esforco="Alto", fase=3, freq="Mensal", acao="Alerta", ref="Legislação da UF"),
    dict(cod="AUD-C11", g="C", nome="Reforma: grupos IBS/CBS nos documentos",
         verifica="CST IBS/CBS, cClassTrib, bases e alíquotas nos XML emitidos (obrigatório: NF-e/CT-e desde 03/08/2026, NFS-e desde 01/10/2026, Simples em 01/01/2027). A SEFAZ ainda não rejeita a falta do grupo: só a auditoria pega.",
         fontes="XML × tabelas da RTC × escrituração", regimes="Todos", tributos="CBS, IBS",
         risco="Alto", esforco="Médio", fase=1, freq="Mensal", acao="Alerta", ref="LC 214/2025; Ato Conjunto RFB/CGIBS 4/2026; NT 2025.002-RTC"),

    # ---------------- D. Apuração (recálculo-sombra) ----------------
    dict(cod="AUD-D01", g="D", nome="Simples Nacional: recálculo do DAS",
         verifica="Recalcula RBT12, anexo, faixa, alíquota efetiva e repartição, com segregações (ST, monofásico, exportação, ISS retido) × Domínio × PGDAS-D.",
         fontes="Receitas × tabelas LC 123 × Domínio × PGDAS-D", regimes="SN", tributos="DAS",
         risco="Alto", esforco="Médio", fase=1, freq="Mensal", acao="Bloqueia", ref="LC 123/2006; Res. CGSN 140/2018"),
    dict(cod="AUD-D02", g="D", nome="Simples Nacional: limite e sublimite",
         verifica="Receita acumulada e RBT12 × sublimite (R$ 3,6 mi) e limite (R$ 4,8 mi); alerta preventivo a partir de 80%.",
         fontes="Receitas 12 meses", regimes="SN", tributos="DAS, ICMS, ISS",
         risco="Alto", esforco="Baixo", fase=1, freq="Mensal", acao="Alerta", ref="LC 123/2006, arts. 3º e 13-A"),
    dict(cod="AUD-D03", g="D", nome="Simples Nacional: Fator R",
         verifica="Folha de 12 meses (salários, pró-labore, FGTS, CPP) ÷ RBT12 ≥ 28% define Anexo III × V; confere o anexo aplicado.",
         fontes="Domínio Folha × receitas × apuração", regimes="SN", tributos="DAS",
         risco="Alto", esforco="Médio", fase=2, freq="Mensal", acao="Bloqueia", ref="LC 123/2006, art. 18 (fator r)"),
    dict(cod="AUD-D04", g="D", nome="Lucro Presumido: IRPJ e CSLL",
         verifica="Base de presunção por atividade, acréscimo de 10% nos percentuais sobre a receita acima de R$ 5 mi/ano (R$ 1,25 mi/trimestre; IRPJ desde 01/2026, CSLL desde 04/2026), adicional de IRPJ e retenções compensadas.",
         fontes="Receitas por atividade × apuração Domínio × DCTFWeb/MIT", regimes="LP", tributos="IRPJ, CSLL",
         risco="Alto", esforco="Médio", fase=2, freq="Trimestral", acao="Bloqueia", ref="Lei 9.249/1995, arts. 15 e 20; LC 224/2025; IN RFB 2.305/2025 e 2.306/2026"),
    dict(cod="AUD-D05", g="D", nome="PIS/COFINS: débitos e créditos",
         verifica="Recalcula débitos (cumulativo 0,65%/3%; não cumulativo 1,65%/7,6%), exclusões e créditos × apuração × EFD-Contribuições, incluindo a redução de benefícios da LC 224/2025 (até 12/2026; depois, revisão retroativa).",
         fontes="Escrituração × EFD-Contribuições", regimes="LP, LR", tributos="PIS/COFINS",
         risco="Alto", esforco="Médio", fase=3, freq="Mensal", acao="Alerta", ref="Leis 9.718/1998, 10.637/2002 e 10.833/2003; LC 224/2025"),
    dict(cod="AUD-D06", g="D", nome="ICMS regime normal: apuração",
         verifica="Recalcula débitos e créditos pelos documentos (C190) × apuração da Domínio (E110) × declaração estadual; saldo credor transportado.",
         fontes="EFD ICMS/IPI × apuração × GIA/declaração da UF", regimes="LP, LR", tributos="ICMS",
         risco="Alto", esforco="Médio", fase=2, freq="Mensal", acao="Bloqueia", ref=""),
    dict(cod="AUD-D07", g="D", nome="ISS próprio e retido",
         verifica="ISS dos serviços prestados × alíquota e local de incidência; ISS retido por tomadores deduzido; ISS retido em serviços tomados recolhido.",
         fontes="NFS-e × escrituração × guias municipais", regimes="Todos", tributos="ISS",
         risco="Médio", esforco="Médio", fase=2, freq="Mensal", acao="Alerta", ref="LC 116/2003, arts. 3º e 6º"),
    dict(cod="AUD-D08", g="D", nome="Retenções federais e INSS",
         verifica="Serviços tomados e prestados com IRRF, CSRF (4,65%) e INSS (11%) × EFD-Reinf (R-2010/R-2020/R-4020) × DCTFWeb.",
         fontes="NFS-e × escrituração × EFD-Reinf × DCTFWeb", regimes="Todos", tributos="IRRF, CSRF, INSS",
         risco="Alto", esforco="Médio", fase=2, freq="Mensal", acao="Bloqueia", ref="Lei 10.833/2003, art. 30; Lei 8.212/1991, art. 31"),
    dict(cod="AUD-D09", g="D", nome="Carga tributária fora do padrão",
         verifica="Carga efetiva do mês (tributos ÷ receita) × média de 12 meses e faixa esperada do segmento.",
         fontes="Apurações × receitas (histórico)", regimes="Todos", tributos="Todos",
         risco="Médio", esforco="Baixo", fase=3, freq="Mensal", acao="Alerta", ref=""),
    dict(cod="AUD-D10", g="D", nome="Lucros e dividendos acima de R$ 50 mil/mês",
         verifica="Pagamentos de lucros à mesma pessoa física acima de R$ 50 mil no mês: IRRF de 10% retido × EFD-Reinf (R-4010) × DCTFWeb. Interface com contábil/DP.",
         fontes="Distribuições (contábil) × EFD-Reinf × DCTFWeb", regimes="Todos", tributos="IRRF",
         risco="Alto", esforco="Baixo", fase=2, freq="Mensal", acao="Alerta", ref="Lei 15.270/2025; NT EFD-Reinf 02/2026"),

    # ---------------- E. Declarado × apurado × pago ----------------
    dict(cod="AUD-E01", g="E", nome="Apuração × declaração transmitida",
         verifica="Valores da Domínio × PGDAS-D, DCTFWeb/MIT, EFD-Contribuições, EFD ICMS/IPI e declarações estaduais/municipais.",
         fontes="Domínio × Integra Contador × recibos", regimes="Todos", tributos="Todos",
         risco="Alto", esforco="Médio", fase=2, freq="Mensal", acao="Bloqueia", ref=""),
    dict(cod="AUD-E02", g="E", nome="Guia emitida × guia paga",
         verifica="DAS, DARF e guias estaduais/municipais emitidas × pagamentos localizados; aviso ao cliente antes do vencimento.",
         fontes="Guias × consulta de pagamentos (e-CAC) × conta corrente da UF", regimes="Todos", tributos="Todos",
         risco="Alto", esforco="Médio", fase=2, freq="Mensal", acao="Alerta", ref=""),
    dict(cod="AUD-E03", g="E", nome="Obrigações entregues no prazo",
         verifica="Matriz de obrigações de cada empresa × recibos de entrega; alerta 5 dias antes do vencimento.",
         fontes="Cadastro mestre × recibos", regimes="Todos", tributos="Todos",
         risco="Alto", esforco="Baixo", fase=2, freq="Diária", acao="Alerta", ref=""),
    dict(cod="AUD-E04", g="E", nome="Parcelamentos em dia",
         verifica="Parcelas emitidas e pagas (Simples, federais e estaduais); risco de rescisão.",
         fontes="Integra Contador (parcelamentos) × pagamentos", regimes="Todos", tributos="Todos",
         risco="Médio", esforco="Médio", fase=3, freq="Mensal", acao="Alerta", ref=""),
    dict(cod="AUD-E05", g="E", nome="CBS: apuração assistida × escrituração",
         verifica="A partir de 2027, débitos e créditos da apuração assistida da Plataforma CBS (APIs da Receita) × escrituração da Domínio × hub.",
         fontes="APIs da apuração da CBS × Domínio × hub", regimes="LP, LR", tributos="CBS (IBS depois)",
         risco="Alto", esforco="Médio", fase=2, freq="Mensal", acao="Bloqueia", ref="LC 214/2025"),

    # ---------------- F. Cadastro e situação fiscal ----------------
    dict(cod="AUD-F01", g="F", nome="Regime tributário e CNAE",
         verifica="Regime cadastrado na Domínio × situação na Receita (optante do Simples/SIMEI) e opção semestral pelo IBS/CBS fora do DAS (a partir de 2027); CNAEs × atividades escrituradas e anexo usado.",
         fontes="Cadastro Domínio × consulta Receita", regimes="Todos", tributos="Todos",
         risco="Alto", esforco="Baixo", fase=1, freq="Mensal", acao="Bloqueia", ref=""),
    dict(cod="AUD-F02", g="F", nome="Certificados e procurações a vencer",
         verifica="Validade dos certificados A1 (clientes e escritório), procurações eletrônicas e acessos estaduais: alertas em 30, 15 e 5 dias.",
         fontes="Cofre de certificados × cadastro mestre", regimes="Todos", tributos="—",
         risco="Alto", esforco="Baixo", fase=1, freq="Diária", acao="Alerta", ref=""),
    dict(cod="AUD-F03", g="F", nome="Situação fiscal e caixa postal",
         verifica="Pendências no relatório de situação fiscal, mensagens da Caixa Postal do e-CAC e DTE-SN, domicílios eletrônicos estaduais, termos de exclusão do Simples.",
         fontes="Integra Contador × portais da UF", regimes="Todos", tributos="Todos",
         risco="Alto", esforco="Médio", fase=2, freq="Semanal", acao="Alerta", ref=""),
    dict(cod="AUD-F04", g="F", nome="IE e situação de fornecedores",
         verifica="IE do cliente ativa e fornecedores relevantes inaptos/baixados (crédito glosável).",
         fontes="Cadastro × consulta de contribuintes (CCC/SINTEGRA)", regimes="LP, LR", tributos="ICMS",
         risco="Médio", esforco="Médio", fase=3, freq="Mensal", acao="Alerta", ref=""),

    # ---------------- G. Analítica e indícios de risco ----------------
    dict(cod="AUD-G01", g="G", nome="Variação atípica de receitas e compras",
         verifica="Variação do mês × média de 12 meses fora da faixa; queda brusca de faturamento; compras sem vendas no mês.",
         fontes="Histórico do hub de dados", regimes="Todos", tributos="Todos",
         risco="Médio", esforco="Baixo", fase=3, freq="Mensal", acao="Alerta", ref=""),
    dict(cod="AUD-G02", g="G", nome="Compras incompatíveis com receitas",
         verifica="Entradas maiores que saídas de forma recorrente no comércio (indício de omissão de receita ou estoque inflado).",
         fontes="Histórico do hub de dados", regimes="Todos", tributos="Todos",
         risco="Médio", esforco="Baixo", fase=3, freq="Trimestral", acao="Alerta", ref=""),
    dict(cod="AUD-G03", g="G", nome="Fiscal × contábil",
         verifica="Faturamento do fiscal × receitas contábeis; tributos apurados × contas de tributos a recolher (quando expandir para o contábil).",
         fontes="Escrita Fiscal × Contabilidade", regimes="Todos", tributos="Todos",
         risco="Médio", esforco="Médio", fase=4, freq="Mensal", acao="Alerta", ref=""),
]

CAMPOS = ["cod", "grupo", "nome", "verifica", "fontes", "regimes", "tributos",
          "risco", "esforco", "fase", "freq", "acao", "ref"]

PESO = {"Alto": 3, "Médio": 2, "Baixo": 1}


def enriquecer():
    out = []
    for r in REGRAS:
        d = dict(r)
        d["grupo"] = f"{r['g']}. {GRUPOS[r['g']]}"
        # prioridade = risco (1-3) × 2 + (4 - esforço) -> 3..9 ; quanto maior, antes
        d["prioridade"] = PESO[r["risco"]] * 2 + (4 - PESO[r["esforco"]])
        out.append(d)
    return out


def main(saida_csv, saida_json, saida_md):
    regras = enriquecer()
    cods = [r["cod"] for r in regras]
    assert len(cods) == len(set(cods)), "código duplicado"

    with open(saida_csv, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["Código", "Grupo", "Regra", "O que verifica", "Fontes cruzadas", "Regimes",
                    "Tributos", "Risco", "Esforço", "Fase", "Frequência", "Ação", "Referência",
                    "Prioridade (3-9)"])
        for r in regras:
            w.writerow([r["cod"], r["grupo"], r["nome"], r["verifica"], r["fontes"], r["regimes"],
                        r["tributos"], r["risco"], r["esforco"], r["fase"], r["freq"], r["acao"],
                        r["ref"], r["prioridade"]])

    with open(saida_json, "w", encoding="utf-8") as f:
        json.dump({"grupos": GRUPOS, "regras": regras}, f, ensure_ascii=False, indent=1)

    with open(saida_md, "w", encoding="utf-8") as f:
        for letra, nome in GRUPOS.items():
            f.write(f"\n### {letra}. {nome}\n\n")
            f.write("| Código | Regra | O que verifica | Fontes cruzadas | Regimes | Risco | Esforço | Fase | Ação |\n")
            f.write("|---|---|---|---|---|---|---|---|---|\n")
            for r in regras:
                if r["g"] != letra:
                    continue
                verifica = r["verifica"] + (f" _Ref.: {r['ref']}._" if r["ref"] else "")
                f.write(f"| {r['cod']} | {r['nome']} | {verifica} | {r['fontes']} | {r['regimes']} | "
                        f"{r['risco']} | {r['esforco']} | {r['fase']} | {r['acao']} |\n")

    por_fase = {}
    for r in regras:
        por_fase[r["fase"]] = por_fase.get(r["fase"], 0) + 1
    print("total", len(regras), "por fase", dict(sorted(por_fase.items())))


if __name__ == "__main__":
    main(*sys.argv[1:4])
