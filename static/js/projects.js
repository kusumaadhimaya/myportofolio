const projectPage = document.getElementById('projects');
const projectsEndpoint = projectPage.dataset.projectsEndpoint;
const starUrlTemplate = projectPage.dataset.starUrlTemplate;
const deleteUrlTemplate = projectPage.dataset.deleteUrlTemplate;
const isAuthenticated = projectPage.dataset.authenticated === 'true';
const isSuperuser = projectPage.dataset.superuser === 'true';

const projectGrid = document.getElementById('project-grid');
const projectLoading = document.getElementById('project-loading');
const projectError = document.getElementById('project-error');
const projectEmpty = document.getElementById('project-empty');
const projectSearch = document.getElementById('project-search-input');
const projectForm = document.getElementById('project-form');

let projectSearchTimer;
let projectRequest;

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

function projectCsrfInput() {
    const input = document.createElement('input');
    input.type = 'hidden';
    input.name = 'csrfmiddlewaretoken';
    input.value = getProjectCookie('csrftoken');
    return input;
}

function projectUrlFor(template, projectId) {
    return template.replace(
        '00000000-0000-0000-0000-000000000000',
        encodeURIComponent(projectId),
    );
}

function makeProjectCard(item) {
    const project = item.fields;
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
    actions.className = 'project-actions';
    const projectUrl = safeProjectUrl(project.project_url);
    if (projectUrl) {
        const link = document.createElement('a');
        link.className = 'button';
        link.href = projectUrl;
        link.target = '_blank';
        link.rel = 'noopener noreferrer';
        link.textContent = 'Lihat Project';
        actions.appendChild(link);
    }

    const starCount = document.createElement('span');
    starCount.className = 'project-star-count';
    starCount.textContent = `⭐ ${project.star_count}`;
    actions.appendChild(starCount);

    if (isAuthenticated) {
        const starForm = document.createElement('form');
        starForm.method = 'post';
        starForm.action = projectUrlFor(starUrlTemplate, item.pk);
        starForm.appendChild(projectCsrfInput());
        const starButton = document.createElement('button');
        starButton.type = 'submit';
        starButton.className = 'button button-secondary';
        starButton.textContent = project.is_starred ? 'Unstar' : 'Star';
        starForm.appendChild(starButton);
        actions.appendChild(starForm);
    }

    if (isSuperuser) {
        const deleteForm = document.createElement('form');
        deleteForm.method = 'post';
        deleteForm.action = projectUrlFor(deleteUrlTemplate, item.pk);
        deleteForm.appendChild(projectCsrfInput());
        const deleteButton = document.createElement('button');
        deleteButton.type = 'submit';
        deleteButton.className = 'button button-danger';
        deleteButton.textContent = 'Hapus';
        deleteButton.addEventListener('click', event => {
            if (!confirm(`Yakin ingin menghapus project “${project.title}”?`)) {
                event.preventDefault();
            }
        });
        deleteForm.appendChild(deleteButton);
        actions.appendChild(deleteForm);
    }

    card.appendChild(actions);
    return card;
}

async function fetchProjects(title = '') {
    if (projectRequest) projectRequest.abort();
    projectRequest = new AbortController();
    showProjectState('loading');

    const params = new URLSearchParams();
    if (title) params.set('title', title);

    try {
        const response = await fetch(`${projectsEndpoint}?${params}`, {
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

document.getElementById('project-search-form').addEventListener('submit', event => {
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

if (projectForm) {
    projectForm.addEventListener('submit', async event => {
        event.preventDefault();
        projectForm.querySelectorAll('.form-error').forEach(node => {
            node.textContent = '';
        });

        try {
            const response = await fetch(projectForm.action, {
                method: 'POST',
                body: new FormData(projectForm),
                headers: { 'X-CSRFToken': getProjectCookie('csrftoken') },
            });
            const data = await response.json();

            if (response.status === 201) {
                projectForm.reset();
                document.getElementById('add-project-modal').hidePopover();
                showToast('Berhasil', data.message, 'success');
                fetchProjects(projectSearch.value.trim());
            } else if (response.status === 400 && data.errors) {
                Object.entries(data.errors).forEach(([field, errors]) => {
                    const target = document.getElementById(`project-${field}-error`);
                    if (target) {
                        target.textContent = errors.map(error => error.message).join(' ');
                    }
                });
                showToast('Gagal', 'Periksa kembali data project.', 'error');
            } else {
                showToast('Gagal', data.message || 'Project tidak dapat ditambahkan.', 'error');
            }
        } catch (_) {
            showToast('Gagal', 'Terjadi kesalahan saat menambahkan project.', 'error');
        }
    });
}

fetchProjects(projectSearch.value.trim());
