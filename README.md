# Simulação de Interação Gravitacional 2D (N-Corpos)

Este projeto implementa um simulador numérico bidimensional para a interação gravitacional de N-corpos (focado inicialmente em problemas de 2 corpos). Desenvolvido com foco em arquitetura modular, o software separa o motor de cálculo físico da geração de animações.

---

## 🛠️ Pré-Requisitos e Instalação

1. Clone o repositório para a sua máquina local.
2. Certifique-se de ter o Python 3.10+ instalado.
3. Abra o terminal na raiz do projeto e execute os comandos abaixo:

### 1. Criar o Ambiente Virtual (venv)
```bash
python -m venv venv
```

# Ativação da venv (Windows)
```bash
.\venv\Scripts\activate
```
# Instalação dos pacotes obrigatórios
```bash
pip install -r requirements.txt
```
# Executar os calculos
```bash
python main.py
```
# Gerar animações
```
python src/create_animations.py
```
**Para alterar os cenários modifique diretamente o arquivo config.yaml**

## 🚀 Funcionalidades

- **Configuração Dinâmica:** Todos os cenários, massas, posições e velocidades iniciais são controlados centralizadamente por um arquivo `config.yaml`.
- **Motor Físico Otimizado:** Cálculos baseados na Lei da Gravitação Universal de Newton 
- **Renderização Eficiente:** Geração de animações `.gif` via Matplotlib 
- **Execução em Lote:** Capacidade de simular múltiplos cenários complexos de forma sequencial com um único comando.

---

## 📂 Estrutura do Projeto

O projeto adota uma estrutura modular para garantir que os dados brutos da física não poluam o código-fonte ou os arquivos de mídia gerados:

```text
MECANICA-CLASSICA-E-QUANTICA-N-CORPOS/
│
├── src/                          # Código fonte do projeto
│   ├── simulador_gravitacao.py   # Motor físico (equações de movimento)
│   ├── mecanica_problema_dois_corpos.py   #Simulação alternativa
│   └── create_animations.py      # Renderizador de gráficos e animações
│
├── config.yaml                   # Definição e parâmetros dos cenários
├── main.py                       # Orquestrador (calcula a física em lote)
├── requirements.txt              # Dependências do projeto (pip freeze)
│
├── outputs/                      # Arquivos gerados pela execução
│
└── venv/                         # Ambiente virtual Python