#!/usr/bin/env python3
"""
Script para analisar arquivos HTML e contar caracteres e tokens (Anthropic).
Gera um arquivo Excel com os resultados.
"""

import os
import glob
import pandas as pd
from anthropic import Anthropic

def count_tokens_anthropic(text):
    """
    Conta tokens usando o método da Anthropic.
    """
    try:
        client = Anthropic()
        # Usa o método count_tokens para contar tokens
        token_count = client.count_tokens(text)
        return token_count
    except Exception as e:
        # Se falhar (por exemplo, sem API key), usa estimativa: ~4 chars por token
        # Esta é uma aproximação comum para modelos Claude
        return len(text) // 4

def analyze_files():
    """
    Analisa todos os arquivos HTML no diretório atual.
    """
    # Lista todos os arquivos HTML
    html_files = sorted(glob.glob("*.html"))

    if not html_files:
        print("Nenhum arquivo HTML encontrado!")
        return

    print(f"Encontrados {len(html_files)} arquivos HTML")
    print("Analisando arquivos...")

    # Lista para armazenar os resultados
    results = []

    for i, filename in enumerate(html_files, 1):
        print(f"[{i}/{len(html_files)}] Processando: {filename}")

        try:
            # Lê o conteúdo do arquivo
            with open(filename, 'r', encoding='utf-8') as f:
                content = f.read()

            # Conta caracteres
            char_count = len(content)

            # Conta tokens
            token_count = count_tokens_anthropic(content)

            # Adiciona aos resultados
            results.append({
                'Nome do Arquivo': filename,
                'Quantidade de Caracteres': char_count,
                'Quantidade de Tokens (Anthropic)': token_count
            })

        except Exception as e:
            print(f"  Erro ao processar {filename}: {e}")
            results.append({
                'Nome do Arquivo': filename,
                'Quantidade de Caracteres': 0,
                'Quantidade de Tokens (Anthropic)': 0
            })

    # Cria DataFrame
    df = pd.DataFrame(results)

    # Adiciona linha de totais
    totals = pd.DataFrame([{
        'Nome do Arquivo': 'TOTAL',
        'Quantidade de Caracteres': df['Quantidade de Caracteres'].sum(),
        'Quantidade de Tokens (Anthropic)': df['Quantidade de Tokens (Anthropic)'].sum()
    }])

    df = pd.concat([df, totals], ignore_index=True)

    # Salva em Excel
    output_file = 'analise_arquivos.xlsx'
    df.to_excel(output_file, index=False, sheet_name='Análise')

    print(f"\n✓ Análise concluída!")
    print(f"✓ Arquivo gerado: {output_file}")
    print(f"\nResumo:")
    print(f"  Total de arquivos: {len(html_files)}")
    print(f"  Total de caracteres: {df.iloc[-1]['Quantidade de Caracteres']:,}")
    print(f"  Total de tokens: {df.iloc[-1]['Quantidade de Tokens (Anthropic)']:,}")

    return output_file

if __name__ == "__main__":
    analyze_files()
