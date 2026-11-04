const categoriesContainer = document.getElementById('skill-categories');
const skillsEndpoint = categoriesContainer.dataset.skillsEndpoint;
const starUrlTemplate = categoriesContainer.dataset.starUrlTemplate;
const deleteUrlTemplate = categoriesContainer.dataset.deleteUrlTemplate;
const isAuthenticated = categoriesContainer.dataset.authenticated === 'true';
const isSuperuser = categoriesContainer.dataset.superuser === 'true';

const loadingState = document.getElementById('loading');
const errorState = document.getElementById('error');
const emptyState = document.getElementById('empty');
const searchForm = document.getElementById('skill-search-form');
const searchInput = document.getElementById('search-input');
const skillForm = document.getElementById('skill-form');

const searchDebounceDelay = 300;
let searchDebounceTimer;

function getCookie(name) {
    for (const cookie of document.cookie.split(';')) {
        const [key, ...value] = cookie.trim().split('=');
        if (key === name) return decodeURIComponent(value.join('='));
    }
    return null;
}

function displayPageSection({
    showLoading = false,
    showError = false,
    showEmpty = false,
    showSkills = false,
}) {
    loadingState.classList.toggle('hide', !showLoading);
    errorState.classList.toggle('hide', !showError);
    emptyState.classList.toggle('hide', !showEmpty);
    categoriesContainer.classList.toggle('hide', !showSkills);
}

function createCsrfInput() {
    const input = document.createElement('input');
    input.type = 'hidden';
    input.name = 'csrfmiddlewaretoken';
    input.value = getCookie('csrftoken') || '';
    return input;
}

function skillUrlFor(template, skillId) {
    return template.replace(
        '00000000-0000-0000-0000-000000000000',
        encodeURIComponent(skillId),
    );
}

function buildSkillCardElement(skill) {
    const fields = skill.fields;
    const article = document.createElement('article');
    article.className = 'skill-card';

    const title = document.createElement('h3');
    title.textContent = fields.title;
    article.appendChild(title);

    const description = document.createElement('p');
    description.className = 'skill-desc';
    description.textContent = fields.description;
    article.appendChild(description);

    const starCount = document.createElement('p');
    starCount.textContent = `⭐ ${fields.star_count}`;
    article.appendChild(starCount);

    if (isAuthenticated) {
        const actions = document.createElement('div');
        actions.className = 'skill-actions';

        const starForm = document.createElement('form');
        starForm.method = 'POST';
        starForm.action = skillUrlFor(starUrlTemplate, skill.pk);
        starForm.appendChild(createCsrfInput());

        const starButton = document.createElement('button');
        starButton.type = 'submit';
        starButton.className = 'button';
        starButton.textContent = fields.is_starred ? 'Unstar' : 'Star';
        starForm.appendChild(starButton);
        actions.appendChild(starForm);

        if (isSuperuser) {
            const deleteForm = document.createElement('form');
            deleteForm.method = 'POST';
            deleteForm.action = skillUrlFor(deleteUrlTemplate, skill.pk);
            deleteForm.appendChild(createCsrfInput());

            const deleteButton = document.createElement('button');
            deleteButton.type = 'submit';
            deleteButton.className = 'button button-danger';
            deleteButton.textContent = 'Hapus Skill';
            deleteButton.addEventListener('click', event => {
                if (!confirm('Apakah Anda yakin ingin menghapus skill ini?')) {
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

function renderSkills(skills) {
    categoriesContainer.replaceChildren();
    const groupedSkills = new Map();

    skills.forEach(skill => {
        const category = skill.fields.category;
        if (!groupedSkills.has(category)) groupedSkills.set(category, []);
        groupedSkills.get(category).push(skill);
    });

    groupedSkills.forEach((skillsInCategory, category) => {
        const categorySection = document.createElement('section');
        categorySection.className = 'skill-category';

        const categoryTitle = document.createElement('h2');
        categoryTitle.className = 'skill-category-title';
        categoryTitle.textContent = category;

        const skillsGrid = document.createElement('div');
        skillsGrid.className = 'skills-grid';
        skillsInCategory.forEach(skill => {
            skillsGrid.appendChild(buildSkillCardElement(skill));
        });

        categorySection.append(categoryTitle, skillsGrid);
        categoriesContainer.appendChild(categorySection);
    });
}

async function fetchSkills(title = '') {
    displayPageSection({ showLoading: true });
    const params = new URLSearchParams();
    if (title) params.set('title', title);

    try {
        const response = await fetch(`${skillsEndpoint}?${params}`);
        if (!response.ok) throw new Error('Gagal mengambil data skill.');

        const skills = await response.json();
        if (!skills.length) return displayPageSection({ showEmpty: true });

        renderSkills(skills);
        displayPageSection({ showSkills: true });
    } catch (_) {
        displayPageSection({ showError: true });
    }
}

searchForm.addEventListener('submit', event => {
    event.preventDefault();
});

searchInput.addEventListener('input', () => {
    clearTimeout(searchDebounceTimer);
    searchDebounceTimer = setTimeout(() => {
        fetchSkills(searchInput.value.trim());
    }, searchDebounceDelay);
});

if (skillForm) {
    skillForm.addEventListener('submit', async event => {
        event.preventDefault();
        const formData = new FormData(skillForm);

        try {
            const response = await fetch(skillForm.action, {
                method: 'POST',
                body: formData,
                headers: { 'X-CSRFToken': getCookie('csrftoken') },
            });
            const data = await response.json();

            if (response.status === 201) {
                showToast('Berhasil', data.message, 'success');
                skillForm.reset();
                document.getElementById('add-skill-modal').hidePopover();
                fetchSkills(searchInput.value.trim());
                return;
            }

            if (response.status === 403) {
                showToast('Akses ditolak', data.message, 'error');
                return;
            }

            if (response.status === 400 && data.errors) {
                Object.entries(data.errors).forEach(([fieldName, errors]) => {
                    const errorElement = document.getElementById(`${fieldName}-error`);
                    if (errorElement) {
                        errorElement.textContent = errors
                            .map(error => error.message)
                            .join(' ');
                    }
                });
                showToast(
                    'Gagal menambahkan skill',
                    'Periksa kembali data yang dimasukkan.',
                    'error',
                );
                return;
            }

            showToast('Gagal', 'Terjadi kesalahan saat menambahkan skill.', 'error');
        } catch (_) {
            showToast('Gagal', 'Tidak dapat terhubung ke server.', 'error');
        }
    });
}

fetchSkills(searchInput.value.trim());
