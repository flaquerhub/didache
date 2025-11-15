#!/usr/bin/env python3
"""
Script para extrair comentários do HTML para facilitar tradução.
"""

import json
import re
from bs4 import BeautifulSoup


def extract_commentaries(html_file):
    """Extrai comentários do arquivo HTML."""

    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()

    soup = BeautifulSoup(html_content, 'html.parser')

    commentaries = []

    # Encontra todos os parágrafos com comentários
    paragraphs = soup.find_all('p', class_=['calibre_6', 'calibre_16', 'calibre_3'])

    for para in paragraphs:
        # Procura por links com referências de versículos
        link = para.find('a')
        if not link:
            continue

        verse_ref = link.get_text(strip=True)

        # Extrai o texto do comentário completo
        full_text = para.get_text()

        # Remove a referência do início
        comment_text = full_text.replace(verse_ref, '', 1).strip()

        if not comment_text or len(comment_text) < 10:
            continue

        commentaries.append({
            'verse_ref': verse_ref,
            'original_text': comment_text
        })

    return commentaries


if __name__ == "__main__":
    comms = extract_commentaries("Commentary on 1 Chronicles.html")

    print(f"Total de comentários: {len(comms)}\n")

    for i, c in enumerate(comms, 1):
        print(f"=== Comentário {i} ===")
        print(f"Ref: {c['verse_ref']}")
        print(f"Texto: {c['original_text'][:100]}...")
        print()

    # Salva em JSON para referência
    with open('extracted_commentaries.json', 'w', encoding='utf-8') as f:
        json.dump(comms, f, ensure_ascii=False, indent=2)

    print(f"✓ Comentários extraídos salvos em: extracted_commentaries.json")
