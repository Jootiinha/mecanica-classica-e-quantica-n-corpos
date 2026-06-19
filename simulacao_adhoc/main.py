from simulacao import simular_dois_corpos_3d

# Constantes
G = 1.0
eps = 0.03 # parametro de suavização numérica da f gravitacional - Evita que a força fique infinita quando os dois corpos se aproximam muito


casos = []
# Migrar para YAML's
casos.append(
    {
        "nome": "Cenário 1 - Massas iguais e próximas em repouso",
        "G": G,
        "m1": 1.0,
        "m2": 1.0,
        "eps": eps, # Parametro de suavização numérica da força gravitacional
        "r1": [-0.5, 0.0, 0.0],
        "r2": [0.5, 0.0, 0.0],
        "v1": [0.0, 0.0, 0.0],
        "v2": [0.0, 0.0, 0.0],
        "V_CM": [0.0, 0.0, 0.0], # Velocidade do centro de massa do objeto
        "massa_variavel": False,
        "tau1": 60.0, # Tempo característico de perda de massa dos corpos 1 e 2
        "tau2": 100.0, # Tempo característico de perda de massa dos corpos 1 e 2
        "t_final": 8.0, # Tempo da simulação em segundos
        
        # Geração do vídeo
        "n_pontos": 4000,
        "fps": 30,
        "dpi": 200,
        "skip": 4
    }
)

for caso in casos:
    resultado = simular_dois_corpos_3d(caso=caso)

print(12*"=")
print("Final da simulação")
print(12*'=')
