/* ===================================================
   OSINFOR - JavaScript Frontend | Lógica del chatbot
   =================================================== */

let imagenSeleccionada = null;
let archivoSeleccionado = null;
let tipoArchivo = null; // 'imagen' o 'documento'

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
      const proveedor = data.proveedor || 'IA';
      statusLabel.textContent = `${proveedor} activo`;
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
          Soy tu asistente de verificación forestal con IA. Puedo:
          <br/>💬 <strong>Responder tus preguntas</strong> sobre especies forestales, trazabilidad y conservación
          <br/>📷 <strong>Identificar árboles</strong> mediante fotos y verificar si están en el 
          <strong>inventario forestal</strong> y <strong>planes de manejo vigentes</strong>
          <br/>📄 <strong>Leer documentos</strong> (PDF, DOCX, imágenes con texto) y responder preguntas sobre ellos
          <br/><br/>
          📊 Estado del inventario:
          <span class="stat-inline"> ${stats.total_arboles ?? 0} árboles</span> ·
          <span class="stat-inline">${stats.total_especies ?? 0} especies</span> ·
          <span class="stat-inline">${stats.total_planes ?? 0} planes activos</span>
        </div>
        <div class="welcome-hint">
          ${apiActiva
            ? '✅ IA activada — Identificación real y conversación habilitadas.'
            : '⚠️ Modo demo activo — Configure XAI_API_KEY (Grok) o GEMINI_API_KEY para funcionalidad completa.'}
          <br/>💬 Pregúntame lo que quieras, 📷 sube una foto de árbol, o 📄 sube un documento para analizar.
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
    if (e.target.files[0]) procesarArchivo(e.target.files[0]);
  });

  // Drag & Drop
  zone.addEventListener('dragover', (e) => { e.preventDefault(); zone.classList.add('drag-over'); });
  zone.addEventListener('dragleave', () => zone.classList.remove('drag-over'));
  zone.addEventListener('drop', (e) => {
    e.preventDefault();
    zone.classList.remove('drag-over');
    const file = e.dataTransfer.files[0];
    if (file) procesarArchivo(file);
  });
}

function procesarArchivo(file) {
  const ext = file.name.split('.').pop().toLowerCase();
  const imageExts = ['jpg', 'jpeg', 'png', 'gif', 'webp', 'bmp'];
  const docExts = ['pdf', 'docx', 'doc', 'txt', 'md'];
  
  if (imageExts.includes(ext) || file.type.startsWith('image/')) {
    tipoArchivo = 'imagen';
    imagenSeleccionada = file;
    archivoSeleccionado = file;
    mostrarPreviewImagen(file);
  } else if (docExts.includes(ext)) {
    tipoArchivo = 'documento';
    archivoSeleccionado = file;
    imagenSeleccionada = null;
    mostrarPreviewDocumento(file);
  } else {
    mostrarToast('⚠️ Formato no soportado. Usa imágenes (JPG, PNG) o documentos (PDF, DOCX, TXT).', 'warning');
  }
}

function mostrarPreviewImagen(file) {
  const reader = new FileReader();
  reader.onload = (e) => {
    document.getElementById('preview-img').src = e.target.result;
    document.getElementById('upload-content').style.display = 'none';
    document.getElementById('upload-preview').style.display = 'flex';
    
    // Actualizar botón para identificación de árbol
    const btnVerify = document.getElementById('btn-verify');
    btnVerify.innerHTML = '<span class="btn-icon">🔍</span> Verificar en inventario';
    btnVerify.onclick = verificarArbol;
  };
  reader.readAsDataURL(file);
}

function mostrarPreviewDocumento(file) {
  const ext = file.name.split('.').pop().toLowerCase();
  const iconMap = {
    'pdf': '📕',
    'docx': '📘',
    'doc': '📘',
    'txt': '📄',
    'md': '📝'
  };
  const icon = iconMap[ext] || '📄';
  
  document.getElementById('preview-img').src = '';
  document.getElementById('preview-img').style.display = 'none';
  
  // Crear preview personalizado para documentos
  const preview = document.getElementById('upload-preview');
  preview.innerHTML = `
    <div style="text-align: center; padding: 20px;">
      <div style="font-size: 64px; margin-bottom: 10px;">${icon}</div>
      <div style="font-size: 14px; font-weight: 600; margin-bottom: 5px;">${file.name}</div>
      <div style="font-size: 12px; color: var(--text-muted);">${(file.size / 1024).toFixed(1)} KB</div>
      <div style="margin-top: 15px; width: 100%;">
        <input 
          type="text" 
          id="pregunta-documento" 
          placeholder="💬 ¿Qué quieres saber sobre este documento? (opcional)"
          style="width: 100%; padding: 10px; border: 1px solid var(--border-color); border-radius: 8px; font-size: 13px;"
        />
      </div>
    </div>
    <div class="preview-actions">
      <button class="btn-verify" id="btn-verify" onclick="procesarDocumento()">
        <span class="btn-icon">📖</span>
        Analizar documento
      </button>
      <button class="btn-cancel" onclick="cancelarImagen()">✕ Cancelar</button>
    </div>
  `;
  
  document.getElementById('upload-content').style.display = 'none';
  preview.style.display = 'flex';
}

function cancelarImagen() {
  imagenSeleccionada = null;
  archivoSeleccionado = null;
  tipoArchivo = null;
  document.getElementById('file-input').value = '';
  document.getElementById('upload-content').style.display = 'block';
  
  const preview = document.getElementById('upload-preview');
  preview.style.display = 'none';
  
  // Restaurar preview de imagen
  const previewImg = document.getElementById('preview-img');
  previewImg.style.display = 'block';
  preview.innerHTML = `
    <img id="preview-img" src="" alt="Vista previa" />
    <div class="preview-actions">
      <button class="btn-verify" id="btn-verify" onclick="verificarArbol()">
        <span class="btn-icon">🔍</span>
        Verificar en inventario
      </button>
      <button class="btn-cancel" onclick="cancelarImagen()">✕ Cancelar</button>
    </div>
  `;
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

// ---- MENSAJES DE TEXTO ----
async function enviarMensaje() {
  const textInput = document.getElementById('text-input');
  const mensaje = textInput.value.trim();
  
  if (!mensaje) return;
  
  // Limpiar input
  textInput.value = '';
  
  // Agregar mensaje del usuario
  agregarMensajeUsuarioTexto(mensaje);
  
  // Mostrar typing indicator
  const typingId = mostrarTyping();
  
  try {
    const res = await fetch('/api/mensaje', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ mensaje })
    });
    
    const json = await res.json();
    quitarTyping(typingId);
    
    if (!json.success) {
      agregarMensajeBot(`❌ Error: ${json.error}`);
      return;
    }
    
    const data = json.data;
    
    // Agregar respuesta del bot
    let respuestaFormateada = data.respuesta
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\n/g, '<br/>');
    
    // Si hay datos del inventario, agregarlos
    if (data.datos_inventario) {
      const inv = data.datos_inventario;
      respuestaFormateada += `
        <br/><br/>
        <div style="background:var(--bg-card);padding:12px;border-radius:8px;margin-top:8px;">
          <strong>📊 Datos del inventario:</strong><br/>
          <small style="color:var(--text-muted)">
          • Especie: <strong>${inv.especie}</strong> (<em>${inv.nombre_cientifico}</em>)<br/>
          • Árboles registrados: <strong>${inv.total_arboles}</strong><br/>
          • Planes de manejo: <strong>${inv.planes.length}</strong>
          </small>
        </div>`;
    }
    
    agregarMensajeBot(respuestaFormateada);
    
  } catch (e) {
    quitarTyping(typingId);
    agregarMensajeBot('❌ Error de conexión. Verifica que el servidor esté activo.');
    console.error('Error:', e);
  }
}

function agregarMensajeUsuarioTexto(texto) {
  const msgs = document.getElementById('chat-messages');
  const div = document.createElement('div');
  div.className = 'msg msg-user';
  div.innerHTML = `
    <div class="msg-bubble">${texto}</div>
    <div class="msg-avatar">👤</div>`;
  msgs.appendChild(div);
  scrollChat();
}

// ---- PROCESAMIENTO DE DOCUMENTOS ----
async function procesarDocumento() {
  if (!archivoSeleccionado) return;

  const btnVerify = document.getElementById('btn-verify');
  const preguntaInput = document.getElementById('pregunta-documento');
  const pregunta = preguntaInput ? preguntaInput.value.trim() : '';
  
  // Mensaje del usuario en el chat
  if (pregunta) {
    agregarMensajeUsuarioDocumento(archivoSeleccionado.name, pregunta);
  } else {
    agregarMensajeUsuarioDocumento(archivoSeleccionado.name);
  }

  // Mostrar indicador de procesamiento
  const typingId = mostrarTyping();

  btnVerify.disabled = true;
  btnVerify.innerHTML = '<span class="spinner"></span> Analizando...';

  try {
    const formData = new FormData();
    formData.append('documento', archivoSeleccionado);
    if (pregunta) {
      formData.append('pregunta', pregunta);
    }

    const res = await fetch('/api/procesar-documento', { method: 'POST', body: formData });
    const json = await res.json();

    quitarTyping(typingId);

    if (!json.success) {
      agregarMensajeBot(`❌ Error: ${json.error}`);
      mostrarToast('Error al procesar el documento.', 'error');
      return;
    }

    const data = json.data;

    // Mostrar resultado del documento procesado
    if (data.tipo === 'documento_procesado' || data.tipo === 'documento_consultado') {
      let mensaje = `✅ <strong>Documento analizado exitosamente</strong><br/><br/>`;
      
      if (data.estadisticas) {
        const stats = data.estadisticas;
        mensaje += `📄 <strong>${stats.archivo}</strong><br/>`;
        mensaje += `📊 ${stats.palabras.toLocaleString()} palabras · ${stats.caracteres.toLocaleString()} caracteres<br/><br/>`;
      }
      
      if (data.respuesta) {
        // Si hay una consulta sobre el documento
        mensaje += `<div style="background:var(--bg-card);padding:14px;border-radius:10px;margin-top:10px;line-height:1.6;">`;
        mensaje += `<strong style="color:var(--primary);">📋 Respuesta:</strong><br/><br/>`;
        mensaje += data.respuesta.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>').replace(/\n/g, '<br/>');
        mensaje += `</div>`;
      } else if (data.texto) {
        // Mostrar resumen del contenido
        const palabras = data.texto.split(/\s+/).length;
        const textoMostrar = data.texto.substring(0, 800);
        mensaje += `<div style="background:var(--bg-card);padding:14px;border-radius:10px;margin-top:10px;">`;
        mensaje += `<strong style="color:var(--primary);">📄 Contenido del documento:</strong><br/><br/>`;
        mensaje += `<div style="font-size:13px;color:var(--text);line-height:1.6;">`;
        mensaje += textoMostrar.replace(/\n/g, '<br/>');
        if (data.texto.length > 800) mensaje += '<br/><br/><em style="color:var(--text-muted);">... (continúa)</em>';
        mensaje += `</div></div><br/>`;
        mensaje += `<div style="background:var(--success-light);padding:10px;border-radius:8px;font-size:12px;">`;
        mensaje += `💬 <strong>Ahora puedes hacerme preguntas específicas sobre este documento.</strong><br/>`;
        mensaje += `Por ejemplo: "¿Cuál es el tema principal?", "Resume el contenido", "¿Qué dice sobre...?"`;
        mensaje += `</div>`;
      }
      
      agregarMensajeBot(mensaje);
      mostrarToast('✅ Documento procesado correctamente', 'success');
    } else if (data.tipo === 'error') {
      agregarMensajeBot(`❌ ${data.mensaje}`);
      mostrarToast(data.mensaje, 'error');
    }

  } catch (e) {
    quitarTyping(typingId);
    agregarMensajeBot('❌ Error de conexión. Verifica que el servidor esté activo.');
    mostrarToast('Error de conexión.', 'error');
  } finally {
    btnVerify.disabled = false;
    btnVerify.innerHTML = '<span class="btn-icon">📖</span> Analizar documento';
    cancelarImagen();
  }
}

function agregarMensajeUsuarioDocumento(nombreArchivo, pregunta = null) {
  const msgs = document.getElementById('chat-messages');
  const div = document.createElement('div');
  div.className = 'msg msg-user';
  
  let contenido = `📎 Analizando documento: <strong>${nombreArchivo}</strong>`;
  if (pregunta) {
    contenido += `<br/><br/>💬 Pregunta: <em>"${pregunta}"</em>`;
  }
  
  div.innerHTML = `
    <div class="msg-bubble">
      ${contenido}
    </div>
    <div class="msg-avatar">👤</div>`;
  msgs.appendChild(div);
  scrollChat();
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
