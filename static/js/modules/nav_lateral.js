export default function nav_lateral() {
    const btn_ocultar = document.getElementById("btn_ocultar");
    if (btn_ocultar) {
        const header = document.querySelector(".cabecalho");
        const main = document.querySelector("main");
        btn_ocultar.addEventListener("click", (event) => {
            header.classList.toggle("hidden");
            main.classList.toggle("nav_hidden");
        });
    }
}