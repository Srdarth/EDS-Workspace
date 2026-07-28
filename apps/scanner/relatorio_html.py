#!/usr/bin/env python3
"""
Gera relatorio HTML do patrimonio digital.
Abra o arquivo no navegador.
"""

import psycopg2
from datetime import datetime

DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "database": "eddydb",
    "user": "postgres",
    "password": "postgres"
}

def get_db():
    return psycopg2.connect(**DB_CONFIG)

def gerar_html():
    conn = get_db()
    cursor = conn.cursor()
    
    # Estatisticas gerais
    cursor.execute("SELECT COUNT(*), COALESCE(SUM(size_bytes),0) FROM files")
    total_arquivos, tamanho_total = cursor.fetchone()
    
    cursor.execute("SELECT COALESCE(SUM(duplicates_found),0) FROM scans")
    total_duplicatas = cursor.fetchone()[0]
    
    # Por tipo
    cursor.execute("""
        SELECT extension, COUNT(*), pg_size_pretty(SUM(size_bytes))
        FROM files 
        GROUP BY extension 
        ORDER BY COUNT(*) DESC
    """)
    por_tipo = cursor.fetchall()
    
    # Maiores arquivos
    cursor.execute("""
        SELECT filename, pg_size_pretty(size_bytes), path
        FROM files 
        ORDER BY size_bytes DESC 
        LIMIT 10
    """)
    maiores = cursor.fetchall()
    
    # Ultimas scans
    cursor.execute("""
        SELECT root_path, total_files, duplicates_found, scanned_at
        FROM scans 
        ORDER BY scanned_at DESC 
        LIMIT 5
    """)
    scans = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    # Gerar HTML
    html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>NeverLost - Relatorio de Patrimonio Digital</title>
    <style>
        body {{ font-family: 'Segoe UI', Arial, sans-serif; margin: 40px; background: #0f0f23; color: #e0e0e0; }}
        h1 {{ color: #00d4aa; border-bottom: 2px solid #00d4aa; padding-bottom: 10px; }}
        h2 {{ color: #00d4aa; margin-top: 30px; }}
        .card {{ background: #1a1a2e; border-radius: 12px; padding: 20px; margin: 15px 0; border-left: 4px solid #00d4aa; }}
        .stat {{ font-size: 2em; color: #00d4aa; font-weight: bold; }}
        .label {{ color: #888; font-size: 0.9em; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 15px; }}
        th {{ background: #00d4aa; color: #0f0f23; padding: 12px; text-align: left; }}
        td {{ padding: 10px; border-bottom: 1px solid #333; }}
        tr:hover {{ background: #252540; }}
        .duplicata {{ color: #ff6b6b; }}
        .ok {{ color: #00d4aa; }}
    </style>
</head>
<body>
    <h1>🔍 NeverLost - Diagnostico Digital</h1>
    <p>Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}</p>
    
    <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; margin: 30px 0;">
        <div class="card">
            <div class="stat">{total_arquivos}</div>
            <div class="label">Arquivos Unicos</div>
        </div>
        <div class="card">
            <div class="stat duplicata">{total_duplicatas}</div>
            <div class="label">Duplicatas Detectadas</div>
        </div>
        <div class="card">
            <div class="stat">{round(tamanho_total / (1024*1024*1024), 2)} GB</div>
            <div class="label">Espaco Total</div>
        </div>
    </div>
    
    <h2>📂 Arquivos por Tipo</h2>
    <div class="card">
        <table>
            <tr><th>Extensao</th><th>Quantidade</th><th>Tamanho</th></tr>
"""
    
    for ext, qtd, tam in por_tipo:
        html += f"            <tr><td>{ext or '(sem)'}</td><td>{qtd}</td><td>{tam}</td></tr>\n"
    
    html += """        </table>
    </div>
    
    <h2>🐘 Maiores Arquivos</h2>
    <div class="card">
        <table>
            <tr><th>Tamanho</th><th>Nome</th></tr>
"""
    
    for nome, tam, caminho in maiores:
        html += f"            <tr><td>{tam}</td><td title='{caminho}'>{nome}</td></tr>\n"
    
    html += """        </table>
    </div>
    
    <h2>🕐 Historico de Varreduras</h2>
    <div class="card">
        <table>
            <tr><th>Data</th><th>Pasta</th><th>Arquivos</th><th>Duplicatas</th></tr>
"""
    
    for pasta, arqs, dup, data in scans:
        html += f"            <tr><td>{data}</td><td>{pasta}</td><td>{arqs}</td><td class='duplicata'>{dup}</td></tr>\n"
    
    html += """        </table>
    </div>
    
    <div class="card" style="margin-top: 40px; text-align: center;">
        <p style="color: #666;">NeverLost by EDS - Seus dados, sua maquina, sua soberania.</p>
    </div>
</body>
</html>"""
    
    nome_arquivo = f"relatorio_{datetime.now().strftime('%Y%m%d_%H%M')}.html"
    with open(nome_arquivo, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print("\n✅ Relatorio gerado: " + nome_arquivo)
    print("📂 Abra no navegador: file://" + os.path.abspath(nome_arquivo))

if __name__ == "__main__":
    import os
    gerar_html()
