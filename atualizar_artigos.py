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

def fetch_group_oa_articles(orcids):
    artigos_unicos = {}
    
    for orcid in orcids:
        print(f"Buscando publicações OA para ORCID: {orcid}...")
        # Filtra pelo ORCID do autor e força is_oa=true (apenas Open Access)
        url = f"https://api.openalex.org/works?filter=author.orcid:https://orcid.org/{orcid},is_oa:true"
        
        # Boas práticas: o OpenAlex pede um e-mail no header (polite pool) para requisições mais rápidas
        headers = {"User-Agent": "mailto:seu_email@instituicao.edu.br"}
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            resultados = response.json().get('results', [])
            for artigo in resultados:
                # Usa o ID do artigo como chave para evitar duplicatas 
                # (útil quando pesquisadores do grupo publicam juntos)
                artigo_id = artigo.get('id')
                artigos_unicos[artigo_id] = artigo
                
    # Ordenar por ano (do mais recente para o mais antigo)
    return sorted(artigos_unicos.values(), key=lambda x: x.get('publication_year', 0), reverse=True)

def salvar_em_markdown(artigos, nome_arquivo="publicacoes.md"):
    with open(nome_arquivo, 'w', encoding='utf-8') as f:
        f.write("# 📚 Produção Científica (Open Access)\n\n")
        f.write(f"*Lista atualizada automaticamente em: {datetime.now().strftime('%d/%m/%Y')}*\n\n")
        
        for artigo in artigos:
            titulo = artigo.get('title', 'Sem título')
            ano = artigo.get('publication_year', '')
            
            # Formatar a lista de autores
            autores = ", ".join([a['author']['display_name'] for a in artigo.get('authorships', [])])
            
            # Localizar URL direta do PDF ou da página aberta
            oa_url = artigo.get('open_access', {}).get('oa_url')
            if not oa_url:
                oa_url = artigo.get('doi', '#')
                
            f.write(f"### {titulo}\n")
            f.write(f"**Autores:** {autores} | **Ano:** {ano}\n")
            f.write(f"[📄 Acessar Artigo Completo]({oa_url})\n\n")
            f.write("---\n\n")

if __name__ == "__main__":
    artigos_encontrados = fetch_group_oa_articles(ORCIDS)
    if artigos_encontrados:
        salvar_em_markdown(artigos_encontrados)
        print(f"Sucesso! {len(artigos_encontrados)} artigos de acesso aberto catalogados.")
