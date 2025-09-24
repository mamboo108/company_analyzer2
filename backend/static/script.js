document.getElementById('qform').onsubmit = async (e) => {
  e.preventDefault();
  const company = document.getElementById('company').value;
  const query = document.getElementById('query').value;
  document.getElementById('out').innerText = "Thinking...";
  const resp = await fetch('/api/query', {
    method:'POST',
    headers: {'Content-Type':'application/json'},
    body: JSON.stringify({company, query})
  });
  const j = await resp.json();
  if (j.error) document.getElementById('out').innerText = "Error: " + j.error;
  else document.getElementById('out').innerText = j.answer;
}
