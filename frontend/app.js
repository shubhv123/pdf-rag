/**
 * DocQuery — app.js
 * Handles: drag-and-drop upload, session tracking, chat UI, source modal.
 */

const API_BASE = 'http://localhost:8000/api';

// ── State ─────────────────────────────────────────────────────
const state = {
  sessions: [],          // [{ sessionId, filename, chunkCount }]
  activeSessionId: null,
  isUploading: false,
  isQuerying: false,
};

// ── DOM refs ──────────────────────────────────────────────────
const dropZone       = document.getElementById('drop-zone');
const fileInput      = document.getElementById('file-input');
const browseBtn      = document.getElementById('browse-btn');
const uploadStatus   = document.getElementById('upload-status');
const statusBar      = document.getElementById('status-bar');
const statusText     = document.getElementById('status-text');
const docList        = document.getElementById('doc-list');
const docItems       = document.getElementById('doc-items');
const emptyState     = document.getElementById('empty-state');
const chatMessages   = document.getElementById('chat-messages');
const chatForm       = document.getElementById('chat-form');
const questionInput  = document.getElementById('question-input');
const sendBtn        = document.getElementById('send-btn');
const sourceModal    = document.getElementById('source-modal');
const modalBackdrop  = document.getElementById('modal-backdrop');
const modalClose     = document.getElementById('modal-close');
const modalBody      = document.getElementById('modal-body');

// ── Upload ────────────────────────────────────────────────────

browseBtn.addEventListener('click', () => fileInput.click());
fileInput.addEventListener('change', () => {
  if (fileInput.files[0]) handleFile(fileInput.files[0]);
});

dropZone.addEventListener('keydown', (e) => {
  if (e.key === 'Enter' || e.key === ' ') fileInput.click();
});

// Drag events
['dragenter', 'dragover'].forEach(evt =>
  dropZone.addEventListener(evt, (e) => {
    e.preventDefault();
    dropZone.classList.add('drag-over');
  })
);
['dragleave', 'drop'].forEach(evt =>
  dropZone.addEventListener(evt, (e) => {
    e.preventDefault();
    dropZone.classList.remove('drag-over');
  })
);
dropZone.addEventListener('drop', (e) => {
  const file = e.dataTransfer.files[0];
  if (file) handleFile(file);
});
dropZone.addEventListener('click', (e) => {
  if (e.target !== browseBtn) fileInput.click();
});

async function handleFile(file) {
  if (state.isUploading) return;

  const allowed = ['.pdf', '.txt', '.md'];
  const ext = '.' + file.name.split('.').pop().toLowerCase();
  if (!allowed.includes(ext)) {
    showStatusError(`Unsupported file type: ${ext}. Use PDF, TXT, or MD.`);
    return;
  }

  state.isUploading = true;
  showStatusLoading(`Uploading ${file.name}…`);

  const formData = new FormData();
  formData.append('file', file);

  try {
    const res = await fetch(`${API_BASE}/upload`, {
      method: 'POST',
      body: formData,
    });

    const data = await res.json();

    if (!res.ok) {
      throw new Error(data.detail || `Upload failed (${res.status})`);
    }

    showStatusSuccess(`Indexed ${data.chunk_count} chunks from "${data.filename}"`);
    addSession(data.session_id, data.filename, data.chunk_count);
    setActiveSession(data.session_id);
    // Reset file input so same file can be re-uploaded
    fileInput.value = '';
  } catch (err) {
    showStatusError(err.message);
  } finally {
    state.isUploading = false;
  }
}

// ── Status helpers ────────────────────────────────────────────

function showStatusLoading(text) {
  uploadStatus.hidden = false;
  statusBar.className = 'status-bar-fill indeterminate';
  statusBar.style.width = '';
  statusText.textContent = text;
}

function showStatusSuccess(text) {
  statusBar.className = 'status-bar-fill';
  statusBar.style.width = '100%';
  statusText.textContent = '✓ ' + text;
  setTimeout(() => { uploadStatus.hidden = true; }, 3000);
}

function showStatusError(text) {
  statusBar.className = 'status-bar-fill';
  statusBar.style.width = '0%';
  statusText.textContent = '✗ ' + text;
}

// ── Session / Doc List ────────────────────────────────────────

function addSession(sessionId, filename, chunkCount) {
  state.sessions.push({ sessionId, filename, chunkCount });
  renderDocList();
}

function renderDocList() {
  docList.hidden = state.sessions.length === 0;
  docItems.innerHTML = '';

  state.sessions.forEach(({ sessionId, filename, chunkCount }) => {
    const li = document.createElement('li');
    li.className = 'doc-item' + (sessionId === state.activeSessionId ? ' active' : '');
    li.dataset.sessionId = sessionId;
    li.innerHTML = `
      <span class="doc-dot"></span>
      <div class="doc-info">
        <div class="doc-name" title="${filename}">${filename}</div>
        <div class="doc-chunks">${chunkCount} chunks indexed</div>
      </div>
    `;
    li.addEventListener('click', () => setActiveSession(sessionId));
    docItems.appendChild(li);
  });
}

function setActiveSession(sessionId) {
  state.activeSessionId = sessionId;
  renderDocList();
  // Show chat UI, hide empty state
  emptyState.hidden = true;
  chatMessages.hidden = false;
  chatForm.hidden = false;
  chatMessages.innerHTML = '';
  questionInput.focus();
}

// ── Chat ──────────────────────────────────────────────────────

chatForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  if (state.isQuerying) return;

  const question = questionInput.value.trim();
  if (!question || !state.activeSessionId) return;

  questionInput.value = '';
  autoResize(questionInput);
  sendBtn.disabled = true;
  state.isQuerying = true;

  appendMessage('user', question);
  const typingMsg = appendTypingIndicator();

  try {
    const res = await fetch(`${API_BASE}/query`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        session_id: state.activeSessionId,
        question,
      }),
    });

    const data = await res.json();

    typingMsg.remove();

    if (!res.ok) {
      appendMessage('error', `Error: ${data.detail || res.statusText}`);
      return;
    }

    appendAnswerMessage(data.question, data.answer, data.sources);
  } catch (err) {
    typingMsg.remove();
    appendMessage('error', `Network error: ${err.message}`);
  } finally {
    state.isQuerying = false;
    sendBtn.disabled = false;
    questionInput.focus();
  }
});

function appendMessage(role, content) {
  const div = document.createElement('div');
  div.className = `message ${role}`;

  const roleLabel = role === 'user' ? 'You' : role === 'error' ? 'Error' : 'Assistant';

  div.innerHTML = `
    <span class="message-role">${roleLabel}</span>
    <div class="message-bubble">${escapeHTML(content)}</div>
  `;
  chatMessages.appendChild(div);
  scrollChat();
  return div;
}

function appendTypingIndicator() {
  const div = document.createElement('div');
  div.className = 'message assistant';
  div.innerHTML = `
    <span class="message-role">Assistant</span>
    <div class="message-bubble">
      <div class="typing-indicator">
        <span></span><span></span><span></span>
      </div>
    </div>
  `;
  chatMessages.appendChild(div);
  scrollChat();
  return div;
}

function appendAnswerMessage(question, answer, sources) {
  const div = document.createElement('div');
  div.className = 'message assistant';

  // Animate text character-by-character
  const bubble = document.createElement('div');
  bubble.className = 'message-bubble';

  const textEl = document.createElement('div');
  textEl.className = 'answer-text';
  bubble.appendChild(textEl);

  // Sources button
  if (sources && sources.length > 0) {
    const citeBtn = document.createElement('button');
    citeBtn.className = 'source-cite-btn';
    citeBtn.innerHTML = `<svg viewBox="0 0 16 16" width="10" height="10" fill="none" stroke="currentColor" stroke-width="1.5"><rect x="2" y="2" width="12" height="12" rx="1"/><line x1="5" y1="6" x2="11" y2="6"/><line x1="5" y1="9" x2="9" y2="9"/></svg> ${sources.length} sources`;
    citeBtn.addEventListener('click', () => openSourceModal(sources));
    bubble.appendChild(citeBtn);
  }

  div.innerHTML = `<span class="message-role">Assistant</span>`;
  div.appendChild(bubble);
  chatMessages.appendChild(div);
  scrollChat();

  // Typewriter reveal
  animateText(textEl, answer);
}

function animateText(el, text) {
  let i = 0;
  const interval = setInterval(() => {
    el.textContent = text.slice(0, ++i);
    if (i >= text.length) clearInterval(interval);
    scrollChat();
  }, 12);
}

function scrollChat() {
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

// ── Textarea auto-resize ──────────────────────────────────────

questionInput.addEventListener('input', () => autoResize(questionInput));
questionInput.addEventListener('keydown', (e) => {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    chatForm.requestSubmit();
  }
});

function autoResize(el) {
  el.style.height = 'auto';
  el.style.height = Math.min(el.scrollHeight, 120) + 'px';
}

// ── Source Modal ──────────────────────────────────────────────

function openSourceModal(sources) {
  modalBody.innerHTML = '';
  sources.forEach((src, idx) => {
    const chunk = document.createElement('div');
    chunk.className = 'source-chunk';
    chunk.style.animationDelay = `${idx * 0.06}s`;

    const pageMeta = src.page ? ` · Page ${src.page}` : '';
    const chunkMeta = src.chunk_index != null ? ` · Chunk #${src.chunk_index}` : '';

    chunk.innerHTML = `
      <div class="source-chunk-meta">${escapeHTML(src.source)}${pageMeta}${chunkMeta}</div>
      <div class="source-chunk-text">${escapeHTML(src.content)}</div>
    `;
    modalBody.appendChild(chunk);
  });

  sourceModal.hidden = false;
  document.body.style.overflow = 'hidden';
}

function closeModal() {
  sourceModal.hidden = true;
  document.body.style.overflow = '';
}

modalClose.addEventListener('click', closeModal);
modalBackdrop.addEventListener('click', closeModal);
document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape' && !sourceModal.hidden) closeModal();
});

// ── Utilities ─────────────────────────────────────────────────

function escapeHTML(str) {
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}
