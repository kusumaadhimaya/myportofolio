const categoriesContainer = document.getElementById('skill-categories');
const skillsEndpoint = categoriesContainer.dataset.skillsEndpoint;
const starUrlTemplate = categoriesContainer.dataset.starUrlTemplate;
const deleteUrlTemplate = categoriesContainer.dataset.deleteUrlTemplate;
const updateUrlTemplate = categoriesContainer.dataset.updateUrlTemplate;
const isAuthenticated = categoriesContainer.dataset.authenticated === 'true';
const isSuperuser = categoriesContainer.dataset.superuser === 'true';

const loadingState = document.getElementById('loading');
const errorState = document.getElementById('error');
const emptyState = document.getElementById('empty');
const searchForm = document.getElementById('skill-search-form');
const searchInput = document.getElementById('search-input');
const skillForm = document.getElementById('skill-form');
const skillModal = document.getElementById('add-skill-modal');
const skillModalTitle = document.getElementById('add-skill-modal-title');
const skillSubmitButton = document.getElementById('skill-submit-button');
let editingSkill = false;

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

    const actions = document.createElement('div');
    actions.className = 'card-actions';

    const leftActions = document.createElement('div');
    leftActions.className = 'card-actions__left';
    const rightActions = document.createElement('div');
    rightActions.className = 'card-actions__right';

    if (isAuthenticated) {
        const starForm = document.createElement('form');
        starForm.method = 'POST';
        starForm.action = skillUrlFor(starUrlTemplate, skill.pk);
        starForm.dataset.action = 'star';
        starForm.appendChild(createCsrfInput());

        const starButton = document.createElement('button');
        starButton.type = 'submit';
        starButton.className = 'card-star-button';
        starButton.setAttribute('aria-pressed', String(fields.is_starred));
        starButton.setAttribute(
            'aria-label',
            `${fields.is_starred ? 'Remove star' : 'Add star'} (${fields.star_count} stars)`,
        );
        starButton.textContent = fields.star_count;
        starForm.appendChild(starButton);
        rightActions.appendChild(starForm);
    } else {
        const starCount = document.createElement('span');
        starCount.className = 'star-count';
        starCount.setAttribute('role', 'img');
        starCount.setAttribute('aria-label', `${fields.star_count} stars`);
        starCount.textContent = fields.star_count;
        rightActions.appendChild(starCount);
    }

    if (isSuperuser) {
        const editButton = document.createElement('button');
        editButton.type = 'button';
        editButton.className = 'button';
        editButton.textContent = 'Edit';
        editButton.addEventListener('click', () => openSkillEditor(skill));
        leftActions.appendChild(editButton);

        const deleteForm = document.createElement('form');
        deleteForm.method = 'POST';
        deleteForm.action = skillUrlFor(deleteUrlTemplate, skill.pk);
        deleteForm.dataset.action = 'delete';
        deleteForm.dataset.skillTitle = fields.title;
        deleteForm.appendChild(createCsrfInput());

        const deleteButton = document.createElement('button');
        deleteButton.type = 'submit';
        deleteButton.className = 'button button-danger';
        deleteButton.textContent = 'Hapus';
        deleteForm.appendChild(deleteButton);
        leftActions.appendChild(deleteForm);
    }

    if (leftActions.childElementCount) actions.appendChild(leftActions);
    actions.appendChild(rightActions);
    article.appendChild(actions);
    return article;
}

categoriesContainer.addEventListener('submit', async event => {
    const form = event.target.closest('form[data-action]');
    if (!form) return;
    event.preventDefault();

    if (form.dataset.action === 'delete') {
        const deleteButton = form.querySelector('button[type="submit"]');
        window.openDeleteConfirmation({
            itemType: 'skill',
            itemName: form.dataset.skillTitle,
            onConfirm: async () => {
                deleteButton.disabled = true;
                try {
                    const response = await fetch(form.action, {
                        method: 'POST',
                        body: new FormData(form),
                        headers: {
                            Accept: 'application/json',
                            'X-CSRFToken': getCookie('csrftoken'),
                            'X-Requested-With': 'XMLHttpRequest',
                        },
                    });
                    const data = await response.json().catch(() => ({}));
                    if (!response.ok) {
                        throw new Error(data.message || 'Permintaan skill gagal.');
                    }

                    showToast('Berhasil', data.message, 'success');
                    await fetchSkills(searchInput.value.trim());
                    return true;
                } catch (error) {
                    showToast('Gagal', error.message, 'error');
                    deleteButton.disabled = false;
                    return false;
                }
            },
        });
        return;
    }

    const button = form.querySelector('button[type="submit"]');
    button.disabled = true;
    try {
        const response = await fetch(form.action, {
            method: 'POST',
            body: new FormData(form),
            headers: {
                Accept: 'application/json',
                'X-CSRFToken': getCookie('csrftoken'),
                'X-Requested-With': 'XMLHttpRequest',
            },
        });
        const data = await response.json().catch(() => ({}));
        if (!response.ok) throw new Error(data.message || 'Permintaan skill gagal.');

        showToast('Berhasil', data.message, 'success');
        await fetchSkills(searchInput.value.trim());
    } catch (error) {
        showToast('Gagal', error.message, 'error');
        button.disabled = false;
    }
});

function clearSkillErrors() {
    skillForm.querySelectorAll('.form-error').forEach(node => {
        node.textContent = '';
    });
}

function openSkillEditor(skill) {
    editingSkill = true;
    skillForm.action = skillUrlFor(updateUrlTemplate, skill.pk);
    skillModalTitle.textContent = 'Edit Skill';
    skillSubmitButton.textContent = 'Simpan Perubahan';
    skillForm.elements.namedItem('title').value = skill.fields.title;
    skillForm.elements.namedItem('description').value = skill.fields.description;
    skillForm.elements.namedItem('category').value = skill.fields.category === 'Uncategorized'
        ? ''
        : skill.fields.category;
    clearSkillErrors();
    skillModal.showPopover();
}

function openSkillCreator() {
    editingSkill = false;
    skillForm.reset();
    skillForm.action = categoriesContainer.dataset.createEndpoint;
    skillModalTitle.textContent = 'Tambah Skill Baru';
    skillSubmitButton.textContent = 'Tambah Skill';
    clearSkillErrors();
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
            const editing = editingSkill;
            const response = await fetch(skillForm.action, {
                method: 'POST',
                body: formData,
                headers: { 'X-CSRFToken': getCookie('csrftoken') },
            });
            const data = await response.json();

            if (response.ok) {
                showToast('Berhasil', data.message, 'success');
                skillForm.reset();
                skillModal.hidePopover();
                openSkillCreator();
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
                    editing ? 'Gagal memperbarui skill' : 'Gagal menambahkan skill',
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

document.querySelector('[popovertarget="add-skill-modal"]')?.addEventListener('click', openSkillCreator);

fetchSkills(searchInput.value.trim());
