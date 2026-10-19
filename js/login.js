
/* =====================================
   TOXEIRAHOUSE FINANCEIRO
   Login com API REST em Python
===================================== */

// Altere esta URL para o endereço da sua API.
const API_URL = "http://127.0.0.1:8000/api/auth/login";

// Captura os elementos do HTML.
const loginForm = document.getElementById("login-form");
const emailInput = document.getElementById("email");
const passwordInput = document.getElementById("password");
const loginButton = loginForm.querySelector(".login-button");

// Cria uma área para exibir mensagens sem precisar alterar o HTML.
const messageElement = document.createElement("p");

messageElement.className = "form-message";
messageElement.setAttribute("role", "status");
messageElement.setAttribute("aria-live", "polite");

loginForm.appendChild(messageElement);


// Exibe mensagens para o usuário.
function showMessage(message, type = "error") {
    messageElement.textContent = message;

    messageElement.style.color =
        type === "success" ? "#237a45" : "#c62828";
}


// Envia o formulário para a API Python.
loginForm.addEventListener("submit", async function (event) {

    // Impede que o navegador recarregue a página.
    event.preventDefault();

    const email = emailInput.value.trim();
    const password = passwordInput.value;

    // Validação básica.
    if (!email || !password) {
        showMessage("Preencha o e-mail e a senha.");
        return;
    }

    // Evita envios repetidos enquanto aguarda a API.
    loginButton.disabled = true;
    showMessage("Verificando seus dados...", "success");

    try {

        // Envia os dados como JSON para o backend.
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

        // Tenta interpretar a resposta JSON.
        const data = await response.json().catch(() => ({}));

        // Trata erros retornados pela API.
        if (!response.ok) {

            if (response.status === 401) {
                throw new Error("E-mail ou senha incorretos.");
            }

            if (response.status === 422) {
                throw new Error("Confira os dados informados.");
            }

            throw new Error(
                data.detail ||
                data.message ||
                "Não foi possível realizar o login."
            );
        }

        // Verifica se o backend informou sucesso.
        if (data.success === false) {
            throw new Error(
                data.message || "Não foi possível realizar o login."
            );
        }

        // Se a API retornar um token, guarda-o apenas nesta sessão.
        // O backend precisa definir o formato da resposta.
        if (data.access_token) {
            sessionStorage.setItem("access_token", data.access_token);
        }

        showMessage("Login realizado com sucesso!", "success");

        // Redireciona para a página inicial após o login.
        window.location.href = "dashboard.html";

    } catch (error) {

        // Diferencia falhas de comunicação de erros de autenticação.
        if (error instanceof TypeError) {
            showMessage(
                "Não foi possível conectar ao servidor. " +
                "Verifique se o backend Python está funcionando."
            );
        } else {
            showMessage(error.message);
        }

    } finally {

        // Libera o botão novamente.
        loginButton.disabled = false;
    }

});
