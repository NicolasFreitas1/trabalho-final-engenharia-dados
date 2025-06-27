#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Tentar diferentes encodings
encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']

for encoding in encodings:
    try:
        with open('dashboard_tabelas_backup.py', 'r', encoding=encoding) as f:
            content = f.read()
        
        # Escrever o arquivo com encoding UTF-8
        with open('dashboard_tabelas.py', 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"Encoding corrigido com sucesso usando {encoding}!")
        break
    except UnicodeDecodeError:
        print(f"Falhou com encoding {encoding}")
        continue
else:
    print("Não foi possível corrigir o encoding") 