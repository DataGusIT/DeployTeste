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

    // ================================= //
    //          LÓGICA DO BANNER DE COOKIES
    // ================================= //

    // Função para buscar um cookie específico pelo nome
    function getCookie(name) {
        let cookieArr = document.cookie.split(";");
        for (let i = 0; i < cookieArr.length; i++) {
            let cookiePair = cookieArr[i].split("=");
            if (name == cookiePair[0].trim()) {
                return decodeURIComponent(cookiePair[1]);
            }
        }
        return null;
    }

    // Seleciona os elementos do banner
    const cookieBanner = $('#cookie-banner');
    const acceptBtn = $('#cookie-accept-btn');

    // Verifica se o cookie 'cookie_consent' NÃO existe
    if (!getCookie('cookie_consent')) {
        // Se não existir, mostra o banner adicionando a classe 'show'
        cookieBanner.addClass('show');
    }

    // Adiciona um evento de clique ao botão de aceitar
    acceptBtn.on('click', function () {
        // Define o cookie para expirar em 1 ano (365 dias)
        let expiryDate = new Date();
        expiryDate.setDate(expiryDate.getDate() + 365);
        document.cookie = "cookie_consent=true; expires=" + expiryDate.toUTCString() + "; path=/";

        // Esconde o banner removendo a classe 'show'
        cookieBanner.removeClass('show');
    });
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

