// Grille Talk 3D keychain stage: loads a keychain GLB (nodes: keychain > body, details, lights; link_0..n; ring)
// and hangs the chain from the keyring tab with a verlet rope (gravity, damping, fixed link lengths).
// Dragging turns the keychain, which moves the tab, which swings the chain. Paused off screen and in hidden tabs.
// Static (single render, no physics) under prefers-reduced-motion.
import {
  WebGLRenderer, Scene, PerspectiveCamera, Color, Vector3, Quaternion, Box3, Group,
  DirectionalLight, PMREMGenerator, SRGBColorSpace, ACESFilmicToneMapping, MathUtils,
  GLTFLoader, MeshoptDecoder, RoomEnvironment,
} from 'vendor-three';

const UP = new Vector3(0, 1, 0);
const GRAVITY = -9.81;
const TIME_SCALE = 0.62;      // real 4 cm chains swing very fast; slowed slightly so the motion reads
const DAMPING = 0.986;
const ITERATIONS = 10;
const SUBSTEPS = 3;

export const reducedMotion = () => window.matchMedia('(prefers-reduced-motion: reduce)').matches;

export function webglAvailable() {
  try {
    const c = document.createElement('canvas');
    return !!(window.WebGLRenderingContext && (c.getContext('webgl2') || c.getContext('webgl')));
  } catch (e) {
    return false;
  }
}

const loader = new GLTFLoader().setMeshoptDecoder(MeshoptDecoder);
const cache = new Map();
export function loadGLB(url) {
  if (!cache.has(url)) {
    const p = loader.loadAsync(url);
    p.catch(() => cache.delete(url));
    cache.set(url, p);
  }
  return cache.get(url).then((g) => g.scene.clone(true));
}

export class KeychainStage {
  /**
   * @param {HTMLElement} container element the canvas fills
   * @param {object} opts { align: HTMLElement|null (map the keychain onto this box, for the hero), viewBoxMarginMM: 1,
   *                        fit: 0.8 (share of the canvas the keychain body spans), interactive: true, onReady }
   */
  constructor(container, opts = {}) {
    this.container = container;
    this.opts = { align: null, fit: 0.62, interactive: true, ...opts };
    this.static = reducedMotion();
    this.renderer = new WebGLRenderer({ antialias: true, alpha: true, powerPreference: 'low-power' });
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
    this.renderer.outputColorSpace = SRGBColorSpace;
    this.renderer.toneMapping = ACESFilmicToneMapping;
    this.canvas = this.renderer.domElement;
    this.canvas.setAttribute('aria-hidden', 'true');
    container.appendChild(this.canvas);

    this.scene = new Scene();
    const pmrem = new PMREMGenerator(this.renderer);
    this.scene.environment = pmrem.fromScene(new RoomEnvironment(), 0.04).texture;
    this.scene.environmentIntensity = 0.55;
    const key = new DirectionalLight(0xffffff, 1.6); key.position.set(-0.4, 0.8, 1.2);
    const rim = new DirectionalLight(0xffffff, 0.6); rim.position.set(0.8, 0.2, -0.6);
    this.scene.add(key, rim);
    this.camera = new PerspectiveCamera(16, 1, 0.005, 5);

    this.visible = true;
    this.active = opts.active !== false;   // an inactive stage loads but does not render frames
    this.running = false;
    this.yaw = 0; this.yawV = 0; this.pitch = 0; this.pitchV = 0; this.t = 0;
    this.offsetX = 0; this.offsetV = 0;
    this._last = 0;
    this._tick = this._tick.bind(this);

    this.ro = new ResizeObserver(() => this.resize());
    this.ro.observe(container);
    if (this.opts.align) this.ro.observe(this.opts.align);
    this.io = new IntersectionObserver(([e]) => { this.visible = e.isIntersecting; this._maybeRun(); });
    this.io.observe(container);
    this._onVis = () => this._maybeRun();
    document.addEventListener('visibilitychange', this._onVis);
    if (this.opts.interactive && !this.static) this._bindDrag();
    if (window.__PREVIEW__) (window.__gtStages = window.__gtStages || []).push(this);   // local preview debugging only
  }

  async load(url, color) {
    const root = await loadGLB(url);
    if (this.disposed) return;
    if (this.root) this.scene.remove(this.root);
    this.root = root;
    const kc = root.getObjectByName('keychain');
    // pivot the keychain about its body centre, so turning it moves the tab and the chain follows
    kc.updateMatrixWorld(true);
    const box = new Box3();
    ['body', 'details'].forEach((n) => { const o = kc.getObjectByName(n); if (o) box.expandByObject(o); });
    this.bodyBox = box.clone();
    const c = box.getCenter(new Vector3());
    this.pivot = new Group();
    this.pivot.position.copy(c);
    root.add(this.pivot);
    this.pivot.add(kc);
    kc.position.sub(c);
    this.kc = kc;
    this.materials = [];
    root.traverse((o) => {
      if (o.isMesh && o.material && o.material.name === 'body') {
        o.material = o.material.clone();
        this.materials.push(o.material);
      }
    });
    if (color) this.setColor(color);
    this._initChain(root);
    this.scene.add(root);
    this.resize();
    this.render();
    this._maybeRun();
    if (this.opts.onReady) this.opts.onReady(this);
    return this;
  }

  setActive(on) {
    this.active = on;
    if (on) { this.resize(); this._maybeRun(); }
  }

  setColor({ hex, metal = 0, rough = 0.55 }) {
    for (const m of this.materials || []) { m.color.set(hex); m.metalness = metal; m.roughness = rough; }
    this.render();
  }

  _initChain(root) {
    const nodes = [];
    for (let i = 0; ; i++) { const n = root.getObjectByName(`link_${i}`); if (!n) break; nodes.push(n); }
    const ring = root.getObjectByName('ring');
    if (ring) nodes.push(ring);
    this.links = nodes;
    // particle 0 = keyring hole (keychain-local origin), then one particle per link/ring centre
    this.hole = new Vector3();
    this.kc.updateMatrixWorld(true);
    this.kc.localToWorld(this.hole.set(0, 0, 0));
    root.worldToLocal(this.hole);
    const pts = [this.hole.clone(), ...nodes.map((n) => n.position.clone())];
    this.p = pts.map((v) => v.clone());
    this.prev = pts.map((v) => v.clone());
    this.rest = [];
    for (let i = 1; i < pts.length; i++) this.rest.push(pts[i].distanceTo(pts[i - 1]));
    // rest orientation of each node relative to its hanging direction (alternating 90 degree twist)
    this.restQ = nodes.map((n, i) => {
      const dir = pts[i].clone().sub(pts[i + 1]).normalize();
      const q = new Quaternion().setFromUnitVectors(UP, dir).invert();
      return q.multiply(n.quaternion.clone());
    });
  }

  nudge(vx = 0, vy = 0) {
    // carousel moves and swipes: kick the chain sideways (shift previous positions = add velocity)
    if (!this.prev || this.static) return;
    for (let i = 1; i < this.prev.length; i++) { this.prev[i].x -= vx * 0.004 * i; this.prev[i].y -= vy * 0.002; }
    this.yawV += vx * 1.6;
    this._maybeRun();
  }

  _bindDrag() {
    let down = false, lx = 0, ly = 0, lt = 0, startX = 0, startY = 0, decided = false, horizontal = false;
    const el = this.canvas;
    el.addEventListener('pointerdown', (e) => {
      if (this.opts.interactive === 'mouse' && e.pointerType !== 'mouse') return;   // touch swipes belong to the carousel
      down = true; decided = false; lx = startX = e.clientX; ly = startY = e.clientY; lt = performance.now();
    });
    window.addEventListener('pointermove', (e) => {
      if (!down) return;
      const dx = e.clientX - lx, dy = e.clientY - ly;
      if (!decided && Math.hypot(e.clientX - startX, e.clientY - startY) > 6) {
        decided = true; horizontal = Math.abs(e.clientX - startX) > Math.abs(e.clientY - startY);
        if (horizontal && e.pointerType !== 'mouse') el.setPointerCapture?.(e.pointerId);
      }
      if (e.pointerType !== 'mouse' && decided && !horizontal) return;   // let vertical swipes scroll the page
      const now = performance.now(), dt = Math.max(8, now - lt);
      this.yaw = MathUtils.clamp(this.yaw + dx * 0.012, -1.3, 1.3);
      this.pitch = MathUtils.clamp(this.pitch + dy * 0.006, -0.5, 0.5);
      this.yawV = (dx * 0.012) / (dt / 1000);
      this.pitchV = (dy * 0.006) / (dt / 1000);
      lx = e.clientX; ly = e.clientY; lt = now;
      this._maybeRun();
    });
    const up = () => { down = false; };
    window.addEventListener('pointerup', up);
    window.addEventListener('pointercancel', up);
    this._dragging = () => down;
  }

  resize() {
    const w = this.container.clientWidth, h = this.container.clientHeight;
    if (!w || !h || !this.root) return;
    this.renderer.setSize(w, h, false);
    this.camera.aspect = w / h;
    const tan = Math.tan(MathUtils.degToRad(this.camera.fov / 2));
    const b = this.bodyBox, size = b.getSize(new Vector3()), c = b.getCenter(new Vector3());
    let ppm, ox = 0, oy = 0;   // pixels per metre at z = 0, and screen offset (px) of the body centre from canvas centre
    if (this.opts.align) {
      // map the body box (plus the SVG's 1 mm margin) exactly onto the align element, as the hero art does
      const a = this.opts.align.getBoundingClientRect(), r = this.container.getBoundingClientRect();
      const vbW = size.x + 0.002, vbH = size.y + 0.002;
      ppm = Math.min(a.width / vbW, a.height / vbH);
      ox = a.left + a.width / 2 - (r.left + r.width / 2);
      oy = a.top + a.height / 2 - (r.top + r.height / 2);
    } else {
      ppm = Math.min((w * this.opts.fit) / size.x, (h * this.opts.fit * 0.82) / size.y);
      oy = -h * 0.12;   // body sits above centre so the chain has room below
    }
    const dist = h / (2 * tan * ppm);
    this.camera.position.set(c.x - ox / ppm, c.y + oy / ppm, dist);
    this.camera.lookAt(this.camera.position.x, this.camera.position.y, 0);
    this.camera.near = dist / 20; this.camera.far = dist * 4;
    this.camera.updateProjectionMatrix();
    this.render();
  }

  _maybeRun() {
    const should = this.active && this.visible && !document.hidden && this.root && !this.static && !this.disposed;
    if (should && !this.running) { this.running = true; this._last = performance.now(); requestAnimationFrame(this._tick); }
    if (!should) this.running = false;
  }

  _tick(now) {
    if (!this.running) return;
    const dt = Math.min(0.05, Math.max(0, (now - this._last) / 1000));   // rAF time can precede the start stamp
    this._last = now;
    this.step(dt);
    this.render();
    requestAnimationFrame(this._tick);
  }

  step(dt) {
    this.t += dt;
    const dragging = this._dragging && this._dragging();
    if (!dragging) {
      // spring back toward a slow idle sway
      const target = Math.sin(this.t * 0.6) * 0.16;
      this.yawV += (target - this.yaw) * 14 * dt; this.yawV *= Math.pow(0.04, dt);
      this.pitchV += (0 - this.pitch) * 18 * dt; this.pitchV *= Math.pow(0.02, dt);
      this.yaw += this.yawV * dt; this.pitch += this.pitchV * dt;
    }
    this.pivot.rotation.set(this.pitch, this.yaw, Math.sin(this.t * 0.9) * 0.012);
    this.pivot.updateMatrixWorld(true);
    // pinned particle follows the tab
    this.kc.localToWorld(this.hole.set(0, 0, 0));
    this.root.worldToLocal(this.hole);
    const p = this.p, prev = this.prev, n = p.length;
    const sdt = (dt * TIME_SCALE) / SUBSTEPS;
    for (let s = 0; s < SUBSTEPS; s++) {
      p[0].copy(this.hole); prev[0].copy(this.hole);
      for (let i = 1; i < n; i++) {
        const vx = (p[i].x - prev[i].x) * DAMPING, vy = (p[i].y - prev[i].y) * DAMPING, vz = (p[i].z - prev[i].z) * DAMPING;
        prev[i].copy(p[i]);
        p[i].x += vx; p[i].y += vy + GRAVITY * sdt * sdt; p[i].z += vz;
      }
      for (let k = 0; k < ITERATIONS; k++) {
        for (let i = 1; i < n; i++) {
          const a = p[i - 1], b = p[i];
          const dx = b.x - a.x, dy = b.y - a.y, dz = b.z - a.z;
          const d = Math.sqrt(dx * dx + dy * dy + dz * dz) || 1e-9;
          const diff = (d - this.rest[i - 1]) / d;
          if (i === 1) { b.x -= dx * diff; b.y -= dy * diff; b.z -= dz * diff; }
          else { a.x += dx * diff * 0.5; a.y += dy * diff * 0.5; a.z += dz * diff * 0.5; b.x -= dx * diff * 0.5; b.y -= dy * diff * 0.5; b.z -= dz * diff * 0.5; }
        }
        p[0].copy(this.hole);
        // keep the chain from passing through the plate's front face
        for (let i = 1; i < n; i++) if (p[i].z < -0.004) p[i].z = -0.004;
      }
    }
    const dir = new Vector3(), q = new Quaternion();
    for (let i = 0; i < this.links.length; i++) {
      const node = this.links[i];
      node.position.copy(p[i + 1]);
      dir.copy(p[i]).sub(p[i + 1]).normalize();
      q.setFromUnitVectors(UP, dir);
      node.quaternion.copy(q).multiply(this.restQ[i]);
    }
  }

  render() {
    if (this.root) this.renderer.render(this.scene, this.camera);
  }

  dispose() {
    this.disposed = true; this.running = false;
    this.ro.disconnect(); this.io.disconnect();
    document.removeEventListener('visibilitychange', this._onVis);
    this.renderer.dispose();
    this.canvas.remove();
  }
}
