const projectPage = document.getElementById('projects');
const projectsEndpoint = projectPage.dataset.projectsEndpoint;
const detailUrlTemplate = projectPage.dataset.detailUrlTemplate;
const starUrlTemplate = projectPage.dataset.starUrlTemplate;
const isAuthenticated = projectPage.dataset.authenticated === 'true';
const isSuperuser = projectPage.dataset.superuser === 'true';

const projectGrid = document.getElementById('project-grid');
const projectLoading = document.getElementById('project-loading');
const projectError = document.getElementById('project-error');
const projectEmpty = document.getElementById('project-empty');
const projectSearch = document.getElementById('project-search-input');
const projectSearchForm = document.getElementById('project-search-form');
const projectForm = document.getElementById('project-form');
const projectModal = document.getElementById('add-project-modal');
const projectModalTitle = document.getElementById('add-project-modal-title');
const projectSubmitButton = document.getElementById('project-submit-button');

let projectSearchTimer;
let projectRequest;
let editingProject = false;

function showProjectState(state) {
    projectLoading.classList.toggle('hide', state !== 'loading');
    projectError.classList.toggle('hide', state !== 'error');
    projectEmpty.classList.toggle('hide', state !== 'empty');
    projectGrid.classList.toggle('hide', state !== 'grid');
}

function getProjectCookie(name) {
    for (const entry of document.cookie.split(';')) {
        const [key, ...value] = entry.trim().split('=');
        if (key === name) return decodeURIComponent(value.join('='));
    }
    return '';
}

function safeProjectUrl(value) {
    if (!value) return '';
    try {
        const url = new URL(value, window.location.origin);
        return ['http:', 'https:'].includes(url.protocol) ? url.href : '';
    } catch (_) {
        return '';
    }
}

function projectUrlFor(template, projectId) {
    return template.replace(
        '00000000-0000-0000-0000-000000000000',
        encodeURIComponent(projectId),
    );
}

function makeProjectCard(project) {
    const card = document.createElement('article');
    card.className = 'project-card';

    const imageUrl = safeProjectUrl(project.project_image_url);
    if (imageUrl) {
        const image = document.createElement('img');
        image.className = 'project-image';
        image.src = imageUrl;
        image.alt = project.title;
        image.loading = 'lazy';
        card.appendChild(image);
    }

    const title = document.createElement('h2');
    title.textContent = project.title;
    card.appendChild(title);

    const description = document.createElement('p');
    description.className = 'project-description';
    description.textContent = project.description;
    card.appendChild(description);

    const stack = document.createElement('p');
    stack.className = 'project-tech-stack';
    stack.textContent = project.tech_stack;
    card.appendChild(stack);

    const actions = document.createElement('div');
    actions.className = 'card-actions project-actions';
    const leftActions = document.createElement('div');
    leftActions.className = 'card-actions__left';
    const rightActions = document.createElement('div');
    rightActions.className = 'card-actions__right';

    if (isSuperuser) {
        const editButton = document.createElement('button');
        editButton.type = 'button';
        editButton.className = 'button';
        editButton.dataset.action = 'edit';
        editButton.dataset.projectId = project.id;
        editButton.textContent = 'Edit';
        leftActions.appendChild(editButton);

        const deleteButton = document.createElement('button');
        deleteButton.type = 'button';
        deleteButton.className = 'button button-danger';
        deleteButton.dataset.action = 'delete';
        deleteButton.dataset.projectId = project.id;
        deleteButton.dataset.projectTitle = project.title;
        deleteButton.textContent = 'Hapus';
        leftActions.appendChild(deleteButton);
    }

    const projectUrl = safeProjectUrl(project.project_url);
    if (projectUrl) {
        const link = document.createElement('a');
        link.className = 'button';
        link.href = projectUrl;
        link.target = '_blank';
        link.rel = 'noopener noreferrer';
        link.textContent = 'Lihat Project';
        leftActions.appendChild(link);
    }

    if (isAuthenticated) {
        const starButton = document.createElement('button');
        starButton.type = 'button';
        starButton.className = 'card-star-button';
        starButton.dataset.action = 'star';
        starButton.dataset.projectId = project.id;
        starButton.title = project.starred_by_names || '';
        starButton.setAttribute('aria-pressed', String(project.is_starred));
        starButton.setAttribute(
            'aria-label',
            `${project.is_starred ? 'Remove star' : 'Add star'} (${project.star_count} stars)`,
        );
        starButton.textContent = project.star_count;
        rightActions.appendChild(starButton);
    } else {
        const starCount = document.createElement('span');
        starCount.className = 'star-count';
        starCount.setAttribute('role', 'img');
        starCount.setAttribute('aria-label', `${project.star_count} stars`);
        starCount.textContent = project.star_count;
        rightActions.appendChild(starCount);
    }

    if (leftActions.childElementCount) actions.appendChild(leftActions);
    actions.appendChild(rightActions);
    card.appendChild(actions);
    return card;
}

function projectApiErrorMessage(data, status) {
    if (data?.detail) return data.detail;

    const messages = Object.values(data || {})
        .flatMap(errors => Array.isArray(errors) ? errors : [errors])
        .map(error => typeof error === 'string' ? error : error.message)
        .filter(Boolean);

    return messages.join(' ') || `Request failed (HTTP ${status}).`;
}

async function fetchProjects(title = '') {
    if (projectRequest) projectRequest.abort();
    projectRequest = new AbortController();
    showProjectState('loading');

    const params = new URLSearchParams();
    if (title) params.set('title', title);

    try {
        const response = await fetch(`${projectsEndpoint}?${params}`, {
            headers: { Accept: 'application/json' },
            signal: projectRequest.signal,
        });
        if (!response.ok) throw new Error('Project request failed');

        const projects = await response.json();
        projectGrid.replaceChildren();
        if (!projects.length) return showProjectState('empty');

        projects.forEach(project => {
            projectGrid.appendChild(makeProjectCard(project));
        });
        showProjectState('grid');
    } catch (error) {
        if (error.name !== 'AbortError') showProjectState('error');
    }
}

async function writeProject(url, method) {
    const response = await fetch(url, {
        method,
        headers: {
            Accept: 'application/json',
            'X-CSRFToken': getProjectCookie('csrftoken'),
        },
    });

    if (response.status === 204) return null;

    const data = await response.json().catch(() => ({}));
    if (!response.ok) {
        throw new Error(projectApiErrorMessage(data, response.status));
    }
    return data;
}

projectSearchForm.addEventListener('submit', event => {
    event.preventDefault();
    clearTimeout(projectSearchTimer);
    fetchProjects(projectSearch.value.trim());
});

projectSearch.addEventListener('input', () => {
    clearTimeout(projectSearchTimer);
    projectSearchTimer = setTimeout(() => {
        fetchProjects(projectSearch.value.trim());
    }, 300);
});

projectGrid.addEventListener('click', async event => {
    const button = event.target.closest('button[data-action]');
    if (!button || button.disabled) return;

    const action = button.dataset.action;
    const projectId = button.dataset.projectId;
    if (action === 'edit') {
        button.disabled = true;
        try {
            const response = await fetch(projectUrlFor(detailUrlTemplate, projectId), {
                headers: { Accept: 'application/json' },
            });
            const project = await response.json().catch(() => ({}));
            if (!response.ok) throw new Error(projectApiErrorMessage(project, response.status));

            editingProject = true;
            projectForm.action = projectUrlFor(detailUrlTemplate, projectId);
            projectForm.elements.namedItem('title').value = project.title;
            projectForm.elements.namedItem('description').value = project.description;
            projectForm.elements.namedItem('tech_stack').value = project.tech_stack;
            projectForm.elements.namedItem('project_url').value = project.project_url;
            projectForm.elements.namedItem('project_image_url').value = project.project_image_url;
            projectModalTitle.textContent = 'Edit Project';
            projectSubmitButton.textContent = 'Simpan Perubahan';
            projectForm.querySelectorAll('.form-error').forEach(node => {
                node.textContent = '';
            });
            projectModal.showPopover();
        } catch (error) {
            showToast('Gagal', error.message, 'error');
        } finally {
            button.disabled = false;
        }
        return;
    }
    if (
        action === 'delete'
        && !window.confirm('Yakin ingin menghapus project ini?')
    ) {
        return;
    }

    const endpointTemplate = action === 'star'
        ? starUrlTemplate
        : detailUrlTemplate;
    const method = action === 'star' ? 'POST' : 'DELETE';
    button.disabled = true;

    try {
        const data = await writeProject(projectUrlFor(endpointTemplate, projectId), method);
        showToast(
            'Berhasil',
            action === 'star'
                ? (data.is_starred
                    ? `Anda memberi "${data.title}" star.`
                    : 'Star dibatalkan.')
                : `"${button.dataset.projectTitle}" berhasil dihapus.`,
            'success',
        );
        await fetchProjects(projectSearch.value.trim());
    } catch (error) {
        showToast('Gagal', error.message, 'error');
        button.disabled = false;
    }
});

if (projectForm) {
    projectForm.addEventListener('submit', async event => {
        event.preventDefault();
        projectForm.querySelectorAll('.form-error').forEach(node => {
            node.textContent = '';
        });

        const formData = new FormData(projectForm);
        const fieldNames = [
            'title',
            'description',
            'tech_stack',
            'project_url',
            'project_image_url',
        ];
        const payload = Object.fromEntries(
            fieldNames.map(name => [name, formData.get(name)]),
        );
        const submitButton = projectForm.querySelector('button[type="submit"]');
        submitButton.disabled = true;

        const editing = editingProject;
        try {
            const response = await fetch(projectForm.action, {
                method: editing ? 'PATCH' : 'POST',
                headers: {
                    Accept: 'application/json',
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getProjectCookie('csrftoken'),
                },
                body: JSON.stringify(payload),
            });
            const data = await response.json().catch(() => ({}));

            if ((editing && response.ok) || response.status === 201) {
                projectForm.reset();
                projectModal.hidePopover();
                editingProject = false;
                projectForm.action = projectsEndpoint;
                projectModalTitle.textContent = 'Tambah Project Baru';
                projectSubmitButton.textContent = 'Tambah Project';
                showToast(
                    'Berhasil',
                    editing
                        ? `"${data.title}" berhasil diperbarui.`
                        : `"${data.title}" berhasil ditambahkan.`,
                    'success',
                );
                await fetchProjects(projectSearch.value.trim());
            } else if (response.status === 400) {
                Object.entries(data).forEach(([field, errors]) => {
                    const target = document.getElementById(`project-${field}-error`);
                    if (target) {
                        target.textContent = (Array.isArray(errors) ? errors : [errors])
                            .map(error => typeof error === 'string' ? error : error.message)
                            .filter(Boolean)
                            .join(' ');
                    }
                });
                showToast(
                    'Gagal',
                    projectApiErrorMessage(data, response.status),
                    'error',
                );
            } else {
                throw new Error(projectApiErrorMessage(data, response.status));
            }
        } catch (error) {
            showToast('Gagal', error.message || 'Terjadi kesalahan saat menambahkan project.', 'error');
        } finally {
            submitButton.disabled = false;
        }
    });
}

document.querySelector('[popovertarget="add-project-modal"]')?.addEventListener('click', () => {
    editingProject = false;
    projectForm.reset();
    projectForm.action = projectsEndpoint;
    projectModalTitle.textContent = 'Tambah Project Baru';
    projectSubmitButton.textContent = 'Tambah Project';
    projectForm.querySelectorAll('.form-error').forEach(node => {
        node.textContent = '';
    });
});

fetchProjects(projectSearch.value.trim());
