// Auto-dismiss alerts
document.addEventListener('DOMContentLoaded', function() {
    // إخفاء الرسائل تلقائياً بعد 5 ثواني
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });

    // Smooth scroll
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
});

// قوالب جاهزة للكتّاب
const chapterTemplates = {
    basic: `<h2>عنوان الفصل</h2>
<p class="chapter-start">بداية الفصل هنا...</p>
<p>المحتوى الأساسي للفصل.</p>`,

    dialogue: `<p class="dialogue">"الحوار الأول من الشخصية الأولى"</p>
<p>قال الراوي بصوت هادئ.</p>
<p class="dialogue">"الحوار الثاني من الشخصية الثانية"</p>
<p>ردت عليه بحماس.</p>`,

    flashback: `<p class="scene-break">* * *</p>
<p><em>الماضي، قبل خمس سنوات...</em></p>
<p>محتوى الفلاش باك هنا</p>
<p class="scene-break">* * *</p>`,

    letter: `<blockquote class="letter">
<p>عزيزتي...</p>
<p>محتوى الرسالة يكتب هنا. يمكن أن تكون رسالة حب، أو رسالة رسمية، أو أي نوع آخر من الرسائل.</p>
<p>مع خالص الحب،<br>الاسم</p>
</blockquote>`,

    thought: `<p>نظر إلى السماء وفكر في نفسه: <span class="thought">ماذا لو لم أعد إلى هنا أبداً؟</span></p>`,

    description: `<div class="description">
<p>كان المكان يبدو مهجوراً تماماً. الجدران الرمادية المتآكلة، والنوافذ المحطمة، كل شيء يوحي بأن لا أحد زار هذا المكان منذ سنوات طويلة.</p>
</div>`
};

// دالة تحميل القالب
function loadTemplate(templateName) {
    if (typeof tinymce !== 'undefined' && tinymce.activeEditor) {
        const template = chapterTemplates[templateName];
        if (template) {
            tinymce.activeEditor.insertContent(template);
        }
    }
}

// تأكيد الحذف
document.querySelectorAll('[onclick*="confirm"]').forEach(function(element) {
    element.addEventListener('click', function(e) {
        if (!confirm('هل أنت متأكد من هذا الإجراء؟')) {
            e.preventDefault();
            return false;
        }
    });
});

// Print Chapter
function printChapter() {
    window.print();
}

// Export as TXT
function exportAsTXT() {
    if (typeof tinymce !== 'undefined' && tinymce.activeEditor) {
        const content = tinymce.activeEditor.getContent({
            format: 'text'
        });
        const blob = new Blob([content], {
            type: 'text/plain'
        });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'chapter.txt';
        a.click();
        window.URL.revokeObjectURL(url);
    }
}

// Character counter for regular textareas (not TinyMCE)
document.querySelectorAll('textarea:not(#content)').forEach(function(textarea) {
    if (!textarea.id.includes('content')) {
        textarea.addEventListener('input', function() {
            const counter = this.nextElementSibling;
            if (counter && counter.classList.contains('char-counter')) {
                counter.textContent = this.value.length + ' حرف';
            }
        });
    }
});

// Auto-save notification
function showAutoSaveNotification() {
    const notification = document.createElement('div');
    notification.className = 'alert alert-success position-fixed top-0 end-0 m-3';
    notification.style.zIndex = '9999';
    notification.innerHTML = '<i class="bi bi-check-circle"></i> تم الحفظ التلقائي';
    document.body.appendChild(notification);

    setTimeout(() => {
        notification.remove();
    }, 2000);
}

// Keyboard shortcuts info
document.addEventListener('keydown', function(e) {
    // Ctrl + S للحفظ
    if (e.ctrlKey && e.key === 's') {
        e.preventDefault();
        const form = document.querySelector('form');
        if (form) {
            form.submit();
        }
    }

    // Ctrl + ? لإظهار الاختصارات
    if (e.ctrlKey && e.shiftKey && e.key === '?') {
        e.preventDefault();
        const modal = document.getElementById('shortcutsModal');
        if (modal) {
            const bsModal = new bootstrap.Modal(modal);
            bsModal.show();
        }
    }
});

console.log('NarrEyes App Loaded Successfully! 📚✨');
// ==================== Enhanced Mobile Experience ====================

document.addEventListener('DOMContentLoaded', function() {

    // Auto-dismiss alerts
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            const bsAlert = bootstrap.Alert.getInstance(alert) || new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });

    // Smooth scroll
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Add loading state to forms
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function() {
            const submitBtn = this.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.classList.add('loading');
                submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Loading...';
            }
        });
    });

    // Confirm delete actions
    document.querySelectorAll('[onclick*="confirm"]').forEach(function(element) {
        element.addEventListener('click', function(e) {
            if (!confirm('Are you sure you want to delete this?')) {
                e.preventDefault();
                return false;
            }
        });
    });

    // Auto-resize textareas
    const textareas = document.querySelectorAll('textarea');
    textareas.forEach(textarea => {
        textarea.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = this.scrollHeight + 'px';
        });
    });

    // Add animation to cards on scroll
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-fade-in');
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);

    document.querySelectorAll('.card').forEach(card => {
        observer.observe(card);
    });

    // Touch swipe support for mobile
    let touchStartX = 0;
    let touchEndX = 0;

    document.addEventListener('touchstart', e => {
        touchStartX = e.changedTouches[0].screenX;
    });

    document.addEventListener('touchend', e => {
        touchEndX = e.changedTouches[0].screenX;
        handleSwipe();
    });

    function handleSwipe() {
        if (touchEndX < touchStartX - 50) {
            // Swiped left
            console.log('Swiped left');
        }
        if (touchEndX > touchStartX + 50) {
            // Swiped right
            console.log('Swiped right');
        }
    }

    // Add ripple effect to buttons
    const buttons = document.querySelectorAll('.btn');
    buttons.forEach(button => {
        button.addEventListener('click', function(e) {
            const ripple = document.createElement('span');
            ripple.classList.add('ripple');
            this.appendChild(ripple);

            const rect = this.getBoundingClientRect();
            const size = Math.max(rect.width, rect.height);
            const x = e.clientX - rect.left - size / 2;
            const y = e.clientY - rect.top - size / 2;

            ripple.style.width = ripple.style.height = size + 'px';
            ripple.style.left = x + 'px';
            ripple.style.top = y + 'px';

            setTimeout(() => ripple.remove(), 600);
        });
    });

    // Offline detection
    window.addEventListener('online', () => {
        showToast('You are back online!', 'success');
    });

    window.addEventListener('offline', () => {
        showToast('You are offline. Some features may not work.', 'warning');
    });

});

// ==================== Utility Functions ====================

function showToast(message, type = 'info') {
    const toastHTML = `
        <div class="toast align-items-center text-white bg-${type} border-0" role="alert">
            <div class="d-flex">
                <div class="toast-body">${message}</div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        </div>
    `;

    let container = document.querySelector('.toast-container');
    if (!container) {
        container = document.createElement('div');
        container.className = 'toast-container';
        document.body.appendChild(container);
    }

    container.insertAdjacentHTML('beforeend', toastHTML);
    const toastElement = container.lastElementChild;
    const toast = new bootstrap.Toast(toastElement);
    toast.show();

    toastElement.addEventListener('hidden.bs.toast', () => {
        toastElement.remove();
    });
}

// Copy to clipboard
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        showToast('Copied to clipboard!', 'success');
    }).catch(() => {
        showToast('Failed to copy', 'danger');
    });
}

// Print page
function printPage() {
    window.print();
}

// Share content (if supported)
function shareContent(title, text, url) {
    if (navigator.share) {
        navigator.share({
            title: title,
            text: text,
            url: url
        }).catch(() => {
            showToast('Sharing cancelled', 'info');
        });
    } else {
        copyToClipboard(url);
        showToast('Link copied to clipboard', 'success');
    }
}

// Add ripple CSS
const style = document.createElement('style');
style.textContent = `
    .btn {
        position: relative;
        overflow: hidden;
    }

    .ripple {
        position: absolute;
        border-radius: 50%;
        background: rgba(255, 255, 255, 0.6);
        transform: scale(0);
        animation: ripple-animation 0.6s ease-out;
        pointer-events: none;
    }

    @keyframes ripple-animation {
        to {
            transform: scale(4);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);

console.log('✨ NarrEyes Enhanced - Mobile Optimized');
