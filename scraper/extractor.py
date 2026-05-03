import requests
from bs4 import BeautifulSoup
from datetime import datetime

URL = "http://scp-pt-br.wikidot.com/scp-3516"

# Títulos que identificam seções principais — não viram conteúdo adjacente
SECOES_PRINCIPAIS = [
    "item nº:",
    "classe do objeto:",
    "procedimentos especiais de contenção:",
    "descrição:"
]

def buscar_html(url: str) -> BeautifulSoup:
    response = requests.get(url)
    return BeautifulSoup(response.text, "html.parser")


def extrair_campo_simples(soup: BeautifulSoup, rotulo: str) -> str:
    """
    Encontra um <strong> pelo texto do rótulo e retorna o texto irmão logo após.
    Usado para campos de valor único como itemNumber e objectClass.
    """
    strong = soup.find("strong", string=lambda t: t and rotulo.lower() in t.lower())
    if not strong:
        return ""
    # next_sibling pega o texto que vem logo depois do <strong> dentro do mesmo <p>
    return strong.next_sibling.strip() if strong.next_sibling else ""


def extrair_secao_texto(soup: BeautifulSoup, rotulo_inicio: str, rotulos_fim: list) -> str:
    """
    Extrai um bloco de texto que começa em um <strong> e vai até o próximo título de seção.
    Usado para campos longos como procedimentos e descrição.
    """
    strong_inicio = soup.find("strong", string=lambda t: t and rotulo_inicio.lower() in t.lower())
    if not strong_inicio:
        return ""

    paragrafos = []
    # começa a varrer a partir do <p> que contém o título
    elemento = strong_inicio.find_parent("p").next_sibling

    while elemento:
        # para quando encontrar o próximo título de seção
        if elemento.name == "p":
            strong = elemento.find("strong")
            if strong and any(fim.lower() in strong.get_text().lower() for fim in rotulos_fim):
                break
            paragrafos.append(elemento.get_text(strip=True))

        elemento = elemento.next_sibling

    return "\n".join(paragrafos)


def extrair_conteudos_adjacentes(soup: BeautifulSoup) -> list:
    """ (Não finalizado)
    Varre todos os <strong> do documento e coleta os que não são seções principais.
    Cada um vira um objeto {titulo, conteudo} na lista de conteúdos adjacentes.
    """
    conteudos = []
    todos_strong = soup.find_all("strong")

    for strong in todos_strong:
        texto = strong.get_text(strip=True).lower()

        # ignora os títulos de seções principais
        if any(secao in texto for secao in SECOES_PRINCIPAIS):
            continue

        # ignora <strong> que estão dentro de parágrafos de conteúdo (sem ":")
        if ":" not in strong.get_text():
            continue

        titulo = strong.get_text(strip=True).replace(":", "").strip()
        paragrafos = []
        elemento = strong.find_parent("p").next_sibling

        while elemento:
            if elemento.name == "p":
                proximo_strong = elemento.find("strong")
                if proximo_strong and ":" in proximo_strong.get_text():
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
    # isola o container principal do verbete — ignora menu, rodapé, etc.
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
        "objectClass": dados["objectClass"],
        "containmentProcedures": dados["containmentProcedures"],
        "description": dados["description"],
        "conteudos_adjacentes": dados["conteudos_adjacentes"],
        "metadados": {
            "url_origem": url,
            "data_scraping": datetime.utcnow().isoformat()
        }
    }


def main():
    soup = buscar_html(URL)
    dados = extrair_scp(soup)
    dto = montar_dto(dados, URL)
    print(dto)


if __name__ == "__main__":
    main()