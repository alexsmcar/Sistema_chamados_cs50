export default function check_forms() {
    const href = window.location.pathname;
    const path = "/cadastrar_chamados";
    const form_chamados = document.getElementById("formulario_cad");
    const form_clientes = document.getElementById("formulario_clientes");
    if (form_chamados) {
        if (path === href) {
            const dataAtual = new Date();
            const dataFormat = dataAtual.toLocaleString('sv-SE', { timeZoneName: 'short' }).slice(0, 16);
            console.log(dataFormat);
            form_chamados["entrada"].value = dataFormat;
        }

        function validadeChamados(event) {
            const cliente = this["cliente"];
            const descricao = this["descricao"];
            const defeitos = this["defeitos"];
            const isValid = validarCampos("campo_invalido", cliente,descricao,defeitos);
            console.log(isValid);
            if (!isValid) {
               event.preventDefault();
            }
        }
        form_chamados.addEventListener("submit", validadeChamados)
        
  
    }

    if (form_clientes) {
        function validarClientes(event) {
            const registro = this["registro"];
            const nome = this["nome"];
            const telefone = this["telefone"];
            const logradouro = this["logradouro"];
            const bairro = this["bairro"];
            const cidade = this["cidade"];
            const uf = this["uf"];
            const isValid = validarCampos("campo_invalido", registro, nome, telefone,logradouro,bairro,cidade,uf);
            if (!isValid) {
                event.preventDefault();
            }
            
        }
        form_clientes.addEventListener("submit", validarClientes)
    }

    function validarCampos(classe, ...itens) {
        let isValid = true;
        itens.forEach((item => {
            if (item.value.trim() === "" || (item.tagName === "SELECT" && item.value === "Selecione")) {
                item.classList.add(classe);
                isValid = false;
            }
            else {
                item.classList.remove(classe);
            }
           
        }))
        return isValid;
    }
    
    
}