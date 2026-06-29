(function () {
  var canvas = document.getElementById('sceneCanvas');
  if (!canvas || typeof THREE === 'undefined') return;

  var reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var stage = canvas.parentElement;

  var scene = new THREE.Scene();
  var camera = new THREE.PerspectiveCamera(42, 1, 0.1, 100);
  camera.position.set(0, 5.2, 8.4);
  camera.lookAt(0, 0, 0);

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

  var rig = new THREE.Group();
  rig.rotation.x = -0.92;
  scene.add(rig);

  // concentric geofence rings on the "ground"
  [1.6, 2.6, 3.6].forEach(function (r, i) {
    var ring = new THREE.Mesh(
      new THREE.TorusGeometry(r, 0.012, 8, 96),
      new THREE.MeshBasicMaterial({ color: SIGNAL, transparent: true, opacity: 0.55 - i * 0.13 })
    );
    rig.add(ring);
  });

  // faint ground grid
  var grid = new THREE.GridHelper(9, 18, LINE, LINE);
  grid.material.transparent = true;
  grid.material.opacity = 0.35;
  rig.add(grid);

  // center pillar -> satellite
  var centerDot = new THREE.Mesh(
    new THREE.SphereGeometry(0.09, 16, 16),
    new THREE.MeshBasicMaterial({ color: SIGNAL })
  );
  rig.add(centerDot);

  var satellite = new THREE.Mesh(
    new THREE.IcosahedronGeometry(0.18, 0),
    new THREE.MeshBasicMaterial({ color: SIGNAL, wireframe: true })
  );
  satellite.position.set(0, 0, 3.4);
  rig.add(satellite);

  var beamGeo = new THREE.BufferGeometry().setFromPoints([
    new THREE.Vector3(0, 0, 0), new THREE.Vector3(0, 0, 3.4)
  ]);
  var beam = new THREE.Line(beamGeo, new THREE.LineDashedMaterial({ color: SIGNAL, dashSize: 0.12, gapSize: 0.09, transparent: true, opacity: 0 }));
  beam.computeLineDistances();
  rig.add(beam);

  // orbiting visitor ping
  var visitor = new THREE.Mesh(
    new THREE.SphereGeometry(0.1, 16, 16),
    new THREE.MeshBasicMaterial({ color: ALERT })
  );
  rig.add(visitor);

  var ringPulse = new THREE.Mesh(
    new THREE.RingGeometry(0.12, 0.16, 32),
    new THREE.MeshBasicMaterial({ color: ALERT, transparent: true, opacity: 0.7, side: THREE.DoubleSide })
  );
  ringPulse.rotation.x = -Math.PI / 2;
  rig.add(ringPulse);

  var t = 0;
  function frame() {
    t += 0.01;
    var orbitR = 3.6;
    var angle = t * 0.6;
    var x = Math.cos(angle) * orbitR;
    var z = Math.sin(angle) * orbitR;
    visitor.position.set(x, 0, z);
    ringPulse.position.set(x, 0.01, z);

    var dist = Math.sqrt(x * x + z * z);
    var inside = dist < 1.7;
    var targetColor = inside ? SIGNAL : ALERT;
    visitor.material.color.setHex(targetColor);
    ringPulse.material.color.setHex(targetColor);
    beam.material.opacity = inside ? 0.8 : 0.05;

    var pulse = 1 + Math.sin(t * 6) * 0.25;
    ringPulse.scale.set(pulse, pulse, 1);

    rig.rotation.z += 0.0015;
    satellite.rotation.y += 0.01;
    satellite.position.y = 0.15 + Math.sin(t * 1.4) * 0.05;

    renderer.render(scene, camera);
    if (!reduceMotion) requestAnimationFrame(frame);
  }

  resize();
  frame();
  if (reduceMotion) renderer.render(scene, camera);
})();
