const hydrateIcons = () => {
	if (window.lucide) {
		lucide.createIcons();
	}
};

if (typeof window.requestIdleCallback === "function") {
	window.requestIdleCallback(hydrateIcons);
} else {
	window.setTimeout(hydrateIcons, 0);
}

const miniChat = document.querySelector(".mini-chat");

if (miniChat) {
	const observer = new IntersectionObserver(
		([entry]) => {
			if (entry.isIntersecting) {
				miniChat.classList.add("animate-chat");
				observer.unobserve(miniChat);
			}
		},
		{ threshold: 0.35 }
	);

	observer.observe(miniChat);
}