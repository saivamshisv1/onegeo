const API_BASE = (window.ONEGEO_API_BASE || '').replace(/\/$/, '');

function apiUrl(path) {
  return `${API_BASE}${path}`;
}

async function loadFiles() {
  const res = await fetch(apiUrl('/api/files'));
  const files = await res.json();
  const fileSelect = document.getElementById('fileSelect');
  fileSelect.innerHTML = '';

  files.forEach((f) => {
    const opt = document.createElement('option');
    opt.value = f.id;
    opt.textContent = `${f.filename} (${f.min_depth} - ${f.max_depth})`;
    opt.dataset.curves = JSON.stringify(f.curves);
    fileSelect.appendChild(opt);
  });

  if (files.length) {
    populateCurves(files[0].curves);
  }
}

function populateCurves(curves) {
  const curveSelect = document.getElementById('curveSelect');
  curveSelect.innerHTML = '';
  curves.slice(1).forEach((curve) => {
    const opt = document.createElement('option');
    opt.value = curve;
    opt.textContent = curve;
    curveSelect.appendChild(opt);
  });
}

function selectedCurves() {
  return [...document.getElementById('curveSelect').selectedOptions].map((o) => o.value);
}

function selectedFileId() {
  return document.getElementById('fileSelect').value;
}

function depthParams() {
  const startDepth = document.getElementById('startDepth').value;
  const endDepth = document.getElementById('endDepth').value;
  return {
    start_depth: startDepth ? Number(startDepth) : null,
    end_depth: endDepth ? Number(endDepth) : null,
  };
}

async function plotCurves() {
  const fileId = selectedFileId();
  if (!fileId) return;

  const params = new URLSearchParams();
  selectedCurves().forEach((curve) => params.append('curves', curve));

  const depths = depthParams();
  if (depths.start_depth !== null) params.append('start_depth', depths.start_depth);
  if (depths.end_depth !== null) params.append('end_depth', depths.end_depth);

  const res = await fetch(apiUrl(`/api/files/${fileId}/curves?${params.toString()}`));
  if (!res.ok) {
    alert((await res.json()).detail || 'Could not fetch curve data');
    return;
  }
  const data = await res.json();

  const traces = Object.entries(data.curves).map(([name, values]) => ({
    x: values,
    y: data.depth,
    type: 'scatter',
    mode: 'lines',
    name,
  }));

  Plotly.newPlot('plot', traces, {
    yaxis: { autorange: 'reversed', title: 'Depth' },
    xaxis: { title: 'Log Value' },
    legend: { orientation: 'h' },
    margin: { t: 25 },
  });
}

async function runInterpretation() {
  const fileId = selectedFileId();
  if (!fileId) return;

  const body = {
    curves: selectedCurves(),
    ...depthParams(),
  };

  const res = await fetch(apiUrl(`/api/files/${fileId}/interpret`), {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  const result = await res.json();
  document.getElementById('interpretation').textContent = JSON.stringify(result, null, 2);
}

async function askChat() {
  const fileId = selectedFileId();
  const message = document.getElementById('chatInput').value;
  if (!fileId || !message.trim()) return;

  const res = await fetch(apiUrl(`/api/files/${fileId}/chat`), {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      message,
      curves: selectedCurves(),
      ...depthParams(),
    }),
  });
  const result = await res.json();
  document.getElementById('chatOutput').textContent = result.answer;
}

document.getElementById('uploadBtn').addEventListener('click', async () => {
  const input = document.getElementById('lasFile');
  if (!input.files.length) return;

  const formData = new FormData();
  formData.append('file', input.files[0]);

  const res = await fetch(apiUrl('/api/uploads'), { method: 'POST', body: formData });
  const status = document.getElementById('uploadStatus');
  if (!res.ok) {
    status.textContent = `Upload failed: ${(await res.json()).detail}`;
    return;
  }

  const file = await res.json();
  status.textContent = `Uploaded ${file.filename}`;
  await loadFiles();
});

document.getElementById('plotBtn').addEventListener('click', plotCurves);
document.getElementById('interpretBtn').addEventListener('click', runInterpretation);
document.getElementById('chatBtn').addEventListener('click', askChat);
document.getElementById('fileSelect').addEventListener('change', (event) => {
  const curves = JSON.parse(event.target.selectedOptions[0]?.dataset.curves ?? '[]');
  populateCurves(curves);
});

loadFiles();
