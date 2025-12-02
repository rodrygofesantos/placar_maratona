# Placar de Maratona de Programação

Um sistema de placar em tempo real para competições de programação (estilo ICPC/Maratona SBC), desenvolvido em **Python** com **Streamlit**. O sistema possui cronômetro sincronizado, gestão de submissões, cálculo automático de penalidades e modo exclusivo para projeção (Telão).

![Status](https://img.shields.io/badge/Status-Funcional-brightgreen)
![Python](https://img.shields.io/badge/Python-3.8+-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.0+-red)

## Funcionalidades

* **Cronômetro Gigante:** Estilo digital (7 segmentos) que muda de cor (Verde para Vermelho) nos últimos 10 minutos.
* **Placar Automático:** Ordenação por número de problemas resolvidos e penalidade (tempo + tentativas).
* **Indicadores Visuais:** Balões coloridos para acertos e destaque "First to Solve" (primeira equipe a resolver o problema).
* **Modo Telão:** Visualização limpa e otimizada para projetores (fundo branco, sem menus).
* **Painel do Juiz:** Interface administrativa para cadastro de equipes, submissões e upload de logo.
* **Persistência de Dados:** Uso de banco de dados SQLite (o tempo e o placar não são perdidos se o computador desligar).

---

## Instalação

Siga os passos abaixo para rodar o projeto na sua máquina.

### 1. Pré-requisitos
Certifique-se de ter o **Python** instalado (versão 3.8 ou superior).

### 2. Clonar ou Baixar
Baixe os arquivos deste repositório para uma pasta no seu computador.

### 3. Instalar Dependências
Abra o terminal na pasta do projeto e instale as bibliotecas necessárias.
Recomenda-se criar um arquivo chamado `requirements.txt` com o conteúdo abaixo:

```text
streamlit
Pillow
```

Em seguida, execute o comando abaixo no terminal:

```bash
pip install -r requirements.txt
```

*(Caso prefira instalar manualmente sem o arquivo de texto, use: `pip install streamlit Pillow`)*

---

## Como Executar

Para iniciar o sistema, execute o seguinte comando no terminal dentro da pasta do projeto:

```bash
streamlit run app.py
```

*(Substitua `app.py` pelo nome do seu arquivo Python, caso você tenha salvo com outro nome).*

O sistema abrirá automaticamente no seu navegador padrão (geralmente em `http://localhost:8501`).

---

## Manual de Operação

O sistema possui dois modos de visualização: **Modo Juiz** (Admin) e **Modo Telão** (Projetor).

### 1. Painel do Juiz (Admin)
Ao abrir o sistema normalmente, você verá uma barra lateral à esquerda com as opções de controle.

* **Carregar Logo:** Faça upload de uma imagem (PNG/JPG) para personalizar o topo da página com a identidade visual do evento.
* **Cadastrar Equipe:**
    1. Clique no botão "Cadastrar Equipe".
    2. Insira o nome da equipe e os nomes dos 3 alunos.
    3. Clique em "Salvar".
* **Registrar Submissão:**
    1. Clique no botão "Registrar Submissão".
    2. Selecione a equipe na lista.
    3. Escolha o problema (A, B, C...).
    4. Defina o tempo (minuto da prova). *O sistema sugere o tempo atual automaticamente.*
    5. Defina o resultado: **Correto** ou **Erro**.
    6. Clique em "Registrar".
    *Nota: O sistema calcula automaticamente a penalidade e atualiza o ranking.*

### 2. Modo Telão (Projetor)
Para projetar o placar para os competidores sem mostrar os botões de administração:

1. Abra o sistema no navegador.
2. Adicione `?telao=1` ao final da URL na barra de endereços.
    * Exemplo: `http://localhost:8501/?telao=1`
3. Pressione `F11` para deixar o navegador em tela cheia.

**Diferenciais do Modo Telão:**
* Fundo branco para melhor contraste em projetores.
* Menu lateral oculto (impossibilita alterações acidentais).
* Atualização automática (auto-refresh) a cada 30 segundos.

### 3. Zona de Perigo (Reset)
No final da barra lateral do Admin, existem opções críticas marcadas em vermelho:

* **Reiniciar Prova:** Apaga todas as submissões e reinicia o cronômetro para 1h30, mas **mantém as equipes cadastradas**. Útil se precisar reiniciar a contagem de tempo.
* **ZERAR BANCO DE DADOS:** Apaga **TUDO** (equipes, submissões, configurações). O sistema volta ao estado zero.

---

## Tecnologias Utilizadas

* **Linguagem:** Python
* **Frontend/Framework:** Streamlit
* **Banco de Dados:** SQLite (Arquivo `maratona.db` gerado automaticamente pelo sistema)
* **Fontes:** DSEG7 (via CDN) para a renderização do relógio digital.

---

## Estrutura de Arquivos

```text
/
├── app.py              # Código fonte principal da aplicação
├── maratona.db         # Banco de dados (criado automaticamente após a 1ª execução)
├── requirements.txt    # Lista de dependências para instalação
├── README.md           # Este manual de instruções
└── logo_maratona.jpg   # (Opcional) Logo padrão caso não seja feito upload
```

---

## Dicas Importantes

1. **Persistência:** Se você fechar o navegador ou o terminal, o tempo da prova **continua correndo** no banco de dados. Ao abrir novamente, o relógio estará correto e sincronizado.
2. **Rede Local:** Para que outros computadores acessem o placar (se estiverem na mesma rede Wi-Fi), o Streamlit geralmente exibe uma "Network URL" no terminal (ex: `http://192.168.1.15:8501`). Use esse endereço no computador do projetor.
