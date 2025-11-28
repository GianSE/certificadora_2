# 🌡️ Sistema de Monitoramento IoT - Arquitetura MVC

> **Desenvolvido por:** Gian
> **Contexto:** Projeto Acadêmico (Certificadora)

Este projeto é um sistema completo de monitoramento ambiental (Temperatura e Umidade) baseado em IoT (Internet das Coisas). Ele captura dados de sensores em tempo real, transmite via protocolo MQTT e oferece visualização multi-plataforma (Desktop e Web), com persistência histórica em banco de dados.

---

## 🚀 Funcionalidades Principais

* **📡 Coleta em Tempo Real:** Leitura de sensores DHT22 via ESP32 (Simulação Wokwi).
* **🔄 Arquitetura Modular:** Separação clara entre Dados (Model), Conexão (Service) e Interfaces (View).
* **💾 Persistência de Dados:** Histórico salvo automaticamente no MariaDB usando ORM (SQLAlchemy).
* **💻 Interface Desktop:** Aplicação nativa Windows usando `Tkinter` e gráficos estáticos com `Matplotlib`.
* **🌍 Interface Web (Mobile):** Dashboard moderno usando `Flask` e gráficos dinâmicos com `Chart.js`, acessível pelo celular na mesma rede Wi-Fi.
* **🛡️ Robustez:** Sistema "Graceful Degradation" (continua funcionando em memória RAM mesmo se o banco de dados cair).

---

## 🛠️ Tecnologias Utilizadas

### Backend & Core
* **Python 3.12+**
* **SQLAlchemy:** ORM para gerenciamento do Banco de Dados.
* **MariaDB Connector:** Driver oficial para conexão com o banco.
* **Paho-MQTT:** Cliente para comunicação com o broker IoT.
* **Pandas:** Manipulação de dados e buffer em memória.

### Frontend
* **Flask:** Servidor Web leve.
* **Chart.js:** Biblioteca JavaScript para gráficos animados.
* **Tkinter:** GUI nativa do Python.
* **Matplotlib:** Plotagem de gráficos científicos (Desktop).

### Hardware / IoT
* **ESP32:** Microcontrolador (Simulado).
* **MicroPython:** Linguagem utilizada no firmware do ESP32.
* **Wokwi:** Plataforma de simulação de eletrônica.

---

## 📂 Estrutura do Projeto

O projeto segue padrões de **Clean Architecture** e **MVC**:

```text
📁 certificadora_2/
│
├── 📄 launcher.py       # Ponto de entrada (Menu Principal com detecção de IP)
├── 📄 config.py         # Configurações sensíveis (Senhas, Hosts, Portas)
│
├── 🧱 Camada de Dados
│   ├── 📄 database.py   # Gerenciamento de conexão SQL (SQLAlchemy)
│   └── 📄 model.py      # Lógica de negócios e gerenciamento de filas
│
├── 📡 Camada de Serviço
│   └── 📄 service.py    # Cliente MQTT (Recebe dados do ESP32)
│
├── 🖥️ Camada de Interface (Views)
│   ├── 📄 desktop_app.py # Aplicação Desktop (Tkinter)
│   ├── 📄 app_flask.py   # Servidor Web (Flask)
│   └── 📁 templates/
│        └── 📄 index.html # Frontend Web (HTML + JS + Chart.js)
```

## ⚙️ Instalação e Configuração
### 1. Pré-requisitos
Certifique-se de ter instalado:

Python 3.x

MariaDB Server

### 2. Instalação das Dependências
No terminal, execute:

```bash
    pip install flask sqlalchemy mariadb pandas paho-mqtt matplotlib
```

### 3. Configuração do Banco de Dados
Abra seu gerenciador SQL (HeidiSQL, Workbench).

O sistema cria a tabela automaticamente, mas certifique-se de que o serviço MariaDB esteja rodando.

Edite o arquivo config.py com suas credenciais:

```bash
DB_USER = "root"
DB_PASS = "" # Sua senha
```

## ▶️ Como Executar

Inicie o Painel de Controle: Execute o arquivo principal na raiz do projeto:

```bash
    python launcher.py
```

Escolha o Modo:

### 🌍 Servidor Flask: Inicia o servidor web e abre o navegador automaticamente. Use o IP exibido para acessar pelo celular.

### 💻 Interface Desktop: Abre a janela nativa do Windows para monitoramento local.

Inicie a Simulação (IoT):

Acesse o projeto no Wokwi.com.

Certifique-se de que o código MicroPython do ESP32 está apontando para o mesmo tópico MQTT (gian/projeto/sensor).

Dê "Play" na simulação.

## 📊 Diagrama de Fluxo de Dados

```mermaid
graph TD
    %% Estilos
    classDef sensor fill:#ffeba1,stroke:#d4b106,color:black;
    classDef controller fill:#c6e2ff,stroke:#005cbf,color:black;
    classDef model fill:#d4edda,stroke:#28a745,color:black;
    classDef view fill:#f8d7da,stroke:#dc3545,color:black;
    classDef db fill:#e2e3e5,stroke:#383d41,color:black;

    %% Nós
    Sensor([📡 ESP32 / Wokwi]) ::: sensor
    Broker(☁️ Mosquitto MQTT) ::: sensor
    
    %% Camadas do Software
    subgraph Controller_Layer [Controller / Service]
        Service[service.py] ::: controller
    end

    subgraph Model_Layer [Model & Data]
        Model[model.py] ::: model
        DatabaseLib[database.py] ::: model
        Queue{Fila Thread-Safe} ::: model
    end

    subgraph Persistence_Layer [Persistência]
        MariaDB[(🗄️ MariaDB)] ::: db
    end

    subgraph View_Layer [Views / Interfaces]
        Flask[🌍 Flask Server] ::: view
        Tkinter[💻 Tkinter App] ::: view
    end

    %% Ligações
    Sensor --> Broker
    Broker -- "Subscrição" --> Service
    Service -- "Dados Crus" --> Model
    
    Model -- "Validação" --> Queue
    Model -- "Validação" --> DatabaseLib
    
    DatabaseLib -- "SQL Insert" --> MariaDB
    
    Queue --> Flask
    Queue --> Tkinter
```