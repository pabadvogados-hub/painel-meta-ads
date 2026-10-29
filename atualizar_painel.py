"""Puxa os numeros da sua campanha na Meta e grava dentro do dashboard.html.

Uso:
  python atualizar_painel.py                  # atualiza o painel (ultimos 7 dias)
  python atualizar_painel.py --campanhas      # lista as campanhas da conta (para achar o ID)
  python atualizar_painel.py --periodo last_30d
Periodos: today, yesterday, last_7d, last_14d, last_30d, maximum
"""
import argparse
import json
import os
import re
from datetime import datetime

import meta_ads as meta

HTML = os.path.join(meta.RAIZ, 'dashboard.html')


def num(v):
    try:
        return float(v or 0)
    except (TypeError, ValueError):
        return 0.0


def linha(r):
    gasto = round(num(r.get('spend')), 2)
    conv = meta.contar(r.get('actions'))
    return {'gasto': gasto, 'conversas': conv,
            'custo': round(gasto / conv, 2) if conv else 0,
            'impressoes': int(num(r.get('impressions'))), 'alcance': int(num(r.get('reach'))),
            'cliques': int(num(r.get('clicks'))), 'ctr': round(num(r.get('ctr')), 2)}


def montar(campanha, periodo):
    total = meta.insights(campanha, 'campaign', periodo)
    conjuntos = []
    for r in meta.insights(campanha, 'adset', periodo, campos='adset_name,spend,impressions,clicks,ctr,actions'):
        d = linha(r)
        d['nome'] = r.get('adset_name', '?')
        conjuntos.append(d)
    anuncios = []
    for r in meta.insights(campanha, 'ad', periodo, campos='ad_name,spend,impressions,clicks,ctr,actions'):
        d = linha(r)
        d['nome'] = r.get('ad_name', '?')
        anuncios.append(d)
    serie = []
    for r in meta.insights(campanha, 'campaign', periodo, dia_a_dia=True, campos='spend,actions'):
        serie.append({'dia': r.get('date_start'), 'gasto': round(num(r.get('spend')), 2),
                      'conversas': meta.contar(r.get('actions'))})
    alvo = os.getenv('CUSTO_ALVO_CONVERSA', '').replace(',', '.').strip()
    return {'demo': False, 'nome': os.getenv('PAINEL_NOME') or 'Minha campanha', 'periodo': periodo,
            'atualizado': datetime.now().strftime('%d/%m/%Y %H:%M'),
            'alvo': float(alvo) if alvo else None,
            'total': linha(total[0]) if total else linha({}),
            'conjuntos': sorted(conjuntos, key=lambda x: -x['conversas']),
            'anuncios': sorted(anuncios, key=lambda x: -x['conversas']), 'serie': serie}


def gravar(dados):
    with open(HTML, encoding='utf-8') as f:
        html = f.read()
    bloco = '/*DADOS*/ const DATA = %s; /*FIM*/' % json.dumps(dados, ensure_ascii=False)
    novo, n = re.subn(r'/\*DADOS\*/.*?/\*FIM\*/', lambda _: bloco, html, count=1, flags=re.S)
    if n != 1:
        raise SystemExit('Marcadores /*DADOS*/ ... /*FIM*/ nao encontrados no dashboard.html')
    with open(HTML, 'w', encoding='utf-8') as f:
        f.write(novo)
    with open(os.path.join(meta.RAIZ, 'dados.json'), 'w', encoding='utf-8') as f:
        json.dump(dados, f, ensure_ascii=False, indent=1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--campanhas', action='store_true')
    ap.add_argument('--periodo', default='last_7d')
    a = ap.parse_args()
    conta = os.getenv('META_AD_ACCOUNT', '')
    if a.campanhas:
        for c in meta.listar_campanhas(conta):
            print('%-20s %-10s %s' % (c['id'], c.get('effective_status', ''), c.get('name', '')))
        return
    camp = os.getenv('META_CAMPANHA_ID', '').strip()
    if not camp:
        raise SystemExit('Defina META_CAMPANHA_ID no .env (use --campanhas para listar os IDs).')
    d = montar(camp, a.periodo)
    gravar(d)
    t = d['total']
    print('Painel atualizado: gasto R$ %.2f | %d conversas | R$ %.2f por conversa' % (t['gasto'], t['conversas'], t['custo']))
    print('Abra o dashboard.html no navegador.')


if __name__ == '__main__':
    main()
