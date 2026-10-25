# ⚡ Veltora — Gerador de Sites + CRM para Prospecção Local

> Ferramenta completa para agências e freelancers gerarem sites profissionais para negócios locais e automatizarem a prospecção via WhatsApp.

![Preview](https://img.shields.io/badge/Status-Ativo-green) ![License](https://img.shields.io/badge/Licen%C3%A7a-MIT-blue) ![Language](https://img.shields.io/badge/Stack-HTML%20%7C%20JS%20%7C%20Python%20%7C%20Node.js-purple)

---

## 🎯 O que é

O **Veltora** foi criado para agências digitais que fazem prospecção ativa de negócios locais (barbearias, restaurantes, clínicas, etc.). Em segundos você:

1. Gera um site profissional completo para o cliente
2. Cria a mensagem de abordagem no WhatsApp
3. Gerencia todo o funil de leads no CRM integrado
4. (Opcional) Automatiza o envio via bot WhatsApp com IA

---

## 🛠️ Componentes

| Arquivo | Descrição |
|---|---|
| `index.html` | Landing page de vendas (acesso vitalício por R$25) |
| `tool.html` | Painel principal: gerador + CRM (protegido por código) |
| `admin.html` | Painel admin para gerar códigos de acesso |
| `site_gen.py` | Gerador de sites em Python (20+ categorias) |
| `mockup.py` | Gerador de mensagens de prospecção WA |
| `bot-v2.mjs` | Bot WhatsApp com Baileys + IA Groq |

---

## 🚀 Como usar

### Ferramenta Web (sem instalação)
1. Abra `index.html` no navegador
2. Acesse `tool.html` com seu código de acesso
3. Preencha os dados do negócio → clique em **Gerar Site**
4. Copie a mensagem WA e entre em contato

### Bot WhatsApp (Node.js)
```bash
# Instalar dependências
npm install @whiskeysockets/baileys

# Configurar variáveis (copiar .env.example → .env)
cp .env.example .env

# Rodar
node bot-v2.mjs
```

### Gerador Python
```bash
# Gerar site de uma barbearia em Curitiba
python site_gen.py

# Gerar mensagem de prospecção
python mockup.py
```

---

## ⚙️ Categorias suportadas

Barbearia · Cabeleireiro · Estética · Clínica Médica · Odontologia · Restaurante · Pizzaria · Lanchonete · Academia · Imobiliária · Pet Shop · Farmácia · Oficina Mecânica · Advocacia · Padaria · Mercado · Hotel · e mais...

---

## 📋 CRM de Leads

O `tool.html` inclui um CRM completo com:
- ✅ Status: Novo → Abordado → Viu o site → Interessado → Vendido / Perdido
- 📊 Estatísticas em tempo real
- 📤 Import/Export CSV
- 💬 Geração automática de mensagem WA por lead

---

## 🔐 Sistema de acesso

O painel (`tool.html`) é protegido por código de acesso. O `admin.html` gera os códigos com validação SHA-256 — sem backend necessário.

---

## 📄 Licença

MIT — use, modifique e distribua livremente.

---

Feito com ☕ no Brasil 🇧🇷
