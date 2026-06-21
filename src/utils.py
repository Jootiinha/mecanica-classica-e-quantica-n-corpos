import os

def _slugify_nome_arquivo(nome):
    nome_normalizado = "".join(
        caractere.lower() if caractere.isalnum() else "_"
        for caractere in nome
    )
    while "__" in nome_normalizado:
        nome_normalizado = nome_normalizado.replace("__", "_")
    return nome_normalizado.strip("_") or "simulacao"