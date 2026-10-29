# Painel de Campanhas (Meta Ads)

Um painel simples, em uma pagina, para acompanhar uma campanha de anuncios da Meta (Facebook e Instagram) com a **sua** conta. Mostra:

- investimento, conversas, custo por conversa, cliques e CTR;
- grafico dia a dia;
- ranking de conjuntos de anuncios e de anuncios;
- comparacao com o custo-alvo que voce definir.

Funciona so de leitura: o painel **nao altera nada** na sua conta de anuncios.

## Como funciona

```
.env (seu token)  ->  atualizar_painel.py  ->  grava os numeros dentro do dashboard.html
```

Nao tem servidor nem banco. Voce roda o script quando quiser atualizar e abre o `dashboard.html` no navegador.

Ao abrir o `dashboard.html` pela primeira vez voce ve **dados de exemplo** (marcados com um aviso amarelo). Eles somem assim que voce rodar o atualizador.

## Passo a passo

### 1. Pre-requisitos
- Conta no Meta Business com uma conta de anuncio.
- Python 3.9 ou superior.

### 2. Instalar
```bash
pip install -r requirements.txt
```

### 3. Gerar o seu token (uma vez so)
1. Entre em business.facebook.com e va em **Configuracoes do Negocio**.
2. **Usuarios > Usuarios do Sistema > Adicionar** (tipo Admin).
3. **Adicionar ativos**: selecione a sua conta de anuncio com permissao de leitura.
4. **Gerar novo token**, escolha o seu app (crie um gratuito em developers.facebook.com, tipo *Empresa*, se nao tiver) e marque a permissao `ads_read`.
5. Copie o token. Ele nao expira.

> O token e so seu. Nao envie por WhatsApp, nao cole em conversa com ninguem e nunca suba o arquivo `.env` no GitHub (ele ja esta no `.gitignore`).

### 4. Configurar
```bash
cp .env.example .env      # no Windows: copy .env.example .env
```
Abra o `.env` e preencha `META_ADS_TOKEN` e `META_AD_ACCOUNT` (formato `act_123...`).

### 5. Descobrir o ID da campanha
```bash
python atualizar_painel.py --campanhas
```
Copie o ID da campanha desejada para `META_CAMPANHA_ID` no `.env`.

### 6. Atualizar o painel
```bash
python atualizar_painel.py                    # ultimos 7 dias
python atualizar_painel.py --periodo last_30d # ou today, yesterday, last_14d, maximum
```
Abra o `dashboard.html` no navegador.

## Personalizar

| O que | Onde |
|---|---|
| Nome no topo | `PAINEL_NOME` no `.env` |
| Custo-alvo por conversa | `CUSTO_ALVO_CONVERSA` no `.env` (ex.: `8,50`) |
| Tipo de resultado contado | `META_ACAO_CONVERSA` no `.env`. Use `lead` para campanha de formulario |
| Cores e layout | bloco `<style>` do `dashboard.html` (acompanha modo claro e escuro) |

## Ideias para evoluir
- Agendar o `atualizar_painel.py` (Agendador de Tarefas do Windows ou `cron`) para atualizar sozinho.
- Cruzar com o seu CRM para ver quantas conversas viraram cliente.
- Pedir ao Claude Code para adicionar uma aba por produto ou por publico.

## Estrutura

```
.
├── dashboard.html        # o painel (abre no navegador)
├── atualizar_painel.py   # busca os dados na Meta e grava no painel
├── meta_ads.py           # cliente minimo da Graph API (somente leitura)
├── .env.example          # modelo de configuracao
├── requirements.txt
└── .gitignore
```
