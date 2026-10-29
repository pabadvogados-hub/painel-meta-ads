"""Cliente minimo da Meta Marketing API (Graph API) - somente leitura.

Configuracao por variaveis de ambiente (arquivo .env):
  META_ADS_TOKEN, META_AD_ACCOUNT, META_CAMPANHA_ID, META_ACAO_CONVERSA
"""
import os
import sys

import requests

BASE = 'https://graph.facebook.com/v21.0'
RAIZ = os.path.dirname(os.path.abspath(__file__))


def carregar_env(caminho=None):
    """Le o .env da pasta do projeto sem sobrescrever o que ja esta no ambiente."""
    caminho = caminho or os.path.join(RAIZ, '.env')
    if not os.path.exists(caminho):
        return
    with open(caminho, encoding='utf-8', errors='ignore') as f:
        for linha in f:
            linha = linha.strip()
            if '=' in linha and not linha.startswith('#'):
                k, v = linha.split('=', 1)
                os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


carregar_env()


def acao_conversa():
    return os.getenv('META_ACAO_CONVERSA') or 'onsite_conversion.messaging_conversation_started_7d'


def _get(caminho, params=None):
    token = os.getenv('META_ADS_TOKEN', '')
    if not token or token.startswith('COLE_AQUI'):
        sys.exit('META_ADS_TOKEN nao configurado. Copie .env.example para .env e preencha.')
    p = dict(params or {})
    p['access_token'] = token
    r = requests.get('%s/%s' % (BASE, caminho), params=p, timeout=60)
    if r.status_code != 200:
        try:
            msg = r.json().get('error', {}).get('message', r.text[:200])
        except Exception:
            msg = r.text[:200]
        sys.exit('Meta API %s: %s' % (r.status_code, msg))
    return r.json()


def insights(objeto, nivel='campaign', periodo='last_7d', dia_a_dia=False, campos=None):
    campos = campos or 'spend,impressions,reach,clicks,ctr,cpc,actions,cost_per_action_type'
    p = {'level': nivel, 'fields': campos, 'date_preset': periodo, 'limit': 500}
    if dia_a_dia:
        p['time_increment'] = 1
    return _get('%s/insights' % objeto, p).get('data', [])


def contar(actions, tipo=None):
    tipo = tipo or acao_conversa()
    for a in actions or []:
        if a.get('action_type') == tipo:
            return int(float(a['value']))
    return 0


def listar_campanhas(conta):
    return _get('%s/campaigns' % conta, {'fields': 'id,name,effective_status,objective', 'limit': 200}).get('data', [])
