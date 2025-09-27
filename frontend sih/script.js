// Location search (dummy handler)
document.getElementById("locationInput").addEventListener("keyup", function (e) {
  if (e.key === "Enter") {
    alert("Searching for location: " + this.value);
  }
});

// Toggle collapse/expand
document.querySelectorAll('.feature-card').forEach(card => {
  card.addEventListener('click', function(e) {
    // prevent immediate redirect when toggling
    if(e.target.tagName.toLowerCase() === 'h3' || e.target.tagName.toLowerCase() === 'p'){
      e.stopPropagation();
      this.classList.toggle('collapsed');
    }
  });
});
// --- Site wallpaper upload and persistence ---
const siteWallpaperInput = document.getElementById('siteWallpaperInput');
const siteOverlay = document.querySelector('.site-overlay');

// helper to set wallpaper URL and persist
function setSiteWallpaper(url) {
  document.body.style.backgroundImage = url ? `url('${url}')` : '';
  try { localStorage.setItem('siteWallpaper', url || ''); } catch(e){ /* ignore storage errors */ }
}

// load saved wallpaper (if any) on page load
try {
  const saved = localStorage.getItem('siteWallpaper');
  if (saved) {
    // saved may be a blob URL or data URL
    setSiteWallpaper(saved);
  }
} catch(e) { /* ignore */ }

// when user selects a file, create an object URL and set as background
if (siteWallpaperInput) {
  siteWallpaperInput.addEventListener('change', (e) => {
    const f = e.target.files && e.target.files[0];
    if (!f) return;
    // small safety: only allow images
    if (!f.type.startsWith('image/')) {
      alert('Please upload an image file for the wallpaper.');
      return;
    }
    const url = URL.createObjectURL(f);
    setSiteWallpaper(url);

    // release previous object URLs on page unload is optional;
    // keep it stored in localStorage so reloading keeps the wallpaper during this session.
  });
}

// Optional helper: toggle overlay darkness (you can call from console or create a button)
window.toggleSiteOverlayDark = function(toggle) {
  if (!siteOverlay) return;
  if (toggle === undefined) siteOverlay.classList.toggle('dark');
  else if (toggle) siteOverlay.classList.add('dark');
  else siteOverlay.classList.remove('dark');
};
// Wait until the DOM is fully loaded
document.addEventListener('DOMContentLoaded', function () {
  // Wallpaper upload preview
  const wallpaperInput = document.getElementById('wallpaperInput');
  if (wallpaperInput) {
    wallpaperInput.addEventListener('change', function (e) {
      const file = e.target.files[0];
      if (file) {
        const url = URL.createObjectURL(file);
        document.querySelector('.features-hero').style.backgroundImage = `url('${url}')`;
      }
    });
  }

  // Side image upload preview
//   const sideImageInput = document.getElementById('sideImageInput');
//   if (sideImageInput) {
//     sideImageInput.addEventListener('change', function (e) {
//       const file = e.target.files[0];
//       if (file) {
//         const url = URL.createObjectURL(file);
//         document.getElementById('sideImagePreview').src = url;
//       }
//     });
//   }
// });
// document.getElementById("languageSelect").addEventListener("change", function () {
//   const selectedLang = this.value;
//   console.log("Language switched to:", selectedLang);

//   // Example: update `data-i18n` texts if you add translations later
//   // translatePage(selectedLang);
// });
const translations = {
  en: {
    featuresHeading: "Features",
    featuresSub: "Explore powerful features that make water harvesting easier and healthier.",
    plansHeading: "Subscription Plans"
  },
  hi: {
    featuresHeading: "विशेषताएँ",
    featuresSub: "पानी संरक्षण को आसान और स्वास्थ्यकर बनाने वाली शक्तिशाली विशेषताओं का अन्वेषण करें।",
    plansHeading: "सदस्यता योजनाएँ"
  }
};
function translatePage(lang) {
  document.querySelectorAll("[data-i18n]").forEach(el => {
    const key = el.getAttribute("data-i18n");
    if (translations[lang] && translations[lang][key]) {
      el.textContent = translations[lang][key];
    }
  });
}
document.getElementById("languageSelect").addEventListener("change", function () {
  const selectedLang = this.value;
  translatePage(selectedLang);
});

// Initialize map (hidden at first)
// Initialize map (hidden at first)
const map = L.map("map", { zoomControl: true }).setView([20.5937, 78.9629], 5);

// Add OpenStreetMap tiles
L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
  attribution: "© OpenStreetMap contributors"
}).addTo(map);

// let map = null;
let userMarker = null;

// GPS tracking with map popup
document.getElementById("gpsBtn").addEventListener("click", function () {
  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(
      function (pos) {
        const lat = pos.coords.latitude;
        const lon = pos.coords.longitude;

        // Show the map
        const mapDiv = document.getElementById("map");
        mapDiv.style.visibility = "visible";

        // Initialize map if not already
        if (!map) {
          map = L.map("map", { zoomControl: true }).setView([lat, lon], 15);
          L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
            attribution: "© OpenStreetMap contributors"
          }).addTo(map);
        } else {
          map.setView([lat, lon], 15);
          map.invalidateSize();
        }

        // Update input box
        const input = document.getElementById("locationInput");
        input.value = `${lat.toFixed(5)}, ${lon.toFixed(5)}`;

        // Add or move marker with popup
        if (userMarker) {
          userMarker.setLatLng([lat, lon]).bindPopup("📍 You are here!").openPopup();
        } else {
          userMarker = L.marker([lat, lon]).addTo(map)
            .bindPopup("📍 You are here!")
            .openPopup();
        }

      },
      function (err) {
        alert("Error getting location: " + err.message);
      }
    );
  } else {
    alert("Geolocation not supported in this browser.");
  }
});
