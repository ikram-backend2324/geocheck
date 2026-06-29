(function () {
  function init() {
    var mapEl = document.getElementById('adminZoneMap');
    if (!mapEl || typeof L === 'undefined') return;

    var latInput = document.getElementById('id_center_lat');
    var lngInput = document.getElementById('id_center_lng');
    var radiusInput = document.getElementById('id_radius_m');
    var colorInput = document.getElementById('id_color');
    if (!latInput || !lngInput) return;

    // The map is the source of truth now — stop hand-typed coordinates.
    latInput.setAttribute('readonly', 'readonly');
    lngInput.setAttribute('readonly', 'readonly');
    latInput.style.opacity = '0.7';
    lngInput.style.opacity = '0.7';

    var FALLBACK = [42.4531, 59.6103]; // Nukus
    var hasInitial = latInput.value && lngInput.value;
    var start = hasInitial
      ? [parseFloat(latInput.value), parseFloat(lngInput.value)]
      : FALLBACK;

    var map = L.map('adminZoneMap').setView(start, hasInitial ? 14 : 12);
    L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
      attribution: '&copy; OpenStreetMap &copy; CARTO',
      maxZoom: 19
    }).addTo(map);

    function currentColor() {
      return (colorInput && colorInput.value) || '#4cf0b0';
    }
    function currentRadius() {
      var v = parseInt((radiusInput && radiusInput.value) || '150', 10);
      return isNaN(v) ? 150 : v;
    }

    var marker = L.marker(start, { draggable: true }).addTo(map);
    var circle = L.circle(start, {
      radius: currentRadius(),
      color: currentColor(),
      fillColor: currentColor(),
      fillOpacity: 0.15
    }).addTo(map);

    function setPoint(latlng) {
      latInput.value = latlng.lat.toFixed(6);
      lngInput.value = latlng.lng.toFixed(6);
      marker.setLatLng(latlng);
      circle.setLatLng(latlng);
    }

    if (!hasInitial) setPoint(L.latLng(start[0], start[1]));

    map.on('click', function (e) { setPoint(e.latlng); });
    marker.on('drag', function (e) { setPoint(e.target.getLatLng()); });

    if (radiusInput) {
      radiusInput.addEventListener('input', function () {
        circle.setRadius(currentRadius());
      });
    }
    if (colorInput) {
      colorInput.addEventListener('input', function () {
        circle.setStyle({ color: currentColor(), fillColor: currentColor() });
      });
    }

    // Jazzmin/AdminLTE sometimes renders the form inside a tab that's
    // hidden at first paint — Leaflet needs a visible container to size
    // itself correctly, so re-measure shortly after load.
    setTimeout(function () { map.invalidateSize(); }, 300);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
