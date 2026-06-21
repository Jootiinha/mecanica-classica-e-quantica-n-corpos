import os
from src.performance_metrics import ExecutionProfiler, append_metrics_csv
from src.simulacao import simular_dois_corpos_3d


G = 1.0
eps = 0.03  # Evita que a forca fique infinita quando os corpos se aproximam muito.


def construir_casos():
    casos = []
    # Migrar para YAML's
    casos.append(
        {
            "nome": "Cenário 7 - Massas difernetes e Estrea com perda moderada",
            "G": G,
            "m1": 1.0,
            "m2": (1.0 / 333000.0),
            "eps": eps, # Parametro de suavização numérica da força gravitacional
            "r1":   [-0.5, 0.0, 0.0],
            "r2":   [3.0, 0.0, 0.0],
            "v1":   [0.0, 0.0, 0.0],
            "v2":   [0.0, 0.577, 0.0],
            "V_CM": [0.0, 0.0, 0.06], # Velocidade do centro de massa do objeto
            "massa_variavel": True,
            "tau1": 60.0, # Tempo característico de perda de massa dos corpos 1 e 2
            "tau2": 1000.0, # Tempo característico de perda de massa dos corpos 1 e 2
            "t_final": 700.0, # Tempo da simulação em segundos
            
            # Geração do vídeo
            "n_pontos": 4000,
            "fps": 30,
            "dpi": 200,
            "skip": 4,
            "skip_pillow": 12,
            "dpi_pillow": 90,
            "mostrar_grafico": False,
            "salvar_animacao": True
        }
    )
    return casos


def executar_simulacao_adhoc():
    casos = construir_casos()

    for caso in casos:
        simular_dois_corpos_3d(caso=caso)

    print(12 * "=")
    print("Final da simulação")
    print(12 * "=")

    return len(casos), "outputs"


if __name__ == "__main__":
    profiler = ExecutionProfiler()
    os.makedirs("outputs", exist_ok=True)
    run_label = os.environ.get("RUN_LABEL")

    scenario_count, output_dir = executar_simulacao_adhoc()
    metrics = profiler.finish(scenario_count=scenario_count, run_label=run_label)
    caminho_csv = append_metrics_csv(output_dir, metrics)

    print(f"Métricas salvas em: {caminho_csv}")
    print(f"Tempo total: {metrics.wall_time_seconds:.3f}s")
    print(f"Tempo de CPU: {metrics.cpu_time_seconds:.3f}s")
    if metrics.peak_memory_mb is not None:
        print(f"Pico de memória: {metrics.peak_memory_mb:.3f} MB")
