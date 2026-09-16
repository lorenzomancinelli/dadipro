import os
import json
import random
import re
from datetime import datetime, timezone
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

# ---- HTML + CSS + JS (multiplayer simultaneo) ----
html_content = """
<!doctype html>
<html lang="it">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>ROLLING CUBES</title>
<style>
.winner-celebration {
  font-size: 32px;
  font-weight: 900;
  color: #fff;
  background: linear-gradient(90deg, #ff7675, #ffeaa7, #55efc4, #74b9ff);
  background-size: 400% 400%;
  padding: 20px;
  border-radius: 12px;
  animation: gradientFlow 5s ease infinite, bounce 1s infinite;
  text-align: center;
  margin-top: 20px;
}

@keyframes gradientFlow {
  0% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}

@keyframes bounce {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-8px); }
}

/* coriandoli */
.confetti {
  position: fixed;
  width: 8px;
  height: 8px;
  background: red;
  top: -10px;
  animation: fall 3s linear forwards;
}

@keyframes fall {
  to {
    transform: translateY(100vh) rotate(360deg);
    opacity: 0;
  }
}

.topbar {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.row-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  align-items: center;
}
#btn-new-game {
  background: var(--accent);
  color: #fff;
}

.row-settings {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
  align-items: center;
  font-size: 20px;
  font-weight: 700;
}
.verify-big {
  display:block;
  margin:16px auto;
  padding:16px 24px;
  font-size:20px;
  font-weight:700;
  border-radius:12px;
}
.player-controls label,
.player-controls button {
  margin-left: 8px;
}
.timer-display {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 120px;
  height: 60px;
  background: var(--accent);
  color: #ffffff !important;
  font-size: 28px;
  font-weight: 900;
  border-radius: 12px;
  margin-left: 10px;
}
.topbar button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 10px 20px;
  font-size: 18px;
  font-weight: 600;
  border-radius: 14px;
  background: var(--accent);
  color: #fff;
  cursor: pointer;
  margin: 10px;
}
#player-name {
  font-size: 20px;
  padding: 14px 20px;
  border-radius: 10px;
  border: 2px solid #ccc;
  width: 190px;   /* aumenta la larghezza */
  margin-right: 10px;
}
:root { --bg:#f5f6fa; --box:#fff; --text:#2d3436; --accent:#0984e3; }
* { box-sizing:border-box; }
body { margin:0; font-family:system-ui,Segoe UI,Roboto,Arial; background:var(--bg); color:var(--text); padding:18px; }
main { max-width:1200px; margin:0 auto; }
.topbar { display:flex; justify-content:space-between; gap:12px; align-items:center; margin-bottom:12px; flex-wrap:wrap; }
.player-controls input { padding:6px 8px; }
button { background:var(--accent); color:#fff; border:none; padding:8px 10px; border-radius:8px; cursor:pointer; font-weight:1000; margin-right:10px; }
button:active { transform:translateY(1px); }
.timer-display { min-width:70px; font-weight:700; color:var(--accent); margin-left:6px; text-align:center; }
.status { margin-bottom:12px; }
.scoreboard { background:var(--box); padding:8px; border-radius:8px; box-shadow:0 8px 18px rgba(0,0,0,0.06); }
.scoreboard-grid { display:grid; grid-template-columns: repeat(6, 1fr); gap:6px; }
.scoreboard .player { padding:6px 8px; border-radius:6px; background:#fafafa; display:flex; justify-content:space-between; align-items:center; }
.dice-pool { display:flex; flex-wrap:wrap; gap:10px; padding:12px; background:var(--box); border-radius:12px; box-shadow:0 6px 18px rgba(0,0,0,0.06); }
.die { width:60px; height:60px; border-radius:10px; display:flex; align-items:center; justify-content:center; font-size:22px; font-weight:700; cursor:pointer; box-shadow:0 6px 12px rgba(0,0,0,0.08); border:3px solid transparent; }
.die.digit, .die.decsym { background:#BFDDEA; color:#0E3B52; border-color:#7fb3d5; }
.die.fracnum { background:#BFDDEA; color:#0E3B52; border-color:#7fb3d5; font-size:14px; }
.die.addsub { background:#F6CE8E; color:#5A3A10; border-color:#d99a3d; font-size:26px; }
.die.muldiv { background:#E2432B; color:#fff; border-color:#a8281a; font-size:26px; }
.die.advop { background:#8B6BC9; color:#fff; border-color:#5f4696; font-size:20px; }
.die.paren, .die.equals { background:#BFE0B8; color:#1F3A1C; border-color:#7fae77; font-size:22px; }
.die.slot-empty { background:transparent; border:none; box-shadow:none; cursor:default; }
.slots { display:flex; flex-wrap:wrap; gap:8px; padding:12px; background:var(--box); border-radius:12px; box-shadow:0 6px 18px rgba(0,0,0,0.06); }
.slot { width:60px; height:60px; border-radius:10px; background:#dfe6e9; display:flex; align-items:center; justify-content:center; border:3px dashed #636e72; }
.slot.filled { border-style:solid; border-color:var(--accent); background:#e6f3ff; }
.feedback { margin-top:14px; min-height:26px; font-size:18px; font-weight:600; display:flex; align-items:center; justify-content:center; }
.rules{margin-top:18px;padding:12px;background:var(--box);border-radius:10px}
</style>
</head>
<body>
<main>
  <h1>ROLLING CUBES</h1>
<section class="topbar">
  <!-- Prima riga -->
  <div class="row-buttons">
    <input id="player-name" placeholder="Nome giocatore" />
    <button id="btn-add-player">Aggiungi / Entra</button>
    <button id="btn-reset">Azzera partita</button>
    <button id="btn-roll">Lancia dadi</button>
    <button id="btn-new-game">Crea nuova partita</button>
  </div>

  <!-- Seconda riga -->
  <div class="row-settings">
    <label>Punti per la Vittoria:
      <select id="victory-select">
        <option value="30">30</option>
        <option value="40">40</option>
        <option value="50" selected>50</option>
        <option value="60">60</option>
      </select>
    </label>

    <label>Timer:
      <select id="timer-select">
        <option value="0">Off</option>
        <option value="30">30s</option>
        <option value="60" selected>60s</option>
        <option value="120">120s</option>
      </select>
    </label>

    <div id="timer-display" class="timer-display"></div>
  </div>
</section>


  <section class="status">
    <div>Partita: <b id="game-id"></b></div>
    <div class="scoreboard">
      <h3>Classifica</h3>
      <div id="players-list" class="scoreboard-grid"></div>
    </div>
  </section>

  <section class="dice-area">
    <h2>Dadi (clicca per spostare nei tuoi slot / rimuovere)</h2>
    <div id="dice-pool" class="dice-pool" aria-live="polite"></div>
  </section>

  <section class="slots-area">
    <h2>I tuoi Slot (13)</h2>
    <div id="slots" class="slots"></div>
    <button id="btn-verify" class="verify-big">Verifica equazione</button>
  </section>

  <section class="feedback-area">
    <div id="feedback" class="feedback"></div>
  </section>

  <section class="rules">
    <h3>Tessere e punteggio (regole Pytagora Pro)</h3>
    <ul>
      <li>Cifre: punteggio posizionale (unità 1, decine 2, centinaia 3, ...).</li>
      <li>Virgola decimale e simbolo di periodo: +1 ciascuno.</li>
      <li>Frazioni (es. 1/2): +1.</li>
      <li>Parentesi aperta: +1 (la parentesi chiusa non dà punti, sempre disponibile).</li>
      <li>+ e −: +1. × e ÷: +2/+3, ridotti a +1 se uno degli operandi è 1 o è una divisione per sé stesso.</li>
      <li>Radice quadrata/cubica/quarta e potenza²/³/⁴: +1 se l'argomento vale 1, altrimenti +2.</li>
      <li>Zero iniziale non ammesso; zero finale dopo la virgola non ammesso; niente moltiplicazioni/divisioni per zero.</li>
      <li>Un solo tentativo di verifica per giocatore per round; reroll automatico allo scadere del timer.</li>
    </ul>
  </section>
</main>

<script>
// --- GAME ID in URL (autocreazione) ---
let urlParams = new URLSearchParams(location.search);
let GAME_ID = urlParams.get('game_id');
if (!GAME_ID) {
  GAME_ID = 'game_' + Math.random().toString(36).substring(2, 8);
  window.location = location.pathname + '?game_id=' + GAME_ID;
}
document.getElementById('game-id').textContent = GAME_ID;

// --- Player locale ---
let PLAYER = localStorage.getItem('rc_player') || '';
if (PLAYER) document.getElementById('player-name').value = PLAYER;

// --- Helpers fetch ---
async function apiGet(url) {
  const playerPart = PLAYER ? `&player=${encodeURIComponent(PLAYER)}` : '';
  const r = await fetch(`${url}?game_id=${encodeURIComponent(GAME_ID)}${playerPart}`);
  return await r.json();
}
async function apiPost(url, payload={}) {
  const playerPart = PLAYER ? `&player=${encodeURIComponent(PLAYER)}` : '';
  const r = await fetch(`${url}?game_id=${encodeURIComponent(GAME_ID)}${playerPart}`, {
    method:'POST',
    headers:{'Content-Type':'application/json'},
    body: JSON.stringify(payload)
  });
  return await r.json();
}

// --- DOM refs ---
const poolDiv = document.getElementById('dice-pool');
const slotsDiv = document.getElementById('slots');
const playersGrid = document.getElementById('players-list');
const feedbackDiv = document.getElementById('feedback');
const timerSel = document.getElementById('timer-select');
const timerDisp = document.getElementById('timer-display');
const victorySel = document.getElementById('victory-select');

// --- Slot personali (13) ---
function ensureSlots() {
  if (slotsDiv.children.length === 13) return;
  slotsDiv.innerHTML = '';
  for (let i = 0; i < 13; i++) {
    const s = document.createElement('div');
    s.className = 'slot';
    s.dataset.index = i;

    // permette il dragover (necessario per il drop)
    s.addEventListener("dragover", (ev) => {
      ev.preventDefault();
    });

    // gestisce il drop
    s.addEventListener("drop", async (ev) => {
      ev.preventDefault();
      const dieId = ev.dataTransfer.getData("text/plain");
      const idx = s.dataset.index;
      // rimuovi da slot precedente (se già piazzato)
      await apiPost("/api/remove", { die_id: dieId });
      // piazza nel nuovo slot
      await apiPost("/api/place", { die_id: dieId, slot: idx });
      // aggiorna stato
      const st = await apiGet("/api/state");
      renderState(st);
    });

    slotsDiv.appendChild(s);
  }
}


ensureSlots();

// --- Render stato ---
async function renderState(state) {
  // aggiorna dropdown (server authoritative)
  if (state && typeof state.victory_score === 'number') {
    victorySel.value = String(state.victory_score);
  }
  if (state && typeof state.timer === 'number') {
    timerSel.value = String(state.timer);
  }

  // classifica
  playersGrid.innerHTML = '';
  (state.players || []).forEach((p, i) => {
    const tile = document.createElement('div');
    tile.className = 'player';
    tile.textContent = `${i+1}: ${p} — ${state.scores && state.scores[p] ? state.scores[p] : 0}`;
    playersGrid.appendChild(tile);
  });


  // feedback / winner
  if (state.winner) {
    feedbackDiv.innerHTML = `🎉🎉 <b>${state.winner}</b> ha vinto la partita! 🎉🎉`;
    feedbackDiv.className = "winner-celebration";

    // suona audio applausi/fanfara
    const winAudio = document.getElementById("win-sound");
    if (winAudio) {
        winAudio.currentTime = 0;
        winAudio.play().catch(e => console.log("Audio non avviato:", e));
    }
    // genera coriandoli
    for (let i = 0; i < 100; i++) {
        const confetti = document.createElement("div");
        confetti.className = "confetti";
        confetti.style.left = Math.random() * window.innerWidth + "px";
        confetti.style.background = `hsl(${Math.random()*360}, 100%, 50%)`;
        confetti.style.animationDuration = (2 + Math.random() * 3) + "s";
        document.body.appendChild(confetti);
        setTimeout(() => confetti.remove(), 5000);
     }
    } else {
        feedbackDiv.textContent = state.last_feedback || '';
        feedbackDiv.className = "feedback";
        feedbackDiv.style.color = '';
        feedbackDiv.style.fontSize = '';
    }


  // timer globale
  if (state.round_started_at && state.timer) {
    const started = Date.parse(state.round_started_at);
    const now = Date.now();
    const remaining = Math.max(0, Math.ceil((started + state.timer * 1000 - now) / 1000));
    timerDisp.textContent = remaining ? `${remaining}s` : '';
  } else {
    timerDisp.textContent = '';
  }

  // svuota pool e slots
  poolDiv.innerHTML = '';
  [...slotsDiv.children].forEach(s => { s.innerHTML = ''; s.classList.remove('filled'); });

  const mySlots = (state.personal_slots && PLAYER ? state.personal_slots[PLAYER] : null) || Array(13).fill(null);

  // crea i dadi
  (state.dice_pool || []).forEach(d => {
    const el = document.createElement('div');
    el.className = 'die ' + d.type;
    el.textContent = d.value;
    el.dataset.id = d.id;

    // click toggle
    el.addEventListener('click', async () => {
      if (state.winner) return;
      const current = (state.personal_slots && state.personal_slots[PLAYER]) || Array(13).fill(null);
      const idxInSlots = current.indexOf(d.id);
      if (idxInSlots !== -1) {
        await apiPost('/api/remove', { die_id: d.id });
      } else {
        await apiPost('/api/place', { die_id: d.id });
      }
      const st = await apiGet('/api/state');
      renderState(st);
    });

    // drag & drop
    el.setAttribute("draggable", "true");
    el.addEventListener("dragstart", (ev) => {
      ev.dataTransfer.setData("text/plain", d.id);
    });

    // posiziona il dado nella UI
    const idx = mySlots.indexOf(d.id);
    if (idx !== -1) {
      const s = slotsDiv.children[idx];
      if (s) { s.appendChild(el); s.classList.add('filled'); }
    } else {
      poolDiv.appendChild(el);
    }
  });
}


// --- Eventi UI ---
document.getElementById('btn-new-game').addEventListener('click', () => {
  const newGameId = 'game_' + Math.random().toString(36).substring(2, 8);
  window.location = location.pathname + '?game_id=' + newGameId;
});

document.getElementById('btn-add-player').addEventListener('click', async () => {
  const name = document.getElementById('player-name').value.trim();
  if (!name) { alert('Inserisci un nome'); return; }
  PLAYER = name; localStorage.setItem('rc_player', PLAYER);
  const st = await apiPost('/api/add_player', { name });
  renderState(st);
});
document.getElementById('btn-roll').addEventListener('click', async () => {
  renderState(await apiPost('/api/roll'));
});
document.getElementById('btn-verify').addEventListener('click', async () => {
  const res = await apiPost('/api/verify');
  if (res.state) renderState(res.state);
});
document.getElementById('btn-reset').addEventListener('click', async () => {
  renderState(await apiPost('/api/reset_game'));
});

// imposta punteggio vittoria
victorySel.addEventListener('change', async () => {
  await apiPost('/api/set_victory', { victory: victorySel.value });
  const st = await apiGet('/api/state'); renderState(st);
});

// imposta timer globale (server-side)
timerSel.addEventListener('change', async () => {
  await apiPost('/api/set_timer', { seconds: parseInt(timerSel.value, 10) || 0 });
  const st = await apiGet('/api/state'); renderState(st);
});

// polling stato
setInterval(async () => { const st = await apiGet('/api/state'); renderState(st); }, 1000);

// init
(async function init(){ renderState(await apiGet('/api/state')); })();
</script>
<audio id="win-sound" preload="auto">
  <source src="https://www.soundjay.com/human/applause-8.mp3" type="audio/mpeg">
</audio>
</body>
</html>
"""

# ---- Cartella dati partite ----
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data", "games")
os.makedirs(DATA_DIR, exist_ok=True)

def game_path(game_id):
    safe = re.sub(r'[^a-zA-Z0-9_\-]', '_', game_id or 'default')
    return os.path.join(DATA_DIR, f"{safe}.json")

# ---- Stato di default (senza turni a rotazione) ----
def default_game_state(game_id):
    return {
        "game_id": game_id,
        "created_at": datetime.utcnow().replace(tzinfo=timezone.utc).isoformat(),
        "players": [],
        "scores": {},
        "dice_pool": [],              # set di dadi condiviso
        "personal_slots": {},         # player -> lista(13) di die_id o None
        "timer": 60,                  # durata round globale
        "round_started_at": None,     # inizio round corrente
        "last_feedback": "Nuova partita",
        "winner": None,
        "slots_by_player": {},        # alias/back-compat (non usato direttamente)
        "already_verified": [],       # giocatori che hanno già verificato nel round
        "victory_score": 50           # soglia di vittoria (30/40/50/60)
    }

# ---- I/O su file ----
def load_game(game_id):
    path = game_path(game_id)
    if not os.path.exists(path):
        return default_game_state(game_id)
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = f.read().strip()
            if not data:
                return default_game_state(game_id)
            return json.loads(data)
    except (json.JSONDecodeError, IOError):
        return default_game_state(game_id)

def save_game(game_id, state):
    path = game_path(game_id)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

# ============================================================================
# TESSERE PYTAGORA PRO (stesso conteggio del gioco da tavolo/edizione digitale)
# ============================================================================
def new_die_id():
    return f"d{random.randint(10**6, 10**7-1)}"

# "=" e ")" sono sempre disponibili in numero abbondante (nel gioco originale
# sono pezzi "gratuiti", illimitati): qui ne generiamo diversi per round cosi'
# che piu' giocatori possano comporre la propria uguaglianza in parallelo.
EXTRA_EQUALS_PER_ROUND = 6
EXTRA_CLOSEPAREN_PER_ROUND = 6
POOL_SAMPLE_SIZE = 30  # quante tessere pescate dal sacchetto si vedono a schermo ogni round

def build_full_bag_templates():
    """Ricostruisce l'intero sacchetto di Pytagora Pro (226 tessere pescabili,
    escluse '=' e ')' che sono gratuite/illimitate)."""
    bag = []
    digit_counts = {0:9,1:11,2:9,3:10,4:10,5:10,6:9,7:8,8:8,9:8}
    for d, n in digit_counts.items():
        for _ in range(n):
            bag.append({"cat":"digit", "display":str(d), "value":d})
    fracs = [(1,2,2),(1,3,2),(1,4,2),(2,3,1),(3,4,1),(1,5,1),(1,6,1),(1,7,1),(1,8,1),(1,9,1),(1,10,1)]
    for num, den, count in fracs:
        for _ in range(count):
            bag.append({"cat":"fracnum", "display":f"{num}/{den}", "value":num/den, "num":num, "den":den})
    for _ in range(10):
        bag.append({"cat":"decsym", "display":",", "kind":"comma"})
    for _ in range(3):
        bag.append({"cat":"decsym", "display":"\u203e", "kind":"period"})
    for _ in range(17):
        bag.append({"cat":"addsub", "display":"+", "op":"+"})
    for _ in range(25):
        bag.append({"cat":"addsub", "display":"\u2212", "op":"-"})
    for _ in range(25):
        bag.append({"cat":"muldiv", "display":"\u00d7", "op":"*"})
    for _ in range(13):
        bag.append({"cat":"muldiv", "display":"\u00f7", "op":"/"})
    for _ in range(6):
        bag.append({"cat":"advop", "display":"\u221a", "kind":"sqrt"})
    for _ in range(3):
        bag.append({"cat":"advop", "display":"\u221b", "kind":"cbrt"})
    for _ in range(1):
        bag.append({"cat":"advop", "display":"\u221c", "kind":"root4"})
    for _ in range(6):
        bag.append({"cat":"advop", "display":"\u00b2", "kind":"sq"})
    for _ in range(3):
        bag.append({"cat":"advop", "display":"\u00b3", "kind":"cube"})
    for _ in range(1):
        bag.append({"cat":"advop", "display":"\u2074", "kind":"sq4"})
    for _ in range(7):
        bag.append({"cat":"paren", "display":"(", "side":"open"})
    return bag

FULL_BAG_TEMPLATES = build_full_bag_templates()

def make_tile(tpl):
    t = dict(tpl)
    t["id"] = new_die_id()
    t["type"] = t["cat"]      # il frontend usa "type" per la classe CSS
    t["value"] = t.get("display")  # il frontend mostra "value" come testo della tessera
    return t

def roll_full_set():
    pool = random.sample(FULL_BAG_TEMPLATES, min(POOL_SAMPLE_SIZE, len(FULL_BAG_TEMPLATES)))
    dice = [make_tile(t) for t in pool]
    for _ in range(EXTRA_EQUALS_PER_ROUND):
        dice.append(make_tile({"cat":"equals", "display":"="}))
    for _ in range(EXTRA_CLOSEPAREN_PER_ROUND):
        dice.append(make_tile({"cat":"paren", "display":")", "side":"close"}))
    random.shuffle(dice)
    return dice

# ============================================================================
# MOTORE: dai riferimenti negli slot alla sequenza di tessere, al parsing
# aritmetico, alla validita' e al punteggio (stesse regole della versione
# digitale di Pytagora Pro).
# ============================================================================
def resolve_slot_sequence(dice_pool, slots_list):
    """Dagli id negli slot (in ordine) alla lista di tessere (dict) posizionate,
    saltando gli slot vuoti."""
    by_id = {d["id"]: d for d in dice_pool}
    seq = []
    for ref in slots_list:
        if ref is None:
            continue
        tile = by_id.get(ref)
        if tile:
            seq.append(tile)
    return seq

def split_by_sides(tiles):
    sides = [[]]
    for t in tiles:
        if t["cat"] == "equals":
            sides.append([])
        else:
            sides[-1].append(t)
    return sides

def build_atoms_for_side(tiles):
    atoms = []
    num_buf = None
    def flush():
        nonlocal num_buf
        if num_buf is not None:
            atoms.append(num_buf)
            num_buf = None
    for t in tiles:
        cat = t["cat"]
        if cat == "digit":
            if num_buf is None:
                num_buf = {"type":"num", "digits":[], "dec_digits":[], "has_comma":False, "period":False}
            if num_buf["has_comma"]:
                num_buf["dec_digits"].append(t["value"])
            else:
                num_buf["digits"].append(t["value"])
        elif cat == "decsym" and t.get("kind") == "comma":
            if num_buf is None:
                num_buf = {"type":"num", "digits":[0], "dec_digits":[], "has_comma":False, "period":False}
            num_buf["has_comma"] = True
        elif cat == "decsym" and t.get("kind") == "period":
            if num_buf is not None:
                num_buf["period"] = True
        elif cat == "fracnum":
            flush()
            atoms.append({"type":"num", "is_frac":True, "value":t["value"], "display":t["display"]})
        elif cat in ("addsub", "muldiv"):
            flush()
            atoms.append({"type":"op", "op":t["op"], "tile":t})
        elif cat == "paren":
            flush()
            atoms.append({"type":"lparen" if t.get("side")=="open" else "rparen", "tile":t})
        elif cat == "advop":
            flush()
            kind = t["kind"]
            if kind in ("sqrt","cbrt","root4"):
                atoms.append({"type":"prefix", "kind":kind, "tile":t})
            else:
                atoms.append({"type":"postfix", "kind":kind, "tile":t})
    flush()
    return atoms

def num_atom_value(a):
    if a.get("is_frac"):
        return a["value"]
    int_part = "".join(str(d) for d in a["digits"]) or "0"
    val = int(int_part)
    if a["has_comma"]:
        dec_str = "".join(str(d) for d in a["dec_digits"])
        val = float(f"{int_part}.{dec_str or '0'}")
    return val

def num_atom_display(a):
    if a.get("is_frac"):
        return a["display"]
    s = "".join(str(d) for d in a["digits"])
    if a["has_comma"]:
        s += "," + "".join(str(d) for d in a["dec_digits"])
    if a.get("period"):
        s += "\u203e"
    return s

def num_atom_validity(a):
    if a.get("is_frac"):
        return None
    if len(a["digits"]) > 1 and a["digits"][0] == 0:
        return f"zero iniziale non ammesso in \"{num_atom_display(a)}\""
    if a["has_comma"]:
        if not a["dec_digits"]:
            return "virgola senza cifre decimali"
        if a["dec_digits"][-1] == 0:
            return f"zero finale dopo la virgola non ammesso in \"{num_atom_display(a)}\""
    return None

class ParseError(Exception):
    pass

def parse_side(atoms):
    pos = [0]
    def peek():
        return atoms[pos[0]] if pos[0] < len(atoms) else None
    def primary():
        a = peek()
        if a is None:
            raise ParseError("espressione incompleta")
        if a["type"] == "lparen":
            open_tile = a["tile"]; pos[0]+=1
            inner = expr()
            if peek() is None or peek()["type"] != "rparen":
                raise ParseError("parentesi non bilanciate")
            close_tile = peek()["tile"]; pos[0]+=1
            return {"kind":"group", "value":inner["value"], "child":inner, "open_tile":open_tile, "close_tile":close_tile}
        if a["type"] == "prefix":
            pos[0]+=1
            arg = primary()
            if a["kind"]=="sqrt": v = arg["value"] ** 0.5
            elif a["kind"]=="cbrt": v = arg["value"] ** (1/3) if arg["value"]>=0 else -((-arg["value"])**(1/3))
            else: v = arg["value"] ** 0.25
            return {"kind":"radical", "value":v, "rad_kind":a["kind"], "arg":arg, "tile":a["tile"]}
        if a["type"] == "num":
            pos[0]+=1
            err = num_atom_validity(a)
            return {"kind":"num", "value":num_atom_value(a), "atom":a, "valid": err is None, "invalid_msg": err}
        raise ParseError("simbolo inatteso")
    def postfix_level():
        node = primary()
        while peek() and peek()["type"]=="postfix":
            p = peek(); pos[0]+=1
            p2 = 2 if p["kind"]=="sq" else (3 if p["kind"]=="cube" else 4)
            node = {"kind":"power", "value": node["value"]**p2, "base":node, "pow":p2, "tile":p["tile"]}
        return node
    def term():
        node = postfix_level()
        while peek() and peek()["type"]=="op" and peek()["op"] in ("*","/"):
            optok = peek(); pos[0]+=1
            right = postfix_level()
            v = node["value"]*right["value"] if optok["op"]=="*" else node["value"]/right["value"]
            node = {"kind":"binop", "value":v, "op":optok["op"], "left":node, "right":right, "tile":optok["tile"]}
        return node
    def expr():
        node = term()
        while peek() and peek()["type"]=="op" and peek()["op"] in ("+","-"):
            optok = peek(); pos[0]+=1
            right = term()
            v = node["value"]+right["value"] if optok["op"]=="+" else node["value"]-right["value"]
            node = {"kind":"binop", "value":v, "op":optok["op"], "left":node, "right":right, "tile":optok["tile"]}
        return node
    root = expr()
    if pos[0] != len(atoms):
        raise ParseError("simboli in eccesso")
    return root

def collect_invalid(node, errs):
    if node is None:
        return
    k = node["kind"]
    if k == "num":
        if not node["valid"]:
            errs.append(node["invalid_msg"])
        return
    if k == "group":
        collect_invalid(node["child"], errs); return
    if k == "radical":
        collect_invalid(node["arg"], errs); return
    if k == "power":
        collect_invalid(node["base"], errs); return
    if k == "binop":
        collect_invalid(node["left"], errs); collect_invalid(node["right"], errs)
        if node["op"]=="*" and (node["left"]["value"]==0 or node["right"]["value"]==0):
            errs.append("moltiplicazione per zero non ammessa")
        if node["op"]=="/" and node["left"]["value"]==0:
            errs.append("non si puo' dividere zero per un numero")
        if node["op"]=="/" and node["right"]["value"]==0:
            errs.append("divisione per zero non ammessa")

def score_points(node, breakdown):
    def walk_num(nd):
        a = nd["atom"]; local = 0; n = len(a["digits"])
        for idx, d in enumerate(a["digits"]):
            place = n-1-idx
            val = place+1
            local += val
            breakdown.append({"label": f"cifra '{d}'" + (" (posizionale)" if place>0 else ""), "pts": val})
        if a["has_comma"]:
            local += 1
            breakdown.append({"label":"virgola", "pts":1})
            for idx, d in enumerate(a["dec_digits"]):
                place = idx+1
                local += place
                breakdown.append({"label": f"cifra decimale '{d}'" + (" (posizionale)" if place>1 else ""), "pts": place})
        if a.get("period"):
            local += 1
            breakdown.append({"label":"periodo", "pts":1})
        return local

    def walk(nd):
        pts = 0
        k = nd["kind"]
        if k == "num":
            if nd["atom"].get("is_frac"):
                pts += 1
                breakdown.append({"label": f"frazione '{nd['atom']['display']}'", "pts":1})
                return pts
            return walk_num(nd)
        if k == "group":
            pts += walk(nd["child"])
            pts += 1
            breakdown.append({"label":"parentesi aperta", "pts":1})
            return pts
        if k == "radical":
            pts += walk(nd["arg"])
            arg_is_one = nd["arg"]["value"] == 1
            val = 1 if arg_is_one else 2
            pts += val
            label = {"sqrt":"radice quadrata","cbrt":"radice cubica","root4":"radice quarta"}[nd["rad_kind"]]
            breakdown.append({"label":label, "pts":val})
            return pts
        if k == "power":
            pts += walk(nd["base"])
            base_is_one = nd["base"]["value"] == 1
            val = 1 if base_is_one else 2
            pts += val
            breakdown.append({"label": f"potenza ^{nd['pow']}", "pts":val})
            return pts
        if k == "binop":
            pts += walk(nd["left"]); pts += walk(nd["right"])
            val = 1
            if nd["op"] in ("*","/"):
                op_by_one = nd["left"]["value"]==1 or nd["right"]["value"]==1
                self_div = nd["op"]=="/" and nd["left"]["value"]==nd["right"]["value"]
                base = 2 if nd["op"]=="*" else 3
                val = 1 if (op_by_one or self_div) else base
            pts += val
            sym = "\u00d7" if nd["op"]=="*" else ("\u00f7" if nd["op"]=="/" else nd["op"])
            breakdown.append({"label": sym, "pts": val})
            return pts
        return 0
    return walk(node)

def round4(x):
    return round(x*10000)/10000

def evaluate_sequence(tiles):
    """tiles: lista ordinata di tessere (dict) posizionate negli slot.
    Ritorna dict: {ok, message, total, breakdown}"""
    if not tiles:
        return {"ok": False, "message": "Nessuna tessera posizionata."}
    sides_tiles = split_by_sides(tiles)
    if len(sides_tiles) < 2:
        return {"ok": False, "message": "Manca il simbolo di uguale."}
    if any(len(s)==0 for s in sides_tiles):
        return {"ok": False, "message": "Lato dell'uguaglianza vuoto."}
    parsed_sides = []
    try:
        for s in sides_tiles:
            atoms = build_atoms_for_side(s)
            parsed_sides.append(parse_side(atoms))
    except ParseError as e:
        return {"ok": False, "message": f"Espressione non valida: {e}"}

    errs = []
    for n in parsed_sides:
        collect_invalid(n, errs)
    if errs:
        return {"ok": False, "message": errs[0]}

    for i in range(1, len(parsed_sides)):
        if abs(parsed_sides[i]["value"] - parsed_sides[0]["value"]) > 1e-9:
            return {"ok": False, "message": f"I due lati non sono uguali ({round4(parsed_sides[0]['value'])} \u2260 {round4(parsed_sides[i]['value'])})."}

    breakdown = []
    total = 0
    for side in parsed_sides:
        total += score_points(side, breakdown)

    if total <= 0:
        return {"ok": False, "message": "L'uguaglianza non introduce punti validi."}
    return {"ok": True, "total": total, "breakdown": breakdown}

# ---- ROUTES ----
@app.route("/")
def home():
    return render_template_string(html_content)

@app.get("/api/state")
def api_state():
    game_id = request.args.get("game_id", "default")
    player = request.args.get("player")
    state = load_game(game_id)

    # Forza reroll se timer scaduto
    if state.get("round_started_at") and state.get("timer"):
        try:
            started = datetime.fromisoformat(state["round_started_at"])
        except Exception:
            started = None
        if started is not None:
            now_utc = datetime.utcnow().replace(tzinfo=timezone.utc)
            elapsed = (now_utc - started).total_seconds()
            if elapsed >= state["timer"]:
                state["dice_pool"] = roll_full_set()
                for p in state.get('players', []):
                    state.setdefault('personal_slots', {})[p] = [None]*13
                state['round_started_at'] = now_utc.isoformat()
                state['already_verified'] = []
                state['last_feedback'] = "⏰ Tempo scaduto! Nuovi dadi generati."
                save_game(game_id, state)

    # ordina i giocatori per punteggio (top first)
    state['players'] = sorted(state.get('players', []), key=lambda p: state['scores'].get(p, 0), reverse=True)

    # garantisci 13 slot per ciascun player
    for p in state.get('players', []):
        state.setdefault('personal_slots', {}).setdefault(p, [None]*13)

    view = dict(state)
    view['my_slots'] = state.get('personal_slots', {}).get(player, [None]*13) if player else [None]*13
    return jsonify(view)

@app.post("/api/add_player")
def api_add_player():
    game_id = request.args.get("game_id", "default")
    name = (request.json or {}).get("name", "").strip()
    if not name:
        return jsonify({"error": "Nome richiesto"}), 400

    state = load_game(game_id)
    if name not in state.get("players", []):
        state.setdefault("players", []).append(name)
        state.setdefault("scores", {})[name] = state.get("scores", {}).get(name, 0)
        state.setdefault('personal_slots', {})[name] = [None]*13
        state.setdefault('slots_by_player', {})[name] = [None]*13  # back-compat
        save_game(game_id, state)
    return jsonify(state)

@app.post("/api/roll")
def api_roll():
    game_id = request.args.get("game_id", "default")
    state = load_game(game_id)
    state["dice_pool"] = roll_full_set()
    for p in state.get('players', []):
        state.setdefault('personal_slots', {})[p] = [None]*13
    state['round_started_at'] = datetime.utcnow().replace(tzinfo=timezone.utc).isoformat()
    state['already_verified'] = []
    state['last_feedback'] = "Nuovi dadi generati"
    save_game(game_id, state)
    return jsonify(state)

@app.post("/api/place")
def api_place():
    game_id = request.args.get("game_id", "default")
    player = request.args.get('player') or (request.json or {}).get('player')
    payload = request.get_json(silent=True) or {}
    die_id = payload.get("die_id")
    target_slot = payload.get("slot")

    if not die_id:
        return jsonify({"error": "die_id richiesto"}), 400

    state = load_game(game_id)
    if not player:
        return jsonify({"error": "player richiesto"}), 400
    if player not in state.get('players', []):
        return jsonify({"error": "Player non registrato"}), 400

    valid_ids = {d["id"] for d in state.get("dice_pool", [])}
    if die_id not in valid_ids:
        return jsonify({"error": "Dado non trovato"}), 404

    pslots = state.setdefault('personal_slots', {}).setdefault(player, [None]*13)
    if die_id in pslots:
        return jsonify({"error": "Dado già piazzato nei tuoi slot", "state": state}), 400

    if target_slot is not None:
        try:
            idx = int(target_slot)
        except (TypeError, ValueError):
            return jsonify({"error": "slot deve essere un intero tra 0 e 12"}), 400
        if not (0 <= idx < len(pslots)):
            return jsonify({"error": "Indice slot fuori range"}), 400
        if pslots[idx] is not None:
            return jsonify({"error": "Slot già occupato"}), 400
    else:
        try:
            idx = pslots.index(None)
        except ValueError:
            return jsonify({"error": "Nessuno slot libero nei tuoi slot"}), 400

    pslots[idx] = die_id
    save_game(game_id, state)
    return jsonify(state)

@app.post("/api/remove")
def api_remove():
    game_id = request.args.get("game_id", "default")
    player = request.args.get('player') or (request.json or {}).get('player')
    die_id = (request.json or {}).get("die_id")

    state = load_game(game_id)
    if not player:
        return jsonify({"error": "player richiesto"}), 400

    pslots = state.setdefault('personal_slots', {}).setdefault(player, [None]*13)
    for i, ref in enumerate(pslots):
        if ref == die_id:
            pslots[i] = None
            break

    save_game(game_id, state)
    return jsonify(state)

@app.post("/api/verify")
def api_verify():
    game_id = request.args.get("game_id", "default")
    player = request.args.get('player') or (request.json or {}).get('player')
    state = load_game(game_id)

    if not player:
        return jsonify({"ok": False, "message": "player richiesto", "state": state}), 400

    # un solo tentativo per round
    if player in state.get('already_verified', []):
        return jsonify({"ok": False, "message": "Hai già verificato in questo round", "state": state}), 200

    pslots = state.get('personal_slots', {}).get(player, [None]*13)
    tiles = resolve_slot_sequence(state.get('dice_pool', []), pslots)
    result = evaluate_sequence(tiles)
    if not result["ok"]:
        state["last_feedback"] = f"❌ {result['message']}"
        save_game(game_id, state)
        return jsonify({"ok": False, "message": result["message"], "state": state}), 200

    points = result["total"]
    state.setdefault('scores', {})[player] = state.get('scores', {}).get(player, 0) + points
    state.setdefault('personal_slots', {})[player] = [None]*13
    state.setdefault('already_verified', []).append(player)

    # vittoria
    if state['scores'][player] >= state.get('victory_score', 50):
        state['winner'] = player
        state['last_feedback'] = f"🎉 {player} ha vinto raggiungendo {state['scores'][player]} punti!"
    else:
        state['last_feedback'] = f"✅ {player}: +{points} punti"

    save_game(game_id, state)
    return jsonify({"ok": True, "points": points, "breakdown": result.get("breakdown", []), "state": state})

@app.post("/api/set_victory")
def api_set_victory():
    game_id = request.args.get("game_id", "default")
    state = load_game(game_id)
    value = (request.json or {}).get("victory")
    try:
        val = int(value)
        if val in [30, 40, 50, 60]:
            state['victory_score'] = val
            save_game(game_id, state)
            return jsonify(state)
    except Exception:
        pass
    return jsonify({"error": "Valore non valido"}), 400

@app.post("/api/set_timer")
def api_set_timer():
    game_id = request.args.get("game_id", "default")
    state = load_game(game_id)
    seconds = (request.json or {}).get("seconds", 60)
    try:
        sec = int(seconds)
        if sec >= 0 and sec <= 3600:
            state['timer'] = sec
            # se non c'è round in corso, parte da ora; se c'è, manteniamo start e si aggiorna al prossimo reroll
            if state.get('round_started_at') is None and sec > 0:
                state['round_started_at'] = datetime.utcnow().replace(tzinfo=timezone.utc).isoformat()
            save_game(game_id, state)
            return jsonify(state)
    except Exception:
        pass
    return jsonify({"error": "Timer non valido"}), 400

@app.post("/api/reset_game")
def api_reset_game():
    game_id = request.args.get("game_id", "default")
    fresh = default_game_state(game_id)
    save_game(game_id, fresh)
    return jsonify(fresh)


# ---- Avvio locale ----
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
