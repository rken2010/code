async function loadHealth() {
  const el = document.getElementById("health");
  try {
    const response = await fetch("/health");
    const data = await response.json();
    el.textContent = data.status === "ok" ? "✅ API operativa" : "⚠️ API con estado inesperado";
  } catch (err) {
    el.textContent = "❌ No se pudo conectar con la API";
  }
}

loadHealth();
