const experiencePage = document.getElementById('experience');
const experiencesEndpoint = experiencePage.dataset.experiencesEndpoint;
const createExperienceEndpoint = experiencePage.dataset.createEndpoint;
const detailUrlTemplate = experiencePage.dataset.detailUrlTemplate;
const starUrlTemplate = experiencePage.dataset.starUrlTemplate;
const isAuthenticated = experiencePage.dataset.authenticated === 'true';
const isSuperuser = experiencePage.dataset.superuser === 'true';
const isEditor = experiencePage.dataset.editor === 'true';

const loadingState = document.getElementById('loading');
const errorState = document.getElementById('error');
const emptyState = document.getElementById('empty');
const gridContainer = document.getElementById('grid');
const searchForm = document.getElementById('experience-search-form');
const searchInput = document.getElementById('search-input');
const experienceForm = document.getElementById('experience-form');
const experienceModal = document.getElementById('add-experience-modal');
const experienceModalTitle = document.getElementById('experience-modal-title');
const experienceSubmitButton = document.getElementById('experience-submit-button');

const searchDebounceDelay = 300;
let searchDebounceTimer;
let experiencesAbortController;
let editingExperience = false;

function displayPageSection({
    showLoading = false,
    showError = false,
    showEmpty = false,
    showGrid = false,
}) {
    loadingState.classList.toggle('hide', !showLoading);
    errorState.classList.toggle('hide', !showError);
    emptyState.classList.toggle('hide', !showEmpty);
    gridContainer.classList.toggle('hide', !showGrid);
}

function getExperienceCookie(name) {
    for (const entry of document.cookie.split(';')) {
        const [key, ...value] = entry.trim().split('=');
        if (key === name) return decodeURIComponent(value.join('='));
    }
    return '';
}

function safeExperienceImageUrl(value) {
    if (!value) return '';
    try {
        const url = new URL(value, window.location.origin);
        return ['http:', 'https:'].includes(url.protocol) ? url.href : '';
    } catch (_) {
        return '';
    }
}

function experienceUrlFor(template, experienceId) {
    return template.replace(
        '00000000-0000-0000-0000-000000000000',
        encodeURIComponent(experienceId),
    );
}

function createDateLine(label, value) {
    const line = document.createElement('p');
    line.className = 'experience-date';
    const strong = document.createElement('strong');
    strong.textContent = `${label}: `;
    line.append(strong, document.createTextNode(value));
    return line;
}

function buildExperienceCardElement(item) {
    const experience = item.fields;
    const article = document.createElement('article');
    article.className = 'experience-card';

    const category = document.createElement('span');
    category.className = 'experience-category';
    category.textContent = experience.category;
    article.appendChild(category);

    const title = document.createElement('h2');
    title.textContent = experience.title;
    article.appendChild(title);

    const description = document.createElement('p');
    description.className = 'experience-description';
    description.textContent = experience.description;
    article.appendChild(description);

    const imageUrl = safeExperienceImageUrl(experience.thumbnail);
    if (imageUrl) {
        const image = document.createElement('img');
        image.src = imageUrl;
        image.alt = experience.title;
        image.className = 'experience-thumbnail';
        image.loading = 'lazy';
        article.appendChild(image);
    }

    const dates = document.createElement('div');
    dates.className = 'experience-dates';
    dates.appendChild(createDateLine('Mulai', experience.started_at));
    if (experience.is_ongoing) {
        const ongoing = document.createElement('p');
        ongoing.className = 'experience-status';
        ongoing.textContent = 'Sedang berlangsung';
        dates.appendChild(ongoing);
    } else {
        dates.appendChild(createDateLine('Selesai', experience.ended_at));
    }
    article.appendChild(dates);

    const actions = document.createElement('div');
    actions.className = 'experience-actions card-actions';
    const leftActions = document.createElement('div');
    leftActions.className = 'card-actions__left';
    const rightActions = document.createElement('div');
    rightActions.className = 'card-actions__right';

    if (isSuperuser || isEditor) {
            const editButton = document.createElement('button');
            editButton.type = 'button';
            editButton.className = 'button';
            editButton.dataset.action = 'edit';
            editButton.dataset.experienceId = item.pk;
            editButton.textContent = 'Edit';
            leftActions.appendChild(editButton);

        if (isSuperuser) {
            const deleteButton = document.createElement('button');
                deleteButton.type = 'button';
            deleteButton.className = 'button button-danger';
                deleteButton.dataset.action = 'delete';
                deleteButton.dataset.experienceId = item.pk;
            deleteButton.dataset.experienceTitle = experience.title;
            deleteButton.textContent = 'Hapus';
                leftActions.appendChild(deleteButton);
        }
    }

    if (isAuthenticated) {
        const starButton = document.createElement('button');
        starButton.type = 'button';
        starButton.className = 'card-star-button';
        starButton.dataset.action = 'star';
        starButton.dataset.experienceId = item.pk;
        starButton.setAttribute('aria-pressed', String(experience.is_starred));
        starButton.setAttribute('aria-label', `${experience.star_count} stars`);
        starButton.textContent = experience.star_count;
        rightActions.appendChild(starButton);
    } else {
        const starCount = document.createElement('span');
        starCount.className = 'star-count';
        starCount.setAttribute('aria-label', `${experience.star_count} stars`);
        starCount.textContent = experience.star_count;
        rightActions.appendChild(starCount);
    }

    if (leftActions.childElementCount) actions.appendChild(leftActions);
    actions.appendChild(rightActions);
    article.appendChild(actions);

    return article;
}

async function fetchExperiences(title = '') {
    if (experiencesAbortController) experiencesAbortController.abort();
    experiencesAbortController = new AbortController();
    displayPageSection({ showLoading: true });

    const params = new URLSearchParams();
    if (title) params.set('title', title);

    try {
        const response = await fetch(`${experiencesEndpoint}?${params}`, {
            signal: experiencesAbortController.signal,
        });
        if (!response.ok) throw new Error('Gagal mengambil data experience.');

        const experiences = await response.json();
        gridContainer.replaceChildren();
        if (!experiences.length) return displayPageSection({ showEmpty: true });

        experiences.forEach(item => {
            gridContainer.appendChild(buildExperienceCardElement(item));
        });
        displayPageSection({ showGrid: true });
    } catch (error) {
        if (error.name !== 'AbortError') displayPageSection({ showError: true });
    }
}

async function submitExperienceForm(event) {
    event.preventDefault();
    clearExperienceErrors();
    const formData = new FormData(experienceForm);
    const fields = ['title', 'description', 'category', 'thumbnail', 'started_at', 'ended_at'];
    const submitButton = experienceForm.querySelector('button[type="submit"]');
    submitButton.disabled = true;

    try {
        const headers = {
            Accept: 'application/json',
            'X-CSRFToken': experienceForm.querySelector(
                '[name=csrfmiddlewaretoken]',
            ).value,
        };
        const request = {
            method: editingExperience ? 'PATCH' : 'POST',
            headers,
        };

        if (editingExperience) {
            headers['Content-Type'] = 'application/json';
            request.body = JSON.stringify(Object.fromEntries(
                fields.map(name => [
                    name,
                    name === 'ended_at' ? (formData.get(name) || null) : formData.get(name),
                ]),
            ));
        } else {
            request.body = formData;
        }

        const response = await fetch(experienceForm.action, request);
        const data = await response.json().catch(() => ({}));

        if (!response.ok) {
            const errors = data.errors || data;
            Object.entries(errors).forEach(([fieldName, messages]) => {
                const errorElement = document.getElementById(`experience-${fieldName}-error`);
                if (errorElement && Array.isArray(messages)) {
                    errorElement.textContent = messages
                        .map(error => typeof error === 'string' ? error : error.message)
                        .filter(Boolean)
                        .join(' ');
                }
            });
            const message = data.message || data.detail || 'Periksa kembali data experience.';
            showToast('Gagal', message, 'error');
            return;
        }

        const message = editingExperience
            ? `"${data.title}" berhasil diperbarui.`
            : data.message;
        showToast('Berhasil', message, 'success');
        experienceForm.reset();
        experienceModal.hidePopover();
        setExperienceCreateMode();
        await fetchExperiences(searchInput.value.trim());
    } catch (_) {
        showToast('Error', 'Terjadi kesalahan saat menyimpan experience.', 'error');
    } finally {
        submitButton.disabled = false;
    }
}

function setExperienceCreateMode() {
    editingExperience = false;
    experienceForm.action = createExperienceEndpoint;
    experienceModalTitle.textContent = 'Tambah Experience Baru';
    experienceSubmitButton.textContent = 'Tambah Experience';
    clearExperienceErrors();
}

function clearExperienceErrors() {
    experienceForm.querySelectorAll('.form-error').forEach(element => {
        element.textContent = '';
    });
}

async function sendExperienceAction(url, method) {
    const response = await fetch(url, {
        method,
        headers: {
            Accept: 'application/json',
            'X-CSRFToken': getExperienceCookie('csrftoken'),
            'X-Requested-With': 'XMLHttpRequest',
        },
    });
    const data = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(data.detail || data.message || 'Permintaan gagal.');
    return data;
}

async function openExperienceEditor(experienceId, button) {
    button.disabled = true;
    try {
        const response = await fetch(experienceUrlFor(detailUrlTemplate, experienceId), {
            headers: { Accept: 'application/json' },
        });
        const experience = await response.json();
        if (!response.ok) throw new Error(experience.detail || 'Gagal memuat experience.');

        editingExperience = true;
        experienceForm.action = experienceUrlFor(detailUrlTemplate, experienceId);
        clearExperienceErrors();
        Object.entries(experience).forEach(([name, value]) => {
            const field = experienceForm.elements.namedItem(name);
            if (field && name !== 'id' && name !== 'is_ongoing') field.value = value || '';
        });
        experienceModalTitle.textContent = 'Edit Experience';
        experienceSubmitButton.textContent = 'Simpan Perubahan';
        experienceModal.showPopover();
    } catch (error) {
        showToast('Gagal', error.message, 'error');
    } finally {
        button.disabled = false;
    }
}

gridContainer.addEventListener('click', async event => {
    const button = event.target.closest('button[data-action]');
    if (!button || button.disabled) return;

    const { action, experienceId } = button.dataset;
    if (action === 'edit') {
        await openExperienceEditor(experienceId, button);
        return;
    }
    if (action === 'delete' && !window.confirm('Yakin ingin menghapus experience ini?')) return;

    button.disabled = true;
    try {
        const endpoint = action === 'star'
            ? experienceUrlFor(starUrlTemplate, experienceId)
            : experienceUrlFor(detailUrlTemplate, experienceId);
        const data = await sendExperienceAction(endpoint, action === 'star' ? 'POST' : 'DELETE');
        const message = data.message || `"${button.dataset.experienceTitle}" berhasil dihapus.`;
        showToast('Berhasil', message, 'success');
        await fetchExperiences(searchInput.value.trim());
    } catch (error) {
        showToast('Gagal', error.message, 'error');
        button.disabled = false;
    }
});

searchInput.addEventListener('input', () => {
    clearTimeout(searchDebounceTimer);
    searchDebounceTimer = setTimeout(() => {
        fetchExperiences(searchInput.value.trim());
    }, searchDebounceDelay);
});

searchForm.addEventListener('submit', event => {
    event.preventDefault();
    clearTimeout(searchDebounceTimer);
    fetchExperiences(searchInput.value.trim());
});

if (experienceForm) {
    experienceForm.addEventListener('submit', submitExperienceForm);
}

document.querySelector('[popovertarget="add-experience-modal"]')?.addEventListener(
    'click',
    setExperienceCreateMode,
);

fetchExperiences(searchInput.value.trim());
