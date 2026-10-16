import os, html, yaml
E = html.escape

def define_env(env):
    docs = env.conf['docs_dir']
    root = os.path.dirname(env.conf['config_file_path'])

    def titre(p, d):
        try:
            for l in open(p, encoding='utf-8'):
                if l.startswith('# '):
                    return l[2:].strip()
        except OSError:
            pass
        return d

    def charge(n):
        return yaml.safe_load(open(os.path.join(root, 'data', n + '.yml'), encoding='utf-8')) or []

    def fichiers(d):
        return sorted(f for f in os.listdir(d) if f.endswith('.md') and f != 'index.md')

    @env.macro
    def cours_cards():
        base = os.path.join(docs, 'cours')
        out = ['<div class="grid cards" markdown>', '']
        for d in sorted(os.listdir(base)):
            p = os.path.join(base, d)
            if os.path.isdir(p):
                n = len(fichiers(p))
                out += [f'-   📗 **[{titre(os.path.join(p, "index.md"), d)}]({d}/index.md)**', '',
                        f'    {n} module{"s" if n > 1 else ""}', '']
        return '\n'.join(out + ['</div>'])

    @env.macro
    def liste_pages():
        d = os.path.dirname(os.path.join(docs, env.page.file.src_path))
        fs = fichiers(d)
        if not fs:
            return '!!! info "Rien ici pour l\'instant"\n    Ajoute une page avec `python scripts/nouveau.py` (voir « Ajouter du contenu »).'
        return '\n'.join(f'- [{titre(os.path.join(d, f), f)}]({f})' for f in fs)

    def filtre(items, theme):
        sel = lambda c, lab, vals: (f'<select class="{c}" aria-label="{lab}"><option value="">{lab}</option>'
                                    + ''.join(f'<option>{E(v)}</option>' for v in vals) + '</select>')
        cats = sorted({i['c'] for i in items if i.get('c')})
        ths = sorted({i['t'] for i in items if i.get('t')})
        h = ['<div data-filtre class="filtre"><div class="f-barre">',
             '<input class="f-q" type="search" placeholder="Terme, mot-clé…" aria-label="Rechercher">',
             sel('f-cat', 'Toutes les catégories', cats)]
        if theme:
            h.append(sel('f-theme', 'Tous les thèmes', ths))
        h += ['</div><div class="f-lettres"></div><p class="f-n"></p><div class="f-liste">']
        for i in sorted(items, key=lambda i: i['n'].lower()):
            c, t = i.get('c', ''), i.get('t', '')
            s = ' '.join([i['n'], i.get('d', ''), c, t, ' '.join(i.get('g', []))]).lower()
            h.append(f'<article class="f-item" data-s="{E(s)}" data-c="{E(c)}" data-t="{E(t)}" data-l="{E(i["n"][0].upper())}">'
                     f'<h3>{E(i["n"])}</h3><p>{E(i.get("d", ""))}</p>')
            if i.get('x'):
                h.append(f'<pre><code>{E(i["x"])}</code></pre>')
            meta = ' · '.join(v for v in (c, t) if v)
            if meta:
                h.append(f'<p class="meta">{E(meta)}</p>')
            if i.get('g'):
                h.append('<p class="tags">' + ''.join(f'<span>{E(g)}</span>' for g in i['g']) + '</p>')
            h.append('</article>')
        return ''.join(h) + '</div></div>'

    env.macro(lambda nom: filtre(charge(nom), True), 'commandes')
    env.macro(lambda: filtre(charge('glossaire'), False), 'glossaire')
