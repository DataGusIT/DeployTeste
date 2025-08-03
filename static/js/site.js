// Back to top button - JAVASCRIPT CORRIGIDO
$(document).ready(function () {
    const backToTopBtn = $('#back-to-top');

    // Mostrar/esconder botão baseado no scroll
    $(window).scroll(function () {
        if ($(this).scrollTop() > 300) {
            backToTopBtn.addClass('show');
        } else {
            backToTopBtn.removeClass('show');
        }
    });

    // Ação do clique
    backToTopBtn.click(function (e) {
        e.preventDefault();
        $('html, body').animate({
            scrollTop: 0
        }, 500);
        return false;
    });

    // Verificar se já deve mostrar o botão na carga da página
    if ($(window).scrollTop() > 300) {
        backToTopBtn.addClass('show');
    }
});

$(document).ready(function () {
    // Código existente aqui...

    // Fix para a travadinha do menu hambúrguer
    const navbarToggler = $('.navbar-toggler');
    const navbarCollapse = $('#navbarNav');

    // Garante que a animação funcione corretamente
    navbarCollapse.on('show.bs.collapse', function () {
        navbarToggler.attr('aria-expanded', 'true');
    });

    navbarCollapse.on('hide.bs.collapse', function () {
        navbarToggler.attr('aria-expanded', 'false');
    });

    // Force o estado inicial correto
    navbarToggler.attr('aria-expanded', 'false');
});

// Add animation to elements when they become visible
function animateOnScroll() {
    $('.animate__animated').each(function () {
        const position = $(this).offset().top;
        const scroll = $(window).scrollTop();
        const windowHeight = $(window).height();

        if (scroll + windowHeight > position) {
            const animation = $(this).data('animation');
            $(this).addClass(animation);
        }
    });
}

$(window).scroll(animateOnScroll);
$(document).ready(animateOnScroll);

// static/js/main.js

document.addEventListener("DOMContentLoaded", function () {
    const animatedElements = document.querySelectorAll('[data-animation]');

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('is-visible');
                // Opcional: para a animação não repetir
                // observer.unobserve(entry.target); 
            }
        });
    }, {
        threshold: 0.1 // A animação começa quando 10% do elemento está visível
    });

    animatedElements.forEach(element => {
        observer.observe(element);
    });
});