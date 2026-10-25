"""Gera o SITE REAL (HTML premium e responsivo) do lead — o modelo clicável.
TEMPLATES POR CATEGORIA (baseado no print do usuário):
- Barbearia: dark theme, stats (+2.500 clientes, 4.9 avaliação), card flutuante "Agendamentos online"
- Clínica: clean/light, chips flutuantes (Atendimento online / Especialistas / Exames e vacinas)
- Imobiliária: barra de busca de imóveis, card flutuante, minis (verificados/especializado/financiamento)
- Academia: dark/energetic (rosa), chips flutuantes (Treinos personalizados / Acompanhamento / Resultados)
- Restaurante/Pizzaria/Lanchonete: light, menu Cardápio, CTA "Pedir agora"
- Demais categorias: template genérico premium
Cada categoria tem cores, frase-hero, menu e CTA próprios. Usa fotos reais do Pexels
(fotos.py) quando há chave; senão gradientes elegantes no lugar das fotos.
"""
import html as H
import unicodedata
import urllib.parse

try:
    import fotos
except ImportError:
    fotos = None

# chave -> (accent, accent2, theme, hero_query, sobre_query, servicos, frase, layout)
# theme: dark | clean | light ; layout: barber | clinic | realestate | gym | restaurant | generic
_CAT = {
    "barbea": ("#c9a24a", "#8a6d2f", "dark", "barber shop man haircut professional", "barber shop interior modern",
              [("✂️", "Corte masculino", "Estilo e precisão em cada corte."),
               ("🧔", "Barba", "Barba alinhada e bem cuidada."),
               ("🔥", "Combo completo", "Corte + barba com atendimento top."),
               ("⭐", "Experiência", "Ambiente pensado pra você relaxar.")],
              "Mais que um corte, uma experiência.", "barber"),
    "clinic": ("#0fa37f", "#0b7d61", "clean", "medical clinic doctor professional smiling", "modern medical clinic interior",
              [("🩺", "Consultas", "Atendimento humanizado e de qualidade."),
               ("⚕️", "Especialistas", "Profissionais de diversas áreas."),
               ("💉", "Exames e vacinas", "Tecnologia e precisão no diagnóstico."),
               ("📅", "Agendamento online", "Marque sua consulta pelo WhatsApp.")],
              "Sua saúde em boas mãos", "clinic"),
    "odontolog": ("#0fa37f", "#0b7d61", "clean", "dental clinic dentist smile", "modern dental clinic",
              [("🦷", "Clínica geral", "Saúde bucal completa e preventiva."),
               ("✨", "Estética dental", "Clareamento, lentes e um sorriso novo."),
               ("🩺", "Urgências", "Atendimento rápido quando você precisa."),
               ("😁", "Ortodontia", "Alinhe seu sorriso com conforto.")],
              "Seu sorriso em boas mãos", "clinic"),
    "estetic": ("#c07a86", "#9a5a66", "clean", "aesthetic clinic skincare beautiful woman", "spa beauty clinic interior",
              [("✨", "Estética facial", "Tratamentos que realçam sua beleza natural."),
               ("💆", "Limpeza de pele", "Pele renovada, saudável e radiante."),
               ("💉", "Harmonização", "Equilíbrio e beleza em cada detalhe."),
               ("🌿", "Bem-estar", "Um momento só seu, com todo o carinho.")],
              "Realce o que te faz única", "clinic"),
    "imobil": ("#5b6cff", "#3f4fd6", "light", "real estate modern house luxury", "real estate office professional",
              [("🏠", "Compra & venda", "O imóvel certo pra você."),
               ("🔑", "Locação", "Alugue com segurança e agilidade."),
               ("📈", "Avaliação", "Saiba o valor justo do seu imóvel."),
               ("🤝", "Assessoria", "Acompanhamento do início ao fim.")],
              "O imóvel ideal para o seu próximo capítulo.", "realestate"),
    "academ": ("#ff3d8b", "#d6246e", "dark", "gym fitness woman training workout", "modern gym interior equipment",
              [("🏋️", "Musculação", "Estrutura completa pra treinar."),
               ("🤸", "Aulas", "Diversas modalidades pra você."),
               ("🥗", "Acompanhamento", "Profissionais pra te orientar."),
               ("🔥", "Resultados", "Alcance seus objetivos com a gente.")],
              "Disciplina hoje, resultados sempre.", "gym"),
    "restaur": ("#e0612f", "#b8481f", "light", "restaurant food plate gourmet", "restaurant interior cozy",
              [("🍽️", "Pratos especiais", "Sabor preparado na hora pra você."),
               ("🛵", "Delivery", "Peça e receba quentinho em casa."),
               ("🎉", "Eventos", "Reserve para seu grupo ou ocasião."),
               ("⭐", "Ambiente", "Um espaço aconchegante pra todos.")],
              "Sabor que conquista", "restaurant"),
    "pizz": ("#e0612f", "#b8481f", "light", "pizza italian food delicious", "pizzeria interior cozy",
              [("🍕", "Pizzas", "Massa artesanal e recheios generosos."),
               ("🛵", "Delivery", "Pizza quentinha na sua porta."),
               ("🎉", "Promoções", "Ofertas especiais toda semana."),
               ("⭐", "Tradição", "O sabor que todo mundo ama.")],
              "A pizza que você ama", "restaurant"),
    "lanch": ("#e0612f", "#b8481f", "light", "burger food snack delicious", "snack bar interior",
              [("🍔", "Lanches", "Os melhores lanches da região."),
               ("🛵", "Delivery", "Entrega rápida, sabor garantido."),
               ("🥤", "Combos", "Combos que cabem no seu bolso."),
               ("⭐", "Qualidade", "Ingredientes fresquinhos sempre.")],
              "Matou a fome, matou a vontade", "restaurant"),
    "belez": ("#c07a86", "#9a5a66", "clean", "beauty salon skincare woman", "spa beauty salon interior",
              [("✨", "Estética facial", "Tratamentos que realçam sua beleza natural."),
               ("💆", "Limpeza de pele", "Pele renovada, saudável e radiante."),
               ("💅", "Design & cuidados", "Detalhes que fazem toda a diferença."),
               ("🌿", "Bem-estar", "Um momento só seu, com todo o carinho.")],
              "Realce o que te faz única", "clinic"),
    "cabele": ("#c07a86", "#9a5a66", "clean", "hair salon woman beauty", "hair salon interior modern",
              [("💇", "Cortes & estilo", "O visual perfeito pra você."),
               ("🎨", "Coloração", "Cores vivas e tratamento completo."),
               ("💆", "Tratamentos", "Cabelos saudáveis e brilhantes."),
               ("✨", "Dia da noiva", "Seu dia especial do jeito que merece.")],
              "Seu estilo, do seu jeito", "clinic"),
    "padaria": ("#c79233", "#9c6f1f", "light", "bakery bread pastry fresh", "bakery interior cozy",
              [("🥖", "Pães frescos", "Saídos do forno todos os dias."),
               ("🎂", "Confeitaria", "Bolos e doces pra adoçar seu dia."),
               ("☕", "Café da manhã", "Comece o dia com o melhor."),
               ("🛵", "Encomendas", "Peça pelo WhatsApp com facilidade.")],
              "Feito fresquinho pra você", "generic"),
    "oficina": ("#e0742a", "#b8571a", "light", "car mechanic auto repair garage", "auto repair shop professional",
              [("🔧", "Mecânica geral", "Revisão completa com garantia."),
               ("🛞", "Pneus & alinhamento", "Segurança na estrada."),
               ("🔋", "Elétrica", "Diagnóstico eletrônico preciso."),
               ("🛠️", "Manutenção", "Seu carro sempre em dia.")],
              "Seu carro em boas mãos", "generic"),
    "petshop": ("#1aa0bd", "#0f7d95", "clean", "pet shop dog cat grooming", "pet shop interior",
              [("🐶", "Banho & tosa", "Seu pet limpinho e cheiroso."),
               ("🏥", "Veterinário", "Saúde e cuidado pro seu amigo."),
               ("🦴", "Produtos", "Tudo que o seu pet precisa."),
               ("❤️", "Carinho", "Tratamos seu pet como família.")],
              "Quem ama, cuida", "generic"),
    "advoc": ("#2a5bb0", "#1d4488", "clean", "law office lawyer professional", "modern law office",
              [("⚖️", "Consultoria", "Orientação jurídica de confiança."),
               ("📄", "Contratos", "Segurança em cada documento."),
               ("🤝", "Atendimento", "Soluções pro seu caso."),
               ("🛡️", "Defesa", "Seus direitos bem representados.")],
              "Seus direitos, nossa prioridade", "generic"),
    "farmac": ("#13a873", "#0c8358", "clean", "pharmacy drugstore health", "modern pharmacy interior",
              [("💊", "Medicamentos", "Tudo que você precisa, pertinho."),
               ("🩹", "Cuidados", "Saúde e bem-estar no dia a dia."),
               ("🛵", "Entrega", "Receba em casa com rapidez."),
               ("💬", "Atendimento", "Tire suas dúvidas pelo WhatsApp.")],
              "Saúde e cuidado perto de você", "generic"),
    "mercado": ("#d4a017", "#a87d0e", "light", "supermarket grocery store", "grocery store interior",
              [("🛒", "Variedade", "De tudo um pouco pra sua casa."),
               ("💰", "Preço bom", "Ofertas que cabem no bolso."),
               ("🛵", "Delivery", "Sua compra na porta de casa."),
               ("⭐", "Qualidade", "Produtos fresquinhos sempre.")],
              "Tudo que você precisa, pertinho", "generic"),
    "hotel": ("#8a5fc0", "#6a4499", "clean", "hotel room luxury hospitality", "hotel lobby luxury",
              [("🛏️", "Conforto", "Quartos pensados pro seu descanso."),
               ("🍳", "Café incluso", "Comece bem o seu dia."),
               ("📶", "Estrutura", "Wi-Fi, estacionamento e mais."),
               ("⭐", "Atendimento", "Hospitalidade que faz diferença.")],
              "Sinta-se em casa", "generic"),
}

_DEFAULT = ("#b07a45", "#8a5d34", "light", "small business office professional", "modern office interior",
            [("⭐", "Qualidade", "Atendimento de excelência pra você."),
             ("⏱️", "Agilidade", "Rapidez no que realmente importa."),
             ("🤝", "Confiança", "Clientes satisfeitos é o nosso foco."),
             ("💬", "Atendimento", "Fale com a gente pelo WhatsApp.")],
            "Qualidade e confiança pra você", "generic")


def _norm(s):
    return unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode().lower()


def _cfg(categoria):
    c = _norm(categoria)
    for k, v in _CAT.items():
        if _norm(k) in c:
            return v
    return _DEFAULT


def _img(query, seed, cls, c1, c2):
    url = None
    if fotos:
        try:
            url = fotos.foto(query, seed)
        except Exception:
            url = None
    if url:
        return f'<div class="{cls} imgwrap"><img src="{H.escape(url)}" alt="" loading="lazy"></div>'
    return f'<div class="{cls} ph" style="background:linear-gradient(135deg,{c1},{c2})"></div>'


# Rótulos do menu e do botão principal por layout (igual ao print)
_MENU = {
    "barber":     (["Início", "Serviços", "Sobre", "Contato"], "Agendar"),
    "clinic":     (["Início", "Especialidades", "Equipe", "Depoimentos"], "Agendar consulta"),
    "realestate": (["Início", "Imóveis", "Sobre", "Contato"], "Falar com um corretor"),
    "gym":        (["Início", "Planos", "Treinos", "Sobre"], "Quero treinar"),
    "restaurant": (["Início", "Cardápio", "Sobre", "Contato"], "Pedir agora"),
    "generic":    (["Início", "Serviços", "Sobre", "Depoimentos"], "Fale conosco"),
}

_ANCHORS = {
    "Início": "#inicio", "Serviços": "#servicos", "Sobre": "#sobre", "Contato": "#contato",
    "Especialidades": "#servicos", "Equipe": "#sobre", "Depoimentos": "#depoimentos",
    "Imóveis": "#servicos", "Planos": "#servicos", "Treinos": "#sobre", "Cardápio": "#servicos",
}


def gerar_html(lead):
    nome = H.escape(lead.get("nome_fantasia") or lead.get("razao_social") or "Sua Empresa")
    cat_raw = lead.get("cnae_descricao") or ""
    cat = H.escape(cat_raw.capitalize())
    cidade = H.escape(lead.get("municipio") or "")
    tel = lead.get("telefone") or lead.get("whatsapp") or ""
    wa = "".join(c for c in str(tel) if c.isdigit())
    if wa and not wa.startswith("55"):
        wa = "55" + wa
    endereco = H.escape(lead.get("endereco") or "")
    seed = nome
    ac, ac2, theme, heroq, sobreq, servicos, frase, layout = _cfg(cat_raw)
    inicial = (nome.strip()[:1] or "S").upper()
    wa_link = (f"https://wa.me/{wa}?text=" if wa else "#contato")
    wa_attr = f'href="{wa_link}" target="_blank" rel="noopener"' if wa else 'href="#contato"'

    menu_items, cta_label = _MENU.get(layout, _MENU["generic"])
    nav_links = "".join(f'<a href="{_ANCHORS.get(m, "#")}">{m}</a>' for m in menu_items)
    drawer_links = "".join(f'<a href="{_ANCHORS.get(m, "#")}" onclick="mm()">{m}</a>' for m in menu_items)

    cards = "".join(
        f'<div class="svc reveal"><div class="svc-ic">{i}</div><h3>{H.escape(t)}</h3><p>{H.escape(d)}</p></div>'
        for i, t, d in servicos)

    hero_img = _img(heroq, seed, "hero-img", ac, ac2)
    sobre_img = _img(sobreq, seed + "s", "sobre-img", ac2, ac)

    _mq = " ".join(x for x in [lead.get("nome_fantasia") or lead.get("razao_social") or "",
                               lead.get("endereco") or "", lead.get("municipio") or "",
                               lead.get("uf") or ""] if x)
    mapa_q = urllib.parse.quote_plus(_mq)
    mapa_html = (
        f'<section class="mapa"><div class="wrap">'
        f'<div class="head reveal"><div class="eye">Localização</div>'
        f'<h2>Onde nos encontrar</h2></div>'
        f'<div class="mapwrap reveal"><iframe src="https://maps.google.com/maps?q={mapa_q}&z=15&output=embed" '
        f'loading="lazy" referrerpolicy="no-referrer-when-downgrade" title="Mapa"></iframe></div>'
        f'</div></section>') if (cidade or endereco) else ''

    # ---- variações de tema ----
    if theme == "dark":
        css_theme = (
            ":root{--ink:#f3f1ee;--mut:#a39e98;--bg:#161616;--card:#202020;--line:#2e2e2e}"
            "header{background:rgba(20,20,20,.9)}"
            ".servicos,.depo{background:#1b1b1b}.svc,.dcard{background:#222;border-color:#303030}"
            ".search-bar{background:#222;border-color:#333}.search-bar input{background:#1b1b1b;border-color:#333;color:#eee}"
            "footer{background:#0e0e0e}.btn-ghost{color:var(--ink);border-color:#3a3a3a}")
    elif theme == "clean":
        css_theme = ":root{--bg:#ffffff;--card:#f6f8f8}.servicos,.depo{background:#f6f8f8}"
    else:
        css_theme = ""

    # ---- blocos específicos por layout (hero) ----
    if layout == "barber":
        hero_extra = (
            '<div class="hero-stats">'
            '<div class="hs"><b>+2.500</b><span>clientes atendidos</span></div>'
            '<div class="hs"><b>4.9</b><span>avaliação média</span></div>'
            '<div class="hs"><b>100%</b><span>satisfação</span></div></div>')
        float_card = (
            '<div class="float-card"><span class="fc-ic">📅</span>'
            '<div><b>Agendamentos</b><span>online</span></div></div>')
        css_layout = (
            ".hero-stats{display:flex;gap:34px;margin-top:30px;flex-wrap:wrap}"
            ".hs b{font-family:'Playfair Display',serif;font-size:34px;color:var(--ac);display:block;line-height:1}"
            ".hs span{color:var(--mut);font-size:12.5px}"
            ".float-card{position:absolute;right:-14px;bottom:26px;background:#222;color:#fff;border-radius:16px;padding:14px 18px;"
            "display:flex;gap:12px;align-items:center;box-shadow:0 20px 40px -16px rgba(0,0,0,.6)}"
            ".float-card .fc-ic{width:38px;height:38px;border-radius:10px;background:var(--ac);display:grid;place-items:center;font-size:18px}"
            ".float-card b{display:block;font-size:14px}.float-card span{font-size:11.5px;color:#bbb}"
            ".hero-imgwrap{position:relative}")
    elif layout == "clinic":
        hero_extra = ""
        float_card = (
            '<div class="chip-list">'
            '<div class="chip"><span>🟢</span>Atendimento online</div>'
            '<div class="chip"><span>👥</span>Especialistas</div>'
            '<div class="chip"><span>💉</span>Exames e vacinas</div></div>')
        css_layout = (
            ".chip-list{position:absolute;right:-10px;top:50%;transform:translateY(-50%);display:flex;flex-direction:column;gap:12px}"
            ".chip{background:#fff;border:1px solid var(--line);border-radius:14px;padding:12px 16px;display:flex;gap:10px;align-items:center;"
            "font-weight:600;font-size:13.5px;box-shadow:0 14px 30px -16px rgba(0,0,0,.25);white-space:nowrap}"
            ".hero-imgwrap{position:relative}")
    elif layout == "realestate":
        hero_extra = (
            '<div class="search-bar"><div class="sb-row">'
            '<input type="text" placeholder="Buscar por cidade, bairro ou tipo de imóvel...">'
            '<button>🔍</button></div></div>'
            '<div class="minis" style="margin-top:22px">'
            '<div class="mini"><b>✓</b>Imóveis verificados</div>'
            '<div class="mini"><b>★</b>Atendimento especializado</div>'
            '<div class="mini"><b>♥</b>Financiamento facilitado</div></div>')
        float_card = (
            '<div class="float-card fc-light"><span class="fc-ic">🏠</span>'
            '<div><b>Lugares que</b><span>transformam vidas</span></div></div>')
        css_layout = (
            ".search-bar{background:#fff;border:1px solid var(--line);border-radius:16px;padding:8px;margin-top:28px;"
            "box-shadow:0 14px 34px -16px rgba(0,0,0,.18);max-width:520px}"
            ".sb-row{display:flex;gap:8px}.search-bar input{flex:1;padding:13px 16px;border:1px solid var(--line);border-radius:11px;font-size:14.5px}"
            ".search-bar button{padding:0 18px;background:var(--ac);color:#fff;border:none;border-radius:11px;font-size:16px;cursor:pointer}"
            ".float-card{position:absolute;right:-14px;bottom:26px;background:#1d2433;color:#fff;border-radius:16px;padding:14px 18px;"
            "display:flex;gap:12px;align-items:center;box-shadow:0 20px 40px -16px rgba(0,0,0,.5)}"
            ".float-card .fc-ic{width:38px;height:38px;border-radius:10px;background:var(--ac);display:grid;place-items:center;font-size:18px}"
            ".float-card b{display:block;font-size:14px}.float-card span{font-size:11.5px;color:#aab}"
            ".hero-imgwrap{position:relative}")
    elif layout == "gym":
        hero_extra = ""
        float_card = (
            '<div class="chip-list chip-dark">'
            '<div class="chip"><span>🏆</span>Treinos personalizados</div>'
            '<div class="chip"><span>👤</span>Acompanhamento profissional</div>'
            '<div class="chip"><span>📊</span>Resultados reais</div></div>')
        css_layout = (
            ".hero{background:radial-gradient(700px 400px at 80% 10%,rgba(255,61,139,.12),transparent 60%)}"
            ".chip-list{position:absolute;right:-10px;top:50%;transform:translateY(-50%);display:flex;flex-direction:column;gap:12px}"
            ".chip{background:#222;border:1px solid #333;color:#fff;border-radius:14px;padding:12px 16px;display:flex;gap:10px;align-items:center;"
            "font-weight:600;font-size:13.5px;box-shadow:0 14px 30px -16px rgba(0,0,0,.6);white-space:nowrap}"
            ".hero-imgwrap{position:relative}")
    else:
        hero_extra = (
            '<div class="minis" style="margin-top:26px">'
            '<div class="mini"><b>✓</b>Profissionais especializados</div>'
            '<div class="mini"><b>★</b>Atendimento de excelência</div>'
            '<div class="mini"><b>♥</b>Clientes satisfeitos</div></div>')
        float_card = ""
        css_layout = ""

    css_base = f"""
:root{{--ac:{ac};--ac2:{ac2};--ink:#2b2420;--mut:#7c726a;--bg:#fbf8f5;--card:#fff;--line:#eee6df}}
*{{margin:0;padding:0;box-sizing:border-box}}html{{scroll-behavior:smooth}}
body{{font-family:'Inter',system-ui,sans-serif;color:var(--ink);background:var(--bg);line-height:1.65}}
img{{display:block;max-width:100%}}a{{color:inherit;text-decoration:none}}
.wrap{{max-width:1120px;margin:0 auto;padding:0 22px}}
h1,h2,h3,.serif{{font-family:'Playfair Display',serif}}
.btn{{display:inline-flex;align-items:center;gap:8px;background:var(--ac);color:#fff;font-weight:600;padding:14px 26px;border-radius:999px;font-size:15px;transition:.2s;box-shadow:0 10px 26px -10px var(--ac);border:none;cursor:pointer}}
.btn:hover{{filter:brightness(1.07);transform:translateY(-2px)}}
.btn-ghost{{background:transparent;color:var(--ink);border:1px solid var(--line)}}
.eye{{color:var(--ac);font-weight:700;font-size:12.5px;letter-spacing:.16em;text-transform:uppercase;margin-bottom:14px}}
section{{padding:74px 0}}
header{{position:sticky;top:0;z-index:50;background:rgba(251,248,245,.88);backdrop-filter:blur(10px);border-bottom:1px solid var(--line)}}
.nav{{display:flex;align-items:center;justify-content:space-between;height:70px}}
.brand{{display:flex;align-items:center;gap:11px;font-weight:700}}
.brand .mk{{width:42px;height:42px;border-radius:12px;background:var(--ac);color:#fff;display:grid;place-items:center;font-family:'Playfair Display',serif;font-size:21px;font-weight:700}}
.brand b{{font-size:18px}}.brand span{{display:block;font-size:10.5px;letter-spacing:.14em;text-transform:uppercase;color:var(--mut);font-weight:600}}
.menu{{display:flex;gap:26px;align-items:center}}.menu a{{color:var(--mut);font-size:14.5px;font-weight:500}}.menu a:hover{{color:var(--ink)}}
.burger{{display:none;width:44px;height:44px;border-radius:12px;font-size:22px;background:rgba(0,0,0,.03);border:1px solid var(--line);color:var(--ink);cursor:pointer}}
.scrim{{position:fixed;inset:0;z-index:70;background:rgba(40,28,22,.42);backdrop-filter:blur(2px);opacity:0;visibility:hidden;transition:.25s}}
body.mopen .scrim{{opacity:1;visibility:visible}}
.mdrawer{{position:fixed;z-index:71;top:78px;right:14px;left:14px;max-width:360px;margin-left:auto;background:#fff;border:1px solid var(--line);border-radius:18px;box-shadow:0 30px 70px -20px rgba(40,25,15,.4);padding:10px;opacity:0;visibility:hidden;transform:translateY(-12px) scale(.98);transform-origin:top right;transition:.27s cubic-bezier(.3,.8,.3,1)}}
body.mopen .mdrawer{{opacity:1;visibility:visible;transform:none}}
.mdrawer a{{display:block;padding:14px 16px;color:var(--ink);border-radius:12px;font-weight:600;font-size:16px}}
.mdrawer a:active,.mdrawer a:hover{{background:color-mix(in srgb,var(--ac) 10%,#fff)}}.mdrawer .btn{{display:block;text-align:center;margin-top:6px;color:#fff}}
.hero{{padding:56px 0 70px;background:radial-gradient(700px 360px at 85% 0%,rgba(0,0,0,.025),transparent 60%)}}
.hero-grid{{display:grid;grid-template-columns:1.02fr .98fr;gap:46px;align-items:center}}
.hero h1{{font-size:clamp(34px,5vw,56px);font-weight:800;line-height:1.08;margin:6px 0 18px}}
.hero p.lead{{color:var(--mut);font-size:18px;max-width:520px;margin-bottom:26px}}
.hero-btns{{display:flex;gap:12px;flex-wrap:wrap}}
.minis{{display:flex;gap:24px;flex-wrap:wrap}}.mini{{display:flex;gap:10px;align-items:center;font-size:13.5px;color:var(--mut);font-weight:600}}
.mini b{{width:34px;height:34px;border-radius:10px;background:color-mix(in srgb,var(--ac) 14%,#fff);display:grid;place-items:center;font-size:17px;color:var(--ac)}}
.hero-img,.sobre-img{{border-radius:22px;overflow:hidden;aspect-ratio:4/4.2;box-shadow:0 30px 60px -24px rgba(60,40,30,.35)}}
.hero-img img,.sobre-img img{{width:100%;height:100%;object-fit:cover}}.ph{{border-radius:22px}}
.servicos{{background:#fff;border-top:1px solid var(--line);border-bottom:1px solid var(--line)}}
.head{{text-align:center;max-width:640px;margin:0 auto 46px}}.head h2{{font-size:clamp(27px,3.6vw,38px);font-weight:700;margin-bottom:12px}}.head p{{color:var(--mut)}}
.svc-grid{{display:grid;grid-template-columns:repeat(4,1fr);gap:20px}}
.svc{{background:var(--bg);border:1px solid var(--line);border-radius:18px;padding:26px 22px;text-align:center;transition:.25s}}
.svc:hover{{transform:translateY(-5px);box-shadow:0 20px 40px -20px rgba(60,40,30,.25);border-color:color-mix(in srgb,var(--ac) 40%,var(--line))}}
.svc-ic{{width:58px;height:58px;border-radius:16px;background:color-mix(in srgb,var(--ac) 12%,#fff);display:grid;place-items:center;font-size:27px;margin:0 auto 16px}}
.svc h3{{font-size:18px;margin-bottom:7px}}.svc p{{color:var(--mut);font-size:14px}}
.sobre-grid{{display:grid;grid-template-columns:.95fr 1.05fr;gap:46px;align-items:center}}
.sobre h2{{font-size:clamp(26px,3.6vw,38px);font-weight:700;margin:6px 0 16px}}.sobre p{{color:var(--mut);margin-bottom:14px}}
.stats{{display:flex;gap:30px;margin-top:26px;flex-wrap:wrap}}.stat b{{font-family:'Playfair Display',serif;font-size:32px;color:var(--ac);display:block}}.stat span{{color:var(--mut);font-size:13px}}
.depo{{background:#fff;border-top:1px solid var(--line);border-bottom:1px solid var(--line)}}
.depo-grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:20px}}
.dcard{{background:var(--bg);border:1px solid var(--line);border-radius:18px;padding:26px}}.dcard .stars{{color:#f2b705;margin-bottom:12px;font-size:15px}}
.dcard p{{font-size:14.5px;margin-bottom:16px}}.dcard .who{{display:flex;align-items:center;gap:11px}}
.dcard .av{{width:40px;height:40px;border-radius:50%;background:var(--ac);color:#fff;display:grid;place-items:center;font-weight:700}}
.dcard .who b{{font-size:14px;display:block}}.dcard .who span{{font-size:12px;color:var(--mut)}}
.cta{{text-align:center;background:linear-gradient(135deg,var(--ac),var(--ac2));color:#fff}}.cta h2{{font-size:clamp(26px,3.8vw,40px);margin-bottom:12px}}
.cta p{{opacity:.92;max-width:540px;margin:0 auto 26px}}.cta .btn{{background:#fff;color:var(--ac)}}
.mapwrap{{border-radius:18px;overflow:hidden;border:1px solid var(--line);box-shadow:0 20px 44px -22px rgba(60,40,30,.28)}}.mapwrap iframe{{width:100%;height:380px;border:0;display:block}}
footer{{background:#221c18;color:#cfc6bd;padding:48px 0 26px;font-size:14px}}.fgrid{{display:flex;justify-content:space-between;gap:30px;flex-wrap:wrap;margin-bottom:26px}}
footer .brand .mk{{background:var(--ac)}}footer .brand b,footer .brand{{color:#fff}}footer .ctt p{{margin-bottom:6px}}
.copy{{border-top:1px solid #3a322c;padding-top:20px;text-align:center;color:#8a7f75;font-size:12.5px}}
.wfloat{{position:fixed;right:18px;bottom:18px;z-index:60;width:58px;height:58px;border-radius:50%;background:#25d366;display:grid;place-items:center;box-shadow:0 10px 30px rgba(37,211,102,.5)}}
.badge{{position:fixed;left:14px;bottom:14px;background:#221c18;color:#cfc6bd;font-size:11px;padding:7px 12px;border-radius:999px;opacity:.9;z-index:60}}
.reveal{{opacity:0;transform:translateY(22px);transition:.6s}}.reveal.in{{opacity:1;transform:none}}
@media(max-width:900px){{.hero-grid,.sobre-grid{{grid-template-columns:1fr;gap:30px}}.svc-grid{{grid-template-columns:1fr 1fr}}.depo-grid{{grid-template-columns:1fr}}.menu{{display:none}}.burger{{display:block}}.sobre-img{{order:-1}}.chip-list,.float-card{{display:none}}}}
@media(max-width:560px){{.svc-grid{{grid-template-columns:1fr}}section{{padding:54px 0}}}}
{css_theme}
{css_layout}
"""

    return f"""<!doctype html><html lang="pt-BR"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{nome}{(' · ' + cidade) if cidade else ''}</title>
<meta name="description" content="{nome} — {cat or 'atendimento de qualidade'}{(' em ' + cidade) if cidade else ''}.">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700;800&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>{css_base}</style></head><body>
<header><div class="wrap nav">
<a href="#" class="brand"><span class="mk">{inicial}</span><div><b>{nome}</b><span>{cat or 'Qualidade & confiança'}</span></div></a>
<nav class="menu">{nav_links}<a class="btn" {wa_attr}>{cta_label}</a></nav>
<button class="burger" onclick="mm()" aria-label="menu">☰</button>
</div></header>
<div class="scrim" onclick="mm()"></div>
<nav class="mdrawer">{drawer_links}<a class="btn" {wa_attr}>{cta_label}</a></nav>
<section class="hero" id="inicio"><div class="wrap hero-grid">
<div>
<div class="eye">{cat or 'Atendimento personalizado'}{(' · ' + cidade) if cidade else ''}</div>
<h1>{frase}</h1>
<p class="lead">Na {nome}, cuidamos de cada detalhe com qualidade, dedicação e muito carinho pra você ter a melhor experiência.</p>
<div class="hero-btns"><a class="btn" {wa_attr}>{cta_label} →</a><a class="btn btn-ghost" href="#servicos">Nossos serviços</a></div>
{hero_extra}
</div>
<div class="hero-imgwrap">{hero_img}{float_card}</div>
</div></section>
<section class="servicos" id="servicos"><div class="wrap">
<div class="head reveal"><div class="eye">O que oferecemos</div><h2>Nossos serviços</h2><p>Conheça o que a {nome} preparou pra cuidar de você.</p></div>
<div class="svc-grid">{cards}</div>
</div></section>
<section class="sobre" id="sobre"><div class="wrap sobre-grid">
{sobre_img}
<div class="reveal"><div class="eye">Sobre nós</div>
<h2>Mais que {cat.lower() or 'um serviço'}, é dedicação</h2>
<p>A {nome} nasceu pra oferecer um atendimento diferente{(' aqui em ' + cidade) if cidade else ''}: feito com cuidado, atenção aos detalhes e foco total na sua satisfação.</p>
<p>Nosso compromisso é que você se sinta bem e saia com o melhor resultado — sempre.</p>
<div class="stats"><div class="stat"><b>+5</b><span>anos de experiência</span></div><div class="stat"><b>+3 mil</b><span>clientes atendidos</span></div><div class="stat"><b>100%</b><span>foco em você</span></div></div>
</div></div></section>
<section class="depo" id="depoimentos"><div class="wrap">
<div class="head reveal"><div class="eye">Depoimentos</div><h2>O que dizem sobre a gente</h2></div>
<div class="depo-grid">
<div class="dcard reveal"><div class="stars">★★★★★</div><p>"Atendimento impecável e resultado que superou minhas expectativas. Virei cliente fiel!"</p><div class="who"><span class="av">A</span><div><b>Ana Paula</b><span>Cliente</span></div></div></div>
<div class="dcard reveal"><div class="stars">★★★★★</div><p>"Profissionais atenciosos e um cuidado com cada detalhe. Recomendo de olhos fechados."</p><div class="who"><span class="av">C</span><div><b>Carlos Souza</b><span>Cliente</span></div></div></div>
<div class="dcard reveal"><div class="stars">★★★★★</div><p>"Ambiente acolhedor e serviço de altíssima qualidade. Só tenho a agradecer!"</p><div class="who"><span class="av">M</span><div><b>Mariana Lima</b><span>Cliente</span></div></div></div>
</div>
</div></section>
{mapa_html}
<section class="cta" id="contato"><div class="wrap reveal">
<h2>Pronto pra ser atendido pela {nome}?</h2>
<p>Fale com a gente agora mesmo pelo WhatsApp e agende o seu horário. Será um prazer te atender!</p>
<a class="btn" {wa_attr}>Falar no WhatsApp</a>
{('<p style="margin-top:20px;opacity:.9">📞 ' + H.escape(tel) + (' · 📍 ' + endereco if endereco else '') + '</p>') if tel else ''}
</div></section>
<footer><div class="wrap">
<div class="fgrid">
<div class="brand"><span class="mk">{inicial}</span><div><b>{nome}</b><span style="color:#8a7f75">{cat or ''}{(' · ' + cidade) if cidade else ''}</span></div></div>
<div class="ctt">{('<p>📞 ' + H.escape(tel) + '</p>') if tel else ''}{('<p>📍 ' + endereco + '</p>') if endereco else ''}<p>Atendimento todos os dias</p></div>
</div>
<div class="copy">© {nome} — Todos os direitos reservados.</div>
</div></footer>
<a class="wfloat" {wa_attr} aria-label="WhatsApp"><svg width="30" height="30" viewBox="0 0 24 24" fill="#fff"><path d="M.057 24l1.687-6.163a11.867 11.867 0 01-1.587-5.945C.16 5.335 5.495 0 12.05 0a11.82 11.82 0 018.413 3.488 11.82 11.82 0 013.48 8.414c-.003 6.557-5.338 11.892-11.893 11.892a11.9 11.9 0 01-5.688-1.448L.057 24zm6.597-3.807c1.676.995 3.276 1.591 5.392 1.592 5.448 0 9.886-4.434 9.889-9.885.002-5.462-4.415-9.89-9.881-9.892-5.452 0-9.887 4.434-9.889 9.884a9.86 9.86 0 001.51 5.26l-.999 3.648 3.978-1.615zm11.387-5.464c-.074-.124-.272-.198-.57-.347-.297-.149-1.758-.868-2.031-.967-.272-.099-.47-.149-.669.149-.198.297-.768.967-.941 1.165-.173.198-.347.223-.644.074-.297-.149-1.255-.462-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.297-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.074-.149-.669-1.611-.916-2.206-.242-.579-.487-.5-.669-.51l-.57-.01c-.198 0-.52.074-.792.372s-1.04 1.016-1.04 2.479 1.065 2.876 1.213 3.074c.149.198 2.095 3.2 5.076 4.487.709.306 1.263.489 1.694.626.712.226 1.36.194 1.872.118.571-.085 1.758-.719 2.006-1.413.248-.695.248-1.29.173-1.414z"/></svg></a>
<div class="badge">site modelo · Veltora</div>
<script>
const io=new IntersectionObserver(e=>e.forEach(x=>{{if(x.isIntersecting){{x.target.classList.add('in');io.unobserve(x.target)}}}}),{{threshold:.1}});
document.querySelectorAll('.reveal').forEach(e=>io.observe(e));
function mm(){{document.body.classList.toggle('mopen')}}
window.addEventListener('scroll',()=>{{if(document.body.classList.contains('mopen'))document.body.classList.remove('mopen')}},{{passive:true}});
</script>
</body></html>"""


if __name__ == "__main__":
    for cat_test in ["barbearia", "clinica medica", "imobiliaria", "academia", "restaurante"]:
        lead_test = {
            "nome_fantasia": {"barbearia": "Barber Pro", "clinica medica": "VitaClínica",
                              "imobiliaria": "HomePrime", "academia": "FitZone",
                              "restaurante": "Sabor & Cia"}[cat_test],
            "cnae_descricao": cat_test,
            "municipio": "Curitiba",
            "telefone": "41999999999",
            "endereco": "Rua das Flores, 123",
        }
        out = gerar_html(lead_test)
        print(f"{cat_test:18s} -> {len(out)} bytes")