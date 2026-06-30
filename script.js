document.addEventListener('DOMContentLoaded', function () {
    /* ===== Typing Effect ===== */
    const phrases = [
        'Пишу чистый код на Python',
        'Создаю современные веб-сайты',
        'Автоматизирую бизнес-процессы',
        'Разрабатываю десктоп-приложения',
        'Превращаю идеи в работающий продукт'
    ];

    const el = document.getElementById('typedText');
    let phraseIdx = 0;
    let charIdx = 0;
    let isDeleting = false;

    function typeLoop() {
        const current = phrases[phraseIdx];
        if (!isDeleting) {
            el.textContent = current.substring(0, charIdx + 1);
            charIdx++;
            if (charIdx === current.length) {
                setTimeout(() => { isDeleting = true; typeLoop(); }, 2000);
                return;
            }
            setTimeout(typeLoop, 80);
        } else {
            el.textContent = current.substring(0, charIdx);
            charIdx--;
            if (charIdx < 0) {
                isDeleting = false;
                phraseIdx = (phraseIdx + 1) % phrases.length;
                setTimeout(typeLoop, 500);
                return;
            }
            setTimeout(typeLoop, 40);
        }
    }
    typeLoop();

    /* ===== Navbar Scroll Effect ===== */
    const navbar = document.querySelector('.navbar');
    window.addEventListener('scroll', function () {
        navbar.classList.toggle('scrolled', window.scrollY > 50);
    });

    /* ===== Burger Menu ===== */
    const burger = document.getElementById('burger');
    const navLinks = document.getElementById('navLinks');

    burger.addEventListener('click', function () {
        navLinks.classList.toggle('active');
    });

    document.querySelectorAll('.nav-links a').forEach(function (link) {
        link.addEventListener('click', function () {
            navLinks.classList.remove('active');
        });
    });

    /* ===== Skill Bars Animation ===== */
    const skillFills = document.querySelectorAll('.skill-fill');

    function animateSkills() {
        skillFills.forEach(function (bar) {
            const rect = bar.getBoundingClientRect();
            if (rect.top < window.innerHeight - 50) {
                bar.style.width = bar.dataset.width;
            }
        });
    }

    window.addEventListener('scroll', animateSkills);
    animateSkills();

    /* ===== Contact Form Validation ===== */
    const form = document.getElementById('contactForm');
    const nameInput = document.getElementById('name');
    const emailInput = document.getElementById('email');
    const messageInput = document.getElementById('message');
    const nameError = document.getElementById('nameError');
    const emailError = document.getElementById('emailError');
    const messageError = document.getElementById('messageError');

    function validateEmail(email) {
        return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
    }

    function clearErrors() {
        [nameInput, emailInput, messageInput].forEach(function (el) {
            el.classList.remove('error');
        });
        nameError.textContent = '';
        emailError.textContent = '';
        messageError.textContent = '';
    }

    form.addEventListener('submit', function (e) {
        e.preventDefault();
        clearErrors();

        let valid = true;

        if (!nameInput.value.trim()) {
            nameError.textContent = 'Введите имя';
            nameInput.classList.add('error');
            valid = false;
        }

        if (!emailInput.value.trim()) {
            emailError.textContent = 'Введите email';
            emailInput.classList.add('error');
            valid = false;
        } else if (!validateEmail(emailInput.value.trim())) {
            emailError.textContent = 'Некорректный email';
            emailInput.classList.add('error');
            valid = false;
        }

        if (!messageInput.value.trim()) {
            messageError.textContent = 'Введите сообщение';
            messageInput.classList.add('error');
            valid = false;
        }

        if (valid) {
            showToast('Спасибо! Я свяжусь с вами в ближайшее время.');
            form.reset();
        }
    });

    /* ===== Toast ===== */
    function showToast(text, isError) {
        const toast = document.getElementById('toast');
        toast.textContent = text;
        toast.className = 'toast show';
        if (isError) toast.classList.add('error');
        setTimeout(function () {
            toast.classList.remove('show');
        }, 4000);
    }

    /* ===== Smooth Navbar Hide on Input Focus (mobile keyboard) ===== */
    const inputs = document.querySelectorAll('input, textarea');
    inputs.forEach(function (input) {
        input.addEventListener('focus', function () {
            navbar.style.transform = 'translateY(-100%)';
        });
        input.addEventListener('blur', function () {
            navbar.style.transform = 'translateY(0)';
        });
    });
});
