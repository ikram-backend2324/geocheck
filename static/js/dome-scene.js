(function () {
  var canvas = document.getElementById('domeCanvas');
  if (!canvas || typeof THREE === 'undefined') return;

  var reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var stage = canvas.parentElement;

  var scene = new THREE.Scene();
  var camera = new THREE.PerspectiveCamera(40, 1, 0.1, 100);
  camera.position.set(4.6, 3.2, 5.6);
  camera.lookAt(0, 0.6, 0);

  var renderer = new THREE.WebGLRenderer({ canvas: canvas, antialias: true, alpha: true });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));

  function resize() {
    var w = stage.clientWidth, h = stage.clientHeight;
    renderer.setSize(w, h, false);
    camera.aspect = w / h;
    camera.updateProjectionMatrix();
  }
  resize();
  window.addEventListener('resize', resize);

  var SIGNAL = 0x4cf0b0;
  var ALERT = 0xff8a4c;
  var LINE = 0x243352;
  var DOME_R = 1.9;

  var grid = new THREE.GridHelper(9, 18, LINE, LINE);
  grid.material.transparent = true;
  grid.material.opacity = 0.3;
  scene.add(grid);

  var dome = new THREE.Mesh(
    new THREE.SphereGeometry(DOME_R, 24, 16, 0, Math.PI * 2, 0, Math.PI / 2),
    new THREE.MeshBasicMaterial({ color: SIGNAL, transparent: true, opacity: 0.1, wireframe: false, side: THREE.DoubleSide })
  );
  scene.add(dome);

  var domeWire = new THREE.Mesh(
    new THREE.SphereGeometry(DOME_R, 16, 10, 0, Math.PI * 2, 0, Math.PI / 2),
    new THREE.MeshBasicMaterial({ color: SIGNAL, wireframe: true, transparent: true, opacity: 0.35 })
  );
  scene.add(domeWire);

  var baseRing = new THREE.Mesh(
    new THREE.RingGeometry(DOME_R - 0.02, DOME_R + 0.02, 64),
    new THREE.MeshBasicMaterial({ color: SIGNAL, transparent: true, opacity: 0.6, side: THREE.DoubleSide })
  );
  baseRing.rotation.x = -Math.PI / 2;
  scene.add(baseRing);

  var centerDot = new THREE.Mesh(
    new THREE.SphereGeometry(0.07, 16, 16),
    new THREE.MeshBasicMaterial({ color: SIGNAL })
  );
  scene.add(centerDot);

  var satellite = new THREE.Mesh(
    new THREE.IcosahedronGeometry(0.16, 0),
    new THREE.MeshBasicMaterial({ color: SIGNAL, wireframe: true })
  );
  satellite.position.set(0, 3.1, 0);
  scene.add(satellite);

  var beamGeo = new THREE.BufferGeometry().setFromPoints([
    new THREE.Vector3(0, 0, 0), new THREE.Vector3(0, 3.1, 0)
  ]);
  var beam = new THREE.Line(beamGeo, new THREE.LineDashedMaterial({ color: SIGNAL, dashSize: 0.12, gapSize: 0.08, transparent: true, opacity: 0 }));
  beam.computeLineDistances();
  scene.add(beam);

  var visitor = new THREE.Mesh(
    new THREE.SphereGeometry(0.13, 20, 20),
    new THREE.MeshBasicMaterial({ color: ALERT })
  );
  scene.add(visitor);

  var trailGeo = new THREE.BufferGeometry();
  var trailMat = new THREE.LineBasicMaterial({ color: ALERT, transparent: true, opacity: 0.4 });
  var trail = new THREE.Line(trailGeo, trailMat);
  scene.add(trail);

  var START_R = 3.7;
  var cycle = 6.5; // seconds per loop
  var t = 0;

  function frame(dt) {
    t += dt;
    var p = (t % cycle) / cycle; // 0..1
    var dist = START_R - p * (START_R - 0.15);
    var angle = p * 1.4;
    var x = Math.cos(angle) * dist;
    var z = Math.sin(angle) * dist;
    var y = 0.13;
    visitor.position.set(x, y, z);

    var inside = dist < DOME_R;
    var col = inside ? SIGNAL : ALERT;
    visitor.material.color.setHex(col);
    beam.material.opacity = inside ? Math.min(1, (DOME_R - dist) / DOME_R + 0.3) : 0;
    domeWire.material.opacity = inside ? 0.6 : 0.35;
    baseRing.material.opacity = inside ? 0.9 : 0.6;

    var pts = [];
    var trailLen = 26;
    for (var i = 0; i < trailLen; i++) {
      var tp = Math.max(0, p - i * 0.01);
      var dd = START_R - tp * (START_R - 0.15);
      var aa = tp * 1.4;
      pts.push(new THREE.Vector3(Math.cos(aa) * dd, y, Math.sin(aa) * dd));
    }
    trail.geometry.setFromPoints(pts);
    trail.material.color.setHex(col);

    satellite.rotation.y += dt * 0.6;
    satellite.position.y = 3.0 + Math.sin(t * 1.1) * 0.08;

    renderer.render(scene, camera);
  }

  var last = performance.now();
  function loop(now) {
    var dt = Math.min(0.05, (now - last) / 1000);
    last = now;
    frame(dt);
    if (!reduceMotion) requestAnimationFrame(loop);
  }

  resize();
  if (reduceMotion) {
    frame(0.001);
  } else {
    requestAnimationFrame(loop);
  }
})();
