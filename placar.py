import streamlit as st
import sqlite3
import time
from datetime import datetime, timedelta
from streamlit.components.v1 import html
from PIL import Image

# ----------------------------
# CONFIGURAÇÃO GERAL
# ----------------------------
st.set_page_config(
    page_title="Placar – Maratona UNIPAC",
    page_icon="🏆",
    layout="wide",
    initial_sidebar_state="collapsed"
)

DB_FILE = "maratona.db"
PROBLEMAS = list("ABCDEFG")
CORES_BALOES = ["#f97316", "#3b82f6", "#eab308", "#22c55e", "#a855f7", "#06b6d4", "#fb923c"]


# ----------------------------
# BANCO DE DADOS
# ----------------------------
def get_db_connection():
    return sqlite3.connect(DB_FILE, check_same_thread=False)


def init_db():
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS equipes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT UNIQUE NOT NULL,
            aluno1 TEXT, aluno2 TEXT, aluno3 TEXT
        )''')
        c.execute('''CREATE TABLE IF NOT EXISTS submissoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            equipe_nome TEXT NOT NULL,
            problema TEXT NOT NULL,
            resultado TEXT NOT NULL,
            tempo INTEGER NOT NULL,
            motivo TEXT
        )''')
        c.execute('''CREATE TABLE IF NOT EXISTS config (
            chave TEXT PRIMARY KEY,
            valor TEXT
        )''')
        conn.commit()


init_db()


# ----------------------------
# GERENCIAMENTO DE TEMPO
# ----------------------------
def get_inicio_prova():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        res = cursor.execute("SELECT valor FROM config WHERE chave='inicio_prova'").fetchone()
        if res:
            return datetime.fromisoformat(res[0])
        else:
            agora = datetime.now()
            cursor.execute("INSERT INTO config (chave, valor) VALUES (?, ?)",
                           ('inicio_prova', agora.isoformat()))
            conn.commit()
            return agora


def reset_prova_apenas_dados():
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute("DELETE FROM submissoes")
        agora = datetime.now()
        c.execute("INSERT OR REPLACE INTO config (chave, valor) VALUES ('inicio_prova', ?)",
                  (agora.isoformat(),))
        conn.commit()


def zerar_banco_completo():
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute("DELETE FROM submissoes")
        c.execute("DELETE FROM equipes")
        c.execute("DELETE FROM config")
        conn.commit()


inicio_prova = get_inicio_prova()
duracao_prova = timedelta(hours=1, minutes=30)


# ----------------------------
# MODO TELÃO E ESTILOS GERAIS
# ----------------------------
def is_telao_mode() -> bool:
    qp = st.query_params
    val = qp.get("telao", "0")
    return val == "1"


modo_telao = is_telao_mode()
bg_color = "#ffffff" if modo_telao else "#0f172a"
text_color = "#111827" if modo_telao else "#f3f4f6"

st.markdown(f"""
    <style>
        html, body, [class*="css"] {{
            background-color: {bg_color};
            color: {text_color};
            font-family: "Segoe UI", sans-serif;
        }}

        .scoreboard-container {{
            background: #ffffff;
            border-radius: 12px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            overflow: hidden;
            border: 1px solid #e5e7eb;
            margin-top: 10px;
        }}
        table.scoreboard {{
            width: 100%;
            border-collapse: collapse;
            font-size: 0.95rem;
            color: #1f2937;
        }}
        table.scoreboard th {{
            background: #f3f4f6;
            padding: 12px;
            text-align: center;
            font-weight: 700;
            border-bottom: 2px solid #e5e7eb;
            color: #374151;
        }}
        table.scoreboard td {{
            padding: 10px;
            text-align: center;
            border-bottom: 1px solid #f3f4f6;
            vertical-align: middle;
        }}
        table.scoreboard td:nth-child(2) {{ text-align: left; font-weight: 600; }}

        .rank-1 td {{ background-color: #fefce8 !important; }}
        .rank-2 td {{ background-color: #f8fafc !important; }}
        .rank-3 td {{ background-color: #fff7ed !important; }}

        .balloon {{
            width: 20px; height: 26px;
            border-radius: 50% 50% 50% 50% / 40% 40% 60% 60%;
            margin: 0 auto;
            box-shadow: inset -2px -2px 4px rgba(0,0,0,0.2);
        }}
    </style>
""", unsafe_allow_html=True)


# ----------------------------
# DADOS
# ----------------------------
def obter_dados():
    with get_db_connection() as conn:
        equipes = [r[0] for r in conn.execute("SELECT nome FROM equipes").fetchall()]
        submissoes = conn.execute(
            "SELECT equipe_nome, problema, resultado, tempo FROM submissoes ORDER BY tempo ASC").fetchall()

    dados = {eq: {"total": 0, "penalidade": 0, "probs": {p: [] for p in PROBLEMAS}} for eq in equipes}
    first_solvers = {}

    for eq, prob, res, tempo in submissoes:
        if eq not in dados or prob not in PROBLEMAS: continue
        if any(r == "Correto" for r, _ in dados[eq]["probs"][prob]): continue
        dados[eq]["probs"][prob].append((res, tempo))
        if res == "Correto":
            dados[eq]["total"] += 1
            erros = sum(1 for r, _ in dados[eq]["probs"][prob] if r == "Erro")
            dados[eq]["penalidade"] += tempo + (20 * erros)
            if prob not in first_solvers:
                first_solvers[prob] = eq

    return sorted(dados.items(), key=lambda x: (-x[1]["total"], x[1]["penalidade"])), first_solvers


# ----------------------------
# INTERFACE E MODAIS
# ----------------------------
@st.dialog("Nova Equipe")
def modal_equipe():
    with st.form("team_form"):
        nome = st.text_input("Nome da Equipe")
        c1, c2, c3 = st.columns(3)
        a1, a2, a3 = c1.text_input("Aluno 1"), c2.text_input("Aluno 2"), c3.text_input("Aluno 3")
        if st.form_submit_button("Salvar", type="primary"):
            try:
                with get_db_connection() as conn:
                    conn.execute("INSERT INTO equipes (nome, aluno1, aluno2, aluno3) VALUES (?,?,?,?)",
                                 (nome, a1, a2, a3))
                    conn.commit()
                st.success("Salvo!")
                st.rerun()
            except sqlite3.IntegrityError:
                st.error("Nome já existe.")


@st.dialog("Nova Submissão")
def modal_submissao():
    with get_db_connection() as conn:
        equipes = [r[0] for r in conn.execute("SELECT nome FROM equipes").fetchall()]
    if not equipes:
        st.warning("Sem equipes.")
        return
    with st.form("sub_form"):
        eq = st.selectbox("Equipe", equipes)
        c1, c2 = st.columns(2)
        prob = c1.selectbox("Problema", PROBLEMAS)
        tempo_corrido = int((datetime.now() - inicio_prova).total_seconds() / 60)
        tempo = c2.number_input("Minuto", min_value=0, max_value=300, value=max(0, tempo_corrido))
        res = st.radio("Resultado", ["Correto", "Erro"], horizontal=True)
        if st.form_submit_button("Registrar", type="primary"):
            with get_db_connection() as conn:
                conn.execute(
                    "INSERT INTO submissoes (equipe_nome, problema, resultado, tempo, motivo) VALUES (?,?,?,?,?)",
                    (eq, prob, res, tempo, ""))
                conn.commit()
            st.success("Registrado!")
            st.rerun()


# --- SIDEBAR ADMIN ---
uploaded_logo = None
if not modo_telao:
    with st.sidebar:
        st.header("⚙️ Admin")
        uploaded_logo = st.file_uploader("Logo", type=['png', 'jpg'])

        st.divider()
        if st.button("➕ Cadastrar Equipe"): modal_equipe()
        if st.button("📝 Registrar Submissão"): modal_submissao()

        st.divider()
        st.error("🚨 **Zona de Perigo**")
        if st.button("🔁 Reiniciar Prova (Manter Equipes)"):
            reset_prova_apenas_dados()
            st.rerun()
        if st.button("🧨 ZERAR BANCO DE DADOS"):
            zerar_banco_completo()
            st.rerun()

# --- LAYOUT PRINCIPAL ---
# Define a proporção das colunas. A do relógio (c_clock) precisa ser bem larga.
c1, c_clock = st.columns([1, 4])

with c1:
    if uploaded_logo:
        st.image(uploaded_logo, width=150)
    else:
        try:
            st.image("logo_maratona.jpg", width=150)
        except:
            st.write("🏆 **Maratona**")

    if not modo_telao:
        st.caption("Painel Admin")

with c_clock:
    fim = inicio_prova + duracao_prova
    ts_fim = int(fim.timestamp() * 1000)

    # HTML DO RELÓGIO COM CSS EMBUTIDO (CORREÇÃO DA FALHA)
    # A fonte é carregada DENTRO do iframe do componente HTML
    html(f"""
    <!DOCTYPE html>
    <html>
    <head>
    <style>
        /* Importa a fonte DSEG7 (Estilo Display 7-Segmentos) */
        @font-face {{
            font-family: 'DSEG7';
            src: url('https://cdn.jsdelivr.net/npm/dseg@0.46.0/fonts/DSEG7-Classic/DSEG7Classic-Bold.woff2') format('woff2');
        }}

        body {{
            margin: 0;
            display: flex;
            justify-content: center; /* Centraliza horizontalmente */
            align-items: center;     /* Centraliza verticalmente */
            height: 100vh;
            background-color: transparent;
            font-family: 'Segoe UI', sans-serif;
        }}

        .clock-container {{
            background-color: #000000;
            color: #00ff00; /* Verde Neon Padrão */
            font-family: 'DSEG7', monospace;
            font-size: 110px; /* TAMANHO DA FONTE FORÇADO AQUI */
            line-height: 1;
            padding: 20px 40px;
            border-radius: 15px;
            border: 5px solid #222;
            box-shadow: 0 10px 30px rgba(0,0,0,0.6);
            text-align: center;
            letter-spacing: 5px;
            text-shadow: 0 0 20px rgba(0, 255, 0, 0.8);
            min-width: 550px; /* Garante largura mínima para não quebrar linha */
        }}

        /* Ajuste responsivo se a tela for muito pequena */
        @media (max-width: 800px) {{
            .clock-container {{ font-size: 60px; min-width: 300px; padding: 10px 20px; }}
        }}
    </style>
    </head>
    <body>
        <div id="timer" class="clock-container">--:--:--</div>

        <script>
        const dest = {ts_fim};

        function updateTimer() {{
            const now = new Date().getTime();
            const d = dest - now;
            const el = document.getElementById("timer");

            if (!el) return;

            if (d < 0) {{ 
                el.innerHTML = "00:00:00"; 
                el.style.color = "#ff0000"; // Vermelho
                el.style.textShadow = "0 0 30px rgba(255, 0, 0, 1)";
                return; 
            }}

            const h = Math.floor(d / 3600000);
            const m = Math.floor((d % 3600000) / 60000);
            const s = Math.floor((d % 60000) / 1000);

            // Formatação com zeros à esquerda
            const hStr = h < 10 ? "0" + h : h;
            const mStr = m < 10 ? "0" + m : m;
            const sStr = s < 10 ? "0" + s : s;

            el.innerHTML = hStr + ":" + mStr + ":" + sStr;

            // Regra dos 10 minutos (600.000 ms)
            if (d <= 600000) {{
                el.style.color = "#ff0000";
                el.style.textShadow = "0 0 30px rgba(255, 0, 0, 1)";
            }} else {{
                el.style.color = "#00ff00";
                el.style.textShadow = "0 0 20px rgba(0, 255, 0, 0.8)";
            }}
        }}

        setInterval(updateTimer, 1000);
        updateTimer(); // Executa imediatamente
        </script>
    </body>
    </html>
    """, height=220)  # A altura do iframe precisa ser maior que o relógio para não cortar

# --- TABELA DE PLACAR ---
ranking, firsts = obter_dados()

if not modo_telao:
    if st.button("🚀 Registro Rápido"): modal_submissao()

h = """<div class="scoreboard-container"><table class="scoreboard"><thead><tr><th>#</th><th>Equipe</th>"""
for p in PROBLEMAS: h += f"<th>{p}</th>"
h += "<th>Total</th><th>Penalidade</th></tr></thead><tbody>"

if not ranking: h += f"<tr><td colspan='{4 + len(PROBLEMAS)}'>Aguardando equipes...</td></tr>"

for i, (eq, stt) in enumerate(ranking, 1):
    h += f"<tr class='rank-{i}'><td>{i}</td><td>{eq}</td>"
    for idx, p in enumerate(PROBLEMAS):
        pd = stt["probs"][p]
        suc = any(r == "Correto" for r, _ in pd)
        if suc:
            t = next(tm for r, tm in pd if r == "Correto")
            c = CORES_BALOES[idx % 7]
            f = "<b style='color:green;font-size:0.6em'>★FIRST</b>" if firsts.get(p) == eq else ""
            h += f"<td><div style='display:flex;flex-direction:column;align-items:center'><div class='balloon' style='background:{c}'></div><small>{len(pd)}/{t}'</small>{f}</div></td>"
        elif len(pd) > 0:
            h += f"<td><b style='color:red'>✖</b> <small>({len(pd)})</small></td>"
        else:
            h += "<td>-</td>"
    h += f"<td><b>{stt['total']}</b></td><td>{stt['penalidade']}</td></tr>"

h += "</tbody></table></div>"
st.markdown(h, unsafe_allow_html=True)

if modo_telao:
    time.sleep(30)
    st.rerun()