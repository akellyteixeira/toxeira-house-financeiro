
/* =====================================
   TOXEIRAHOUSE FINANCEIRO
   Cadastro de usuário
===================================== */

// Endereço da API REST em Python
const API_URL = "http://127.0.0.1:8000/api/auth/register";

// Elementos da página
const cadastroForm = document.getElementById("cadastro-form");
const emailInput = document.getElementById("email");
const passwordInput = document.getElementById("password");
const confirmButton = document.getElementById("confirm-button");
const messageElement = document.getElementById("cadastro-message");

// Exibe mensagens na página
function mostrarMensagem(mensagem, tipo = "erro") {
    messageElement.textContent = mensagem;

    if (tipo === "sucesso") {
        messageElement.style.color = "#237a45";
    } else {
        messageElement.style.color = "#c62828";
    }
}

// Trata mensagens de erro retornadas pela API
function obterMensagemErro(data) {
    if (typeof data.detail === "string") {
        return data.detail;
    }

    if (Array.isArray(data.detail)) {
        return data.detail
            .map(erro => erro.msg || "Verifique os dados informados.")
            .join(" ");
    }

    if (typeof data.message === "string") {
        return data.message;
    }

    return "Não foi possível criar a conta.";
}

// Envio do formulário
cadastroForm.addEventListener("submit", async function (event) {

    // Impede o recarregamento da página
    event.preventDefault();

    // Captura os dados
    const email = emailInput.value.trim();
    const password = passwordInput.value;

    // Validação dos campos
    if (!email || !password) {
        mostrarMensagem("Preencha todos os campos.");
        return;
    }

    if (password.length < 8) {
        mostrarMensagem(
            "A senha precisa ter pelo menos 8 caracteres."
        );

        passwordInput.focus();
        return;
    }

    // Evita envios duplicados
    confirmButton.disabled = true;

    mostrarMensagem("Criando sua conta...", "sucesso");

    try {

        // Envia os dados em JSON para o backend Python
        const response = await fetch(API_URL, {
            method: "POST",

            headers: {
                "Content-Type": "application/json",
                "Accept": "application/json"
            },

            body: JSON.stringify({
                email: email,
                password: password
            })
        });

        // Converte a resposta da API em JSON
        const data = await response.json().catch(() => ({}));

        // Trata erros HTTP
        if (!response.ok) {

            if (response.status === 409) {
                throw new Error(
                    "Este e-mail já está cadastrado."
                );
            }

            if (response.status === 422) {
                throw new Error(obterMensagemErro(data));
            }

            throw new Error(obterMensagemErro(data));
        }

        // Verifica se a API informou uma falha
        if (data.success === false) {
            throw new Error(obterMensagemErro(data));
        }

        // Cadastro realizado com sucesso
        mostrarMensagem(
            "Conta criada com sucesso! Redirecionando para o login...",
            "sucesso"
        );

        // Limpa os campos
        cadastroForm.reset();

        // Retorna para a página de login
        window.setTimeout(function () {
            window.location.href = "index.html";
        }, 1200);

    } catch (error) {

        // Trata problemas de conexão
        if (error instanceof TypeError) {
            mostrarMensagem(
                "Não foi possível conectar ao servidor. " +
                "Verifique se a API Python está funcionando."
            );
        } else {
            mostrarMensagem(error.message);
        }

    } finally {

        // Libera o botão novamente
        confirmButton.disabled = false;
    }

});
