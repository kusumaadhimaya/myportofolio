const deleteConfirmationModal = document.getElementById('delete-confirmation-modal');

if (deleteConfirmationModal) {
    const deleteConfirmationMessage = document.getElementById('delete-confirmation-message');
    const deleteConfirmationSubmit = document.getElementById('delete-confirmation-submit');
    let pendingDeleteAction = null;

    window.openDeleteConfirmation = ({ itemType, itemName, onConfirm }) => {
        deleteConfirmationMessage.textContent =
            `Apakah Anda yakin ingin menghapus ${itemType} "${itemName}"?`;
        pendingDeleteAction = onConfirm;
        deleteConfirmationModal.showPopover();
        deleteConfirmationSubmit.focus();
    };

    deleteConfirmationSubmit.addEventListener('click', async () => {
        if (!pendingDeleteAction || deleteConfirmationSubmit.disabled) return;

        deleteConfirmationSubmit.disabled = true;
        try {
            const shouldClose = await pendingDeleteAction();
            if (shouldClose !== false) {
                pendingDeleteAction = null;
                deleteConfirmationModal.hidePopover();
            }
        } finally {
            deleteConfirmationSubmit.disabled = false;
        }
    });

    deleteConfirmationModal.addEventListener('toggle', event => {
        if (event.newState === 'closed') pendingDeleteAction = null;
    });
}
