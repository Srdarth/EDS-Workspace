#!/usr/bin/env python3
"""
EddY Scanner v2.0 - Guarda tudo no PostgreSQL
Nao envia NADA para a internet.
"""

import os
import sys
import hashlib
import psycopg2
from datetime import datetime
from pathlib import Path

DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "database": "eddydb",
    "user": "postgres",
    "password": "postgres"
}

def get_db():
    return psycopg2.connect(**DB_CONFIG)

def calcular_hash(caminho):
    sha = hashlib.sha256()
    try:
        with open(caminho, 'rb') as f:
            while True:
                pedaco = f.read(65536)
                if not pedaco:
                    break
                sha.update(pedaco)
        return sha.hexdigest()
    except (PermissionError, OSError):
        return None

def classificar_arquivo(nome, extensao):
    nome_lower = nome.lower()
    ext = extensao.lower()
    
    if ext in ['.py', '.js', '.html', '.css', '.sql', '.java', '.cpp']:
        return 'codigo', 'programacao'
    elif ext in ['.pdf']:
        if any(p in nome_lower for p in ['curso', 'aula', 'apostila']):
            return 'curso', 'educacao'
        elif any(p in nome_lower for p in ['ebook', 'livro']):
            return 'ebook', 'educacao'
        else:
            return 'documento', 'geral'
    elif ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp']:
        return 'imagem', 'midia'
    elif ext in ['.mp4', '.avi', '.mkv', '.mov', '.wmv']:
        return 'video', 'midia'
    elif ext in ['.mp3', '.wav', '.flac', '.ogg', '.aac']:
        return 'audio', 'midia'
    elif ext in ['.zip', '.rar', '.7z', '.tar', '.gz']:
        return 'compactado', 'backup'
    elif ext in ['.doc', '.docx', '.odt', '.txt', '.md', '.rtf']:
        return 'documento', 'geral'
    elif ext in ['.xls', '.xlsx', '.csv', '.ods']:
        return 'planilha', 'negocios'
    elif ext in ['.ppt', '.pptx', '.odp']:
        return 'apresentacao', 'negocios'
    else:
        return 'outro', 'geral'

def escanear(pasta_raiz):
    conn = get_db()
    cursor = conn.cursor()
    
    root = Path(pasta_raiz).resolve()
    print("\n🔍 Escaneando: " + str(root))
    print("=" * 50)
    
    inseridos = 0
    duplicatas = 0
    erros = 0
    tamanho_total = 0
    
    ignorar = {'.git', '__pycache__', 'node_modules', 'venv', '.env', 
               'temp', 'tmp', 'System Volume Information', '.cache'}
    
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in ignorar]
        
        for filename in filenames:
            caminho_completo = os.path.join(dirpath, filename)
            path_obj = Path(caminho_completo)
            ext = path_obj.suffix
            
            try:
                stat = os.stat(caminho_completo)
                tamanho = stat.st_size
                
                if tamanho == 0:
                    continue
                
                file_hash = calcular_hash(caminho_completo)
                if file_hash is None:
                    erros += 1
                    continue
                
                tipo, categoria = classificar_arquivo(filename, ext)
                modificado = datetime.fromtimestamp(stat.st_mtime)
                
                cursor.execute("""
                    INSERT INTO files (path, filename, extension, size_bytes, 
                                     modified_at, sha256, status)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (sha256) DO NOTHING
                    RETURNING id;
                """, (str(caminho_completo), filename, ext, tamanho, 
                      modificado, file_hash, 'observed'))
                
                if cursor.fetchone():
                    inseridos += 1
                    tamanho_total += tamanho
                else:
                    duplicatas += 1
                
                if (inseridos + duplicatas) % 100 == 0:
                    print("  ... " + str(inseridos) + " novos, " + str(duplicatas) + " duplicatas")
                    
            except Exception as e:
                erros += 1
                continue
    
    cursor.execute("""
        INSERT INTO scans (root_path, total_files, total_size, duplicates_found)
        VALUES (%s, %s, %s, %s)
    """, (str(root), inseridos, tamanho_total, duplicatas))
    
    conn.commit()
    cursor.close()
    conn.close()
    
    print("\n" + "=" * 50)
    print("✅ ESCANEAMENTO CONCLUIDO")
    print("=" * 50)
    print("📁 Pasta: " + str(root))
    print("📄 Arquivos novos: " + str(inseridos))
    print("♊ Duplicatas encontradas: " + str(duplicatas))
    print("⚠️  Erros: " + str(erros))
    print("💾 Tamanho total (novos): " + str(round(tamanho_total / (1024*1024), 2)) + " MB")
    print("=" * 50)
    
    return inseridos, duplicatas, tamanho_total

def gerar_relatorio():
    conn = get_db()
    cursor = conn.cursor()
    
    print("\n📊 RELATORIO DO PATRIMONIO DIGITAL")
    print("=" * 50)
    
    cursor.execute("SELECT COUNT(*), COALESCE(SUM(size_bytes),0) FROM files")
    total, tamanho = cursor.fetchone()
    print("Total de arquivos unicos: " + str(total))
    if tamanho:
        print("Espaco ocupado: " + str(round(tamanho / (1024*1024*1024), 2)) + " GB")
    else:
        print("Espaco ocupado: 0 GB")
    
    print("\n📂 Por tipo:")
    cursor.execute("""
        SELECT extension, COUNT(*), pg_size_pretty(SUM(size_bytes))
        FROM files 
        GROUP BY extension 
        ORDER BY COUNT(*) DESC
    """)
    for ext, qtd, tam in cursor.fetchall():
        print("  " + str(ext or '(sem extensao)').ljust(12) + " | " + str(qtd).rjust(5) + " arquivos | " + str(tam))
    
    print("\n🐘 Maiores arquivos:")
    cursor.execute("""
        SELECT filename, pg_size_pretty(size_bytes), path
        FROM files 
        ORDER BY size_bytes DESC 
        LIMIT 5
    """)
    for nome, tam, caminho in cursor.fetchall():
        print("  " + str(tam).rjust(10) + " | " + str(nome[:40]))
    
    print("\n🕐 Ultimas varreduras:")
    cursor.execute("""
        SELECT root_path, total_files, duplicates_found, scanned_at
        FROM scans 
        ORDER BY scanned_at DESC 
        LIMIT 3
    """)
    for pasta, arqs, dup, data in cursor.fetchall():
        print("  " + str(data) + ": " + str(arqs) + " arquivos, " + str(dup) + " duplicatas")
    
    cursor.close()
    conn.close()
    print("=" * 50)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python3 apps/scanner/scanner_db.py <caminho_da_pasta>")
        print("Exemplo: python3 apps/scanner/scanner_db.py /mnt/c/Users/SeuNome/Documents")
        sys.exit(1)
    
    pasta = sys.argv[1]
    if not os.path.exists(pasta):
        print("❌ Pasta nao existe: " + pasta)
        sys.exit(1)
    
    escanear(pasta)
    gerar_relatorio()
