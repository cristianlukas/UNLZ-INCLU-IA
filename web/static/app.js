(() => {
  const appEl = document.querySelector(".app");
  const statusPill = document.getElementById("statusPill");
  const networkHint = document.getElementById("networkHint");
  const liveCaption = document.getElementById("liveCaption");
  const historyList = document.getElementById("historyList");
  const sourceTag = document.getElementById("sourceTag");
  const fontSize = document.getElementById("fontSize");
  const contrastMode = document.getElementById("contrastMode");
  const clearBtn = document.getElementById("clearBtn");
  const menuToggle = document.getElementById("menuToggle");

  let socket = null;

  const savedFont = localStorage.getItem("incluia_font");
  if (savedFont && ["s", "m", "l"].includes(savedFont)) {
    appEl.dataset.font = savedFont;
    fontSize.value = savedFont;
  }

  const savedTheme = localStorage.getItem("incluia_theme");
  if (savedTheme === "contrast") {
    appEl.dataset.theme = "contrast";
  } else if (savedTheme === "oled") {
    appEl.dataset.theme = "oled";
  }

  contrastMode.value =
  savedTheme === "light" ? "normal" :
  savedTheme === "contrast" ? "high" :
  "oled";

  const fmtTime = (ms) => {
    if (!ms) return "";
    try {
      return new Date(ms).toLocaleTimeString();
    } catch {
      return "";
    }
  };

  const setStatus = (stateName, detail = "") => {
    const map = {
      idle: "Idle",
      listening: "Escuchando",
      transcribing: "Transcribiendo",
      error: "Error",
    };

    const label = map[stateName] || stateName || "Desconocido";
    statusPill.textContent = label;

    if (stateName === "error") {
      statusPill.style.background = "#ffe8e8";
      statusPill.style.color = "#8e1f1f";
      return;
    }

    statusPill.style.background = "";
    statusPill.style.color = "";
  };

  const clearHistoryUI = () => {
    historyList.innerHTML = "";
  };

  const appendHistoryItem = (caption) => {
    const item = document.createElement("li");
    item.className = "history-item";

    const ts = document.createElement("span");
    ts.className = "item-time";
    ts.textContent = fmtTime(caption.t_server_ms);

    const content = document.createElement("span");
    content.textContent = caption.text;

    item.appendChild(ts);
    item.appendChild(content);
    // historyList.appendChild(item);                       // Para que el mas nuevo este abajo
    historyList.insertBefore(item, historyList.firstChild); // Para que el mas nuevo este arriba

    if (historyList.children.length > 300) {
      historyList.removeChild(historyList.firstElementChild);
    }
    // historyList.scrollTop = historyList.scrollHeight;    // Para que al llegar un dato nuevo el scroll vaya al mas nuevo automaticamentes
  };

  const onCaption = (caption) => {
    if (!caption || !caption.text) {
      return;
    }

    if (caption.source) {
      sourceTag.textContent = `source: ${caption.source}`;
    }

    if (caption.is_final) {
      appendHistoryItem(caption);
      // Keep the last final caption visible in the live line.
      liveCaption.textContent = caption.text;
      return;
    }

    liveCaption.textContent = caption.text;
  };

  const loadConfig = async () => {
    try {
      const response = await fetch("/api/config");
      if (!response.ok) return null;
      const cfg = await response.json();

      // const url = cfg.ap_url || window.location.origin;
      // const ssid = cfg.ap_ssid ? `Para empezar conectate al WiFi: ${cfg.ap_ssid}` : "WiFi local";
      // networkHint.textContent = `${ssid} | e ingresa en el navegador la URL: ${url}`;
      const url = cfg.ap_url || window.location.origin;
      const ssid = cfg.ap_ssid ? `Para utilizarlo en otro dispositivo recorda conectarte al WiFi: <strong>${cfg.ap_ssid}</strong>` : "WiFi local";
      networkHint.innerHTML = `${ssid}<br>Y abrir en el navegador: <strong>${url}</strong>`;
      sourceTag.textContent = `source: ${cfg.active_source || "-"}`;
      return cfg;
    } catch {
      networkHint.textContent = "Modo local";
      return null;
    }
  };

  const startDemoMode = () => {
    setStatus("idle", "Modo demo local");

    const lines = [
      "Demo local activa.",
      "No hay backend Socket.IO disponible.",
      "Conecta el servidor para subtitulos reales.",
    ];

    let idx = 0;

    setInterval(() => {
      const text = lines[idx % lines.length];
      idx++;

      // partial
      onCaption({
        text,
        is_final: false,
        t_server_ms: Date.now(),
        source: "demo"
      });

      // final después de 1 segundo
      setTimeout(() => {
        onCaption({
          text,
          is_final: true,
          t_server_ms: Date.now(),
          source: "demo"
        });
      }, 1000);

    }, 2500);
  };

  const connectSocket = (cfg = null) => {
    if (typeof io !== "function") {
      startDemoMode();
      return;
    }

    const transport = cfg?.socket_transport || "polling";
    const socketOptions = {
      reconnection: true,
      reconnectionAttempts: Infinity,
      reconnectionDelay: 1000,
      reconnectionDelayMax: 5000,
      timeout: 10000,
    };

    if (transport === "polling") {
      socketOptions.transports = ["polling"];
      socketOptions.upgrade = false;
    } else if (transport === "websocket") {
      socketOptions.transports = ["websocket"];
      socketOptions.upgrade = false;
    }

    socket = io(socketOptions);

    socket.on("connect", () => {
      setStatus("idle", "Conectado");
    });

    socket.on("disconnect", () => {
      setStatus("error", "Desconectado, reintentando");
    });

    socket.on("connect_error", (err) => {
      setStatus("error", `Socket.IO: ${err?.message || "fallo de conexion"}`);
    });

    socket.on("status", (payload) => {
      if (!payload) return;
      setStatus(payload.state, payload.detail);
    });

    socket.on("caption", onCaption);

    socket.on("history", (payload) => {
      clearHistoryUI();
      const items = payload && Array.isArray(payload.items) ? payload.items : [];
      items.forEach((item) => appendHistoryItem(item));
    });

    socket.on("history_cleared", () => {
      clearHistoryUI();
      liveCaption.textContent = "";
    });
  };

  if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
      navigator.serviceWorker.register('/static/serviceWorker.js')
        .then(reg => {
          console.log('Service Worker registrado correctamente:', reg);
        })
        .catch(err => {
          console.error('Error al registrar Service Worker:', err);
        });
    });
  }

  fontSize.addEventListener("change", () => {
    appEl.dataset.font = fontSize.value;
    localStorage.setItem("incluia_font", fontSize.value);
  });

  contrastMode.addEventListener("change", (e) => {
    const value = e.target.value;

    let theme;
    if (value === "normal") theme = "light";
    else if (value === "high") theme = "contrast";
    else if (value === "oled") theme = "oled";

    appEl.dataset.theme = theme;
    localStorage.setItem("incluia_theme", theme);
  });

  clearBtn.addEventListener("click", async () => {
    clearHistoryUI();
    liveCaption.textContent = "";

    if (socket) {
      socket.emit("clear_history");
    }

    try {
      await fetch("/api/clear", { method: "POST" });
    } catch {
      // Best effort only.
    }
  });

  menuToggle.addEventListener("click", () => {
    menuToggle.parentElement.classList.toggle("open");
  });

  loadConfig().then((cfg) => {
    connectSocket(cfg);
  });
})();
