import requests
import json
from datetime import datetime

# Adicione os ORCIDs dos membros do seu grupo de pesquisa
ORCIDS = [
    "0000-0002-6408-451X", # Pesquisador 1
    "0000-0002-7351-3910",  # Pesquisador 2
    "0000-0002-7555-5022", # Pesquisador 3
    "0000-0001-7590-896X", # Pesquisador 4
    "0000-0001-7144-6331", # Pesquisador 5
]

def fetch_group_oa_articles(orcids, target_keyword="tailings"):
    """Busca apenas artigos Open Access filtrados pela palavra-chave."""
    artigos_unicos = {}
    for orcid in orcids:
        print(f"Buscando publicações OA para ORCID: {orcid}...")
        url = f"https://api.openalex.org/works?filter=author.orcid:https://orcid.org/{orcid},is_oa:true&per-page=100"
        headers = {"User-Agent": "mailto:seu_email@instituicao.edu.br"}
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            resultados = response.json().get('results', [])
            for artigo in resultados:
                has_keyword = False
                for kw in artigo.get('keywords', []):
                    if target_keyword.lower() in kw.get('display_name', '').lower():
                        has_keyword = True
                        break
                if not has_keyword:
                    for concept in artigo.get('concepts', []):
                        if target_keyword.lower() in concept.get('display_name', '').lower():
                            has_keyword = True
                            break
                if has_keyword:
                    artigo_id = artigo.get('id')
                    artigos_unicos[artigo_id] = artigo
    return sorted(artigos_unicos.values(), key=lambda x: x.get('publication_year', 0), reverse=True)

def fetch_all_articles(orcids):
    """Busca TODAS as publicações sem filtros de acesso ou palavras-chave."""
    artigos_unicos = {}
    for orcid in orcids:
        print(f"Buscando TODAS as publicações para ORCID: {orcid}...")
        url = f"https://api.openalex.org/works?filter=author.orcid:https://orcid.org/{orcid}&per-page=100"
        headers = {"User-Agent": "mailto:seu_email@instituicao.edu.br"}
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            resultados = response.json().get('results', [])
            for artigo in resultados:
                artigo_id = artigo.get('id')
                artigos_unicos[artigo_id] = artigo
    return sorted(artigos_unicos.values(), key=lambda x: x.get('publication_year', 0), reverse=True)

def salvar_oa_em_markdown(artigos, nome_arquivo="docs/publicacoes.md"):
    """Gera o arquivo Markdown para a aba de Open Access."""
    with open(nome_arquivo, 'w', encoding='utf-8') as f:
        f.write("# 🔓 Open Access Papers (Tailings)\n\n")
        f.write(f"*Lista atualizada automaticamente em: {datetime.now().strftime('%d/%m/%Y')}*\n\n")
        for artigo in artigos:
            titulo = artigo.get('title', 'Sem título')
            ano = artigo.get('publication_year', '')
            autores = ", ".join([a['author']['display_name'] for a in artigo.get('authorships', [])])
            oa_url = artigo.get('open_access', {}).get('oa_url')
            if not oa_url:
                oa_url = artigo.get('doi', '#')
            f.write(f"### {titulo}\n")
            f.write(f"**Autores:** {autores} | **Ano:** {ano}\n")
            f.write(f"[📄 Acessar Artigo Completo]({oa_url})\n\n")
            f.write("---\n\n")

def salvar_todas_em_markdown(artigos, nome_arquivo="docs/todas_publicacoes.md"):
    """Gera o arquivo Markdown para a aba de Todas as Publicações."""
    with open(nome_arquivo, 'w', encoding='utf-8') as f:
        f.write("# 📚 All Publications\n\n")
        f.write(f"*Lista completa atualizada automaticamente em: {datetime.now().strftime('%d/%m/%Y')}*\n\n")
        for artigo in artigos:
            titulo = artigo.get('title', 'Sem título')
            ano = artigo.get('publication_year', '')
            autores = ", ".join([a['author']['display_name'] for a in artigo.get('authorships', [])])
            
            # OpenAlex returns the DOI already formatted as a full link (https://doi.org/...)
            doi_link = artigo.get('doi', '#') 
            
            f.write(f"### {titulo}\n")
            f.write(f"**Autores:** {autores} | **Ano:** {ano}\n")
            f.write(f"[see in the publisher]({doi_link})\n\n")
            f.write("---\n\n")

if __name__ == "__main__":
    # 1. Processa a lista Open Access
    artigos_oa = fetch_group_oa_articles(ORCIDS)
    salvar_oa_em_markdown(artigos_oa)
    
    # 2. Processa a lista Completa
    todas_publicacoes = fetch_all_articles(ORCIDS)
    salvar_todas_em_markdown(todas_publicacoes)
    
    print("Sucesso! As duas listas de publicações foram geradas.")
