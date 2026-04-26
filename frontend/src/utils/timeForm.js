/**
 * Time form cascade: when invoice, project, or task dropdowns change,
 * update the other two dropdowns based on the data relationships.
 *
 * Relationships:
 *   Invoice → project (invoice.project), task (project.default_task)
 *   Project → task (project.default_task)
 *   Task    → project (task.project)
 *
 * Requires window.TIME_API_URLS to be set by the template (see edit.html).
 */

function initTimeFormDropdowns() {
  const invoiceSelect = document.getElementById('id_invoice');
  const projectSelect = document.getElementById('id_project');
  const taskSelect = document.getElementById('id_task');

  // Only run when all three dropdowns are present (admin time form)
  if (!invoiceSelect || !projectSelect || !taskSelect) return;

  const apiUrls = window.TIME_API_URLS;
  if (!apiUrls) return;

  let activeController = null;

  function abortPending() {
    if (activeController) {
      activeController.abort();
    }
    activeController = new AbortController();
    return activeController.signal;
  }

  async function fetchJson(url, signal) {
    const resp = await fetch(url, { signal });
    if (!resp.ok) return null;
    return resp.json();
  }

  invoiceSelect.addEventListener('change', async function () {
    const invoiceId = this.value;
    if (!invoiceId) {
      // Clear project and task when invoice is deselected
      projectSelect.value = '';
      taskSelect.value = '';
      return;
    }
    const signal = abortPending();
    try {
      const data = await fetchJson(apiUrls.invoice + invoiceId + '/', signal);
      if (!data) return;
      projectSelect.value = data.project_id || '';
      taskSelect.value = data.default_task_id || '';
    } catch (e) {
      if (e.name !== 'AbortError') console.error('Time form invoice API error:', e);
    }
  });

  projectSelect.addEventListener('change', async function () {
    const projectId = this.value;
    if (!projectId) {
      taskSelect.value = '';
      return;
    }
    const signal = abortPending();
    try {
      const data = await fetchJson(apiUrls.project + projectId + '/', signal);
      if (!data) return;
      taskSelect.value = data.default_task_id || '';
    } catch (e) {
      if (e.name !== 'AbortError') console.error('Time form project API error:', e);
    }
  });

  taskSelect.addEventListener('change', async function () {
    const taskId = this.value;
    if (!taskId) return;
    const signal = abortPending();
    try {
      const data = await fetchJson(apiUrls.task + taskId + '/', signal);
      if (!data) return;
      if (data.project_id) {
        projectSelect.value = data.project_id;
      }
    } catch (e) {
      if (e.name !== 'AbortError') console.error('Time form task API error:', e);
    }
  });
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initTimeFormDropdowns);
} else {
  initTimeFormDropdowns();
}
