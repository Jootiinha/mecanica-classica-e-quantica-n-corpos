import yaml

def load_scenarios(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return yaml.safe_load(file)

def _slugify_nome_arquivo(nome):
    nome_normalizado = "".join(
        caractere.lower() if caractere.isalnum() else "_"
        for caractere in nome
    )
    while "__" in nome_normalizado:
        nome_normalizado = nome_normalizado.replace("__", "_")
    return nome_normalizado.strip("_") or "simulacao"