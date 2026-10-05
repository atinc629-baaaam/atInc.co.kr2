/*
  atInc — cell care visual: a few glass cells with a warm nucleus, drifting slowly.
  Built with three.js r169 (MIT) and its RoomEnvironment (MIT) for studio reflections.
*/
import * as THREE from './three.module.min.js';
import { RoomEnvironment } from './RoomEnvironment.js';

export function mountCells(host) {
  const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const small = window.matchMedia('(max-width: 760px)').matches;
  let renderer;
  try { renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true }); } catch (e) { return null; }
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.05;
  const canvas = renderer.domElement;
  canvas.className = 'cells-canvas';
  canvas.setAttribute('aria-hidden', 'true');
  host.appendChild(canvas);

  const scene = new THREE.Scene();
  const pmrem = new THREE.PMREMGenerator(renderer);
  scene.environment = pmrem.fromScene(new RoomEnvironment(), 0.04).texture;
  const camera = new THREE.PerspectiveCamera(32, 1, 0.1, 100);
  camera.position.set(0, 0, 9);

  const key = new THREE.DirectionalLight(0xfff2e0, 1.4); key.position.set(-3, 4, 5); scene.add(key);
  const rim = new THREE.DirectionalLight(0xd8bd94, 1.0); rim.position.set(4, -2, -3); scene.add(rim);

  const glass = new THREE.MeshPhysicalMaterial({
    color: 0xf6ece0, metalness: 0, roughness: 0.08, transmission: 0.96, thickness: 1.6, ior: 1.38,
    attenuationColor: new THREE.Color('#d9b98f'), attenuationDistance: 3.2,
    clearcoat: 1, clearcoatRoughness: 0.06, iridescence: 0.28, iridescenceIOR: 1.25, iridescenceThicknessRange: [180, 420],
    specularIntensity: 1, envMapIntensity: 1.2,
  });
  const core = new THREE.MeshPhysicalMaterial({ color: 0xc9a27a, roughness: 0.35, metalness: 0.1, sheen: 1, sheenColor: new THREE.Color('#f3dcb6'), sheenRoughness: 0.4 });

  const group = new THREE.Group(); scene.add(group);
  const seg = small ? 64 : 96;
  const cellDefs = [
    { r: 1.35, p: [0.2, 0.15, 0], c: 0.42, sp: 0.18, ph: 0 },
    { r: 0.62, p: [-1.95, -0.85, 0.6], c: 0.3, sp: 0.26, ph: 1.7 },
    { r: 0.44, p: [1.9, 1.25, -0.4], c: 0.32, sp: 0.31, ph: 3.1 },
    { r: 0.3, p: [-1.35, 1.55, -0.9], c: 0.34, sp: 0.35, ph: 4.4 },
    { r: 0.22, p: [1.55, -1.45, 0.8], c: 0.36, sp: 0.4, ph: 5.2 },
  ];
  const cells = cellDefs.map((d) => {
    const g = new THREE.Group();
    const shell = new THREE.Mesh(new THREE.SphereGeometry(d.r, seg, seg), glass);
    const nucleus = new THREE.Mesh(new THREE.SphereGeometry(d.r * d.c, 48, 48), core);
    nucleus.position.set(d.r * 0.12, d.r * 0.08, -d.r * 0.1);
    g.add(nucleus, shell);
    g.position.set(...d.p);
    group.add(g);
    return { g, d, base: new THREE.Vector3(...d.p) };
  });

  let tx = 0, ty = 0, mx = 0, my = 0;
  host.addEventListener('pointermove', (e) => {
    const r = host.getBoundingClientRect();
    tx = ((e.clientX - r.left) / r.width - 0.5) * 0.5; ty = ((e.clientY - r.top) / r.height - 0.5) * 0.35;
  });
  host.addEventListener('pointerleave', () => { tx = 0; ty = 0; });

  function resize() {
    const r = host.getBoundingClientRect();
    renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
    renderer.setSize(Math.max(1, r.width), Math.max(1, r.height), false);
    camera.aspect = r.width / Math.max(1, r.height);
    camera.position.z = camera.aspect < 0.9 ? 11 : 9;
    camera.updateProjectionMatrix();
  }

  let visible = true, raf = 0, t = 0, last = 0;
  function frame(now) {
    raf = 0;
    const dt = last ? Math.min(0.05, (now - last) / 1000) : 0.016; last = now;
    if (!reduce) t += dt;
    mx += (tx - mx) * 0.04; my += (ty - my) * 0.04;
    group.rotation.y = mx; group.rotation.x = my;
    cells.forEach(({ g, d, base }) => {
      g.position.x = base.x + Math.sin(t * d.sp + d.ph) * 0.12;
      g.position.y = base.y + Math.cos(t * d.sp * 0.9 + d.ph) * 0.16;
      g.rotation.y = t * d.sp * 0.6;
    });
    renderer.render(scene, camera);
    if (!reduce && visible && !document.hidden) raf = requestAnimationFrame(frame);
  }
  function kick() { if (!raf) { last = 0; raf = requestAnimationFrame(frame); } }
  resize();
  new ResizeObserver(() => { resize(); kick(); }).observe(host);
  new IntersectionObserver(([e]) => { visible = e.isIntersecting; if (visible) kick(); }, { rootMargin: '80px' }).observe(host);
  document.addEventListener('visibilitychange', () => { if (!document.hidden) kick(); });
  kick();
  host.classList.add('cells-on');
  return { canvas };
}
