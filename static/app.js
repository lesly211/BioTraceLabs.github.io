/* ===================================================
   OSINFOR - JavaScript Frontend | Lógica del chatbot
   =================================================== */

let imagenSeleccionada = null;

// ---- INICIALIZACIÓN ----
document.addEventListener('DOMContentLoaded', async () => {
  await cargarBienvenida();
  await cargarEspecies();
  await cargarHistorial();
  configurarUploadZone();
});

// ---- BIENVENIDA Y STATS ----
async function cargarBienvenida() {
  try {
    const res = await fetch('/api/bienvenida');
    const json = await res.json();
    if (!json.success) return;

    const data = json.data;
    const stats = data.stats || {};

    // Actualizar stats sidebar
    document.getElementById('stat-arboles').textContent = stats.total_arboles ?? '—';
    document.getElementById('stat-especies').textContent = stats.total_especies ?? '—';
    document.getElementById('stat-planes').textContent = stats.total_planes ?? '—';
    document.getElementById('stat-protegidas').textContent = stats.especies_protegidas ?? '—';

    // Estado de la API
    const statusDot = document.querySelector('.status-dot');
    const statusLabel = document.querySelector('.status-label');
    if (data.api_configurada) {
      statusDot.classList.add('online');
      statusLabel.textContent = 'Gemini Vision activo';
    } else {
      statusDot.classList.add('demo');
      statusLabel.textContent = 'Modo demo';
    }

    // Mensaje de bienvenida en el chat
    agregarMensajeBienvenida(stats, data.api_configurada);
  } catch (e) {
    console.error('Error al cargar bienvenida:', e);
    agregarMensajeBienvenida({}, false);
  }
}

function agregarMensajeBienvenida(stats, apiActiva) {
  const msgs = document.getElementById('chat-messages');
  const div = document.createElement('div');
  div.className = 'msg msg-bot';
  div.innerHTML = `
    <div class="msg-avatar">🌳</div>
    <div class="msg-bubble">
      <div class="welcome-card">
        <div class="welcome-title">🌿 Bienvenido al Verificador Forestal OSINFOR</div>
        <div class="welcome-body">
          Soy tu asistente de verificación forestal con IA. Puedo identificar árboles 
          mediante fotos y verificar si están incluidos en el 
          <strong>inventario forestal</strong> y <strong>planes de manejo vigentes</strong>.
          <br/><br/>
          📊 Estado del inventario:
          <span class="stat-inline"> ${stats.total_arboles ?? 0} árboles</span> ·
          <span class="stat-inline">${stats.total_especies ?? 0} especies</span> ·
          <span class="stat-inline">${stats.total_planes ?? 0} planes activos</span>
        </div>
        <div class="welcome-hint">
          ${apiActiva
            ? '✅ API de Google Gemini activa — Identificación real de árboles habilitada.'
            : '⚠️ Modo demo activo — Configure su GEMINI_API_KEY para identificación real.'}
          <br/>📷 Sube una foto del árbol usando el panel de abajo para comenzar.
        </div>
      </div>
    </div>`;
  msgs.appendChild(div);
  scrollChat();
}

// ---- ESPECIES ----
async function cargarEspecies() {
  try {
    const res = await fetch('/api/especies');
    const json = await res.json();
    if (!json.success) return;

    const lista = document.getElementById('species-list');
    lista.innerHTML = '';

    json.data.forEach(esp => {
      const item = document.createElement('div');
      item.className = 'species-item';
      const badgeClass = `badge-${(esp.estado_conservacion || 'lc').toLowerCase()}`;
      item.innerHTML = `
        <div>
          <div class="species-name">${esp.nombre_comun}</div>
          <div class="species-sci">${esp.nombre_cientifico}</div>
        </div>
        <span class="species-badge ${badgeClass}">${esp.estado_conservacion || 'LC'}</span>`;
      lista.appendChild(item);
    });
  } catch (e) {
    console.error('Error cargando especies:', e);
  }
}

// ---- HISTORIAL ----
async function cargarHistorial() {
  try {
    const res = await fetch('/api/historial');
    const json = await res.json();
    if (!json.success || !json.data.length) return;

    const lista = document.getElementById('history-list');
    lista.innerHTML = '';

    json.data.forEach(h => {
      const item = document.createElement('div');
      item.className = 'history-item';
      const resultClass = h.resultado === 'ENCONTRADO' ? 'result-found'
        : h.resultado === 'NO_ENCONTRADO' ? 'result-not-found' : 'result-unidentified';
      const resultText = h.resultado === 'ENCONTRADO' ? '✅ En inventario'
        : h.resultado === 'NO_ENCONTRADO' ? '❌ No encontrado' : '⚠️ No identificado';
      item.innerHTML = `
        <div class="history-species">${h.especie_identificada || 'Desconocida'}</div>
        <div class="history-result ${resultClass}">${resultText}</div>`;
      lista.appendChild(item);
    });
  } catch (e) {
    console.error('Error historial:', e);
  }
}

// ---- UPLOAD ZONE ----
function configurarUploadZone() {
  const zone = document.getElementById('upload-zone');
  const fileInput = document.getElementById('file-input');

  zone.addEventListener('click', (e) => {
    if (!e.target.closest('.preview-actions')) fileInput.click();
  });

  fileInput.addEventListener('change', (e) => {
    if (e.target.files[0]) mostrarPreview(e.target.files[0]);
  });

  // Drag & Drop
  zone.addEventListener('dragover', (e) => { e.preventDefault(); zone.classList.add('drag-over'); });
  zone.addEventListener('dragleave', () => zone.classList.remove('drag-over'));
  zone.addEventListener('drop', (e) => {
    e.preventDefault();
    zone.classList.remove('drag-over');
    const file = e.dataTransfer.files[0];
    if (file && file.type.startsWith('image/')) mostrarPreview(file);
    else mostrarToast('⚠️ Por favor sube solo imágenes.', 'warning');
  });
}

function mostrarPreview(file) {
  imagenSeleccionada = file;
  const reader = new FileReader();
  reader.onload = (e) => {
    document.getElementById('preview-img').src = e.target.result;
    document.getElementById('upload-content').style.display = 'none';
    document.getElementById('upload-preview').style.display = 'flex';
  };
  reader.readAsDataURL(file);
}

function cancelarImagen() {
  imagenSeleccionada = null;
  document.getElementById('file-input').value = '';
  document.getElementById('upload-content').style.display = 'block';
  document.getElementById('upload-preview').style.display = 'none';
}

// ---- VERIFICACIÓN PRINCIPAL ----
async function verificarArbol() {
  if (!imagenSeleccionada) return;

  const btnVerify = document.getElementById('btn-verify');
  const previewSrc = document.getElementById('preview-img').src;

  // Mensaje del usuario en el chat
  agregarMensajeUsuario(previewSrc);

  // Mostrar indicador de procesamiento
  const typingId = mostrarTyping();

  btnVerify.disabled = true;
  btnVerify.innerHTML = '<span class="spinner"></span> Analizando...';

  try {
    const formData = new FormData();
    formData.append('imagen', imagenSeleccionada);

    const res = await fetch('/api/verificar-arbol', { method: 'POST', body: formData });
    const json = await res.json();

    quitarTyping(typingId);

    if (!json.success) {
      agregarMensajeBot(`❌ Error: ${json.error}`);
      mostrarToast('Error al procesar la imagen.', 'error');
      return;
    }

    const data = json.data;

    // Mensaje resumen en el chat
    agregarMensajeResultado(data);

    // Abrir modal con detalle completo
    setTimeout(() => abrirModal(data), 300);

    // Recargar historial
    await cargarHistorial();

  } catch (e) {
    quitarTyping(typingId);
    agregarMensajeBot('❌ Error de conexión. Verifica que el servidor esté activo.');
    mostrarToast('Error de conexión.', 'error');
  } finally {
    btnVerify.disabled = false;
    btnVerify.innerHTML = '<span class="btn-icon">🔍</span> Verificar en inventario';
    cancelarImagen();
  }
}

// ---- MENSAJES DEL CHAT ----
function agregarMensajeUsuario(imgSrc) {
  const msgs = document.getElementById('chat-messages');
  const div = document.createElement('div');
  div.className = 'msg msg-user';
  div.innerHTML = `
    <div class="msg-bubble">
      📸 Verificando árbol...
      <br/><img src="${imgSrc}" class="chat-img-preview" alt="Árbol subido"/>
    </div>
    <div class="msg-avatar">👤</div>`;
  msgs.appendChild(div);
  scrollChat();
}

function mostrarTyping() {
  const msgs = document.getElementById('chat-messages');
  const div = document.createElement('div');
  const id = 'typing-' + Date.now();
  div.id = id;
  div.className = 'msg msg-bot';
  div.innerHTML = `
    <div class="msg-avatar">🌳</div>
    <div class="msg-bubble">
      <div class="typing"><span></span><span></span><span></span></div>
    </div>`;
  msgs.appendChild(div);
  scrollChat();
  return id;
}

function quitarTyping(id) {
  document.getElementById(id)?.remove();
}

function agregarMensajeBot(texto) {
  const msgs = document.getElementById('chat-messages');
  const div = document.createElement('div');
  div.className = 'msg msg-bot';
  div.innerHTML = `
    <div class="msg-avatar">🌳</div>
    <div class="msg-bubble">${texto}</div>`;
  msgs.appendChild(div);
  scrollChat();
}

function agregarMensajeResultado(data) {
  const iconoMap = { success: '✅', danger: '❌', warning: '⚠️' };
  const texto = data.mensaje_principal.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>').replace(/\*(.*?)\*/g, '<em>$1</em>');
  agregarMensajeBot(`${texto} <br/><br/><small style="color:var(--text-muted)">📋 Toca para ver el informe completo.</small>`);
}

function scrollChat() {
  const msgs = document.getElementById('chat-messages');
  msgs.scrollTop = msgs.scrollHeight;
}

// ---- MODAL DE RESULTADO ----
function abrirModal(data) {
  const modal = document.getElementById('result-modal');
  const content = document.getElementById('modal-content');
  const id = data.identificacion || {};
  const inv = data.inventario || [];
  const recs = data.recomendaciones || [];

  const confClass = id.nivel_confianza === 'alta' ? 'conf-high'
    : id.nivel_confianza === 'media' ? 'conf-med' : 'conf-low';

  let inventarioHTML = '';
  if (inv.length > 0) {
    inventarioHTML = inv.map(a => `
      <div class="tree-card">
        <div class="tree-card-header">
          <span class="tree-code">${a.codigo_arbol}</span>
          <span class="tree-status ${a.plan_estado === 'VIGENTE' ? 'status-vigente' : 'status-vencido'}">
            ${a.plan_icono} ${a.plan_estado}
          </span>
        </div>
        <div class="tree-info-grid">
          <div class="tree-info-item"><span class="tree-info-key">Ubicación</span><span class="tree-info-val">${a.ubicacion || '—'}</span></div>
          <div class="tree-info-item"><span class="tree-info-key">Estado fitosanitario</span><span class="tree-info-val">${a.estado_fitosanitario || '—'}</span></div>
          <div class="tree-info-item"><span class="tree-info-key">DAP (cm)</span><span class="tree-info-val">${a.dap_cm ?? '—'}</span></div>
          <div class="tree-info-item"><span class="tree-info-key">Altura (m)</span><span class="tree-info-val">${a.altura_m ?? '—'}</span></div>
          <div class="tree-info-item"><span class="tree-info-key">Plan de manejo</span><span class="tree-info-val">${a.plan_codigo || '—'}</span></div>
          <div class="tree-info-item"><span class="tree-info-key">Titular</span><span class="tree-info-val">${a.plan_titular || '—'}</span></div>
          <div class="tree-info-item"><span class="tree-info-key">Resolución</span><span class="tree-info-val">${a.plan_resolucion || '—'}</span></div>
          <div class="tree-info-item"><span class="tree-info-key">Vencimiento</span><span class="tree-info-val">${a.plan_vencimiento || '—'}</span></div>
          <div class="tree-info-item" style="grid-column:span 2"><span class="tree-info-key">Observaciones</span><span class="tree-info-val">${a.observaciones || '—'}</span></div>
        </div>
      </div>`).join('');
  } else {
    inventarioHTML = '<p style="color:var(--text-muted);font-size:13px;">No se encontraron registros en el inventario para esta especie.</p>';
  }

  const recsHTML = recs.length
    ? `<ul class="rec-list">${recs.map(r => `<li>${r}</li>`).join('')}</ul>`
    : '';

  const charAlternos = (id.alternativos || []).length
    ? `<div class="result-section"><div class="result-section-title">Especies alternativas posibles</div><p style="font-size:12px;color:var(--text-muted)">${id.alternativos.join(' · ')}</p></div>`
    : '';

  const msgFormatted = data.mensaje_principal.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>').replace(/\*(.*?)\*/g, '<em>$1</em>');

  content.innerHTML = `
    <div class="result-header ${data.tipo_alerta}">
      <div class="result-title">${msgFormatted}</div>
    </div>

    <div class="result-section">
      <div class="result-section-title">🔬 Identificación botánica</div>
      <div class="id-grid">
        <div class="id-field"><div class="id-key">Nombre común</div><div class="id-val">${id.nombre_comun || '—'}</div></div>
        <div class="id-field"><div class="id-key">Nombre científico</div><div class="id-val sci">${id.nombre_cientifico || '—'}</div></div>
        <div class="id-field"><div class="id-key">Familia</div><div class="id-val">${id.familia || '—'}</div></div>
        <div class="id-field"><div class="id-key">Confianza</div><div class="id-val ${confClass}">${id.icono_confianza} ${id.confianza_pct}%</div></div>
      </div>
      ${id.descripcion ? `<p style="font-size:12px;color:var(--text-muted);margin-top:10px;padding:10px;background:var(--bg-card);border-radius:8px;">${id.descripcion}</p>` : ''}
      ${id.advertencias ? `<p style="font-size:12px;color:var(--yellow);margin-top:8px">⚠️ ${id.advertencias}</p>` : ''}
    </div>

    <div class="result-section">
      <div class="result-section-title">📋 Registros en inventario (${data.total_encontrados} encontrados)</div>
      ${inventarioHTML}
    </div>

    ${charAlternos}

    ${recsHTML ? `<div class="result-section"><div class="result-section-title">💡 Recomendaciones</div>${recsHTML}</div>` : ''}
  `;

  modal.style.display = 'flex';
}

function cerrarModal(e) {
  if (!e || e.target === document.getElementById('result-modal')) {
    document.getElementById('result-modal').style.display = 'none';
  }
}

// ---- TOAST ----
function mostrarToast(mensaje, tipo = 'info') {
  const container = document.getElementById('toast-container');
  const toast = document.createElement('div');
  toast.className = `toast ${tipo}`;
  toast.innerHTML = `<span>${mensaje}</span>`;
  container.appendChild(toast);
  setTimeout(() => toast.remove(), 4000);
}
