const map = L.map('map').setView([-1.286389, 36.817223], 10); // Nairobi default
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
  maxZoom: 18,
}).addTo(map);

// Custom icon function
function getIcon(profession) {
  let iconUrl = '/static/images/icon-developer.png'; // default

  if (profession.toLowerCase().includes('plumb')) iconUrl = '/static/images/icon-plumber.png';
  else if (profession.toLowerCase().includes('chef')) iconUrl = '/static/images/icon-chef.png';
  else if (profession.toLowerCase().includes('design')) iconUrl = '/static/images/icon-designer.png';
  else if (profession.toLowerCase().includes('tech') || profession.toLowerCase().includes('dev')) iconUrl = '/static/images/icon-developer.png';

  return L.icon({
    iconUrl,
    iconSize: [38, 38],
    iconAnchor: [19, 38],
    popupAnchor: [0, -35],
  });
}

// Client location marker
navigator.geolocation.getCurrentPosition(pos => {
  const { latitude, longitude } = pos.coords;

  // Client pin
  const clientIcon = L.icon({
    iconUrl: '/static/images/icon-client.png',
    iconSize: [40, 40],
    iconAnchor: [20, 40],
    popupAnchor: [0, -35],
  });

  const clientMarker = L.marker([latitude, longitude], { icon: clientIcon }).addTo(map);
  clientMarker.bindPopup("<b>You are here!</b>").openPopup();
  map.setView([latitude, longitude], 13);

  // Fetch professionals nearby
  fetch(`/api/professionals/nearby?lat=${latitude}&lon=${longitude}&radius=10000`)
    .then(res => res.json())
    .then(data => {
      data.forEach(p => {
        const match = p.coords.match(/POINT\((.*?) (.*?)\)/);
        if (!match) return;

        const [lon, lat] = match.slice(1);
        const marker = L.marker([lat, lon], { icon: getIcon(p.profession) }).addTo(map);
        marker.bindPopup(`
          <b>${p.full_name}</b><br>
          ${p.profession}<br>
          Rating: ${p.rating || "N/A"}
        `);
      });
    });
}, err => {
  console.error("Geolocation failed:", err);
  alert("Could not access location — please enable GPS!");
});
