#!/usr/bin/env python3
"""
Script para traduzir comentários bíblicos do inglês para português do Brasil
seguindo rigorosas diretrizes católicas editoriais.
"""

import json
import re
from bs4 import BeautifulSoup
from anthropic import Anthropic
import os

# Mapeamento de livros bíblicos (inglês -> português)
BOOK_NAMES = {
    "1 Chronicles": "1Crônicas",
    "2 Chronicles": "2Crônicas",
    "1 Corinthians": "1Coríntios",
    "2 Corinthians": "2Coríntios",
    # ... adicionar conforme necessário
}

# Prompt de tradução detalhado
TRANSLATION_PROMPT = """Você é um tradutor especializado em literatura teológica católica, com profundo conhecimento de exegese bíblica, doutrina católica e terminologia litúrgica. Sua missão é traduzir comentários bíblicos doutrinários do inglês para o português do Brasil, seguindo rigorosamente os mais altos padrões editoriais das principais editoras católicas brasileiras.

REGRAS CRÍTICAS DE CONVERSÃO:

1. SIGLAS DE DOCUMENTOS (OBRIGATÓRIO):
   - CCC → CIC (Catecismo da Igreja Católica)
   - CSDC → CDSI (Compêndio da Doutrina Social da Igreja)
   - STh → S.Th. (Suma Teológica)
   - Manter números EXATOS após a conversão

2. REFERÊNCIAS BÍBLICAS:
   - Usar vírgula (não dois pontos): Ex 1,6-11 (não Ex 1:6-11)
   - Hífen para intervalos: 1,6-11
   - Ponto para versículos isolados: 1,6.8.10

3. ABREVIAÇÕES DE LIVROS (principais):
   - 1 Samuel → 1Sm
   - 2 Samuel → 2Sm
   - 1 Kings → 1Rs
   - 2 Kings → 2Rs
   - 1 Chronicles → 1Cr
   - 2 Chronicles → 2Cr
   - Job → Jó
   - Psalms → Sl
   - Wisdom → Sb
   - Sirach/Ecclesiasticus → Eclo

4. TERMINOLOGIA CONSAGRADA:
   - Holy Spirit → Espírito Santo
   - Ark of the Covenant → Arca da Aliança
   - Chosen People → Povo Escolhido
   - Promised Land → Terra Prometida
   - Old Testament → Antigo Testamento
   - New Testament → Novo Testamento
   - Church Fathers → Padres da Igreja / Santos Padres
   - tabernacle → tabernáculo
   - Temple → Templo
   - covenant → aliança
   - worship → culto / adoração
   - liturgy → liturgia
   - idolatry → idolatria
   - idols → ídolos
   - Satan → Satanás
   - angel(s) → anjo(s)
   - steadfast love → amor constante / misericórdia
   - mercy seat → propiciatório

5. NOMES PRÓPRIOS:
   - David → Davi / David (aceitos ambos)
   - Solomon → Salomão
   - Israel → Israel
   - Jerusalem → Jerusalém
   - Levites → Levitas
   - Philistines → filisteus

6. NATURALIDADE EM PORTUGUÊS:
   - Evitar anglicismos sintáticos
   - Usar estruturas naturais do português brasileiro
   - Manter formalidade acadêmica mas legível
   - Preferir voz ativa quando possível

Traduza o seguinte comentário mantendo ABSOLUTA fidelidade doutrinal e terminológica:"""


def extract_commentary_data(html_content, book_name="1 Chronicles"):
    """
    Extrai dados dos comentários do HTML.
    """
    soup = BeautifulSoup(html_content, 'html.parser')

    commentaries = []

    # Encontra todos os parágrafos com comentários
    paragraphs = soup.find_all('p', class_=['calibre_6', 'calibre_16'])

    for para in paragraphs:
        # Procura por links com referências de versículos
        link = para.find('a')
        if not link:
            continue

        verse_ref = link.get_text(strip=True)

        # Extrai o texto do comentário (tudo após o link)
        comment_text = ''
        for content in link.next_siblings:
            if isinstance(content, str):
                comment_text += content
            else:
                comment_text += content.get_text()

        comment_text = comment_text.strip()

        if not comment_text:
            continue

        # Extrai referências bibliográficas (CCC, CSDC, etc.)
        biblio_refs = []
        biblio_pattern = r'\((CCC|CSDC|STh)\s+[^)]+\)'
        biblio_matches = re.findall(biblio_pattern, comment_text)

        # Parse da referência de versículos
        verse_parts = verse_ref.split(':')
        if len(verse_parts) == 2:
            chapter = verse_parts[0]
            verses = verse_parts[1]

            if '-' in verses:
                verse_start, verse_end = verses.split('-')
            else:
                verse_start = verses
                verse_end = None
        else:
            # Formato alternativo (ex: "1-9")
            if '-' in verse_ref:
                parts = verse_ref.split('-')
                chapter = parts[0]
                verse_start = parts[0]
                verse_end = parts[1]
            else:
                chapter = verse_ref
                verse_start = verse_ref
                verse_end = None

        commentaries.append({
            'verse_ref': verse_ref,
            'chapter': chapter,
            'verse_start': verse_start,
            'verse_end': verse_end,
            'original_text': comment_text,
            'biblio_refs': biblio_matches
        })

    return commentaries


def translate_commentary(text, client):
    """
    Traduz um comentário usando a API da Anthropic.
    """
    try:
        message = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=4000,
            temperature=0.3,
            messages=[
                {
                    "role": "user",
                    "content": f"{TRANSLATION_PROMPT}\n\n{text}"
                }
            ]
        )

        translation = message.content[0].text.strip()
        return translation

    except Exception as e:
        print(f"Erro na tradução: {e}")
        return None


def process_file(input_file, output_file):
    """
    Processa o arquivo HTML e gera JSON traduzido.
    """
    print(f"Lendo arquivo: {input_file}")

    with open(input_file, 'r', encoding='utf-8') as f:
        html_content = f.read()

    print("Extraindo comentários...")
    commentaries = extract_commentary_data(html_content)

    print(f"Encontrados {len(commentaries)} comentários")

    # Inicializa cliente Anthropic
    api_key = os.environ.get('ANTHROPIC_API_KEY')
    if not api_key:
        print("AVISO: ANTHROPIC_API_KEY não encontrada. Usando tradução simplificada.")
        client = None
    else:
        client = Anthropic(api_key=api_key)

    translated_commentaries = []

    for i, comm in enumerate(commentaries, 1):
        print(f"[{i}/{len(commentaries)}] Traduzindo: {comm['verse_ref']}")

        if client:
            translated_text = translate_commentary(comm['original_text'], client)
        else:
            # Tradução básica automática (sem API)
            translated_text = translate_basic(comm['original_text'])

        if translated_text:
            # Extrai referências bibliográficas traduzidas
            biblio_ref = None
            biblio_extenso = None

            if 'CIC' in translated_text or 'CCC' in comm['original_text']:
                match = re.search(r'(CIC|CCC)\s+(\d+[-,\d\s]*)', translated_text)
                if match:
                    biblio_ref = f"CIC {match.group(2)}"
                    biblio_extenso = "Catecismo da Igreja Católica"

            if 'CDSI' in translated_text or 'CSDC' in comm['original_text']:
                match = re.search(r'(CDSI|CSDC)\s+(\d+)', translated_text)
                if match:
                    biblio_ref = f"CDSI {match.group(2)}"
                    biblio_extenso = "Compêndio da Doutrina Social da Igreja"

            # Remove as referências do texto traduzido
            clean_text = re.sub(r'\s*\([A-Z]{2,6}\s+[^\)]+\)\s*$', '', translated_text)
            clean_text = clean_text.strip()

            translated_commentaries.append({
                "nome_livro": "1Crônicas",
                "capitulo": str(comm['chapter']),
                "versiculo_inicial": str(comm['verse_start']),
                "versiculo_final": str(comm['verse_end']) if comm['verse_end'] else None,
                "texto_comentario": clean_text,
                "referencia_bibliografica": biblio_ref,
                "referencia_bibliografica_extenso": biblio_extenso
            })

    # Salva JSON
    print(f"\nSalvando resultado em: {output_file}")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(translated_commentaries, f, ensure_ascii=False, indent=2)

    print(f"✓ Tradução concluída! {len(translated_commentaries)} comentários traduzidos.")
    return output_file


def translate_basic(text):
    """
    Tradução básica sem API (fallback).
    """
    # Conversões básicas
    text = text.replace('CCC', 'CIC')
    text = text.replace('CSDC', 'CDSI')
    text = text.replace('STh', 'S.Th.')

    # Converte referências bíblicas
    text = re.sub(r'(\d+):(\d+)', r'\1,\2', text)

    return text


if __name__ == "__main__":
    input_file = "Commentary on 1 Chronicles.html"
    output_file = "1Cronicas_traduzido.json"

    process_file(input_file, output_file)
