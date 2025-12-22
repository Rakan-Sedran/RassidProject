document.addEventListener('DOMContentLoaded', () => {
    const navbar = document.getElementById('navbar');
    let lastScrollTop = 0;
    const delta = 5;

    window.addEventListener('scroll', () => {
        const currentScroll = window.scrollY;

        if (currentScroll > 50) {
            navbar.classList.add('scrolled-bg');
        } else {
            navbar.classList.remove('scrolled-bg');
        }

        if (Math.abs(lastScrollTop - currentScroll) <= delta) return;

        if (currentScroll > lastScrollTop && currentScroll > navbar.offsetHeight) {
            navbar.classList.add('nav-hidden');
        } else {
            navbar.classList.remove('nav-hidden');
        }

        lastScrollTop = currentScroll;
    });

    const mobileToggle = document.querySelector('.mobile-toggle');
    const mobileMenu = document.querySelector('.mobile-menu');

    if (mobileToggle && mobileMenu) {
        mobileToggle.addEventListener('click', () => {
            mobileToggle.classList.toggle('active');
            mobileMenu.classList.toggle('active');
        });
    }
});