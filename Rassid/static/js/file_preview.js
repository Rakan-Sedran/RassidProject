document.addEventListener('DOMContentLoaded', function () {
    function getExt(url) {
        try {
            const parts = url.split('?')[0].split('/');
            const name = parts[parts.length - 1] || '';
            const dot = name.lastIndexOf('.');
            return dot === -1 ? '' : name.slice(dot + 1).toLowerCase();
        } catch (e) { return ''; }
    }

    function isImage(ext) {
        return ['png', 'jpg', 'jpeg', 'gif', 'webp', 'svg'].includes(ext);
    }

    function isPdf(ext) { return ext === 'pdf'; }

    const modalOverlay = document.createElement('div');
    modalOverlay.className = 'preview-modal-overlay';
    modalOverlay.innerHTML = `
        <div class="preview-modal" role="dialog" aria-modal="true">
            <div class="preview-header">
                <div class="preview-title" style="color:#fff;font-weight:700"></div>
                <div>
                    <button class="preview-close">Close</button>
                </div>
            </div>
            <div class="preview-body"></div>
        </div>`;
    document.body.appendChild(modalOverlay);

    const previewBody = modalOverlay.querySelector('.preview-body');
    const previewTitle = modalOverlay.querySelector('.preview-title');
    const closeBtn = modalOverlay.querySelector('.preview-close');

    function openPreview(url) {
        const ext = getExt(url);
        previewBody.innerHTML = '';
        previewTitle.textContent = url.split('/').pop().split('?')[0];

        if (isImage(ext)) {
            const img = document.createElement('img');
            img.src = url;
            previewBody.appendChild(img);
            modalOverlay.classList.add('active');
            return;
        }

        if (isPdf(ext)) {
            const iframe = document.createElement('iframe');
            iframe.src = url;
            previewBody.appendChild(iframe);
            modalOverlay.classList.add('active');
            return;
        }

        window.open(url, '_blank');
    }

    function closePreview() {
        modalOverlay.classList.remove('active');
        previewBody.innerHTML = '';
    }

    document.addEventListener('click', function (ev) {
        const el = ev.target.closest && ev.target.closest('.file-action-btn.btn-view');
        if (!el) return;
        ev.preventDefault();
        const url = el.getAttribute('data-file-url') || el.href;
        if (!url) return;
        openPreview(url);
    });

    closeBtn.addEventListener('click', closePreview);

    modalOverlay.addEventListener('click', function (ev) {
        if (ev.target === modalOverlay) closePreview();
    });

    document.addEventListener('keydown', function (ev) {
        if (ev.key === 'Escape') closePreview();
    });
});
