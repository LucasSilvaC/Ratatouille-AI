"""Avaliação da Nutripédia com o conjunto de perguntas em perguntas.json.

Compara a busca vetorial com a híbrida e guarda, para cada pergunta, os trechos
encontrados, a resposta do modelo e as verificações.

Uso (de packages/agents, com o pacote instalado com o extra `rag`):
    python evals/nutripedia/avaliar.py              avaliação completa (chama o Gemini)
    python evals/nutripedia/avaliar.py --so-busca   só a taxa de acerto da busca, sem chamar o Gemini

Gera em evals/nutripedia/resultados/ (fora do Git):
    respostas.json   tudo o que foi medido (também serve para retomar se a execução parar)
    relatorio.html   relatório para ler no navegador
    respostas.csv    planilha com colunas vazias para a sua própria avaliação
"""

import csv
import html
import json
import sys
import time
from pathlib import Path

from ratatouille_agents.tools.nutripedia import K, GeradorGemini, criar_nutripedia, responder
from ratatouille_agents.tools.nutripedia.config import obter_chave_gemini

AQUI = Path(__file__).resolve().parent
PASTA = AQUI / "resultados"
ARQ_JSON = PASTA / "respostas.json"
PAUSA = 4  # segundos entre chamadas ao Gemini, por causa do limite da chave gratuita
# Muitas chamadas seguidas: os modelos "lite" respondem mais rápido e têm cota maior na chave gratuita.
MODELOS_AVALIACAO = ("gemini-3.5-flash-lite", "gemini-3.1-flash-lite", "gemini-3.5-flash")

with open(AQUI / "perguntas.json", encoding="utf-8") as f:
    PERGUNTAS = json.load(f)

BUSCAS = {"vetorial": "buscar_vetorial", "palavra-chave": "buscar_palavras", "híbrida": "buscar_hibrida"}
BUSCAS_COM_RESPOSTA = {"vetorial": "vetorial", "híbrida": "hibrida"}


def acertou_busca(caso, resultados):
    return any(
        caso["arquivo"].lower() in r.trecho.arquivo.lower() and caso["termo"].lower() in r.trecho.texto.lower()
        for r in resultados
    )


def julgar_fidelidade(gerador, resposta):
    contexto = "\n\n".join(r.trecho.texto for r in resposta.fontes)
    prompt = f"""Você é um avaliador rigoroso. Leia os TRECHOS e a RESPOSTA.
Todas as afirmações da RESPOSTA estão apoiadas nos TRECHOS?
Responda com uma única palavra: SIM ou NAO.

TRECHOS:
{contexto}

RESPOSTA:
{resposta.texto}"""
    veredito, _ = gerador.gerar(prompt)
    return veredito.strip().upper().startswith("SIM")


def avaliar_caso(nutripedia, gerador, caso, busca):
    resposta = responder(nutripedia, gerador, caso["pergunta"], K, busca=busca)
    time.sleep(PAUSA)
    fiel = None
    if not resposta.recusou:
        fiel = julgar_fidelidade(gerador, resposta)
        time.sleep(PAUSA)
    return {
        "busca_acertou": acertou_busca(caso, resposta.fontes) if caso["arquivo"] else None,
        "fontes": [
            {
                "arquivo": r.trecho.arquivo,
                "pagina": r.trecho.pagina,
                "texto": r.trecho.texto,
                "similaridade": round(r.similaridade, 3),
            }
            for r in resposta.fontes
        ],
        "resposta": resposta.texto,
        "modelo": resposta.modelo,
        "recusou": resposta.recusou,
        "citou": resposta.citou_fonte,
        "fiel": fiel,
    }


def taxas_de_busca(nutripedia):
    dentro = [c for c in PERGUNTAS if c["arquivo"]]
    tabela = {}
    for nome, metodo in BUSCAS.items():
        buscar = getattr(nutripedia, metodo)
        tabela[nome] = [sum(acertou_busca(c, buscar(c["pergunta"], k)) for c in dentro) / len(dentro) for k in (1, 3, 5)]
    return tabela


def resumo_respostas(resultados, nome):
    dentro = [r[nome] for r in resultados if r["caso"]["arquivo"]]
    fora = [r[nome] for r in resultados if not r["caso"]["arquivo"]]
    respondidas = [r for r in dentro if not r["recusou"]]
    return {
        "dentro": len(dentro),
        "respondidas": len(respondidas),
        "citou": sum(r["citou"] for r in respondidas),
        "fiel": sum(bool(r["fiel"]) for r in respondidas),
        "fora": len(fora),
        "recusou_fora": sum(r["recusou"] for r in fora),
    }


# ---------- Relatórios ----------

SIM_NAO = {True: "sim", False: "não", None: "-"}


def gerar_csv(resultados):
    with open(PASTA / "respostas.csv", "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["numero", "tipo", "pergunta", "busca", "busca_acertou", "respondeu", "citou_fonte",
                    "fiel_segundo_o_juiz", "resposta", "fontes", "minha_avaliacao", "meu_comentario"])
        for i, r in enumerate(resultados, start=1):
            for nome in BUSCAS_COM_RESPOSTA:
                d = r[nome]
                fontes = " | ".join(f"[{n}] {x['arquivo']} p.{x['pagina']} (sim. {x['similaridade']:.2f})"
                                    for n, x in enumerate(d["fontes"], start=1))
                w.writerow([i, "dentro" if r["caso"]["arquivo"] else "fora", r["caso"]["pergunta"], nome,
                            SIM_NAO[d["busca_acertou"]], "não" if d["recusou"] else "sim",
                            "sim" if d["citou"] else "não", SIM_NAO[d["fiel"]], d["resposta"], fontes, "", ""])


ESTILO = """
:root{--fundo:#f6f7f9;--cartao:#fff;--texto:#1c2330;--suave:#5b6577;--borda:#dfe3ea;--ok:#1a7f4b;--okf:#e3f4ea;--ruim:#b3261e;--ruimf:#fbe9e7;--neutro:#5b6577;--neutrof:#eceff4;--destaque:#1f5fbf}
@media (prefers-color-scheme: dark){:root{--fundo:#12151b;--cartao:#1b2029;--texto:#e7eaf0;--suave:#9aa5b8;--borda:#2e3542;--ok:#6fd39b;--okf:#173526;--ruim:#ff9b93;--ruimf:#40201d;--neutro:#9aa5b8;--neutrof:#262c37;--destaque:#8ab4ff}}
*{box-sizing:border-box}body{margin:0;background:var(--fundo);color:var(--texto);font:16px/1.55 system-ui,-apple-system,"Segoe UI",sans-serif}
main{max-width:1000px;margin:0 auto;padding:24px 16px 64px}h1{font-size:1.7rem;margin:0 0 4px}h2{font-size:1.25rem;margin:36px 0 10px}
p.sub{color:var(--suave);margin:0 0 8px}table{border-collapse:collapse;width:100%;background:var(--cartao);border:1px solid var(--borda)}
th,td{padding:8px 12px;border-bottom:1px solid var(--borda);text-align:left;font-variant-numeric:tabular-nums}th{font-size:.85rem;color:var(--suave)}
.melhor{font-weight:700;color:var(--destaque)}.rolagem{overflow-x:auto}
.caso{background:var(--cartao);border:1px solid var(--borda);border-radius:10px;padding:16px;margin:14px 0}
.caso h3{margin:0 0 4px;font-size:1.05rem}.meta{color:var(--suave);font-size:.85rem;margin-bottom:10px}
.colunas{display:grid;grid-template-columns:1fr 1fr;gap:14px}@media (max-width:760px){.colunas{grid-template-columns:1fr}}
.lado{border:1px solid var(--borda);border-radius:8px;padding:12px;min-width:0}.lado h4{margin:0 0 6px;font-size:.95rem}
.selo{display:inline-block;font-size:.75rem;padding:2px 8px;border-radius:999px;margin:0 4px 4px 0}
.ok{background:var(--okf);color:var(--ok)}.ruim{background:var(--ruimf);color:var(--ruim)}.neutro{background:var(--neutrof);color:var(--neutro)}
.resposta{white-space:pre-wrap;margin:8px 0;overflow-wrap:anywhere}summary{cursor:pointer;color:var(--destaque);font-size:.88rem}
.fonte{font-size:.85rem;border-top:1px solid var(--borda);padding:6px 0;overflow-wrap:anywhere}.trecho{color:var(--suave)}
"""


def selo(texto, cor):
    return f'<span class="selo {cor}">{html.escape(texto)}</span>'


def gerar_html(resultados, tabela_busca):
    e = html.escape
    n_dentro = sum(1 for r in resultados if r["caso"]["arquivo"])
    partes = [
        f'<!doctype html><html lang="pt-BR"><head><meta charset="utf-8">'
        f'<meta name="viewport" content="width=device-width, initial-scale=1">'
        f"<title>Avaliação da Nutripédia</title><style>{ESTILO}</style></head><body><main>"
        f"<h1>Avaliação da Nutripédia</h1>"
        f'<p class="sub">{n_dentro} perguntas com resposta na bibliografia e {len(resultados) - n_dentro} fora dela. '
        f'{K} trechos por pergunta. Gerado em {time.strftime("%d/%m/%Y %H:%M")}.</p>',
        "<h2>1. A busca encontra o trecho certo?</h2>"
        '<p class="sub">Acerto: entre os k trechos devolvidos, há um do arquivo esperado que contém o termo esperado.</p>'
        '<div class="rolagem"><table><tr><th>Busca</th><th>k=1</th><th>k=3</th><th>k=5</th></tr>',
    ]
    maiores = [max(t[j] for t in tabela_busca.values()) for j in range(3)]
    for nome, taxas in tabela_busca.items():
        celulas = "".join(f'<td class="{"melhor" if t == maiores[j] else ""}">{t:.0%}</td>' for j, t in enumerate(taxas))
        partes.append(f"<tr><td>{e(nome.capitalize())}</td>{celulas}</tr>")
    partes.append("</table></div>")

    rv, rh = resumo_respostas(resultados, "vetorial"), resumo_respostas(resultados, "híbrida")
    partes.append("<h2>2. As respostas são boas e confiáveis?</h2>"
                  '<div class="rolagem"><table><tr><th>Verificação</th><th>Busca vetorial</th><th>Busca híbrida</th></tr>')
    for rotulo, chave, base in [
        ("Perguntas de dentro respondidas", "respondidas", "dentro"),
        ("Respostas com fonte citada", "citou", "respondidas"),
        ("Respostas fiéis aos trechos (LLM juiz)", "fiel", "respondidas"),
        ("Perguntas de fora recusadas", "recusou_fora", "fora"),
    ]:
        partes.append(f"<tr><td>{e(rotulo)}</td><td>{rv[chave]} de {rv[base]}</td><td>{rh[chave]} de {rh[base]}</td></tr>")
    partes.append("</table></div>")

    partes.append("<h2>3. Pergunta por pergunta</h2>"
                  '<p class="sub">Leia as respostas e julgue você também. O juiz automático pode errar.</p>')
    for i, r in enumerate(resultados, start=1):
        caso = r["caso"]
        dentro = caso["arquivo"] is not None
        esperado = (f'Resposta esperada em: {e(caso["arquivo"])}, trecho com "{e(caso["termo"])}"' if dentro
                    else "Fora da bibliografia: o certo é recusar")
        partes.append(f'<div class="caso"><h3>{i}. {e(caso["pergunta"])}</h3><div class="meta">{esperado}</div><div class="colunas">')
        for nome in BUSCAS_COM_RESPOSTA:
            d = r[nome]
            if dentro:
                selos = [selo("busca acertou", "ok") if d["busca_acertou"] else selo("busca errou", "ruim"),
                         selo("recusou", "ruim") if d["recusou"] else selo("respondeu", "ok")]
            else:
                selos = [selo("recusou (certo)", "ok") if d["recusou"] else selo("respondeu (errado)", "ruim")]
            if not d["recusou"]:
                selos.append(selo("citou fonte", "ok") if d["citou"] else selo("sem fonte", "ruim"))
                selos.append(selo("fiel", "ok") if d["fiel"] else selo("juiz: não fiel", "ruim"))
            selos.append(selo(d["modelo"], "neutro"))
            fontes = "".join(
                f'<div class="fonte"><b>[{n}] {e(x["arquivo"])}, pág. {x["pagina"]}</b> · similaridade {x["similaridade"]:.2f}'
                f'<div class="trecho">{e(x["texto"])}</div></div>' for n, x in enumerate(d["fontes"], start=1))
            partes.append(f'<div class="lado"><h4>Busca {e(nome)}</h4>{"".join(selos)}'
                          f'<div class="resposta">{e(d["resposta"])}</div>'
                          f'<details><summary>Ver os {len(d["fontes"])} trechos enviados ao modelo</summary>{fontes}</details></div>')
        partes.append("</div></div>")
    partes.append("</main></body></html>")
    (PASTA / "relatorio.html").write_text("\n".join(partes), encoding="utf-8")


# ---------- Programa principal ----------


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    PASTA.mkdir(exist_ok=True)
    nutripedia = criar_nutripedia()

    tabela_busca = taxas_de_busca(nutripedia)
    print("Taxa de acerto da busca (k=1, 3, 5):")
    for nome, taxas in tabela_busca.items():
        print(f"  {nome:>14}: " + " | ".join(f"{t:.0%}" for t in taxas))
    if "--so-busca" in sys.argv:
        return

    gerador = GeradorGemini(obter_chave_gemini(), modelos=MODELOS_AVALIACAO, tentativas=4, pausa=8)
    resultados = []
    if ARQ_JSON.exists():
        resultados = json.loads(ARQ_JSON.read_text(encoding="utf-8"))["resultados"]
        print(f"Retomando: {len(resultados)} perguntas já avaliadas.")
    feitas = {r["caso"]["pergunta"] for r in resultados}

    for numero, caso in enumerate(PERGUNTAS, start=1):
        if caso["pergunta"] in feitas:
            continue
        registro = {"caso": caso}
        for nome, busca in BUSCAS_COM_RESPOSTA.items():
            registro[nome] = avaliar_caso(nutripedia, gerador, caso, busca)
        resultados.append(registro)
        ARQ_JSON.write_text(json.dumps({"busca": tabela_busca, "resultados": resultados}, ensure_ascii=False, indent=1),
                            encoding="utf-8")
        marcas = " | ".join(f"{n}: {'recusou' if registro[n]['recusou'] else 'respondeu'}" for n in BUSCAS_COM_RESPOSTA)
        print(f"[{numero}/{len(PERGUNTAS)}] {marcas} | {caso['pergunta'][:60]}", flush=True)

    ordem = {c["pergunta"]: i for i, c in enumerate(PERGUNTAS)}
    resultados.sort(key=lambda r: ordem.get(r["caso"]["pergunta"], 999))
    gerar_csv(resultados)
    gerar_html(resultados, tabela_busca)
    for nome in BUSCAS_COM_RESPOSTA:
        print(nome, resumo_respostas(resultados, nome))
    print("Relatório salvo em", PASTA / "relatorio.html")


if __name__ == "__main__":
    main()
