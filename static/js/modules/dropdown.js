export default function dropdown() {
    const btn_logout = document.querySelector(".btn_logout");
    if (btn_logout) {
        function ativar(event) {
            const logout_btn = event.currentTarget;
            const logoutId = logout_btn.getAttribute("aria-controls");
            const logout = document.getElementById(logoutId);
            const eventoClick = logout.classList.toggle("active");
            if (eventoClick) {
                logout_btn.setAttribute("aria-expanded", "true");
            }
            else {
                logout_btn.setAttribute("aria-expanded", "false");
                
            }
            fecharBtn(logout_btn, logout, () => {
                logout.classList.remove("active");
                logout_btn.setAttribute("aria-expanded", "false");  
            })
            
        }
        function fecharBtn(btn, logout , callback) {
            const html = document.documentElement;
            function clickoutside(event) {
                if (!btn.contains(event.target) && !logout.contains(event.target)) {
                    callback();
                }
            }
            html.addEventListener("click", clickoutside)
        }
        btn_logout.addEventListener("click", ativar)
    }
}
