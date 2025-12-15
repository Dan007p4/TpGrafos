# Quick Start - Comandos Essenciais

Guia rápido para executar o projeto do zero.

**Requisitos**: Apenas Java 17+ e Python 3.8+ (Maven é baixado automaticamente!)

## Setup (uma vez só)

### Windows:
```bash
# 1. Instalar dependências Python
cd python
pip install -r requirements.txt
cd ..

# 2. Configurar token do GitHub
# Edite: src/main/resources/application.yaml
# Coloque seu token na linha: token: SEU_TOKEN_AQUI

# 3. Compilar projeto Java
mvnw.cmd clean compile
```

### Linux/Mac:
```bash
# 1. Instalar dependências Python
cd python
pip install -r requirements.txt
cd ..

# 2. Configurar token do GitHub
# Edite: src/main/resources/application.yaml
# Coloque seu token na linha: token: SEU_TOKEN_AQUI

# 3. Compilar projeto Java
./mvnw clean compile
```

## Executar Análise Completa

### Windows:
```bash
# 1. Minerar dados e calcular métricas (~50 min)
mvnw.cmd exec:java -Dexec.mainClass="br.pucminas.grafos.GrafosApplication"

# 2. Gerar visualizações
cd python
python analysis_visualizer.py
python additional_analysis.py

# 3. (Opcional) Gerar relatório
python generate_report.py
```

### Linux/Mac:
```bash
# 1. Minerar dados e calcular métricas (~50 min)
./mvnw exec:java -Dexec.mainClass="br.pucminas.grafos.GrafosApplication"

# 2. Gerar visualizações
cd python
python analysis_visualizer.py
python additional_analysis.py

# 3. (Opcional) Gerar relatório
python generate_report.py
```

## Comandos em Uma Linha

### Windows:
```bash
# Setup completo
mvnw.cmd clean compile && cd python && pip install -r requirements.txt && cd ..

# Análise completa (após configurar token)
mvnw.cmd exec:java -Dexec.mainClass="br.pucminas.grafos.GrafosApplication" && cd python && python analysis_visualizer.py && python additional_analysis.py && python generate_report.py
```

### Linux/Mac:
```bash
# Setup completo
./mvnw clean compile && cd python && pip install -r requirements.txt && cd ..

# Análise completa (após configurar token)
./mvnw exec:java -Dexec.mainClass="br.pucminas.grafos.GrafosApplication" && cd python && python analysis_visualizer.py && python additional_analysis.py && python generate_report.py
```

## Verificar Resultados

```bash
# Listar figuras geradas
ls output/figures/

# Listar tabelas geradas
ls output/tables/

# Ver métricas estruturais
cat output/tables/table1_structural_metrics.csv
```

## Mudar Repositório

Edite `src/main/resources/application.yaml`:

```yaml
github:
  repository: facebook/react  # Troque para: vuejs/vue, microsoft/vscode, etc
```

Depois execute novamente:

**Windows:**
```bash
mvnw.cmd exec:java -Dexec.mainClass="br.pucminas.grafos.GrafosApplication"
cd python && python analysis_visualizer.py && python additional_analysis.py
```

**Linux/Mac:**
```bash
./mvnw exec:java -Dexec.mainClass="br.pucminas.grafos.GrafosApplication"
cd python && python analysis_visualizer.py && python additional_analysis.py
```

## Troubleshooting Rápido

**Erro 401**: Token inválido → Configure em `application.yaml`

**Rate limit**: Espere 1h ou reduza `maxPages` em `GrafosApplication.java`

**ModuleNotFoundError**: Execute `pip install -r requirements.txt` na pasta `python/`

**FileNotFoundError**: Execute scripts Python **de dentro da pasta python/**