const form = document.getElementById('planner');
const feedback = document.getElementById('result');
document.addEventListener('keydown', (event) => {
  if (event.key === '/' && !event.target.closest('input,select,textarea,button')) {
    event.preventDefault();
    form.elements.sample.focus();
  }
});
form.addEventListener('submit', async (event) => {
  event.preventDefault();
  const button = event.submitter;
  button.disabled = true;
  feedback.value = '排程中…';
  delete feedback.dataset.error;
  try {
    const response = await fetch(form.action, {method:'POST', body:new FormData(form)});
    const data = await response.json();
    if (!response.ok) throw new Error(data.message);
    window.location.assign(data.next);
  } catch (error) {
    feedback.dataset.error = '';
    feedback.value = error.message || '排程失败，请重试。';
    button.disabled = false;
  }
});
