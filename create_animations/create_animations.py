import os
import matplotlib.animation as animation
import matplotlib.pyplot as plt
import numpy as np


def renderizar_gif_cenario(nome_cenario, m1_texto, m2_texto, fator_velocidade=16):
    """Lê os arquivos de um cenário específico e gera o GIF correspondente."""
    caminho_posicoes = f"outputs/{nome_cenario}_posicoes.npy"
    caminho_cm = f"outputs/{nome_cenario}_centro_massa.npy"

    if not os.path.exists(caminho_posicoes):
        return

    # 1. CARREGA OS DADOS ESPECÍFICOS DO CENÁRIO
    historico_r = np.load(caminho_posicoes)
    historico_Rcm = np.load(caminho_cm)

    p1_dados = historico_r[:, 0, :]
    p2_dados = historico_r[:, 1, :]

    # 2. CONFIGURAR A JANELA DO GRÁFICO
    fig, ax = plt.subplots(figsize=(8, 6))

    todos_x = np.concatenate([p1_dados[:, 0], p2_dados[:, 0]])
    todos_y = np.concatenate([p1_dados[:, 1], p2_dados[:, 1]])
    margem = 50
    ax.set_xlim(np.min(todos_x) - margem, np.max(todos_x) + margem)
    ax.set_ylim(np.min(todos_y) - margem, np.max(todos_y) + margem)

    # Título dinâmico baseado no cenário atual
    titulo_formatado = nome_cenario.replace("_", " ").title()
    ax.set_title(f"Simulação: {titulo_formatado}", fontsize=12)
    ax.set_xlabel("Posição X")
    ax.set_ylabel("Posição Y")
    ax.grid(True, linestyle="--", alpha=0.6)

    # 3. CRIAR OS ELEMENTOS VISUAIS 
    (linha_p1,) = ax.plot(
        [], [], "b-", alpha=0.5, label=f"Partícula 1 (m1={m1_texto})"
    )
    (linha_p2,) = ax.plot(
        [], [], "r-", alpha=0.5, label=f"Partícula 2 (m2={m2_texto})"
    )

    (ponto_p1,) = ax.plot([], [], "bo", markersize=10)
    (ponto_p2,) = ax.plot([], [], "ro", markersize=6)
    (ponto_cm,) = ax.plot([], [], "gX", markersize=8, label="Centro de Massa")

    ax.legend(loc="upper right")

    # 4. FUNÇÃO DE ATUALIZAÇÃO
    def atualizar(num_quadro):
        linha_p1.set_data(p1_dados[:num_quadro, 0], p1_dados[:num_quadro, 1])
        linha_p2.set_data(p2_dados[:num_quadro, 0], p2_dados[:num_quadro, 1])

        ponto_p1.set_data([p1_dados[num_quadro, 0]], [p1_dados[num_quadro, 1]])
        ponto_p2.set_data([p2_dados[num_quadro, 0]], [p2_dados[num_quadro, 1]])

        ponto_cm.set_data(
            [historico_Rcm[num_quadro, 0]], [historico_Rcm[num_quadro, 1]]
        )

        return linha_p1, linha_p2, ponto_p1, ponto_p2, ponto_cm

    # 5. GERAR E SALVAR O ANIMAÇÃO COMO GIF 
    print(f"Renderizando quadros para o cenário: {nome_cenario}...")
    quadros_indices = np.arange(0, len(historico_r), fator_velocidade)

    ani = animation.FuncAnimation(
        fig, atualizar, frames=quadros_indices, interval=16, blit=True
    )

    nome_arquivo_gif = f"outputs/simulacao_{nome_cenario}.gif"
    ani.save(nome_arquivo_gif, writer="pillow", fps=60)

    plt.close()
    print(f" Salvo '{nome_arquivo_gif}'.\n")
    
if __name__ == "__main__":
    import yaml

    # Abre o YAML apenas para ler os nomes dos cenários e massas
    with open("config.yaml", "r", encoding="utf-8") as file:
        config = yaml.safe_load(file)

    print("=== Iniciando Renderização Visual dos GIFs ===")
    for cenario in config["cenarios"]:
        nome = cenario["nome"]
        m1_txt = str(cenario["m1"])
        m2_txt = str(cenario["m2"])

        # Gera o GIF lendo o .npy direto da pasta outputs
        renderizar_gif_cenario(nome, m1_txt, m2_txt, fator_velocidade=16)