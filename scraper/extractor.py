import requests
import json
import time
from bs4 import BeautifulSoup
from datetime import datetime

BASE_URL = "http://scp-pt-br.wikidot.com"

PAGINAS_SERIE = [
    "http://scp-pt-br.wikidot.com/scp-series",
    "http://scp-pt-br.wikidot.com/scp-series-2",
    "http://scp-pt-br.wikidot.com/scp-series-3",
    "http://scp-pt-br.wikidot.com/scp-series-4",
    "http://scp-pt-br.wikidot.com/scp-series-5",
    "http://scp-pt-br.wikidot.com/scp-series-6",
    "http://scp-pt-br.wikidot.com/scp-series-7",
    "http://scp-pt-br.wikidot.com/scp-series-8",
    "http://scp-pt-br.wikidot.com/scp-series-9",
]

CLASSE_MAP = {
    "seguro": "Safe",
    "euclid": "Euclid",
    "euclídeo": "Euclid",
    "keter": "Keter",
    "thaumiel": "Thaumiel",
    "apolion": "Apollyon",
    "archon": "Archon",
    "neutralizado": "Neutralized",
    "explicado": "Explained",
    "pendente": "Pending"
}

SECOES_PRINCIPAIS = [
    "item nº:",
    "classe do objeto:",
    "procedimentos especiais de contenção:",
    "descrição:"
]

SUB_CAMPOS = [
    "sujeitos:",
    "diretor do experimento:",
    "procedimento:",
    "resultados:",
    "notas:",
    "teste scp-"
]


def buscar_html(url: str) -> BeautifulSoup:
    response = requests.get(url)
    return BeautifulSoup(response.text, "html.parser")


def buscar_urls_scps(limite: int = None) -> list:
    """
    Raspa as páginas de índice de séries e retorna lista de URLs de SCPs.
    O parâmetro limite permite controlar quantos SCPs raspar por vez.
    """
    urls = []

    for pagina_serie in PAGINAS_SERIE:
        try:
            soup = buscar_html(pagina_serie)
            page_content = soup.find("div", {"id": "page-content"})
            if not page_content:
                continue

            # pega todos os links da página de série
            for a in page_content.find_all("a", href=True):
                href = a["href"]
                # filtra apenas links de SCPs — ignoram páginas de hub, contos, etc.
                if href.startswith("/scp-") and href.count("/") == 1:
                    url_completa = BASE_URL + href
                    if url_completa not in urls:
                        urls.append(url_completa)

            # pausa entre páginas de série para não sobrecarregar o site
            time.sleep(1)

        except Exception as e:
            print(f"[ERRO] Falha ao buscar índice {pagina_serie}: {e}")
            continue

    if limite:
        return urls[:limite]
    return urls


def extrair_campo_simples(soup: BeautifulSoup, rotulo: str) -> str:
    strong = soup.find("strong", string=lambda t: t and rotulo.lower() in t.lower())
    if not strong:
        return ""
    return strong.next_sibling.strip() if strong.next_sibling else ""


def extrair_secao_texto(soup: BeautifulSoup, rotulo_inicio: str, rotulos_fim: list) -> str:
    strong_inicio = soup.find("strong", string=lambda t: t and rotulo_inicio.lower() in t.lower())
    if not strong_inicio:
        return ""

    paragrafos = []
    elemento = strong_inicio.find_parent("p").next_sibling

    while elemento:
        if elemento.name == "p":
            strong = elemento.find("strong")
            if strong and any(fim.lower() in strong.get_text().lower() for fim in rotulos_fim):
                break
            paragrafos.append(elemento.get_text(strip=True))
        elemento = elemento.next_sibling

    return "\n".join(paragrafos)


def extrair_conteudos_adjacentes(soup: BeautifulSoup) -> list:
    conteudos = []
    todos_strong = soup.find_all("strong")

    for strong in todos_strong:
        texto = strong.get_text(strip=True).lower()

        if any(secao in texto for secao in SECOES_PRINCIPAIS):
            continue
        if any(sub in texto for sub in SUB_CAMPOS):
            continue
        if ":" not in strong.get_text():
            continue

        titulo = strong.get_text(strip=True).replace(":", "").strip()
        paragrafos = []
        elemento = strong.find_parent("p").next_sibling

        while elemento:
            if elemento.name == "p":
                proximo_strong = elemento.find("strong")
                if proximo_strong:
                    proximo_texto = proximo_strong.get_text(strip=True).lower()
                    if ":" in proximo_texto and not any(sub in proximo_texto for sub in SUB_CAMPOS + SECOES_PRINCIPAIS):
                        break
                paragrafos.append(elemento.get_text(strip=True))
            elemento = elemento.next_sibling

        if paragrafos:
            conteudos.append({
                "titulo": titulo,
                "conteudo": "\n".join(paragrafos)
            })

    return conteudos


def extrair_scp(soup: BeautifulSoup) -> dict:
    page_content = soup.find("div", {"id": "page-content"})
    if not page_content:
        raise Exception("Container #page-content não encontrado na página")

    return {
        "itemNumber": extrair_campo_simples(page_content, "Item Nº:"),
        "objectClass": extrair_campo_simples(page_content, "Classe do Objeto:"),
        "containmentProcedures": extrair_secao_texto(
            page_content,
            "Procedimentos Especiais de Contenção:",
            ["Descrição:", "Adendo", "Apêndice", "Registro"]
        ),
        "description": extrair_secao_texto(
            page_content,
            "Descrição:",
            ["Adendo", "Apêndice", "Registro", "Entrevista"]
        ),
        "conteudos_adjacentes": extrair_conteudos_adjacentes(page_content),
    }


def montar_dto(dados: dict, url: str) -> dict:
    return {
        "itemNumber": dados["itemNumber"],
        "objectClass": CLASSE_MAP.get(dados["objectClass"].strip().lower(), dados["objectClass"]),
        "containmentProcedures": dados["containmentProcedures"],
        "description": dados["description"],
        "conteudos_adjacentes": dados["conteudos_adjacentes"],
        "metadados": {
            "url_origem": url,
            "data_scraping": datetime.utcnow().isoformat()
        }
    }


def main(url: str) -> dict:
    """
    Raspa um único SCP pela URL e retorna o DTO.
    """
    soup = buscar_html(url)
    dados = extrair_scp(soup)
    dto = montar_dto(dados, url)
    return dto


def raspar_todos(limite: int = None) -> list:
    """
    Raspa todos os SCPs do índice e retorna lista de DTOs.
    Use o parâmetro limite para testar com poucos SCPs primeiro.
    Ex: raspar_todos(limite=10) raspa só os primeiros 10.
    """
    urls = buscar_urls_scps(limite=limite)
    print(f"[SCRAPER] {len(urls)} URLs encontradas")

    dtos = []
    for i, url in enumerate(urls):
        try:
            print(f"[SCRAPER] ({i+1}/{len(urls)}) Raspando {url}")
            dto = main(url)

            # ignora SCPs sem dados — páginas de placeholder ou erro
            if not dto["itemNumber"]:
                print(f"[SCRAPER] Pulando {url} — sem dados")
                continue

            dtos.append(dto)

            # pausa entre requisições para não sobrecarregar o site
            time.sleep(1.5)

        except Exception as e:
            print(f"[ERRO] Falha ao raspar {url}: {e}")
            continue

    print(f"[SCRAPER] Concluído — {len(dtos)} SCPs raspados")
    return dtos


if __name__ == "__main__":
    dtos = raspar_todos()
    with open("scp_output.json", "w", encoding="utf-8") as f:
        json.dump(dtos, f, ensure_ascii=False, indent=4)
    print("Arquivo salvo em: scp_output.json")