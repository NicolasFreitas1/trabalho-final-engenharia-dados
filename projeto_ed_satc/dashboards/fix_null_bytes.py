#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Abrir o arquivo em modo binário
with open('dashboard_tabelas.py', 'rb') as f:
    raw = f.read()

# Remover null bytes
cleaned = raw.replace(b'\x00', b'')

# Salvar novamente em UTF-8
with open('dashboard_tabelas.py', 'wb') as f:
    f.write(cleaned)

print('Null bytes removidos com sucesso!') 