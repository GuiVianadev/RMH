// State
let currentPage = 1;
let currentDocumentId = null;
let allDocuments = [];
let filteredDocuments = [];

// DOM Elements
const uploadForm = document.getElementById('uploadForm');
const documentsList = document.getElementById('documentsList');
const pagination = document.getElementById('pagination');
const loading = document.getElementById('loading');
const emptyState = document.getElementById('emptyState');
const searchInput = document.getElementById('searchInput');
const fileInput = document.getElementById('file');
const fileInfo = document.getElementById('fileInfo');
const uploadBtn = document.getElementById('uploadBtn');

// Modal elements
const modal = document.getElementById('documentModal');
const closeModal = document.getElementById('closeModal');
const modalTitle = document.getElementById('modalTitle');
const modalType = document.getElementById('modalType');
const modalDate = document.getElementById('modalDate');
const modalDescription = document.getElementById('modalDescription');
const modalDescriptionContainer = document.getElementById('modalDescriptionContainer');
const viewBtn = document.getElementById('viewBtn');
const downloadBtn = document.getElementById('downloadBtn');
const deleteBtn = document.getElementById('deleteBtn');
const commentForm = document.getElementById('commentForm');
const commentsList = document.getElementById('commentsList');
const commentsCount = document.getElementById('commentsCount');
const commentsEmpty = document.getElementById('commentsEmpty');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    loadDocuments();
    setupEventListeners();
});

// Event Listeners
function setupEventListeners() {
    uploadForm.addEventListener('submit', handleUpload);
    searchInput.addEventListener('input', handleSearch);
    fileInput.addEventListener('change', handleFileSelect);
    closeModal.addEventListener('click', closeModalHandler);
    modal.addEventListener('click', (e) => {
        if (e.target === modal) closeModalHandler();
    });
    commentForm.addEventListener('submit', handleCommentSubmit);
}

// File selection handler
function handleFileSelect(e) {
    const file = e.target.files[0];
    if (file) {
        const sizeMB = (file.size / (1024 * 1024)).toFixed(2);
        fileInfo.textContent = `${file.name} (${sizeMB} MB)`;
        
        if (file.size > 10 * 1024 * 1024) {
            fileInfo.style.color = 'var(--danger)';
            fileInfo.textContent += ' - Arquivo muito grande!';
        } else {
            fileInfo.style.color = 'var(--gray-500)';
        }
    }
}

// Upload document
async function handleUpload(e) {
    e.preventDefault();
    
    const formData = new FormData();
    formData.append('title', document.getElementById('title').value);
    formData.append('description', document.getElementById('description').value || '');
    formData.append('file', fileInput.files[0]);
    
    setLoading(uploadBtn, true);
    
    try {
        const response = await fetch(`${API_URL}/documents/`, {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Erro ao fazer upload');
        }
        
        showToast('Documento enviado com sucesso!', 'success');
        uploadForm.reset();
        fileInfo.textContent = '';
        loadDocuments();
    } catch (error) {
        showToast(error.message, 'error');
    } finally {
        setLoading(uploadBtn, false);
    }
}

// Load documents
async function loadDocuments(page = 1) {
    loading.style.display = 'block';
    documentsList.innerHTML = '';
    emptyState.style.display = 'none';
    
    try {
        const response = await fetch(`${API_URL}/documents/?page=${page}&page_size=9`);
        const data = await response.json();
        
        allDocuments = data.documents;
        filteredDocuments = allDocuments;
        currentPage = page;
        
        if (filteredDocuments.length === 0) {
            emptyState.style.display = 'block';
        } else {
            renderDocuments(filteredDocuments);
            renderPagination(data.total_pages, page);
        }
    } catch (error) {
        showToast('Erro ao carregar documentos', 'error');
    } finally {
        loading.style.display = 'none';
    }
}

// Render documents
function renderDocuments(documents) {
    documentsList.innerHTML = documents.map(doc => `
        <div class="document-card" onclick="openDocument('${doc.id}')">
            <h3>${escapeHtml(doc.title)}</h3>
            <span class="badge">${doc.file_type.toUpperCase()}</span>
            ${doc.description ? `<p class="description">${escapeHtml(doc.description)}</p>` : ''}
            <div class="meta">
                <span>📅 ${formatDate(doc.created_at)}</span>
            </div>
        </div>
    `).join('');
}

// Render pagination
function renderPagination(totalPages, currentPage) {
    if (totalPages <= 1) {
        pagination.innerHTML = '';
        return;
    }
    
    let html = `
        <button ${currentPage === 1 ? 'disabled' : ''} onclick="loadDocuments(${currentPage - 1})">
            ← Anterior
        </button>
    `;
    
    for (let i = 1; i <= totalPages; i++) {
        if (i === 1 || i === totalPages || (i >= currentPage - 1 && i <= currentPage + 1)) {
            html += `
                <button 
                    class="${i === currentPage ? 'active' : ''}" 
                    onclick="loadDocuments(${i})"
                >
                    ${i}
                </button>
            `;
        } else if (i === currentPage - 2 || i === currentPage + 2) {
            html += '<button disabled>...</button>';
        }
    }
    
    html += `
        <button ${currentPage === totalPages ? 'disabled' : ''} onclick="loadDocuments(${currentPage + 1})">
            Próxima →
        </button>
    `;
    
    pagination.innerHTML = html;
}

// Search documents
function handleSearch(e) {
    const query = e.target.value.toLowerCase();
    
    if (!query) {
        filteredDocuments = allDocuments;
    } else {
        filteredDocuments = allDocuments.filter(doc => 
            doc.title.toLowerCase().includes(query)
        );
    }
    
    if (filteredDocuments.length === 0) {
        documentsList.innerHTML = '';
        emptyState.style.display = 'block';
        pagination.innerHTML = '';
    } else {
        emptyState.style.display = 'none';
        renderDocuments(filteredDocuments);
        pagination.innerHTML = ''; // Remove pagination when searching
    }
}

// Open document modal
async function openDocument(documentId) {
    currentDocumentId = documentId;
    
    try {
        const response = await fetch(`${API_URL}/documents/${documentId}`);
        const doc = await response.json();
        
        modalTitle.textContent = doc.title;
        modalType.textContent = doc.file_type.toUpperCase();
        modalDate.textContent = formatDate(doc.created_at);
        
        if (doc.description) {
            modalDescription.textContent = doc.description;
            modalDescriptionContainer.style.display = 'block';
        } else {
            modalDescriptionContainer.style.display = 'none';
        }
        
        viewBtn.onclick = () => window.open(`${API_URL}/documents/${documentId}/view`, '_blank');
        downloadBtn.onclick = () => window.location.href = `${API_URL}/documents/${documentId}/download`;
        deleteBtn.onclick = () => handleDelete(documentId);
        
        loadComments(documentId);
        modal.classList.add('show');
    } catch (error) {
        showToast('Erro ao carregar documento', 'error');
    }
}

// Close modal
function closeModalHandler() {
    modal.classList.remove('show');
    currentDocumentId = null;
    commentForm.reset();
}

// Load comments
async function loadComments(documentId) {
    try {
        const response = await fetch(`${API_URL}/documents/${documentId}/comments/`);
        const data = await response.json();
        
        commentsCount.textContent = data.total;
        
        if (data.comments.length === 0) {
            commentsList.innerHTML = '';
            commentsEmpty.style.display = 'block';
        } else {
            commentsEmpty.style.display = 'none';
            commentsList.innerHTML = data.comments.map(comment => `
                <div class="comment-item">
                    <div class="comment-date">${formatDate(comment.created_at)}</div>
                    <div class="comment-content">${escapeHtml(comment.content)}</div>
                </div>
            `).join('');
        }
    } catch (error) {
        showToast('Erro ao carregar comentários', 'error');
    }
}

// Submit comment
async function handleCommentSubmit(e) {
    e.preventDefault();
    
    const content = document.getElementById('commentContent').value.trim();
    if (!content) return;
    
    try {
        const response = await fetch(`${API_URL}/documents/${currentDocumentId}/comments/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ content })
        });
        
        if (!response.ok) throw new Error('Erro ao enviar comentário');
        
        showToast('Comentário adicionado!', 'success');
        commentForm.reset();
        loadComments(currentDocumentId);
    } catch (error) {
        showToast(error.message, 'error');
    }
}

// Delete document
async function handleDelete(documentId) {
    if (!confirm('Tem certeza que deseja deletar este documento? Esta ação não pode ser desfeita.')) {
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}/documents/${documentId}`, {
            method: 'DELETE'
        });
        
        if (!response.ok) throw new Error('Erro ao deletar documento');
        
        showToast('Documento deletado com sucesso!', 'success');
        closeModalHandler();
        loadDocuments(currentPage);
    } catch (error) {
        showToast(error.message, 'error');
    }
}

// Utilities
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('pt-BR', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function setLoading(button, isLoading) {
    const btnText = button.querySelector('.btn-text');
    const btnLoader = button.querySelector('.btn-loader');
    
    if (isLoading) {
        btnText.style.display = 'none';
        btnLoader.style.display = 'inline';
        button.disabled = true;
    } else {
        btnText.style.display = 'inline';
        btnLoader.style.display = 'none';
        button.disabled = false;
    }
}

function showToast(message, type = 'success') {
    const toast = document.getElementById('toast');
    toast.textContent = message;
    toast.className = `toast ${type} show`;
    
    setTimeout(() => {
        toast.classList.remove('show');
    }, 3000);
}