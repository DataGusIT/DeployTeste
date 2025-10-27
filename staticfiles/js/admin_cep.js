// core/static/js/admin_cep.js

document.addEventListener('DOMContentLoaded', function () {
    // Pega os campos do formulário
    const cepField = document.querySelector('#id_cep');
    const ruaField = document.querySelector('#id_rua');
    const bairroField = document.querySelector('#id_bairro');
    const cidadeField = document.querySelector('#id_cidade');
    const estadoField = document.querySelector('#id_estado');
    const horarioField = document.querySelector('#id_horario_funcionamento');

    // Função para mostrar mensagens de status (sem alterações)
    const showStatusMessage = (message, isError = false) => {
        const existingMessage = document.querySelector('#cep-status-message');
        if (existingMessage) {
            existingMessage.remove();
        }
        if (message) {
            const statusSpan = document.createElement('span');
            statusSpan.id = 'cep-status-message';
            statusSpan.textContent = message;
            statusSpan.style.fontSize = '12px';
            statusSpan.style.marginTop = '5px';
            statusSpan.style.display = 'block';
            statusSpan.style.color = isError ? '#e35b5b' : '#666';
            cepField.parentNode.insertBefore(statusSpan, cepField.nextSibling);
        }
    };

    if (cepField) {
        cepField.addEventListener('input', function (e) {
            // ==========================================================
            // NOVA LÓGICA PARA A MÁSCARA DO CEP
            // ==========================================================

            // 1. Pega o valor atual e remove tudo que não for número.
            let cepValue = e.target.value.replace(/\D/g, '');

            // 2. Limita o valor a 8 dígitos no máximo.
            if (cepValue.length > 8) {
                cepValue = cepValue.substring(0, 8);
            }

            // 3. Aplica a máscara (adiciona o hífen depois do 5º dígito).
            let maskedValue = cepValue;
            if (cepValue.length > 5) {
                maskedValue = cepValue.substring(0, 5) + '-' + cepValue.substring(5);
            }

            // 4. Atualiza o valor no campo. O navegador move o cursor para o final automaticamente.
            e.target.value = maskedValue;

            // ==========================================================
            // O RESTO DO CÓDIGO CONTINUA IGUAL
            // ==========================================================

            // Remove a mensagem de erro assim que o usuário começa a corrigir
            showStatusMessage(null);

            // Se o CEP (apenas os números) tem 8 dígitos, faz a busca
            if (cepValue.length === 8) {
                const url = `/api/consulta-cep/${cepValue}/`;
                showStatusMessage('Buscando endereço...');

                fetch(url)
                    .then(response => {
                        if (!response.ok) {
                            throw new Error('CEP não encontrado ou inválido.');
                        }
                        return response.json();
                    })
                    .then(data => {
                        if (data.sucesso) {
                            ruaField.value = data.rua;
                            bairroField.value = data.bairro;
                            cidadeField.value = data.cidade;
                            estadoField.value = data.estado;
                            showStatusMessage(null);
                        } else {
                            showStatusMessage(data.erro, true);
                        }
                    })
                    .catch(error => {
                        console.error('Erro ao buscar CEP:', error);
                        showStatusMessage('CEP não encontrado.', true);
                    });
            }
        });
    }

    // --- CÓDIGO PARA A MÁSCARA DE HORÁRIO (sem alterações) ---
    if (horarioField) {
        horarioField.setAttribute('placeholder', 'HH:MM - HH:MM');
        horarioField.addEventListener('input', function (e) {
            let value = e.target.value.replace(/\D/g, '');
            let formattedValue = '';

            if (value.length > 0) formattedValue = value.substring(0, 2);
            if (value.length > 2) formattedValue += ':' + value.substring(2, 4);
            if (value.length > 4) formattedValue += ' - ' + value.substring(4, 6);
            if (value.length > 6) formattedValue += ':' + value.substring(6, 8);

            e.target.value = formattedValue;
        });
    }
});