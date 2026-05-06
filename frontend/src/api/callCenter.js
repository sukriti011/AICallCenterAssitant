const BASE_URL = '/api/v1/call-center';

export async function analyzeCall({ session_id, transcript, customer_id }) {
  const response = await fetch(`${BASE_URL}/analyze`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ session_id, transcript, customer_id }),
  });
  if (!response.ok) {
    const err = await response.text();
    throw new Error(err || `Request failed with status ${response.status}`);
  }
  return response.json();
}

export async function analyzeUpload(formData) {
  const response = await fetch(`${BASE_URL}/analyze/upload`, {
    method: 'POST',
    body: formData,
  });
  if (!response.ok) {
    const err = await response.text();
    throw new Error(err || `Request failed with status ${response.status}`);
  }
  return response.json();
}

export async function healthCheck() {
  const response = await fetch(`${BASE_URL}/health`);
  if (!response.ok) throw new Error('Health check failed');
  return response.json();
}
