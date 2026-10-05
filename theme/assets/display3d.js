// Floating display for the range viewer, built in the keychain's own 3D scene: a stepped metal pedestal with chrome
// rims and a light strip, an overhead ring-light fixture with a glowing lens, a real spotlight that lights the
// keychain and throws its shadow onto the pedestal, and a soft volumetric light beam. Sized to each keychain.
import {
  Group, Mesh, LatheGeometry, CircleGeometry, CylinderGeometry, TorusGeometry, RingGeometry, PlaneGeometry,
  MeshPhysicalMaterial, MeshStandardMaterial, MeshBasicMaterial, ShaderMaterial, AdditiveBlending, DoubleSide,
  Vector2, Vector3, SpotLight, CanvasTexture, Color, PCFSoftShadowMap,
} from 'vendor-three';

const PED_R = 0.068;     // pedestal radius (m): a little wider than the 80.5 mm keychain
const FIX_R = 0.052;

const metalDark = () => new MeshPhysicalMaterial({ color: new Color('#16161a'), metalness: 0.85, roughness: 0.34, clearcoat: 0.7, clearcoatRoughness: 0.18, envMapIntensity: 0.55 });
const chrome = () => new MeshStandardMaterial({ color: new Color('#e9e9ec'), metalness: 1, roughness: 0.12 });
const glow = (o = 1) => new MeshBasicMaterial({ color: 0xffffff, transparent: o < 1, opacity: o });

function radialTexture(stops) {
  const c = document.createElement('canvas');
  c.width = c.height = 256;
  const g = c.getContext('2d');
  const grd = g.createRadialGradient(128, 128, 0, 128, 128, 128);
  stops.forEach(([o, col]) => grd.addColorStop(o, col));
  g.fillStyle = grd;
  g.fillRect(0, 0, 256, 256);
  const t = new CanvasTexture(c);
  return t;
}

function pedestal() {
  const g = new Group();
  const prof = [[0, 0], [0.072, 0], [0.074, 0.0015], [0.074, 0.0105], [0.0715, 0.0125], [0.066, 0.013], [0.066, 0.0205], [0.064, 0.022], [0, 0.022]]
    .map(([x, y]) => new Vector2(x, y));
  const body = new Mesh(new LatheGeometry(prof, 128), metalDark());
  body.receiveShadow = true;
  const top = new Mesh(new CircleGeometry(0.0639, 96), new MeshPhysicalMaterial({ color: new Color('#0c0c0e'), metalness: 0.2, roughness: 0.5, clearcoat: 0.35, clearcoatRoughness: 0.3, envMapIntensity: 0.18 }));
  top.rotation.x = -Math.PI / 2;
  top.position.y = 0.0221;
  top.receiveShadow = true;
  const rimA = new Mesh(new TorusGeometry(0.0716, 0.0006, 12, 160), chrome());
  rimA.rotation.x = Math.PI / 2; rimA.position.y = 0.0125;
  const rimB = new Mesh(new TorusGeometry(0.0641, 0.0005, 12, 160), chrome());
  rimB.rotation.x = Math.PI / 2; rimB.position.y = 0.0221;
  const strip = new Mesh(new TorusGeometry(0.0662, 0.00045, 8, 160), glow());
  strip.rotation.x = Math.PI / 2; strip.position.y = 0.0168;
  g.add(body, top, rimA, rimB, strip);
  g.userData.topY = 0.0222;
  return g;
}

function fixture() {
  const g = new Group();
  const prof = [[0, 0.016], [0.048, 0.016], [0.053, 0.0125], [0.054, 0.004], [0.05, 0], [0, 0]].map(([x, y]) => new Vector2(x, y));
  const housing = new Mesh(new LatheGeometry(prof, 128), metalDark());
  const lens = new Mesh(new CircleGeometry(0.017, 64), glow());
  lens.rotation.x = Math.PI / 2; lens.position.y = -0.0002;
  const reflector = new Mesh(new RingGeometry(0.018, 0.036, 96), new MeshStandardMaterial({ color: '#d9d9dc', metalness: 1, roughness: 0.18, side: DoubleSide }));
  reflector.rotation.x = Math.PI / 2; reflector.position.y = -0.0001;
  const halo = new Mesh(new RingGeometry(0.0375, 0.0392, 128), glow(0.95));
  halo.rotation.x = Math.PI / 2; halo.position.y = -0.0003;
  const rim = new Mesh(new TorusGeometry(0.0505, 0.0006, 12, 160), chrome());
  rim.rotation.x = Math.PI / 2; rim.position.y = 0.0005;
  // soft bloom under the lens (no post-processing): an additive radial sprite
  const bloomTex = radialTexture([[0, 'rgba(255,255,255,0.9)'], [0.18, 'rgba(255,255,255,0.35)'], [0.5, 'rgba(255,255,255,0.08)'], [1, 'rgba(255,255,255,0)']]);
  const bloom = new Mesh(new PlaneGeometry(0.16, 0.16), new MeshBasicMaterial({ map: bloomTex, transparent: true, blending: AdditiveBlending, depthWrite: false }));
  bloom.rotation.x = Math.PI / 2; bloom.position.y = -0.0015;
  g.add(housing, reflector, lens, halo, rim, bloom);
  return g;
}

function beam(height) {
  const geo = new CylinderGeometry(0.016, PED_R * 0.92, height, 96, 1, true);
  const mat = new ShaderMaterial({
    transparent: true, depthWrite: false, blending: AdditiveBlending, side: DoubleSide,
    uniforms: { uStrength: { value: 0.22 } },
    vertexShader: `
      varying vec2 vUv; varying vec3 vN; varying vec3 vV;
      void main() {
        vUv = uv;
        vec4 mv = modelViewMatrix * vec4(position, 1.0);
        vN = normalize(normalMatrix * normal); vV = normalize(-mv.xyz);
        gl_Position = projectionMatrix * mv;
      }`,
    fragmentShader: `
      uniform float uStrength; varying vec2 vUv; varying vec3 vN; varying vec3 vV;
      void main() {
        float facing = abs(dot(vN, vV));               // brighter through the middle of the cone, soft at its edges
        float fall = pow(vUv.y, 1.6);                  // strongest at the lamp, fading toward the pedestal
        float a = uStrength * pow(facing, 2.2) * (0.2 + 0.8 * fall) * smoothstep(0.08, 0.55, vUv.y);   // gone before it reaches the pedestal: the real spotlight pool shows there
        gl_FragColor = vec4(vec3(1.0, 0.99, 0.97) * a, a);
      }`,
  });
  return new Mesh(geo, mat);
}

export class Display {
  constructor(stage) {
    this.stage = stage;
    const r = stage.renderer;
    r.shadowMap.enabled = true;
    r.shadowMap.type = PCFSoftShadowMap;
    this.group = new Group();
    this.ped = pedestal();
    this.fix = fixture();
    this.group.add(this.ped, this.fix);
    this.spot = new SpotLight(0xffffff, 5, 0, 0.5, 0.6, 0);
    this.spot.castShadow = true;
    this.spot.shadow.mapSize.set(1024, 1024);
    this.spot.shadow.bias = -0.0003;
    this.spot.shadow.normalBias = 0.0004;
    this.spot.shadow.camera.near = 0.01;
    this.spot.shadow.camera.far = 0.6;
    this.group.add(this.spot, this.spot.target);
    stage.scene.add(this.group);
    this.beam = null;
  }

  // place the pedestal under the keychain (and its chain) and the fixture above it
  fit(bodyBox, lowestY) {
    const cx = (bodyBox.min.x + bodyBox.max.x) / 2;
    const pedTop = lowestY - 0.012;
    const fixBottom = bodyBox.max.y + 0.03;
    this.ped.position.set(cx, pedTop - this.ped.userData.topY, 0);
    this.fix.position.set(cx, fixBottom, 0);
    const h = fixBottom - pedTop;
    if (this.beam) { this.group.remove(this.beam); this.beam.geometry.dispose(); }
    this.beam = beam(h);
    this.beam.position.set(cx, pedTop + h / 2, 0);
    this.beam.renderOrder = 2;
    this.group.add(this.beam);
    this.spot.position.set(cx, fixBottom - 0.002, 0.006);
    this.spot.target.position.set(cx, pedTop, 0);
    this.spot.angle = Math.atan((PED_R * 0.95) / h);
    this.bounds = { cx, top: fixBottom + 0.018, bottom: pedTop - 0.024, name: new Vector3(cx, pedTop - 0.0105, 0.0745) };
    this.stage.root.traverse((o) => { if (o.isMesh) o.castShadow = true; });
  }
}
