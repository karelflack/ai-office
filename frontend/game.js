// ============================================================
//  AI OFFICE — Pixel Art Agent Visualizer
//  No external dependencies — pure Canvas 2D
// ============================================================

const CANVAS_W = 780;
const CANVAS_H = 560;
const SCALE    = 1;          // retina: set to 2 for HiDPI

// ── Colour palette ──────────────────────────────────────────
const C = {
  floor:      '#d4c5a9',
  floorLine:  '#c2b49a',
  wall:       '#7a6248',
  wallTop:    '#5c4733',
  desk:       '#8b5e3c',
  deskTop:    '#a0724d',
  monitor:    '#1a1a2e',
  monitorGlow:'#4ecdc4',
  bench:      '#6b4c2a',
  benchTop:   '#7d5a35',
  carpet:     '#3d5a80',
  carpetEdge: '#2d4a70',
  window:     '#a8d8ea',
  windowFrame:'#5c4733',
  plant:      '#2d6a4f',
  plantPot:   '#b5703a',
  shadow:     'rgba(0,0,0,0.18)',
  exitDoor:   '#e9c46a',
  exitFrame:  '#5c4733',
  exitSign:   '#e94560',
};

// ── Office layout ────────────────────────────────────────────
const ZONES = {
  boss_desk:   { x: 630, y: 140 },
  reception:   { x: 500, y: 240 },   // agents queue here
  exit:        { x: 390, y: 510 },
  workbenches: [
    { x: 120, y: 145 },
    { x: 120, y: 285 },
    { x: 120, y: 420 },
    { x: 310, y: 145 },
    { x: 310, y: 285 },
  ],
};

// ── Agent config ─────────────────────────────────────────────
const AGENT_COLORS = {
  boss:  '#e94560',
  alice: '#4ecdc4',
  bob:   '#ff6b6b',
  carol: '#ffd93d',
  dave:  '#6bcb77',
  eve:   '#a855f7',
};

const STATE_LABELS = {
  idle:             'Idle',
  walking_to_boss:  'Walking to boss',
  waiting:          'Waiting for boss',
  receiving_task:   'Receiving task',
  walking_to_bench: 'Going to workbench',
  working:          'Working…',
  walking_to_exit:  'Heading outside',
  outside:          'Outside (web search)',
  returning:        'Returning',
  reporting:        'Reporting results',
  thinking:         'Thinking…',
  assigning:        'Assigning tasks',
  synthesizing:     'Synthesizing results',
  done:             'Done!',
};

// ============================================================
//  Agent class
// ============================================================
class Agent {
  constructor(id, name, color, homePos) {
    this.id      = id;
    this.name    = name;
    this.color   = color;
    this.home    = { ...homePos };
    this.x       = homePos.x;
    this.y       = homePos.y;
    this.targetX = homePos.x;
    this.targetY = homePos.y;
    this.state   = 'idle';
    this.task    = '';
    this.result  = '';
    this.walkPhase = 0;
    this.speed   = 1.8;
    this.visible = true;
    this.isBoss  = (id === 'boss');
    this.speechBubble = null; // { text, alpha, timer }
  }

  setSpeechBubble(text, duration = 3500) {
    if (this.speechBubble && this.speechBubble._timeout) {
      clearTimeout(this.speechBubble._timeout);
    }
    const bubble = { text: text.slice(0, 48), alpha: 1 };
    bubble._timeout = setTimeout(() => {
      // Fade out over 600ms
      const start = Date.now();
      const fade = () => {
        const elapsed = Date.now() - start;
        bubble.alpha = Math.max(0, 1 - elapsed / 600);
        if (bubble.alpha > 0) requestAnimationFrame(fade);
        else this.speechBubble = null;
      };
      requestAnimationFrame(fade);
    }, duration);
    this.speechBubble = bubble;
  }

  setTarget(x, y) {
    this.targetX = x;
    this.targetY = y;
  }

  update() {
    const dx = this.targetX - this.x;
    const dy = this.targetY - this.y;
    const dist = Math.sqrt(dx * dx + dy * dy);
    if (dist > 1) {
      this.x += (dx / dist) * Math.min(this.speed, dist);
      this.y += (dy / dist) * Math.min(this.speed, dist);
      this.walkPhase += 0.25;
    }
  }

  isAtTarget() {
    return Math.abs(this.x - this.targetX) < 2 && Math.abs(this.y - this.targetY) < 2;
  }

  draw(ctx) {
    if (!this.visible) return;
    const x = Math.round(this.x);
    const y = Math.round(this.y);
    const moving = Math.abs(this.x - this.targetX) > 2 || Math.abs(this.y - this.targetY) > 2;

    // Shadow
    ctx.fillStyle = C.shadow;
    ctx.beginPath();
    ctx.ellipse(x, y + 16, 8, 4, 0, 0, Math.PI * 2);
    ctx.fill();

    // Legs (animated)
    const legSwing = moving ? Math.sin(this.walkPhase) * 5 : 0;
    ctx.fillStyle = this.color;
    this._px(ctx, x - 4 + legSwing, y + 8, 5, 8);
    this._px(ctx, x + 1 - legSwing, y + 8, 5, 8);

    // Body
    ctx.fillStyle = this.color;
    this._px(ctx, x - 7, y - 8, 14, 16);

    // Arms (animated)
    const armSwing = moving ? Math.sin(this.walkPhase) * 6 : 0;
    ctx.fillStyle = this.color;
    this._px(ctx, x - 11, y - 6 + armSwing, 4, 10);
    this._px(ctx, x + 7,  y - 6 - armSwing, 4, 10);

    // Head
    ctx.fillStyle = '#f5cba7';
    this._px(ctx, x - 6, y - 22, 12, 12);

    // Eyes
    ctx.fillStyle = '#2c2c2c';
    this._px(ctx, x - 4, y - 18, 3, 3);
    this._px(ctx, x + 1, y - 18, 3, 3);

    // Hair / hat colour strip
    ctx.fillStyle = this.color;
    this._px(ctx, x - 6, y - 22, 12, 4);

    // Name tag (small, above head)
    if (!this.isBoss) {
      ctx.font = 'bold 9px "Courier New"';
      ctx.textAlign = 'center';
      ctx.fillStyle = 'rgba(0,0,0,0.6)';
      ctx.fillRect(x - 18, y - 35, 36, 11);
      ctx.fillStyle = '#ffffff';
      ctx.fillText(this.name, x, y - 26);
    }

    // Speech bubble
    if (this.speechBubble && this.speechBubble.alpha > 0) {
      const bub = this.speechBubble;
      const bx = x + 14;
      const by = y - 44;
      const pad = 5;
      ctx.font = '9px "Courier New"';
      const tw = ctx.measureText(bub.text).width;
      const bw = tw + pad * 2;
      const bh = 14;
      ctx.globalAlpha = bub.alpha;
      // Bubble background
      ctx.fillStyle = '#fffde7';
      ctx.beginPath();
      ctx.roundRect(bx, by, bw, bh, 3);
      ctx.fill();
      ctx.strokeStyle = '#999';
      ctx.lineWidth = 1;
      ctx.stroke();
      // Tail
      ctx.fillStyle = '#fffde7';
      ctx.beginPath();
      ctx.moveTo(bx + 6, by + bh);
      ctx.lineTo(bx + 2, by + bh + 5);
      ctx.lineTo(bx + 12, by + bh);
      ctx.fill();
      // Text
      ctx.fillStyle = '#222';
      ctx.textAlign = 'left';
      ctx.fillText(bub.text, bx + pad, by + bh - 3);
      ctx.globalAlpha = 1;
    }

    // State indicator dot
    if (this.state !== 'idle') {
      const dotColor = this.state === 'working' || this.state === 'outside' ? '#ffd93d'
                     : this.state === 'reporting' ? '#6bcb77'
                     : this.state === 'receiving_task' ? '#e94560'
                     : '#4ecdc4';
      ctx.fillStyle = dotColor;
      ctx.beginPath();
      ctx.arc(x + 7, y - 22, 4, 0, Math.PI * 2);
      ctx.fill();
      ctx.fillStyle = '#fff';
      ctx.beginPath();
      ctx.arc(x + 7, y - 22, 2, 0, Math.PI * 2);
      ctx.fill();
    }
  }

  // Draw a crisp pixel-art rectangle
  _px(ctx, x, y, w, h) {
    ctx.fillRect(Math.round(x), Math.round(y), w, h);
  }

  getBounds() {
    return { x: this.x - 12, y: this.y - 26, w: 24, h: 32 };
  }
}

// ============================================================
//  Office renderer
// ============================================================
function drawOffice(ctx) {
  // ── Floor ──────────────────────────────────────────────────
  ctx.fillStyle = C.floor;
  ctx.fillRect(0, 0, CANVAS_W, CANVAS_H);

  // Floor grid lines
  ctx.strokeStyle = C.floorLine;
  ctx.lineWidth = 1;
  for (let x = 0; x < CANVAS_W; x += 40) {
    ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, CANVAS_H); ctx.stroke();
  }
  for (let y = 0; y < CANVAS_H; y += 40) {
    ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(CANVAS_W, y); ctx.stroke();
  }

  // ── Carpet in boss area ────────────────────────────────────
  ctx.fillStyle = C.carpet;
  ctx.fillRect(545, 80, 200, 200);
  ctx.strokeStyle = C.carpetEdge;
  ctx.lineWidth = 3;
  ctx.strokeRect(550, 85, 190, 190);

  // ── Walls (top + left) ────────────────────────────────────
  ctx.fillStyle = C.wall;
  ctx.fillRect(0, 0, CANVAS_W, 30);   // top wall
  ctx.fillRect(0, 0, 30, CANVAS_H);   // left wall
  ctx.fillStyle = C.wallTop;
  ctx.fillRect(0, 0, CANVAS_W, 8);
  ctx.fillRect(0, 0, 8, CANVAS_H);

  // ── Windows on top wall ───────────────────────────────────
  [[100, 0], [280, 0], [460, 0], [640, 0]].forEach(([wx]) => {
    ctx.fillStyle = C.windowFrame;
    ctx.fillRect(wx, 0, 60, 30);
    ctx.fillStyle = C.window;
    ctx.fillRect(wx + 4, 2, 52, 24);
    // Window pane cross
    ctx.strokeStyle = C.windowFrame;
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(wx + 30, 2);
    ctx.lineTo(wx + 30, 26);
    ctx.moveTo(wx + 4, 14);
    ctx.lineTo(wx + 56, 14);
    ctx.stroke();
  });

  // ── Boss desk ─────────────────────────────────────────────
  const bd = ZONES.boss_desk;
  drawDesk(ctx, bd.x - 40, bd.y - 20, 90, 55, true);

  // Boss nameplate
  ctx.fillStyle = '#e94560';
  ctx.fillRect(bd.x - 20, bd.y + 10, 50, 12);
  ctx.fillStyle = '#fff';
  ctx.font = 'bold 9px "Courier New"';
  ctx.textAlign = 'center';
  ctx.fillText('BOSS', bd.x + 5, bd.y + 20);

  // ── Divider wall / partition ──────────────────────────────
  ctx.fillStyle = C.wallTop;
  ctx.fillRect(450, 30, 8, 190);
  ctx.fillStyle = C.wall;
  ctx.fillRect(452, 32, 4, 186);

  // ── Worker benches ────────────────────────────────────────
  const workerNames = ['Alice', 'Bob', 'Carol', 'Dave', 'Eve'];
  ZONES.workbenches.forEach((pos, i) => {
    drawBench(ctx, pos.x - 35, pos.y - 20, 80, 45);
    // Small name label on bench
    ctx.fillStyle = '#555';
    ctx.fillRect(pos.x - 25, pos.y + 5, 50, 10);
    ctx.fillStyle = Object.values(AGENT_COLORS).slice(1)[i] || '#fff';
    ctx.font = '8px "Courier New"';
    ctx.textAlign = 'center';
    ctx.fillText(workerNames[i], pos.x, pos.y + 13);
  });

  // ── Reception counter ─────────────────────────────────────
  const rc = ZONES.reception;
  ctx.fillStyle = C.desk;
  ctx.fillRect(rc.x - 30, rc.y - 12, 60, 30);
  ctx.fillStyle = C.deskTop;
  ctx.fillRect(rc.x - 28, rc.y - 14, 56, 6);
  ctx.fillStyle = '#888';
  ctx.font = '8px "Courier New"';
  ctx.textAlign = 'center';
  ctx.fillText('QUEUE', rc.x, rc.y + 6);

  // ── Exit door ─────────────────────────────────────────────
  const ed = ZONES.exit;
  ctx.fillStyle = C.exitFrame;
  ctx.fillRect(ed.x - 22, ed.y - 10, 44, 50);
  ctx.fillStyle = C.exitDoor;
  ctx.fillRect(ed.x - 18, ed.y - 6, 36, 44);
  // Door knob
  ctx.fillStyle = '#888';
  ctx.beginPath();
  ctx.arc(ed.x + 12, ed.y + 18, 3, 0, Math.PI * 2);
  ctx.fill();
  // EXIT sign above
  ctx.fillStyle = C.exitSign;
  ctx.fillRect(ed.x - 20, ed.y - 26, 40, 16);
  ctx.fillStyle = '#fff';
  ctx.font = 'bold 9px "Courier New"';
  ctx.textAlign = 'center';
  ctx.fillText('EXIT', ed.x, ed.y - 13);

  // ── Plants ────────────────────────────────────────────────
  [[50, 60], [50, 500], [730, 60], [730, 480]].forEach(([px, py]) => {
    drawPlant(ctx, px, py);
  });
}

function drawDesk(ctx, x, y, w, h, isBoss) {
  // Desk shadow
  ctx.fillStyle = C.shadow;
  ctx.fillRect(x + 4, y + 4, w, h);
  // Desk body
  ctx.fillStyle = isBoss ? '#5c3d1e' : C.bench;
  ctx.fillRect(x, y, w, h);
  // Desk top surface
  ctx.fillStyle = isBoss ? '#7a5230' : C.benchTop;
  ctx.fillRect(x, y, w, 10);
  // Monitor
  ctx.fillStyle = C.monitor;
  ctx.fillRect(x + w * 0.5 - 14, y - 20, 28, 20);
  ctx.fillStyle = C.monitorGlow;
  ctx.fillRect(x + w * 0.5 - 12, y - 18, 24, 16);
  // Monitor stand
  ctx.fillStyle = '#555';
  ctx.fillRect(x + w * 0.5 - 3, y, 6, 6);
}

function drawBench(ctx, x, y, w, h) {
  ctx.fillStyle = C.shadow;
  ctx.fillRect(x + 3, y + 3, w, h);
  ctx.fillStyle = C.bench;
  ctx.fillRect(x, y, w, h);
  ctx.fillStyle = C.benchTop;
  ctx.fillRect(x, y, w, 8);
  // Small monitor
  ctx.fillStyle = C.monitor;
  ctx.fillRect(x + 8, y - 14, 20, 14);
  ctx.fillStyle = C.monitorGlow;
  ctx.fillRect(x + 10, y - 12, 16, 10);
  ctx.fillStyle = '#555';
  ctx.fillRect(x + 16, y, 4, 5);
}

function drawPlant(ctx, x, y) {
  ctx.fillStyle = C.plantPot;
  ctx.fillRect(x - 8, y, 16, 14);
  ctx.fillStyle = C.plant;
  ctx.beginPath();
  ctx.arc(x, y - 6, 12, 0, Math.PI * 2);
  ctx.fill();
  ctx.beginPath();
  ctx.arc(x - 10, y - 2, 8, 0, Math.PI * 2);
  ctx.fill();
  ctx.beginPath();
  ctx.arc(x + 10, y - 2, 8, 0, Math.PI * 2);
  ctx.fill();
}

// ============================================================
//  Main App
// ============================================================
class OfficeApp {
  constructor() {
    this.canvas  = document.getElementById('office-canvas');
    this.ctx     = this.canvas.getContext('2d');
    this.canvas.width  = CANVAS_W;
    this.canvas.height = CANVAS_H;
    this.canvas.style.width  = CANVAS_W + 'px';
    this.canvas.style.height = CANVAS_H + 'px';

    this.agents   = {};
    this.ws       = null;
    this.busy     = false;
    this.officeStaticCanvas = document.createElement('canvas');
    this.officeStaticCanvas.width  = CANVAS_W;
    this.officeStaticCanvas.height = CANVAS_H;
    drawOffice(this.officeStaticCanvas.getContext('2d'));

    this.tooltip  = document.getElementById('tooltip');
    this.log      = document.getElementById('task-log');
    this.finalPanel = document.getElementById('final-panel');
    this.finalText  = document.getElementById('final-text');
    this.input    = document.getElementById('task-input');
    this.sendBtn  = document.getElementById('send-btn');
    this.modeBadge = document.getElementById('mode-badge');
    this.time = 0;

    this._initAgents();
    this._initInput();
    this._connectWS();
    this._startLoop();
    this._initHover();
  }

  _initAgents() {
    this.agents['boss'] = new Agent('boss', 'Boss', AGENT_COLORS.boss, ZONES.boss_desk);

    const workers = ['alice', 'bob', 'carol', 'dave', 'eve'];
    workers.forEach((id, i) => {
      const bench = ZONES.workbenches[i] || ZONES.workbenches[0];
      const a = new Agent(id, id.charAt(0).toUpperCase() + id.slice(1),
                          AGENT_COLORS[id], bench);
      this.agents[id] = a;
    });
  }

  _initInput() {
    this.sendBtn.addEventListener('click', () => this._sendTask());
    this.input.addEventListener('keydown', e => {
      if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); this._sendTask(); }
    });
  }

  _sendTask() {
    const text = this.input.value.trim();
    if (!text || this.busy) return;
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({ type: 'task', text }));
      this.input.value = '';
    }
  }

  _connectWS() {
    const proto = location.protocol === 'https:' ? 'wss' : 'ws';
    this.ws = new WebSocket(`${proto}://${location.host}/ws`);

    this.ws.onopen = () => {
      this.modeBadge.textContent = 'CONNECTED';
      this.modeBadge.style.color = '#6bcb77';
    };

    this.ws.onclose = () => {
      this.modeBadge.textContent = 'DISCONNECTED';
      this.modeBadge.style.color = '#e94560';
      setTimeout(() => this._connectWS(), 3000);
    };

    this.ws.onmessage = (e) => {
      const msg = JSON.parse(e.data);
      this._handleMessage(msg);
    };
  }

  _handleMessage(msg) {
    switch (msg.type) {
      case 'connected':
        this.modeBadge.textContent = msg.mock_mode ? 'MOCK MODE' : 'LIVE (Claude API)';
        this._addLog('system', `Office connected. Workers: ${msg.workers.join(', ')}`);
        break;

      case 'new_task':
        this.busy = true;
        this.sendBtn.disabled = true;
        this.sendBtn.textContent = 'BUSY...';
        this.finalPanel.style.display = 'none';
        this.finalText.textContent = '';
        this._addLog('boss', `New task received: ${msg.text}`);
        if (this.agents['boss']) this.agents['boss'].setSpeechBubble(`New task: ${msg.text.slice(0, 30)}...`);
        break;

      case 'boss_state': {
        const boss = this.agents['boss'];
        if (boss) {
          boss.state = msg.state;
          if (msg.message) boss.setSpeechBubble(msg.message);
        }
        this._addLog('boss', `Boss: ${STATE_LABELS[msg.state] || msg.state} — ${msg.message || ''}`);
        break;
      }

      case 'agent_state': {
        const agent = this.agents[msg.id];
        if (!agent) break;
        agent.state = msg.state;
        if (msg.task) agent.task = msg.task;
        if (msg.result) agent.result = msg.result;

        // Speech bubble
        const bubbleText = msg.state === 'receiving_task' ? `Got task!`
          : msg.state === 'working'        ? `Working...`
          : msg.state === 'outside'        ? `Searching web...`
          : msg.state === 'reporting'      ? `Done! Reporting`
          : msg.state === 'idle'           ? `Done.`
          : null;
        if (bubbleText) agent.setSpeechBubble(bubbleText, 2500);

        this._routeAgent(agent, msg.state);
        this._addLog('worker', `${agent.name}: ${STATE_LABELS[msg.state] || msg.state}${msg.task ? ' — ' + msg.task.slice(0, 60) : ''}`);
        break;
      }

      case 'final_answer':
        this.busy = false;
        this.sendBtn.disabled = false;
        this.sendBtn.textContent = 'SEND TASK';
        this._addLog('result', `RESULT: ${msg.text.slice(0, 120)}...`);
        // Show in the final answer panel
        this.finalText.textContent = msg.text;
        this.finalPanel.style.display = 'block';
        if (this.agents['boss']) this.agents['boss'].setSpeechBubble('Task complete!', 4000);
        break;

      case 'error':
        this.busy = false;
        this.sendBtn.disabled = false;
        this.sendBtn.textContent = 'SEND TASK';
        this._addLog('system', `Error: ${msg.message}`);
        break;
    }
  }

  _routeAgent(agent, state) {
    const workerIdx = ['alice','bob','carol','dave','eve'].indexOf(agent.id);
    const bench = ZONES.workbenches[workerIdx];
    // Stagger workers slightly so they don't pile up at the boss desk
    const bossOffset = { x: (workerIdx % 3) * 18 - 18, y: (workerIdx % 2) * 14 };

    switch (state) {
      case 'walking_to_boss':
        agent.visible = true;
        agent.setTarget(ZONES.boss_desk.x - 50 + bossOffset.x, ZONES.boss_desk.y + 40 + bossOffset.y);
        break;
      case 'receiving_task':
        agent.visible = true;
        // Stay near boss
        break;
      case 'walking_to_bench':
        agent.visible = true;
        if (bench) agent.setTarget(bench.x, bench.y);
        break;
      case 'working':
        agent.visible = true;
        if (bench) agent.setTarget(bench.x, bench.y);
        break;
      case 'outside':
        // Walk to exit, then hide
        agent.visible = true;
        agent.setTarget(ZONES.exit.x + bossOffset.x, ZONES.exit.y);
        setTimeout(() => { agent.visible = false; }, 2500);
        break;
      case 'returning':
        agent.visible = true;
        // Walk back from exit toward bench
        if (bench) agent.setTarget(bench.x, bench.y);
        break;
      case 'reporting':
        agent.visible = true;
        agent.setTarget(ZONES.boss_desk.x - 50 + bossOffset.x, ZONES.boss_desk.y + 40 + bossOffset.y);
        break;
      case 'idle':
        agent.visible = true;
        agent.task = '';
        if (bench) agent.setTarget(bench.x, bench.y);
        break;
    }
  }

  _startLoop() {
    const loop = () => {
      this._update();
      this._draw();
      requestAnimationFrame(loop);
    };
    requestAnimationFrame(loop);
  }

  _update() {
    this.time++;
    Object.values(this.agents).forEach(a => a.update());
  }

  _draw() {
    const ctx = this.ctx;
    // Draw pre-rendered static office
    ctx.drawImage(this.officeStaticCanvas, 0, 0);

    // Animated monitor glows for active workers
    this._drawMonitorGlows(ctx);

    // Sort agents by Y so those further down appear in front
    const sorted = Object.values(this.agents)
      .filter(a => a.visible)
      .sort((a, b) => a.y - b.y);
    sorted.forEach(a => a.draw(ctx));
  }

  _drawMonitorGlows(ctx) {
    const workerIds = ['alice', 'bob', 'carol', 'dave', 'eve'];
    const pulse = 0.45 + 0.55 * (0.5 + 0.5 * Math.sin(this.time * 0.08));

    workerIds.forEach((id, i) => {
      const agent = this.agents[id];
      if (!agent || !agent.visible) return;
      const active = agent.state === 'working' || agent.state === 'outside';
      if (!active) return;

      const pos = ZONES.workbenches[i];
      if (!pos) return;

      // Monitor glow rect (matches drawBench coordinates)
      const mx = pos.x - 35 + 10; // x + 10
      const my = pos.y - 20 - 12; // y - 12
      const mw = 16;
      const mh = 10;

      // Outer glow
      ctx.save();
      ctx.shadowColor = agent.color;
      ctx.shadowBlur = 12 * pulse;
      ctx.globalAlpha = 0.6 * pulse;
      ctx.fillStyle = agent.color;
      ctx.fillRect(mx, my, mw, mh);
      ctx.restore();
    });

    // Boss monitor glow when thinking/assigning/synthesizing
    const boss = this.agents['boss'];
    const bossActive = boss && ['thinking', 'assigning', 'synthesizing'].includes(boss.state);
    if (bossActive) {
      const bd = ZONES.boss_desk;
      const mx = bd.x - 40 + 45 - 12; // x + w*0.5 - 12
      const my = bd.y - 20 - 18;       // y - 18
      ctx.save();
      ctx.shadowColor = '#e94560';
      ctx.shadowBlur = 16 * pulse;
      ctx.globalAlpha = 0.65 * pulse;
      ctx.fillStyle = '#e94560';
      ctx.fillRect(mx, my, 24, 16);
      ctx.restore();
    }
  }

  _initHover() {
    this.canvas.addEventListener('mousemove', (e) => {
      const rect = this.canvas.getBoundingClientRect();
      const mx = e.clientX - rect.left;
      const my = e.clientY - rect.top;

      let hit = null;
      for (const agent of Object.values(this.agents)) {
        if (!agent.visible) continue;
        const b = agent.getBounds();
        if (mx >= b.x && mx <= b.x + b.w && my >= b.y && my <= b.y + b.h) {
          hit = agent; break;
        }
      }

      if (hit) {
        document.getElementById('tt-name').textContent  = hit.name;
        document.getElementById('tt-state').textContent = STATE_LABELS[hit.state] || hit.state;
        document.getElementById('tt-task').textContent  = hit.task || '';
        this.tooltip.style.display = 'block';
        this.tooltip.style.left = (e.clientX + 14) + 'px';
        this.tooltip.style.top  = (e.clientY - 10) + 'px';
      } else {
        this.tooltip.style.display = 'none';
      }
    });

    this.canvas.addEventListener('mouseleave', () => {
      this.tooltip.style.display = 'none';
    });
  }

  _addLog(type, text) {
    const el = document.createElement('div');
    el.className = `log-entry ${type}`;
    const time = new Date().toLocaleTimeString('en', { hour12: false });
    el.textContent = `[${time}] ${text}`;
    this.log.appendChild(el);
    this.log.scrollTop = this.log.scrollHeight;
    // Keep log from growing forever
    while (this.log.children.length > 120) this.log.removeChild(this.log.firstChild);
  }
}

// Start when DOM is ready
window.addEventListener('DOMContentLoaded', () => new OfficeApp());
