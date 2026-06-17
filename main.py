import os
import yaml
from simulador_gravitacao import simular_gravitacao__2d
import numpy as np
from create_animations.create_animations import renderizar_gif_cenario
def executar_simulacoes():
    # 1. Carrega as configurações do YAML
    with open("config.yaml", "r", encoding="utf-8") as file:
        config = yaml.safe_load(file)
    
    # Parâmetros globais padrão (caso o cenário não sobrescreva)
    g_global = config.get("g", 1500.0)
    passos_global = config.get("total_passos", 500)
    dt_global = config.get("dt", 0.016)

    # 2. Cria a pasta de saída se ela não existir
    pasta_saida = "outputs"
    os.makedirs(pasta_saida, exist_ok=True)

    print(f"=== Iniciando Processamento de {len(config['cenarios'])} Cenários ===")

    # 3. Itera por todos os cenários configurados no arquivo YAML
    for cenario in config["cenarios"]:
        nome = cenario["nome"]
        print(f"\nRodando física para: {nome}...")

        # Coleta os parâmetros individuais do cenário mapeado no YAML
        m1 = cenario["m1"]
        m2 = cenario["m2"]
        r1_init = cenario["r1_init"]
        r2_init = cenario["r2_init"]
        v1_init = cenario["v1_init"]
        v2_init = cenario["v2_init"]

        # Permite que cenários específicos tenham durações ou dts customizados, caso contrário usa o global
        total_passos = cenario.get("total_passos", passos_global)
        dt = cenario.get("dt", dt_global)
        g = cenario.get("g", g_global)

        hist_r, hist_Rcm, _ = simular_gravitacao__2d(
            g, m1, m2, r1_init, r2_init, v1_init, v2_init, total_passos, dt
        )

        caminho_posicoes = os.path.join(pasta_saida, f"{nome}_posicoes.npy")
        caminho_cm = os.path.join(pasta_saida, f"{nome}_centro_massa.npy")

        np.save(caminho_posicoes, hist_r)
        np.save(caminho_cm, hist_Rcm)

    print("simulações concluídas")

if __name__ == "__main__":
    executar_simulacoes()