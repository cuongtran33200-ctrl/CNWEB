document.addEventListener("DOMContentLoaded", () => {
    const navbar = document.querySelector(".site-navbar");
    if (navbar) {
        const onScroll = () => navbar.classList.toggle("is-scrolled", window.scrollY > 8);
        onScroll();
        window.addEventListener("scroll", onScroll, { passive: true });
    }

    const progress = document.getElementById("readingProgress");
    const article = document.querySelector(".post-content");
    if (progress && article) {
        const update = () => {
            const rect = article.getBoundingClientRect();
            const total = rect.height - window.innerHeight * 0.5;
            const current = Math.min(Math.max(-rect.top, 0), Math.max(total, 1));
            progress.style.width = `${(current / Math.max(total, 1)) * 100}%`;
        };
        update();
        window.addEventListener("scroll", update, { passive: true });
        window.addEventListener("resize", update);
    }

    document.querySelectorAll(".copy-link").forEach((button) => {
        button.addEventListener("click", async () => {
            const label = button.querySelector("span");
            const original = label ? label.textContent : "";
            try {
                if (navigator.clipboard && window.isSecureContext) {
                    await navigator.clipboard.writeText(button.dataset.url || window.location.href);
                } else {
                    const input = document.createElement("textarea");
                    input.value = button.dataset.url || window.location.href;
                    document.body.appendChild(input);
                    input.select();
                    document.execCommand("copy");
                    document.body.removeChild(input);
                }
                if (label) label.textContent = "Đã sao chép";
            } catch (error) {
                if (label) label.textContent = "Không sao chép được";
            }
            window.setTimeout(() => {
                if (label) label.textContent = original;
            }, 2000);
        });
    });

    window.setTimeout(() => {
        document.querySelectorAll(".alert-dismissible").forEach((alert) => {
            if (window.bootstrap) {
                window.bootstrap.Alert.getOrCreateInstance(alert).close();
            }
        });
    }, 5000);
});