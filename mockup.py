"""Gera a MENSAGEM de WhatsApp para o lead (a prévia agora é LINK, não imagem).
Abordagem reescrita para CONVERTER: curta, pessoal, prova social, curiosidade,
e uma pergunta de baixa fricção que a pessoa responde com "sim/quero/manda".
etapa 1 = abertura | 2 = mostra o modelo (link) | 3 = follow-up leve.
"""
import unicodedata


def _primeiro_nome(nome: str) -> str:
    n = (nome or "").strip()
    if not n:
        return ""
    return n.split()[0].capitalize()


# Frases de prova social / dor por categoria (substring normalizada -> frase)
_DOR = {
    "restaur": "quem tá com fome pesquisa no celular antes de escolher onde comer",
    "pizz": "quem quer pizza pesquisa no celular antes de pedir",
    "lanch": "quem tá com fome pesquisa no celular antes de pedir",
    "padaria": "quem quer pão fresquinho pesquisa no celular antes de sair de casa",
    "barbea": "quem quer cortar o cabelo pesquisa no celular antes de escolher a barbearia",
    "cabele": "quem quer cuidar do cabelo pesquisa no celular antes de escolher o salão",
    "belez": "quem quer se cuidar pesquisa no celular antes de escolher o lugar",
    "estetic": "quem quer se cuidar pesquisa no celular antes de escolher a clínica",
    "academ": "quem quer treinar pesquisa no celular antes de escolher a academia",
    "odontolog": "quem precisa de dentista pesquisa no celular antes de marcar",
    "clinic": "quem precisa de consulta pesquisa no celular antes de marcar",
    "petshop": "quem ama o pet pesquisa no celular antes de escolher onde cuidar dele",
    "oficina": "quem precisa de mecânico pesquisa no celular antes de levar o carro",
    "imobil": "quem busca imóvel pesquisa no celular antes de visitar",
    "advoc": "quem precisa de advogado pesquisa no celular antes de contratar",
    "farmac": "quem precisa de remédio pesquisa no celular antes de sair",
    "mercado": "quem faz compra pesquisa no celular antes de escolher o mercado",
    "hotel": "quem viaja pesquisa no celular antes de reservar onde ficar",
}


def _dor(categoria: str) -> str:
    c = unicodedata.normalize("NFKD", categoria or "").encode("ascii", "ignore").decode().lower()
    for k, v in _DOR.items():
        if k in c:
            return v
    return "hoje em dia todo mundo pesquisa no celular antes de escolher"


def gerar_mensagem(nome: str, categoria: str = "", cidade: str = "",
                   etapa: int = 1, agencia: str = "", responsavel: str = "") -> str:
    """Abordagem que converte: pessoal, curta, prova social, curiosidade,
    pergunta de baixa fricção. Usa nome do dono + da empresa + algo real."""
    cat = (categoria or "seu segmento").lower()
    local = f" aí em {cidade}" if cidade else ""
    dono = _primeiro_nome(responsavel)
    saud = f"Oi, {dono}! " if dono else "Oi! Tudo bem? "
    dor = _dor(categoria)

    if etapa == 2:
        # Enviada junto com o LINK do site (o bot manda o link logo após).
        return (
            f"Prontinho! 🙌 Montei uma *prévia do site da {nome}* — é só abrir o link 👆\n\n"
            f"É um modelo: dá pra mudar cores, textos, fotos e deixar com a cara de vocês. "
            f"O que achou? 😊"
        )

    if etapa == 3:
        return (
            f"{saud}Passando rapidinho pra saber se você conseguiu ver a prévia do site da *{nome}* 🙂\n\n"
            f"Se quiser, eu ajusto do seu jeito e já deixo no ar. Quer que eu te mostre os planos e valores?"
        )

    # etapa 1 — ABERTURA que converte
    # Estrutura: saudação pessoal -> quem sou -> o que vi (dor real) -> prova/curiosidade
    # -> entrega de valor grátis -> pergunta de baixa fricção ("posso te mandar?")
    return (
        f"{saud}\n\n"
        f"Aqui é da *Veltora* 👋 a gente ajuda empresas a aparecer no Google e vender mais pela internet.\n\n"
        f"Dei uma olhada na *{nome}*{local} e vi que vocês ainda *não têm um site* — e {dor}. 📱\n\n"
        f"Então eu já montei, *de graça*, uma prévia de como ficaria o site de vocês. Sem compromisso nenhum.\n\n"
        f"Posso te mandar pra você dar uma olhada? 👇"
    )


if __name__ == "__main__":
    print(gerar_mensagem("Barber Pro", "barbearia", "Curitiba"))
    print("---")
    print(gerar_mensagem("VitaClínica", "clinica medica", "Maringá", responsavel="Ana Silva"))