const categoriesContainer = document.getElementById('skill-categories');
const skillsEndpoint = categoriesContainer.dataset.skillsEndpoint;
const detailUrlTemplate = categoriesContainer.dataset.detailUrlTemplate;
const starUrlTemplate = categoriesContainer.dataset.starUrlTemplate;
const isAuthenticated = categoriesContainer.dataset.authenticated === 'true';
const isSuperuser = categoriesContainer.dataset.superuser === 'true';
const isEditor = categoriesContainer.dataset.editor === 'true';
const canEditSkills = isSuperuser || isEditor;

const loadingState = document.getElementById('loading');
const errorState = document.getElementById('error');
const emptyState = document.getElementById('empty');
const searchForm = document.getElementById('skill-search-form');
const searchInput = document.getElementById('search-input');
const skillForm = document.getElementById('skill-form');
const skillModal = document.getElementById('add-skill-modal');
const skillModalTitle = document.getElementById('add-skill-modal-title');
const skillSubmitButton = document.getElementById('skill-submit-button');
const searchDebounceDelay = 300;
let searchDebounceTimer;
let editingSkill = false;

function getCookie(name) {
    for (const cookie of document.cookie.split(';')) {
        const [key, ...value] = cookie.trim().split('=');
        if (key === name) return decodeURIComponent(value.join('='));
    }
    return '';
}

function skillUrlFor(template, skillId) {
    return template.replace(
        '00000000-0000-0000-0000-000000000000',
        encodeURIComponent(skillId),
    );
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

function buildSkillCardElement(skill) {
    const article = document.createElement('article');
    article.className = 'skill-card';

    const title = document.createElement('h3');
    title.textContent = skill.title;
    article.appendChild(title);

    const description = document.createElement('p');
    description.className = 'skill-desc';
    description.textContent = skill.description;
    article.appendChild(description);

    const actions = document.createElement('div');
    actions.className = 'card-actions';
    const leftActions = document.createElement('div');
    leftActions.className = 'card-actions__left';
    const rightActions = document.createElement('div');
    rightActions.className = 'card-actions__right';

    if (canEditSkills) {
        const editButton = document.createElement('button');
        editButton.type = 'button';
        editButton.className = 'button';
        editButton.dataset.action = 'edit';
        editButton.dataset.skillId = skill.id;
        editButton.textContent = 'Edit';
        leftActions.appendChild(editButton);
    }

    if (isSuperuser) {
        const deleteButton = document.createElement('button');
        deleteButton.type = 'button';
        deleteButton.className = 'button button-danger';
        deleteButton.dataset.action = 'delete';
        deleteButton.dataset.skillId = skill.id;
        deleteButton.dataset.skillTitle = skill.title;
        deleteButton.textContent = 'Hapus';
        leftActions.appendChild(deleteButton);
    }

    if (isAuthenticated) {
        const starButton = document.createElement('button');
        starButton.type = 'button';
        starButton.className = 'card-star-button';
        starButton.dataset.action = 'star';
        starButton.dataset.skillId = skill.id;
        starButton.setAttribute('aria-pressed', String(skill.is_starred));
        starButton.setAttribute(
            'aria-label',
            `${skill.is_starred ? 'Remove star' : 'Add star'} (${skill.star_count} stars)`,
        );
        starButton.textContent = skill.star_count;
        rightActions.appendChild(starButton);
    } else {
        const starCount = document.createElement('span');
        starCount.className = 'star-count';
        starCount.setAttribute('role', 'img');
        starCount.setAttribute('aria-label', `${skill.star_count} stars`);
        starCount.textContent = skill.star_count;
        rightActions.appendChild(starCount);
    }

    if (leftActions.childElementCount) actions.appendChild(leftActions);
    actions.appendChild(rightActions);
    article.appendChild(actions);
    return article;
}

function renderSkills(skills) {
    categoriesContainer.replaceChildren();
    const groupedSkills = new Map();

    skills.forEach(skill => {
        const category = skill.category || 'Uncategorized';
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

async function sendSkillRequest(url, method, body) {
    const headers = {
        Accept: 'application/json',
        'X-CSRFToken': getCookie('csrftoken'),
    };
    const options = { method, headers };
    if (body !== undefined) {
        headers['Content-Type'] = 'application/json';
        options.body = JSON.stringify(body);
    }

    const response = await fetch(url, options);
    const data = await response.json().catch(() => ({}));
    if (!response.ok) {
        const detail = data.detail || Object.values(data).flat().join(' ');
        const error = new Error(detail || 'Permintaan skill gagal.');
        error.data = data;
        throw error;
    }
    return data;
}

function clearSkillErrors() {
    skillForm.querySelectorAll('.form-error').forEach(node => {
        node.textContent = '';
    });
}

function showSkillValidationErrors(errors) {
    Object.entries(errors).forEach(([fieldName, messages]) => {
        const errorElement = document.getElementById(`${fieldName}-error`);
        if (!errorElement || !Array.isArray(messages)) return;
        errorElement.textContent = messages.join(' ');
    });
}

function openSkillEditor(skill) {
    editingSkill = true;
    skillForm.action = skillUrlFor(detailUrlTemplate, skill.id);
    skillModalTitle.textContent = 'Edit Skill';
    skillSubmitButton.textContent = 'Simpan Perubahan';
    skillForm.elements.namedItem('title').value = skill.title;
    skillForm.elements.namedItem('description').value = skill.description;
    skillForm.elements.namedItem('category').value = skill.category || '';
    clearSkillErrors();
    skillModal.showPopover();
}

function openSkillCreator() {
    editingSkill = false;
    skillForm.reset();
    skillForm.action = skillsEndpoint;
    skillModalTitle.textContent = 'Tambah Skill Baru';
    skillSubmitButton.textContent = 'Tambah Skill';
    clearSkillErrors();
}

categoriesContainer.addEventListener('click', async event => {
    const button = event.target.closest('button[data-action]');
    if (!button || button.disabled) return;

    const { action, skillId } = button.dataset;
    if (action === 'edit') {
        try {
            const skill = await sendSkillRequest(
                skillUrlFor(detailUrlTemplate, skillId),
                'GET',
            );
            openSkillEditor(skill);
        } catch (error) {
            showToast('Gagal', error.message, 'error');
        }
        return;
    }

    if (action === 'delete') {
        window.openDeleteConfirmation({
            itemType: 'skill',
            itemName: button.dataset.skillTitle,
            onConfirm: async () => {
                button.disabled = true;
                try {
                    await sendSkillRequest(
                        skillUrlFor(detailUrlTemplate, skillId),
                        'DELETE',
                    );
                    showToast(
                        'Berhasil',
                        `"${button.dataset.skillTitle}" berhasil dihapus.`,
                        'success',
                    );
                    await fetchSkills(searchInput.value.trim());
                    return true;
                } catch (error) {
                    showToast('Gagal', error.message, 'error');
                    button.disabled = false;
                    return false;
                }
            },
        });
        return;
    }

    if (action === 'star') {
        button.disabled = true;
        try {
            const skill = await sendSkillRequest(
                skillUrlFor(starUrlTemplate, skillId),
                'POST',
            );
            showToast(
                'Berhasil',
                skill.is_starred
                    ? `Anda memberi "${skill.title}" star.`
                    : 'Star dibatalkan.',
                'success',
            );
            await fetchSkills(searchInput.value.trim());
        } catch (error) {
            showToast('Gagal', error.message, 'error');
            button.disabled = false;
        }
    }
});

searchForm.addEventListener('submit', event => {
    event.preventDefault();
    clearTimeout(searchDebounceTimer);
    fetchSkills(searchInput.value.trim());
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
        clearSkillErrors();
        skillSubmitButton.disabled = true;
        const body = Object.fromEntries(new FormData(skillForm));

        try {
            const skill = await sendSkillRequest(
                skillForm.action,
                editingSkill ? 'PATCH' : 'POST',
                body,
            );
            showToast(
                'Berhasil',
                editingSkill
                    ? `"${skill.title}" berhasil diperbarui.`
                    : `"${skill.title}" berhasil ditambahkan.`,
                'success',
            );
            skillForm.reset();
            skillModal.hidePopover();
            openSkillCreator();
            await fetchSkills(searchInput.value.trim());
        } catch (error) {
            showSkillValidationErrors(error.data || {});
            showToast(
                editingSkill ? 'Gagal memperbarui skill' : 'Gagal menyimpan skill',
                error.message,
                'error',
            );
        } finally {
            skillSubmitButton.disabled = false;
        }
    });
}

document.getElementById('add-skill-button')?.addEventListener('click', openSkillCreator);

fetchSkills(searchInput.value.trim());
