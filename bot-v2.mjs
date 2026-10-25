// LeadBot v2 — Veltora (Baileys + Groq).
// Abertura suave em 2 etapas + follow-up automático após 1h sem resposta.
// Geração de site DESATIVADA: quem quer ver recebe msg de "encaminhado ao time".
// Prompt humanizado; fechamento em 2 tempos; anti bot-vs-bot.

import makeWASocket, {
  useMultiFileAuthState, fetchLatestBaileysVersion, DisconnectReason,
} from '@whiskeysockets/baileys';
import pino from 'pino';
import QRCode from 'qrcode';
import fs from 'node:fs';
import { fileURLToPath } from 'node:url';
import path from 'node:path';

const DIR = path.dirname(fileURLToPath(import.meta.url));
const API = process.env.LH_API || 'http://127.0.0.1:8010';
const TOKEN = process.env.LH_TOKEN || '';
const PAIR_NUMBER = (process.env.PAIR_NUMBER || '').replace(/\D/g, '');
const MODE = process.env.MODE || 'idle';
const TEST_TO = (process.env.TEST_TO || '').replace(/\D/g, '');
const DELAY_MS = parseInt(process.env.DELAY_MS || '60000', 10);
const GROQ_KEY = process.env.GROQ_API_KEY || '';
const GROQ_MODEL = process.env.GROQ_MODEL || 'openai/gpt-oss-120b';
const SITE_BASE = process.env.SITE_BASE || 'https://veltoradigitais.com.br';
const OWNER_NUM = process.env.OWNER_WHATS || '5544998458841';
const LIMITE_DIA = parseInt(process.env.LIMITE_DIA || '24', 10);
const FOLLOWUP_DELAY = parseInt(process.env.FOLLOWUP_DELAY || '3600000', 10);

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const log = (...a) => console.log(new Date().toISOString(), ...a);
const corta = (s, n = 140) => (s || '').replace(/\n/g, ' ').slice(0, n);

function planosMsg(nome) {
  return (
    `Temos 3 planos pra deixar a *${nome}* online 👇\n\n` +
    `🟢 *ESSENCIAL — R$197* _(3x de R$69)_\n` +
    `Site de 1 página, botão WhatsApp, Google Maps e otimização pro Google.\n\n` +
    `🔵 *PROFISSIONAL — R$297* _(3x de R$99)_\n` +
    `Várias seções, catálogo de serviços, formulário e *domínio .com.br grátis no 1º ano*.\n\n` +
    `🟣 *PREMIUM — R$397* _(4x de R$110)_\n` +
    `Hospedagem inclusa, Google Meu Negócio e ajustes ilimitados no 1º mês.\n\n` +
    `Qual combina mais com a *${nome}*? 😊`
  );
}

async function fila(limite = 5) {
  const r = await fetch(`${API}/api/fila?limite=${limite}&token=${encodeURIComponent(TOKEN)}`);
  if (!r.ok) throw new Error('fila HTTP ' + r.status);
  return (await r.json()).fila || [];
}
async function marcarEnviado(cnpj) {
  if (!cnpj) return;
  await fetch(`${API}/api/lead/${encodeURIComponent(cnpj)}/enviado?token=${encodeURIComponent(TOKEN)}`,
    { method: 'POST' }).catch(() => {});
}
async function marcarStatus(cnpj, valor) {
  if (!cnpj) return;
  await fetch(`${API}/api/lead/${encodeURIComponent(cnpj)}/status?valor=${encodeURIComponent(valor)}&token=${encodeURIComponent(TOKEN)}`,
    { method: 'POST' }).catch(() => {});
}

const MAPA = path.join(DIR, 'enviados.json');
function lerMapa() { try { return JSON.parse(fs.readFileSync(MAPA, 'utf8')); } catch { return {}; } }
function salvarMapa(m) { try { fs.writeFileSync(MAPA, JSON.stringify(m)); } catch {} }

const GROQ_USO = path.join(DIR, 'groq-uso.json');
function gravarGroqUso(r) {
  try {
    const h = r.headers;
    const num = (v) => { const n = parseFloat(v); return Number.isFinite(n) ? n : null; };
    const limReq = num(h.get('x-ratelimit-limit-requests'));
    const remReq = num(h.get('x-ratelimit-remaining-requests'));
    const dado = { modelo: GROQ_MODEL, atualizado: new Date().toISOString(), configurado: true };
    if (limReq != null && remReq != null) {
      dado.limite = limReq; dado.restante = remReq; dado.usado = limReq - remReq;
      dado.percentual = limReq > 0 ? Math.round((limReq - remReq) / limReq * 100) : 0;
    }
    if (r.status === 429) dado.limite_atingido = true;
    fs.writeFileSync(GROQ_USO, JSON.stringify(dado));
  } catch {}
}

const CONTADOR = path.join(DIR, 'contador-dia.json');
function hojeStr() { return new Date().toLocaleDateString('en-CA', { timeZone: 'America/Sao_Paulo' }); }
function lerContador() { try { return JSON.parse(fs.readFileSync(CONTADOR, 'utf8')); } catch { return { dia: '', enviados: 0 }; } }
function enviadosHoje() { const c = lerContador(); return c.dia === hojeStr() ? (c.enviados || 0) : 0; }
function registrarEnvio() {
  const h = hojeStr(); const c = lerContador();
  const n = (c.dia === h ? (c.enviados || 0) : 0) + 1;
  try { fs.writeFileSync(CONTADOR, JSON.stringify({ dia: h, enviados: n, max: LIMITE_DIA })); } catch {}
  return n;
}

function variantesBR(num) {
  num = (num || '').replace(/\D/g, '');
  const set = new Set([num]);
  const m = num.match(/^55(\d{2})(\d+)$/);
  if (m) {
    const ddd = m[1], resto = m[2];
    if (resto.length === 9 && resto[0] === '9') set.add('55' + ddd + resto.slice(1));
    if (resto.length === 8) set.add('55' + ddd + '9' + resto);
  }
  return [...set];
}
function acharEstado(mapa, num) {
  for (const v of variantesBR(num)) if (mapa[v]) return [v, mapa[v]];
  const tail = (num || '').replace(/\D/g, '').slice(-8);
  if (tail) for (const k of Object.keys(mapa)) if (k.slice(-8) === tail) return [k, mapa[k]];
  return [(num || '').replace(/\D/g, ''), null];
}

const HIST = {};
let sockAtual = null;
function hist(num) { return (HIST[num] = HIST[num] || []); }

async function iaConversar(num, ctx, txt) {
 if (!GROQ_KEY) return null;
 const sys =
`Você é uma pessoa real da equipe Veltora, conversando pelo WhatsApp. Fale como gente: natural, breve, empático. Nada de texto longo — 1 ou 2 frases curtas, como mensagem de celular. Use emoji com moderação (no máximo 1 por mensagem). Nunca repita o que já disse. Acompanhe o assunto do cliente.

CONTEXTO DO CLIENTE
- Empresa: ${ctx.nome}${ctx.dono ? ' | Contato: ' + ctx.dono : ''}.
- Etapa atual: ${ctx.etapa}.
- Você JÁ mandou a primeira mensagem (abertura suave). Agora está conversando.

SOBRE A VELTORA
Somos uma agência completa de presença digital. Fazemos sites, lojas virtuais, chatbots, SEO, Google Meu Negócio, logo, identidade visual e automações. O cliente precisa sentir que resolvemos TUDO do digital.
Os PLANOS abaixo são só do SITE. Serviços extras são SOB MEDIDA — se o cliente perguntar, diga que montamos um orçamento personalizado. NUNCA invente preço.

PLANOS DO SITE:
- ESSENCIAL R$197 (3x R$69): 1 página, WhatsApp, Maps, SEO básico.
- PROFISSIONAL R$297 (3x R$99): várias seções, catálogo, formulário, domínio .com.br grátis 1º ano.
- PREMIUM R$397 (4x R$110): tudo do Pro + hospedagem, Google Meu Negócio, ajustes ilimitados 1º mês.

FATOS IMPORTANTES: pagamento Pix ou cartão (até 4x); só paga DEPOIS de ver o site pronto; entrega 2-3 dias úteis; ajustes inclusos no 1º mês; fazemos pra qualquer ramo.

REGRAS DE OURO
- Se pedirem pra mudar/personalizar o site: diga que a prévia é um MODELO e que o time ajusta TUDO do jeito deles. NÃO prometa editar na hora. Convide a seguir com um plano.
- Não invente recursos, prazos, preços ou garantias além dos listados.
- Nunca diga que é IA/robô. Nunca peça senha ou dado bancário.
- VALORES: cite UM preço natural OU use [[PLANOS]]. Nunca os dois juntos.

TAGS INTERNAS (invisíveis pro cliente, no FINAL da resposta, MÁXIMO 1 por msg):
- [[PLANOS]] — SÓ quando o cliente pedir EXPLICITAMENTE planos/preços. Texto curto sem números + tag.
- [[FECHOU]] — fechamento em 2 TEMPOS:
 (a) Se disser só o nome do plano SEM confirmar contratação: confirme valor e pergunte se pode seguir. SEM tag.
 (b) Use [[FECHOU]] SÓ quando CONFIRMAR ("pode", "fechado", "vamos nessa"). Comemore, confirme plano, diga que alguém do time fala com ele POR AQUI pra acertar detalhes, e que só paga depois de ver pronto.
- [[RECUSOU]] — SÓ se deixar claro que NÃO quer mais contato. "Agora não" ou "depois" NÃO é recusa. Responda educado, deixe porta aberta.

IMPORTANTE: atualmente NÃO estamos gerando sites automaticamente. Se o cliente quiser ver a prévia ou disser "sim", "quero ver", "manda", "pode mandar": diga algo como "Perfeito! Já encaminhei pro nosso time de desenvolvimento montar a prévia da ${ctx.nome}. Amanhã mesmo te mando pra você ver 😊". NÃO envie link nenhum. NÃO use tag [[MODELO]].`;

 const h = hist(num);
 const msgs = [{ role: 'system', content: sys }, ...h.slice(-10), { role: 'user', content: txt }];
 for (let i = 0; i < 3; i++) {
 let r;
 try {
 r = await fetch('https://api.groq.com/openai/v1/chat/completions', {
 method: 'POST',
 headers: { 'Content-Type': 'application/json', Authorization: 'Bearer ' + GROQ_KEY },
 body: JSON.stringify({ model: GROQ_MODEL, temperature: 0.7, max_tokens: 400, reasoning_effort: 'low', messages: msgs }),
 });
 } catch (e) { if (i < 2) { await sleep(2500); continue; } log('IA erro:', e.message); return null; }
 gravarGroqUso(r);
 if (r.ok) {
 const d = await r.json();
 const out = d.choices?.[0]?.message?.content?.trim();
 if (out) { h.push({ role: 'user', content: txt }, { role: 'assistant', content: out }); if (h.length > 16) h.splice(0, h.length - 16); return out; }
 return null;
 }
 if ((r.status === 429 || r.status >= 500) && i < 2) { log('IA HTTP', r.status, '— retry'); await sleep(3500); continue; }
 log('IA HTTP', r.status); return null;
 }
 return null;
}

// ---------- envios ----------
function normalizarBR(n) {
 let d = String(n || '').replace(/\D/g, '');
 if (d.startsWith('55') && d.length >= 12) return d;
 if (d.length === 10 || d.length === 11) return '55' + d;
 return d;
}

function msgAberturaSuave(nome) {
 const n = (nome || '').trim();
 if (n && n !== 'sua empresa') return `Oi! Falo com a *${n}*? Tem um tempinho pra gente conversar? 😊`;
 return `Oi! Tudo bem? Tem um tempinho pra gente conversar? 😊`;
}

function msgFollowUp(nome) {
 const n = (nome || '').trim();
 const ref = (n && n !== 'sua empresa') ? ` da *${n}*` : '';
 return `Oi de novo! 👋 Queria te apresentar algumas ideias pra deixar seu negócio${ref} com uma presença online profissional — site, Google, redes sociais... Posso te mostrar rapidinho? 😊`;
}

function msgEncaminhado(nome) {
 const n = (nome || '').trim();
 const ref = (n && n !== 'sua empresa') ? ` da *${n}*` : '';
 return `Perfeito! Já encaminhei pro nosso time de desenvolvimento montar a prévia${ref}. Amanhã mesmo te mando pra você ver 😊`;
}

async function enviarOpener(sock, numero, lead) {
 const jid = normalizarBR(numero) + '@s.whatsapp.net';
 const [info] = await sock.onWhatsApp(jid).catch(() => []);
 if (!info?.exists) { log('sem WhatsApp, pulando:', numero); return false; }
 await sock.sendMessage(info.jid, { text: msgAberturaSuave(lead.nome) });
 const key = info.jid.split('@')[0];
 const m = lerMapa();
 m[key] = { cnpj: lead.cnpj, nome: lead.nome || 'sua empresa', responsavel: lead.responsavel || '', etapa: 'abertura', fechado: false, ultimo: 'abertura', ts: Date.now(), ignorouSaudacao: false, followupEnviado: false };
 salvarMapa(m);
 delete HIST[key];
 log('abertura suave ->', lead.nome || numero);
 return true;
}

async function enviarFollowUp(sock, jid, key, st, mapa) {
 await sock.sendMessage(jid, { text: msgFollowUp(st.nome) });
 st.followupEnviado = true; st.etapa = 'followup'; st.ultimo = 'followup'; st.ts = Date.now();
 mapa[key] = st; salvarMapa(mapa);
 log('MSG -> [followup]', key, st.nome);
}

function ehSaudacaoAuto(txt) {
 const t = (txt || '').toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '').trim();
 if (!t) return false;
 const autoTpl = ['mensagem automatica','resposta automatica','assim que possivel','o mais breve possivel','retornaremos','responderemos','horario de atendimento','horario de funcionamento','agradecemos o contato','agradecemos seu contato','obrigado por entrar em contato','obrigada por entrar em contato','em instantes','aguarde','nosso atendimento','seja bem-vindo','seja bem vindo','funcionamos de','estamos fora do horario','fora do horario','como posso te ajudar','como posso ajudar','em que posso ajudar','em breve','horario comercial','logo responderemos'];
 if (autoTpl.some((p) => t.includes(p))) return true;
 const limpo = t.replace(/[!?.,:;@#*_~/\\\-]+/g, ' ').replace(/\s+/g, ' ').trim();
 return /^(oi+|ola+|ole|opa|eai|e ai|bom dia|boa tarde|boa noite|boas|hello|hi|ei)( (tudo bem|td bem|tudo bom|pessoal|gente|a todos|querida?o?))?$/.test(limpo);
}

function detectarPlano(...textos) {
 const t = textos.join(' ').toLowerCase();
 if (/premium/.test(t)) return 'Premium (R$397)';
 if (/profissional/.test(t)) return 'Profissional (R$297)';
 if (/essencial|essêncial|ess[eê]ncial/.test(t)) return 'Essencial (R$197)';
 return 'a confirmar (ver conversa)';
}

async function notificarDono(sock, st, clienteNum, plano) {
 try {
 const jid = normalizarBR(OWNER_NUM) + '@s.whatsapp.net';
 const cliente = String(clienteNum || '').replace(/\D/g, '');
 const contato = (st.responsavel && st.responsavel.trim()) ? st.responsavel.trim() : '(não informado)';
 const msg = `🎉 *VENDA FECHADA!*\n\n🏢 Empresa: *${st.nome || '—'}*\n👤 Contato: ${contato}\n📱 WhatsApp: ${cliente || '(ver painel)'}\n📋 Plano: *${plano}*\n\n👉 Assuma a conversa pra acertar detalhes. Procure *${st.nome || ''}* no painel.`;
 await sock.sendMessage(jid, { text: msg });
 log('🔔 dono avisado:', st.nome, '|', plano);
 } catch (e) { log('erro avisar dono:', e.message); }
}

// ---------- cérebro ----------
async function responder(sock, jid, txt, pn) {
 const num = jid.split('@')[0];
 const pnum = (pn || '').split('@')[0].replace(/\D/g, '');
 const mapa = lerMapa();
 let [key, st] = acharEstado(mapa, pnum || num);
 if (!st && pnum) { const r = acharEstado(mapa, num); key = r[0]; st = r[1]; }
 if (st && st.fechado) { log('MSG <- (fechado)', key, corta(txt)); return; }
 if (!st) {
 const agora = Date.now();
 const cands = Object.values(mapa).filter((v) => v && !v.fechado && (v.etapa === 'abertura' || v.etapa === 'followup') && (agora - (v.ts || 0) < 6 * 3600 * 1000));
 if (cands.length === 1) { st = cands[0]; key = num; st.lid = num; mapa[key] = st; salvarMapa(mapa); log('🔗 vinculado', num, '->', st.nome); }
 }
 if (!st) { st = { cnpj: null, nome: 'sua empresa', responsavel: '', etapa: 'novo', fechado: false, ultimo: '', ts: Date.now() }; key = num; mapa[key] = st; }
 const ctx = { nome: st.nome || 'sua empresa', dono: ((st.responsavel || '').trim().split(' ')[0]) || '', etapa: st.etapa, temLead: !!st.cnpj };
 log('MSG <-', key, corta(txt));

 if (st.etapa === 'abertura' && !st.ignorouSaudacao && ehSaudacaoAuto(txt)) {
 st.ignorouSaudacao = true; mapa[key] = st; salvarMapa(mapa);
 log('🤖 auto-reply ignorado:', key); return;
 }

 await sleep(1300 + Math.random() * 1800);

 if (GROQ_KEY) {
 const ia = await iaConversar(num, ctx, txt);
 if (ia !== null) {
 let reply = ia;
 const wantPlanos = /\[\[\s*PLANOS\s*\]\]/i.test(reply);
 const wantFechou = /\[\[\s*FECHOU\s*\]\]/i.test(reply);
 const wantRecusou = /\[\[\s*RECUSOU\s*\]\]/i.test(reply);
 reply = reply.replace(/\[\[[^\]]*\]\]/g, '').trim();
 if (reply) { await sock.sendMessage(jid, { text: reply }); log('MSG ->', key, corta(reply)); }
 if (wantPlanos) { await sleep(900); await sock.sendMessage(jid, { text: planosMsg(ctx.nome) }); st.etapa = 'planos'; mapa[key] = st; salvarMapa(mapa); }
 if (wantFechou) { st.fechado = true; st.etapa = 'fechado'; mapa[key] = st; salvarMapa(mapa); await marcarStatus(st.cnpj, 'fechado'); log('🎯 FECHOU:', ctx.nome); await notificarDono(sock, st, key, detectarPlano(reply, txt)); }
 if (wantRecusou) { st.fechado = true; st.etapa = 'recusado'; mapa[key] = st; salvarMapa(mapa); await marcarStatus(st.cnpj, 'recusado'); log('✖ RECUSOU:', ctx.nome); }
 return;
 }
 log('IA falhou — fallback regras.');
 }

 await responderRegras(sock, jid, key, st, mapa, ctx, txt);
}

function classificar(t) {
 t = ' ' + (t || '').toLowerCase().normalize('NFC') + ' ';
 if (/(fechar|fechado|contratar|quero contratar|pode fazer|vamos fazer|quero o |pode come(ç|c)ar|aceito o|quero esse)/.test(t)) return 'fechar';
 if (/(quanto|pre(ç|c)o|valor|custa|investimento|plano|planos|or(ç|c)amento)/.test(t)) return 'preco';
 if (/[ ,.!?](sim|quero|pode|aceito|bora|vamos|manda|mostra|quero ver|pode mandar|claro|ok)[ ,.!?]/.test(t)) return 'positivo';
 if (/(n(ã|a)o quero|sem interesse|agora n(ã|a)o|depois|n(ã|a)o obrigad)/.test(t)) return 'negativo';
 return 'duvida';
}

async function responderRegras(sock, jid, key, st, mapa, ctx, txt) {
 const nome = ctx.nome, intent = classificar(txt);
 if (intent === 'fechar') {
 await sock.sendMessage(jid, { text: `Perfeito! 🎉 Vou passar pro nosso time começar o site da *${nome}*. Já já alguém fala com você aqui 🚀` });
 st.fechado = true; st.etapa = 'fechado'; mapa[key] = st; salvarMapa(mapa); await marcarStatus(st.cnpj, 'fechado'); await notificarDono(sock, st, key, detectarPlano(txt)); return;
 }
 if (intent === 'preco') { await sock.sendMessage(jid, { text: planosMsg(nome) }); st.etapa = 'planos'; mapa[key] = st; salvarMapa(mapa); return; }
 if (intent === 'positivo' && (st.etapa === 'abertura' || st.etapa === 'followup')) {
 await sock.sendMessage(jid, { text: msgEncaminhado(nome) });
 st.etapa = 'encaminhado'; mapa[key] = st; salvarMapa(mapa); return;
 }
 if (intent === 'positivo' && st.etapa === 'modelo') { await sock.sendMessage(jid, { text: planosMsg(nome) }); st.etapa = 'planos'; mapa[key] = st; salvarMapa(mapa); return; }
 if (intent === 'negativo') { await sock.sendMessage(jid, { text: `Sem problema! 👍 Quando quiser, é só chamar 😉` }); return; }
 await sock.sendMessage(jid, { text: `Posso te mostrar como ficaria o site da *${nome}* ou te explicar os planos 😊 O que prefere?` });
}

// ---------- follow-up automático ----------
async function loopFollowUp(sock) {
 log('LOOP follow-up ligado. Delay:', FOLLOWUP_DELAY / 1000, 's');
 while (true) {
 if (sock !== sockAtual) { log('loop follow-up encerrado (reconexão)'); return; }
 try {
 const mapa = lerMapa();
 const agora = Date.now();
 for (const [key, st] of Object.entries(mapa)) {
 if (!st || st.fechado || st.followupEnviado) continue;
 if (st.etapa !== 'abertura') continue;
 if (agora - (st.ts || 0) < FOLLOWUP_DELAY) continue;
 const jid = key + '@s.whatsapp.net';
 await enviarFollowUp(sock, jid, key, st, mapa);
 await sleep(5000 + Math.random() * 10000);
 }
 } catch (e) { log('erro follow-up:', e.message); }
 await sleep(60000);
 }
}

// ---------- outreach ----------
async function loopOutreach(sock) {
 log(`OUTREACH ligado. Limite ${LIMITE_DIA}/dia. Já enviados: ${enviadosHoje()}`);
 while (true) {
 if (sock !== sockAtual) { log('loop outreach encerrado'); return; }
 try {
 if (enviadosHoje() >= LIMITE_DIA) {
 log(`🛑 Limite ${LIMITE_DIA} atingido. Pausando.`);
 await sleep(30 * 60 * 1000); continue;
 }
 const leads = await fila(5);
 if (!leads.length) { await sleep(120000); continue; }
 for (const lead of leads) {
 if (enviadosHoje() >= LIMITE_DIA) { log('🛑 Teto atingido no lote.'); break; }
 if (!lead.whatsapp) { await marcarStatus(lead.cnpj, 'sem_whatsapp'); continue; }
 let enviado = false;
 try { enviado = await enviarOpener(sock, lead.whatsapp, lead); if (enviado) { registrarEnvio(); log(`📊 ${enviadosHoje()}/${LIMITE_DIA} -> ${lead.nome}`); } } catch (e) { log('erro opener:', e.message); }
 if (enviado) await marcarEnviado(lead.cnpj); else await marcarStatus(lead.cnpj, 'sem_whatsapp');
 if (enviado) await sleep(DELAY_MS + Math.random() * 60000); else await sleep(1500 + Math.random() * 2500);
 }
 } catch (e) { log('erro loop:', e.message); await sleep(60000); }
 }
}

async function modoTeste(sock) {
 if (!TEST_TO) { log('MODE=test sem TEST_TO.'); return; }
 const leads = await fila(1).catch(() => []);
 if (leads[0]) { await enviarOpener(sock, TEST_TO, leads[0]); log('teste ->', TEST_TO); }
 else await sock.sendMessage(TEST_TO + '@s.whatsapp.net', { text: 'Bot Veltora v2 funcionando! ✅' });
}

// ---------- conexão ----------
async function start() {
 const { state, saveCreds } = await useMultiFileAuthState(path.join(DIR, 'auth'));
 const { version } = await fetchLatestBaileysVersion();
 const sock = makeWASocket({ version, auth: state, printQRInTerminal: false, logger: pino({ level: 'silent' }), browser: ['Veltora', 'Chrome', '1.0'] });
 sock.ev.on('creds.update', saveCreds);
 if (!sock.authState.creds.registered && PAIR_NUMBER) {
 await sleep(3000);
 try { const code = await sock.requestPairingCode(PAIR_NUMBER); log('CÓDIGO PAREAMENTO:', code); } catch (e) { log('erro pareamento:', e.message); }
 }
 sock.ev.on('connection.update', async (u) => {
 const { connection, lastDisconnect } = u;
 if (u.qr) { try { await QRCode.toFile(path.join(DIR, 'qr.png'), u.qr, { width: 420, margin: 2 }); log('📷 QR'); } catch {} }
 if (connection === 'open') {
 fs.rmSync(path.join(DIR, 'qr.png'), { force: true });
 sockAtual = sock;
 log('✅ CONECTADO. MODE=' + MODE + (GROQ_KEY ? ' (IA)' : ' (regras)'));
 if (MODE === 'outreach') { loopOutreach(sock); loopFollowUp(sock); }
 else if (MODE === 'test') await modoTeste(sock);
 else { log('MODE=idle'); loopFollowUp(sock); }
 } else if (connection === 'close') {
 const code = lastDisconnect?.error?.output?.statusCode;
 if (code === DisconnectReason.loggedOut) log('❌ Deslogado. Apague auth/ e pareie de novo.');
 else { log('conexão caiu, reconectando...', code); start(); }
 }
 });

 sock.ev.on('messages.upsert', async ({ messages, type }) => {
 if (type !== 'notify') return;
 for (const m of messages) {
 if (m.key.fromMe || !m.message || m.key.remoteJid?.endsWith('@g.us')) continue;
 const jid = m.key.remoteJid;
 const pn = m.key.senderPn || m.key.participantPn || '';
 const txt = m.message.conversation || m.message.extendedTextMessage?.text || '';
 if (!txt.trim()) continue;
 try { await responder(sock, jid, txt, pn); } catch (e) { log('erro responder:', e.message); }
 }
 });
}

// ---------- envio manual pra leads específicos ----------
async function enviarManual(sock, numero, nome, cnpj) {
 const jid = normalizarBR(numero) + '@s.whatsapp.net';
 const [info] = await sock.onWhatsApp(jid).catch(() => []);
 if (!info?.exists) { log('sem WhatsApp:', numero); return false; }
 const msg = msgEncaminhado(nome);
 await sock.sendMessage(info.jid, { text: msg });
 const key = info.jid.split('@')[0];
 const m = lerMapa();
 m[key] = { cnpj, nome, responsavel: '', etapa: 'encaminhado', fechado: false, ultimo: 'encaminhado', ts: Date.now(), ignorouSaudacao: true, followupEnviado: true };
 salvarMapa(m);
 log('MSG -> [manual]', key, nome);
 return true;
}

start().then(async () => {
 // Aguarda conexão estabilizar antes de enviar mensagens manuais
 await sleep(8000);
 if (sockAtual && MODE !== 'test') {
 // Envia mensagem de encaminhamento para Cantina da Bea (4591430148)
 await enviarManual(sockAtual, '554591430148', 'Cantina da Bea', 'osm-node-6710851885');
 }
}).catch((e) => { log('fatal:', e); process.exit(1); });