/*
  atInc — moving light field + liquid glass
  ------------------------------------------------------------------
  Gradient : ShaderGradient (github.com/ruucm/shadergradient, MIT) — the same
             shaders and scene setup, driven by three.js r169 (MIT), the engine
             that react-three-fiber wraps.
  Glass    : refraction model adapted from liquid-glass-js
             (github.com/dashersw/liquid-glass-js, MIT). Instead of snapshotting
             the page with html2canvas, the glass samples this field directly,
             so it bends the live light behind it.
  Elements marked [data-glass] that sit over the field are drawn as glass.
*/
import * as THREE from './three.module.min.js';
import { SHADERS } from './sg-shaders.js';

export const LOOKS = {
  // espresso ground, bronze body, a slow champagne light drifting through
  hero: {
    type: 'waterPlane', color1: '#5e4432', color2: '#120c08', color3: '#e3c89e',
    uSpeed: 0.03, uStrength: 1.7, uDensity: 1.4, uFrequency: 5.5, uAmplitude: 0,
    pos: [0, -2.1, 0], rot: [0, 0, 225], cam: [180, 95, 2.2], brightness: 1.4, reflection: 0.1, seed: 10,
  },
  deep: {
    type: 'waterPlane', color1: '#4a3326', color2: '#0f0a07', color3: '#c9ab82',
    uSpeed: 0.025, uStrength: 1.6, uDensity: 1.3, uFrequency: 5.5, uAmplitude: 0,
    pos: [0, -2.1, 0], rot: [0, 0, 200], cam: [180, 95, 2.2], brightness: 1.15, reflection: 0.1, seed: 60,
  },
};

const MAX_GLASS = 6;

function makeMaterial(p) {
  const src = SHADERS[p.type];
  const mat = new THREE.MeshPhysicalMaterial({ side: THREE.DoubleSide, metalness: 0.2, roughness: 1 - p.reflection });
  const U = {
    uTime: { value: p.seed || 0 }, uSpeed: { value: p.uSpeed }, uNoiseDensity: { value: p.uDensity },
    uNoiseStrength: { value: p.uStrength }, uFrequency: { value: p.uFrequency }, uAmplitude: { value: p.uAmplitude },
    uLoop: { value: 0 }, uLoopDuration: { value: 5 }, uLoadingTime: { value: 1 }, uIntensity: { value: 0.5 },
  };
  [p.color1, p.color2, p.color3].forEach((hex, i) => {
    const c = new THREE.Color().setStyle(hex, THREE.LinearSRGBColorSpace);
    U[`uC${i + 1}r`] = { value: c.r }; U[`uC${i + 1}g`] = { value: c.g }; U[`uC${i + 1}b`] = { value: c.b };
    U[`uColor${i + 1}`] = { value: new THREE.Vector3(c.r, c.g, c.b) };
  });
  mat.onBeforeCompile = (sh) => {
    Object.assign(sh.uniforms, U);
    sh.vertexShader = src.vertex;
    sh.fragmentShader = src.fragment;
  };
  mat.customProgramCacheKey = () => 'sg:' + p.type;
  return { mat, U };
}

const QUAD_VS = 'varying vec2 vUv; void main(){ vUv = uv; gl_Position = vec4(position.xy, 0.0, 1.0); }';

const BLUR_FS = `
uniform sampler2D tSrc; uniform vec2 uDir; varying vec2 vUv;
void main(){
  vec3 c = texture2D(tSrc, vUv).rgb * 0.2270270270;
  c += texture2D(tSrc, vUv + uDir * 1.3846153846).rgb * 0.3162162162;
  c += texture2D(tSrc, vUv - uDir * 1.3846153846).rgb * 0.3162162162;
  c += texture2D(tSrc, vUv + uDir * 3.2307692308).rgb * 0.0702702703;
  c += texture2D(tSrc, vUv - uDir * 3.2307692308).rgb * 0.0702702703;
  gl_FragColor = vec4(c, 1.0);
}`;

const GLASS_FS = `
uniform sampler2D tScene; uniform sampler2D tBlur;
uniform vec2 uRes; uniform float uDpr; uniform int uCount;
uniform vec4 uRect[${MAX_GLASS}]; uniform float uRad[${MAX_GLASS}];
uniform vec3 uFrost; uniform float uFrostAmt; uniform vec2 uMouse; uniform float uHasMouse;
varying vec2 vUv;
float sdRound(vec2 p, vec2 b, float r){ vec2 q = abs(p) - b + r; return length(max(q, 0.0)) + min(max(q.x, q.y), 0.0) - r; }
vec2 toUv(vec2 px){ vec2 u = px / uRes; u.y = 1.0 - u.y; return clamp(u, 0.001, 0.999); }
void main(){
  vec2 px = vec2(vUv.x * uRes.x, (1.0 - vUv.y) * uRes.y);
  vec3 col = texture2D(tScene, vUv).rgb;
  for (int i = 0; i < ${MAX_GLASS}; i++) {
    if (i >= uCount) break;
    vec4 R = uRect[i];
    vec2 b = R.zw * 0.5; vec2 p = px - (R.xy + b);
    float r = min(uRad[i], min(b.x, b.y));
    float d = sdRound(p, b, r);
    if (d > 2.0 * uDpr) continue;
    vec2 n = vec2(sdRound(p + vec2(1.0, 0.0), b, r) - sdRound(p - vec2(1.0, 0.0), b, r),
                  sdRound(p + vec2(0.0, 1.0), b, r) - sdRound(p - vec2(0.0, 1.0), b, r));
    n = normalize(n + 1e-5);
    float di = max(-d, 0.0) / uDpr;              // distance inside, in CSS px
    float lens = exp(-di / 16.0);                // refraction zone along the rim
    float rim = exp(-di / 1.4);
    // liquid-glass-js: edge + rim intensities push the sample outward along the shape normal
    vec2 off = n * (lens * 22.0 + rim * 6.0) * uDpr;
    vec3 g = texture2D(tBlur, toUv(px + off)).rgb;
    float split = lens * 0.55;
    g.r = mix(g.r, texture2D(tBlur, toUv(px + off * 1.18)).r, split);
    g.b = mix(g.b, texture2D(tBlur, toUv(px + off * 0.84)).b, split);
    float ty = clamp((px.y - R.y) / max(R.w, 1.0), 0.0, 1.0);
    g = mix(g, uFrost, uFrostAmt);
    g += vec3(1.0, 0.94, 0.84) * 0.05 * (1.0 - ty);           // soft top sheen
    vec2 toL = mix(vec2(-0.55, -0.85), normalize(uMouse - (R.xy + b) + 1e-3), uHasMouse);
    float light = 0.5 + 0.5 * dot(n, normalize(toL));
    g += vec3(1.0, 0.95, 0.86) * rim * (0.18 + 0.62 * light);  // specular rim
    g += vec3(1.0, 0.95, 0.86) * exp(-di / 6.0) * 0.035;
    float mask = 1.0 - smoothstep(-0.8 * uDpr, 0.8 * uDpr, d);
    col = mix(col, g, mask);
  }
  gl_FragColor = vec4(col, 1.0);
}`;

function quad(material) {
  const m = new THREE.Mesh(new THREE.PlaneGeometry(2, 2), material);
  m.frustumCulled = false;
  const s = new THREE.Scene(); s.add(m);
  return s;
}

export function mountField(host, opts = {}) {
  const look = Object.assign({}, LOOKS[opts.look] || LOOKS.hero, opts.overrides || {});
  if (opts.seed != null) look.seed = opts.seed;
  const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const small = window.matchMedia('(max-width: 760px)').matches;

  const canvas = document.createElement('canvas');
  canvas.className = 'fx-canvas';
  canvas.setAttribute('aria-hidden', 'true');
  let renderer;
  try {
    renderer = new THREE.WebGLRenderer({ canvas, antialias: false, alpha: false, powerPreference: 'default' });
  } catch (e) { return null; }
  renderer.outputColorSpace = THREE.LinearSRGBColorSpace;
  renderer.toneMapping = THREE.NoToneMapping;
  host.prepend(canvas);

  // ShaderGradient scene
  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(45, 1, 0.1, 1000);
  const geo = look.type === 'sphere' ? new THREE.IcosahedronGeometry(1, 64)
    : new THREE.PlaneGeometry(10, 10, look.type === 'waterPlane' ? (small ? 128 : 192) : 1, small ? 128 : 192);
  const { mat, U } = makeMaterial(look);
  const mesh = new THREE.Mesh(geo, mat);
  mesh.position.set(...look.pos);
  mesh.rotation.set(...look.rot.map(THREE.MathUtils.degToRad));
  scene.add(mesh, new THREE.AmbientLight(0xffffff, look.brightness * Math.PI));
  const [az, pol, dist] = look.cam.map((v, i) => (i < 2 ? THREE.MathUtils.degToRad(v) : v));
  const D = look.type === 'sphere' ? 14 : dist;
  camera.position.set(D * Math.sin(pol) * Math.sin(az), D * Math.cos(pol), D * Math.sin(pol) * Math.cos(az));
  camera.lookAt(0, 0, 0);
  if (look.type === 'sphere') { camera.zoom = look.zoom || 15; camera.updateProjectionMatrix(); }

  // glass passes
  const rtOpt = { depthBuffer: true, stencilBuffer: false, type: THREE.UnsignedByteType };
  const rtScene = new THREE.WebGLRenderTarget(4, 4, rtOpt);
  const rtA = new THREE.WebGLRenderTarget(4, 4, { depthBuffer: false });
  const rtB = new THREE.WebGLRenderTarget(4, 4, { depthBuffer: false });
  const blurMat = new THREE.ShaderMaterial({ vertexShader: QUAD_VS, fragmentShader: BLUR_FS, uniforms: { tSrc: { value: null }, uDir: { value: new THREE.Vector2() } }, depthTest: false, depthWrite: false });
  const blurScene = quad(blurMat);
  const rects = Array.from({ length: MAX_GLASS }, () => new THREE.Vector4());
  const glassMat = new THREE.ShaderMaterial({
    vertexShader: QUAD_VS, fragmentShader: GLASS_FS, depthTest: false, depthWrite: false,
    uniforms: {
      tScene: { value: rtScene.texture }, tBlur: { value: rtA.texture }, uRes: { value: new THREE.Vector2(1, 1) },
      uDpr: { value: 1 }, uCount: { value: 0 }, uRect: { value: rects }, uRad: { value: new Array(MAX_GLASS).fill(0) },
      uMouse: { value: new THREE.Vector2() }, uHasMouse: { value: 0 },
      uFrost: { value: new THREE.Color().setStyle(opts.frost || '#22170f', THREE.LinearSRGBColorSpace) }, uFrostAmt: { value: opts.frostAmt ?? 0.42 },
    },
  });
  const glassScene = quad(glassMat);
  const quadCam = new THREE.OrthographicCamera(-1, 1, 1, -1, 0, 1);


  let W = 0, H = 0, pr = 1;
  function resize() {
    const r = host.getBoundingClientRect();
    W = Math.max(1, Math.round(r.width)); H = Math.max(1, Math.round(r.height));
    pr = Math.min(window.devicePixelRatio || 1, small ? 1.5 : 1.6);
    renderer.setPixelRatio(pr);
    renderer.setSize(W, H, false);
    camera.aspect = W / H; camera.updateProjectionMatrix();
    const bw = Math.round(W * pr), bh = Math.round(H * pr);
    rtScene.setSize(bw, bh);
    rtA.setSize(Math.max(1, bw >> 2), Math.max(1, bh >> 2));
    rtB.setSize(Math.max(1, bw >> 2), Math.max(1, bh >> 2));
    glassMat.uniforms.uRes.value.set(bw, bh);
    glassMat.uniforms.uDpr.value = pr;
  }

  let mouse = null;
  window.addEventListener('pointermove', (e) => { if (e.pointerType === 'mouse') mouse = [e.clientX, e.clientY]; }, { passive: true });
  document.addEventListener('pointerleave', () => { mouse = null; });

  function updateGlass() {
    const hr = canvas.getBoundingClientRect();
    let n = 0;
    for (const el of document.querySelectorAll(opts.glass || '[data-glass]')) {
      if (n >= MAX_GLASS) break;
      const r = el.getBoundingClientRect();
      if (r.width < 2 || r.bottom < hr.top || r.top > hr.bottom || r.right < hr.left || r.left > hr.right) continue;
      if (el.closest('.hdr.is-solid')) continue;
      const rad = parseFloat(getComputedStyle(el).borderTopLeftRadius) || 0;
      rects[n].set((r.left - hr.left) * pr, (r.top - hr.top) * pr, r.width * pr, r.height * pr);
      glassMat.uniforms.uRad.value[n] = Math.min(rad, r.height / 2) * pr;
      n++;
    }
    glassMat.uniforms.uCount.value = n;
    if (mouse) { glassMat.uniforms.uMouse.value.set((mouse[0] - hr.left) * pr, (mouse[1] - hr.top) * pr); glassMat.uniforms.uHasMouse.value = 1; }
    else glassMat.uniforms.uHasMouse.value = 0;
    return n;
  }

  function draw() {
    const n = updateGlass();
    if (!n) { renderer.setRenderTarget(null); renderer.render(scene, camera); return; }
    renderer.setRenderTarget(rtScene); renderer.render(scene, camera);
    const tw = 1 / rtA.width, th = 1 / rtA.height;
    blurMat.uniforms.tSrc.value = rtScene.texture; blurMat.uniforms.uDir.value.set(tw * 1.5, 0);
    renderer.setRenderTarget(rtB); renderer.render(blurScene, quadCam);
    blurMat.uniforms.tSrc.value = rtB.texture; blurMat.uniforms.uDir.value.set(0, th * 1.5);
    renderer.setRenderTarget(rtA); renderer.render(blurScene, quadCam);
    blurMat.uniforms.tSrc.value = rtA.texture; blurMat.uniforms.uDir.value.set(tw * 3, 0);
    renderer.setRenderTarget(rtB); renderer.render(blurScene, quadCam);
    blurMat.uniforms.tSrc.value = rtB.texture; blurMat.uniforms.uDir.value.set(0, th * 3);
    renderer.setRenderTarget(rtA); renderer.render(blurScene, quadCam);
    renderer.setRenderTarget(null); renderer.render(glassScene, quadCam);
  }

  let visible = true, raf = 0, last = performance.now(), t = look.seed || 0;
  function frame(now) {
    raf = 0;
    const dt = Math.min(0.05, (now - last) / 1000); last = now;
    if (!reduce) t += dt;
    U.uTime.value = t;
    draw();
    if (!reduce && visible && !document.hidden) raf = requestAnimationFrame(frame);
  }
  function kick() { if (!raf) { last = performance.now(); raf = requestAnimationFrame(frame); } }

  resize();
  new ResizeObserver(() => { resize(); kick(); }).observe(host);
  new IntersectionObserver(([e]) => { visible = e.isIntersecting; if (visible) kick(); }, { rootMargin: '80px' }).observe(host);
  document.addEventListener('visibilitychange', () => { if (!document.hidden) kick(); });
  if (reduce) window.addEventListener('scroll', kick, { passive: true });
  kick();
  host.classList.add('fx-on');
  return { canvas, redraw: kick };
}
