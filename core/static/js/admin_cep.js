// core/static/js/admin_cep.js

document.addEventListener('DOMContentLoaded', function () {
    // Pega os campos do formulário do admin do Django
    const cepField = document.querySelector('#id_cep');
    const ruaField = document.querySelector('#id_rua');
    const bairroField = document.querySelector('#id_bairro');
    const cidadeField = document.querySelector('#id_cidade');
    const estadoField = document.querySelector('#id_estado');
    const horarioField = document.querySelector('#id_horario_funcionamento'); // Para a próxima funcionalidade

    if (cepField) {
        // Adiciona um "escutador" que dispara quando o usuário sai do campo CEP
        cepField.addEventListener('blur', function () {
            const cepValue = this.value.replace(/\D/g, ''); // Remove tudo que não for número

            if (cepValue.length === 8) {
                // Monta a URL da API que você já criou
                const url = `/api/consulta-cep/${cepValue}/`;

                // Faz a chamada para a API
                fetch(url)
                    .then(response => response.json())
                    .then(data => {
                        if (data.sucesso) {
                            // Preenche os campos com os dados recebidos
                            ruaField.value = data.rua;
                            bairroField.value = data.bairro;
                            cidadeField.value = data.cidade;
                            estadoField.value = data.estado;
                        } else {
                            alert(data.erro);
                        }
                    })
                    .catch(error => console.error('Erro ao buscar CEP:', error));
            }
        });
    }

    // --- CÓDIGO PARA A SOLICITAÇÃO 3 (MÁSCARA DE HORÁRIO) ---
    if (horarioField) {
        horarioField.setAttribute('placeholder', 'HH:MM - HH:MM'); // Adiciona uma dica

        horarioField.addEventListener('input', function (e) {
            let value = e.target.value.replace(/\D/g, '');
            let formattedValue = '';

            if (value.length > 0) {
                formattedValue = value.substring(0, 2);
            }
            if (value.length > 2) {
                formattedValue += ':' + value.substring(2, 4);
            }
            if (value.length > 4) {
                formattedValue += ' - ' + value.substring(4, 6);
            }
            if (value.length > 6) {
                formattedValue += ':' + value.substring(6, 8);
            }

            e.target.value = formattedValue;
        });
    }
});