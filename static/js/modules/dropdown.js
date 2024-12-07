export default function dropdown() {
    const btn_logout = document.querySelector(".btn_logout");
    if (btn_logout) {
        function ativar(event) {
            const logout_btn = event.currentTarget;
            const logoutId = logout_btn.getAttribute("aria-controls");
            const logout = document.getElementById(logoutId);
            logout.classList.toggle("active");
            if (logout.classList.contains("active")) {
                logout_btn.setAttribute("aria-expanded", "true");
            }
            else {
                logout_btn.setAttribute("aria-expanded", "false");
            }
        }
        btn_logout.addEventListener("click", ativar)
    }
}