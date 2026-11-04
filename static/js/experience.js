const experiencePage = document.getElementById('experience');
const experiencesEndpoint = experiencePage.dataset.experiencesEndpoint;
const createExperienceEndpoint = experiencePage.dataset.createEndpoint;
const editUrlTemplate = experiencePage.dataset.editUrlTemplate;
const deleteUrlTemplate = experiencePage.dataset.deleteUrlTemplate;
const isSuperuser = experiencePage.dataset.superuser === 'true';
const isEditor = experiencePage.dataset.editor === 'true';

const loadingState = document.getElementById('loading');
const errorState = document.getElementById('error');
const emptyState = document.getElementById('empty');
const gridContainer = document.getElementById('grid');
const searchForm = document.getElementById('experience-search-form');
const searchInput = document.getElementById('search-input');
const experienceForm = document.getElementById('experience-form');

const searchDebounceDelay = 300;
let searchDebounceTimer;
let experiencesAbortController;

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

function createCsrfInput() {
    const input = document.createElement('input');
    input.type = 'hidden';
    input.name = 'csrfmiddlewaretoken';
    input.value = getExperienceCookie('csrftoken');
    return input;
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

    if (isSuperuser || isEditor) {
        const actions = document.createElement('div');
        actions.className = 'experience-actions';

        const editLink = document.createElement('a');
        editLink.href = experienceUrlFor(editUrlTemplate, item.pk);
        editLink.className = 'button';
        editLink.textContent = 'Edit';
        actions.appendChild(editLink);

        if (isSuperuser) {
            const deleteForm = document.createElement('form');
            deleteForm.method = 'post';
            deleteForm.action = experienceUrlFor(deleteUrlTemplate, item.pk);
            deleteForm.appendChild(createCsrfInput());

            const deleteButton = document.createElement('button');
            deleteButton.type = 'submit';
            deleteButton.className = 'button button-danger';
            deleteButton.textContent = 'Hapus';
            deleteButton.addEventListener('click', event => {
                if (!confirm('Yakin ingin menghapus experience ini?')) {
                    event.preventDefault();
                }
            });
            deleteForm.appendChild(deleteButton);
            actions.appendChild(deleteForm);
        }

        article.appendChild(actions);
    }

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
    const formData = new FormData(experienceForm);

    try {
        const response = await fetch(createExperienceEndpoint, {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': experienceForm.querySelector(
                    '[name=csrfmiddlewaretoken]',
                ).value,
            },
        });
        const data = await response.json();

        if (!response.ok) {
            showToast('Gagal', 'Gagal menambahkan experience.', 'error');
            return;
        }

        showToast('Berhasil', data.message, 'success');
        experienceForm.reset();
        document.getElementById('add-experience-modal').hidePopover();
        fetchExperiences(searchInput.value.trim());
    } catch (_) {
        showToast('Error', 'Terjadi kesalahan saat menambahkan experience.', 'error');
    }
}

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

fetchExperiences(searchInput.value.trim());
