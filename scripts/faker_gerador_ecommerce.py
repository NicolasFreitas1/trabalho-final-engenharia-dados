import random
import pandas as pd
from faker import Faker

fake = Faker('pt_BR')
Faker.seed(0)
random.seed(0)

def gerar_clientes(n):
    return pd.DataFrame([{
        'id': i,
        'nome': fake.name(),
        'email': fake.email(),
        'telefone': fake.phone_number()
    } for i in range(1, n+1)])

def gerar_produtos(n):
    return pd.DataFrame([{
        'id': i,
        'nome': fake.word().capitalize(),
        'preco': round(random.uniform(10, 1000), 2),
        'categoria_id': random.randint(1, 100)
    } for i in range(1, n+1)])

def gerar_enderecos(n):
    return pd.DataFrame([{
        'id': i,
        'cliente_id': random.randint(1, 3000),
        'endereco': fake.address().replace("\n", ", ")
    } for i in range(1, n+1)])

def gerar_pedidos(n):
    return pd.DataFrame([{
        'id': i,
        'cliente_id': random.randint(1, 3000),
        'data': fake.date_this_year(),
        'status': random.choice(['pendente', 'pago', 'enviado', 'entregue', 'cancelado'])
    } for i in range(1, n+1)])

def gerar_itens_pedido(n):
    return pd.DataFrame([{
        'id': i,
        'pedido_id': random.randint(1, 5000),
        'produto_id': random.randint(1, 1000),
        'quantidade': random.randint(1, 5)
    } for i in range(1, n+1)])

def gerar_pagamentos(n):
    return pd.DataFrame([{
        'id': i,
        'pedido_id': random.randint(1, 5000),
        'valor': round(random.uniform(20, 3000), 2),
        'metodo': random.choice(['boleto', 'cartao_credito', 'pix'])
    } for i in range(1, n+1)])

def gerar_transportadoras(n):
    return pd.DataFrame([{
        'id': i,
        'nome': fake.company(),
        'prazo_entrega_dias': random.randint(1, 15)
    } for i in range(1, n+1)])

def gerar_entregas(n):
    return pd.DataFrame([{
        'id': i,
        'pedido_id': random.randint(1, 5000),
        'transportadora_id': random.randint(1, 200),
        'data_envio': fake.date_this_year(),
        'data_entrega': fake.date_this_year()
    } for i in range(1, n+1)])

def gerar_categorias(n):
    return pd.DataFrame([{
        'id': i,
        'nome': fake.word().capitalize()
    } for i in range(1, n+1)])

def gerar_avaliacoes_produto(n):
    return pd.DataFrame([{
        'id': i,
        'cliente_id': random.randint(1, 3000),
        'produto_id': random.randint(1, 1000),
        'nota': random.randint(1, 5),
        'comentario': fake.sentence()
    } for i in range(1, n+1)])

def gerar_carrinhos_abandonados(n):
    return pd.DataFrame([{
        'id': i,
        'cliente_id': random.randint(1, 3000),
        'produto_id': random.randint(1, 1000),
        'data': fake.date_this_year()
    } for i in range(1, n+1)])

# Geração dos datasets
tabelas = {
    "clientes": gerar_clientes(3000),
    "produtos": gerar_produtos(1000),
    "enderecos": gerar_enderecos(2000),
    "pedidos": gerar_pedidos(5000),
    "itens_pedido": gerar_itens_pedido(4000),
    "pagamentos": gerar_pagamentos(2000),
    "transportadoras": gerar_transportadoras(200),
    "entregas": gerar_entregas(2000),
    "categorias": gerar_categorias(100),
    "avaliacoes_produto": gerar_avaliacoes_produto(1500),
    "carrinhos_abandonados": gerar_carrinhos_abandonados(200)
}

# Exportar para CSV
for nome, df in tabelas.items():
    df.to_csv(f"{nome}.csv", index=False)

