/* =========================================================
   enhancements.js
   Site-wide behaviors loaded on every page (included from base.html).
   ========================================================= */
(function () {
    "use strict";

    document.addEventListener("DOMContentLoaded", function () {
        initImageSkeletons();
        initFloatingQuickNav();
        initProjectLightbox();
        initCardTilt();
        initProjectFilter();
        initSkillTagLinks();
        initChatbot();
        initProjectReviews();
        initParallax();
        initDetailModal();
    });

    /* ---------------- Skeleton loaders for images ---------------- */
    function initImageSkeletons() {
        document.querySelectorAll(".project-img img, .blog-card img").forEach(function (img) {
            const wrap = img.parentElement;
            if (!wrap || wrap.classList.contains("img-skeleton-wrap")) return;
            wrap.classList.add("img-skeleton-wrap");
            const skel = document.createElement("div");
            skel.className = "skeleton";
            wrap.insertBefore(skel, img);

            function markLoaded() {
                img.classList.add("loaded");
                skel.remove();
            }
            if (img.complete && img.naturalWidth > 0) {
                markLoaded();
            } else {
                img.addEventListener("load", markLoaded);
                img.addEventListener("error", markLoaded);
            }
        });
    }

    /* ---------------- Floating quick-nav (mobile) ---------------- */
    function initFloatingQuickNav() {
        if (document.querySelector(".floating-quicknav")) return;
        const links = [
            { href: "/", icon: "fa-home" },
            { href: "/projects", icon: "fa-code" },
            { href: "/skills", icon: "fa-cogs" },
            { href: "/blog", icon: "fa-blog" },
            { href: "/contact", icon: "fa-envelope" },
        ];
        const nav = document.createElement("nav");
        nav.className = "floating-quicknav";
        nav.innerHTML = links
            .map(function (l) {
                const active = window.location.pathname === l.href ? "active" : "";
                return `<a href="${l.href}" class="${active}"><i class="fas ${l.icon}"></i></a>`;
            })
            .join("");
        document.body.appendChild(nav);

        let lastScroll = 0;
        window.addEventListener(
            "scroll",
            function () {
                const y = window.scrollY;
                if (y > 240) {
                    nav.classList.add("visible");
                } else {
                    nav.classList.remove("visible");
                }
                lastScroll = y;
            },
            { passive: true }
        );
    }

    /* ---------------- Project image lightbox ---------------- */
    function initProjectLightbox() {
        const images = document.querySelectorAll(".project-img img");
        if (!images.length) return;

        let overlay = document.querySelector(".lightbox-overlay");
        if (!overlay) {
            overlay = document.createElement("div");
            overlay.className = "lightbox-overlay";
            overlay.innerHTML = `<span class="lightbox-close"><i class="fas fa-times"></i></span><img alt="Project preview">`;
            document.body.appendChild(overlay);
            overlay.addEventListener("click", function (e) {
                if (e.target === overlay || e.target.closest(".lightbox-close")) {
                    overlay.classList.remove("open");
                }
            });
            document.addEventListener("keydown", function (e) {
                if (e.key === "Escape") overlay.classList.remove("open");
            });
        }
        const overlayImg = overlay.querySelector("img");

        images.forEach(function (img) {
            img.addEventListener("click", function () {
                overlayImg.src = img.src;
                overlayImg.alt = img.alt;
                overlay.classList.add("open");
            });
        });
    }

    /* ---------------- 3D tilt effect on interactive cards ---------------- */
    function initCardTilt() {
        const cards = document.querySelectorAll(".project-card, .learning-card, .blog-card, .education-card");
        if (!cards.length || window.matchMedia("(hover: none)").matches) return;

        cards.forEach(function (card) {
            card.classList.add("tilt-card");
            card.addEventListener("mousemove", function (e) {
                const rect = card.getBoundingClientRect();
                const x = e.clientX - rect.left;
                const y = e.clientY - rect.top;
                const rotateX = ((y / rect.height) - 0.5) * -8;
                const rotateY = ((x / rect.width) - 0.5) * 8;
                card.style.transition = "transform 0.12s ease-out";
                card.style.transform = `perspective(900px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) translateY(-6px)`;
            });
            card.addEventListener("mouseleave", function () {
                card.style.transition = "transform 0.3s ease";
                card.style.transform = "";
            });
        });
    }

    /* ---------------- Interactive project filter ---------------- */
    function initProjectFilter() {
        const grid = document.querySelectorAll(".project-card");
        if (!grid.length) return;

        // Build category set from data-category attributes injected server-side.
        const cats = new Set();
        grid.forEach(function (card) {
            const c = card.closest("[data-category]");
            if (c) cats.add(c.getAttribute("data-category"));
        });
        if (!cats.size) return;

        const container = document.querySelector("#projects .section-header");
        if (!container || document.querySelector(".project-filter-bar")) return;

        const bar = document.createElement("div");
        bar.className = "project-filter-bar";
        const labels = {
            "ai-ml": "AI / ML",
            "data-analysis": "Data Analysis",
            "web-dev": "Web Dev",
            "python-tools": "Python Tools",
        };
        let chipsHtml = `<span class="filter-chip active" data-filter="all">All</span>`;
        cats.forEach(function (c) {
            chipsHtml += `<span class="filter-chip" data-filter="${c}">${labels[c] || c}</span>`;
        });
        bar.innerHTML = chipsHtml;
        container.after(bar);

        function applyFilter(value) {
            document.querySelectorAll(".filter-chip").forEach(function (c) {
                c.classList.toggle("active", c.getAttribute("data-filter") === value);
            });
            document.querySelectorAll("[data-category]").forEach(function (wrap) {
                const show = value === "all" || wrap.getAttribute("data-category") === value;
                wrap.classList.toggle("filtered-out", !show);
            });
        }

        bar.addEventListener("click", function (e) {
            const chip = e.target.closest(".filter-chip");
            if (!chip) return;
            applyFilter(chip.getAttribute("data-filter"));
        });

        // Support deep-linking from skill tags: /projects?tag=python
        const params = new URLSearchParams(window.location.search);
        const tag = params.get("tag");
        if (tag) {
            document.querySelectorAll("[data-category][data-tags]").forEach(function (wrap) {
                const tags = (wrap.getAttribute("data-tags") || "").split(",");
                if (!tags.includes(tag.toLowerCase())) {
                    wrap.classList.add("filtered-out");
                }
            });
        }
    }

    /* ---------------- Interactive skill tags -> filter projects ---------------- */
    function initSkillTagLinks() {
        document.querySelectorAll(".skill-chip").forEach(function (chip) {
            const text = chip.textContent.trim().split(" ")[0].toLowerCase().replace(/[^a-z0-9.+-]/g, "");
            if (!text) return;
            chip.classList.add("linked");
            chip.title = `See projects using ${chip.textContent.trim()}`;
            chip.addEventListener("click", function () {
                window.location.href = "/projects?tag=" + encodeURIComponent(text);
            });
        });
    }

    /* ---------------- AI Chatbot widget ---------------- */
    function initChatbot() {
        if (document.querySelector(".chatbot-fab")) return;

        const fab = document.createElement("button");
        fab.className = "chatbot-fab";
        fab.setAttribute("aria-label", "Open portfolio assistant");
        fab.innerHTML = '<i class="fas fa-robot"></i>';
        document.body.appendChild(fab);

        const panel = document.createElement("div");
        panel.className = "chatbot-panel";
        panel.innerHTML = `
            <div class="chatbot-header">
                <h5><i class="fas fa-robot"></i> Portfolio Assistant</h5>
                <span class="chatbot-close"><i class="fas fa-times"></i></span>
            </div>
            <div class="chatbot-messages" id="chatMessages">
                <div class="chat-bubble bot">Hi! Ask me about Ravi's projects, skills, or how to get in touch.</div>
            </div>
            <div class="chat-typing" id="chatTyping" style="display:none;">Assistant is typing…</div>
            <form class="chatbot-input-row" id="chatForm">
                <input type="text" id="chatInput" placeholder="Ask a question..." autocomplete="off">
                <button type="submit"><i class="fas fa-paper-plane"></i></button>
            </form>
        `;
        document.body.appendChild(panel);

        const history = [];
        fab.addEventListener("click", function () {
            panel.classList.add("open");
            document.getElementById("chatInput").focus();
        });
        panel.querySelector(".chatbot-close").addEventListener("click", function () {
            panel.classList.remove("open");
        });

        const messagesEl = document.getElementById("chatMessages");
        const typingEl = document.getElementById("chatTyping");

        function addBubble(text, who) {
            const b = document.createElement("div");
            b.className = "chat-bubble " + who;
            b.textContent = text;
            messagesEl.appendChild(b);
            messagesEl.scrollTop = messagesEl.scrollHeight;
        }

        document.getElementById("chatForm").addEventListener("submit", async function (e) {
            e.preventDefault();
            const input = document.getElementById("chatInput");
            const text = input.value.trim();
            if (!text) return;
            addBubble(text, "user");
            history.push({ role: "user", content: text });
            input.value = "";
            typingEl.style.display = "block";

            try {
                const res = await fetch("/api/chatbot", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ message: text, history: history }),
                });
                const data = await res.json();
                typingEl.style.display = "none";
                const reply = data.reply || "Sorry, I couldn't process that.";
                addBubble(reply, "bot");
                history.push({ role: "assistant", content: reply });
            } catch (err) {
                typingEl.style.display = "none";
                addBubble("Network error — please try again in a moment.", "bot");
            }
        });
    }
    /* ---------------- Project reviews & ratings ---------------- */
    function renderStars(container, avg) {
        const full = Math.round(avg || 0);
        container.textContent = "★".repeat(full) + "☆".repeat(5 - full);
    }

    function initProjectReviews() {
        const widgets = document.querySelectorAll(".rating-widget");
        widgets.forEach(function (widget) {
            const slug = widget.getAttribute("data-project-slug");
            const starsEl = widget.querySelector(".rating-stars");
            const summaryEl = widget.querySelector(".rating-summary");
            const toggleLink = widget.querySelector(".review-toggle-link");
            const form = widget.querySelector(".rating-form");
            const starPicker = widget.querySelector(".star-picker");
            const submitBtn = widget.querySelector(".submit-review-btn");

            fetch("/api/projects/" + encodeURIComponent(slug) + "/reviews")
                .then(function (r) { return r.json(); })
                .then(function (data) {
                    renderStars(starsEl, data.average_rating);
                    summaryEl.textContent = data.count
                        ? `${data.average_rating} (${data.count} review${data.count === 1 ? "" : "s"})`
                        : "No reviews yet";
                })
                .catch(function () {});

            if (toggleLink) {
                toggleLink.addEventListener("click", function () {
                    form.classList.toggle("open");
                });
            }

            if (starPicker) {
                const stars = starPicker.querySelectorAll("span");
                stars.forEach(function (star) {
                    star.addEventListener("click", function () {
                        const val = parseInt(star.getAttribute("data-star"), 10);
                        starPicker.setAttribute("data-value", val);
                        stars.forEach(function (s) {
                            s.classList.toggle("active", parseInt(s.getAttribute("data-star"), 10) <= val);
                        });
                    });
                });
            }

            if (submitBtn) {
                submitBtn.addEventListener("click", async function () {
                    const rating = parseInt(starPicker.getAttribute("data-value"), 10) || 0;
                    const name = widget.querySelector(".review-name").value.trim();
                    const comment = widget.querySelector(".review-comment").value.trim();
                    if (!rating || !name) {
                        alert("Please pick a star rating and enter your name.");
                        return;
                    }
                    submitBtn.disabled = true;
                    try {
                        const res = await fetch("/api/projects/" + encodeURIComponent(slug) + "/reviews", {
                            method: "POST",
                            headers: { "Content-Type": "application/json" },
                            body: JSON.stringify({ name: name, rating: rating, comment: comment }),
                        });
                        if (res.ok) {
                            form.classList.remove("open");
                            const refreshed = await fetch("/api/projects/" + encodeURIComponent(slug) + "/reviews").then(function (r) { return r.json(); });
                            renderStars(starsEl, refreshed.average_rating);
                            summaryEl.textContent = `${refreshed.average_rating} (${refreshed.count} review${refreshed.count === 1 ? "" : "s"})`;
                            widget.querySelector(".review-name").value = "";
                            widget.querySelector(".review-comment").value = "";
                        } else {
                            const err = await res.json();
                            alert(err.error || "Could not submit review.");
                        }
                    } catch (e) {
                        alert("Network error — please try again.");
                    } finally {
                        submitBtn.disabled = false;
                    }
                });
            }
        });
    }
    /* ---------------- Parallax scrolling ---------------- */
    function initParallax() {
        if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;

        // Background particle layer(s) drift slower than scroll = classic parallax depth.
        const layers = document.querySelectorAll(".floating-elements");
        const heroImg = document.querySelector(".profile-photo-container, .hero-image");
        if (!layers.length && !heroImg) return;

        let ticking = false;
        layers.forEach(function (l) { l.classList.add("parallax-layer"); });
        if (heroImg) heroImg.classList.add("parallax-layer");
        function onScroll() {
            if (ticking) return;
            ticking = true;
            requestAnimationFrame(function () {
                const y = window.scrollY;
                layers.forEach(function (layer) {
                    layer.style.transform = `translateY(${y * 0.15}px)`;
                });
                if (heroImg) {
                    heroImg.style.transform = `translateY(${y * -0.08}px)`;
                }
                ticking = false;
            });
        }
        window.addEventListener("scroll", onScroll, { passive: true });
    }

    /* ---------------- Read More -> centered detail modal ----------------
       Used by Project cards and My Learning cards. Cards show only a short
       preview; the full description/badges/rating/links live in the same
       DOM node and are physically moved into a shared modal when "Read
       More" is clicked, then moved back to their original spot when the
       modal is closed (so nothing is duplicated and every existing
       interactive bit - star ratings, review forms, links - keeps working).
    ------------------------------------------------------------------- */
    function initDetailModal() {
        if (document.getElementById("detailModalOverlay")) return;

        // Build the modal shell once and attach it to <body>.
        const overlay = document.createElement("div");
        overlay.className = "detail-modal-overlay";
        overlay.id = "detailModalOverlay";
        overlay.innerHTML =
            '<div class="detail-modal" id="detailModalCard">' +
            '<button type="button" class="detail-modal-close" id="detailModalClose" aria-label="Close">&times;</button>' +
            '<div class="detail-modal-body" id="detailModalBody"></div>' +
            "</div>";
        document.body.appendChild(overlay);

        const modalBody = overlay.querySelector("#detailModalBody");
        const closeBtn = overlay.querySelector("#detailModalClose");

        let movedNodes = []; // [{node, parent, next}]
        let activeReadMoreEl = null;

        function restoreMovedNodes() {
            movedNodes
                .slice()
                .reverse()
                .forEach(function (entry) {
                    entry.node.classList.remove("show-text");
                    if (entry.next && entry.next.parentNode === entry.parent) {
                        entry.parent.insertBefore(entry.node, entry.next);
                    } else {
                        entry.parent.appendChild(entry.node);
                    }
                });
            movedNodes = [];
        }

        function closeModal() {
            overlay.classList.remove("active");
            document.body.classList.remove("modal-open");
            if (activeReadMoreEl) {
                activeReadMoreEl.focus({ preventScroll: true });
                activeReadMoreEl = null;
            }
            window.setTimeout(function () {
                restoreMovedNodes();
                modalBody.innerHTML = "";
            }, 300);
        }

        function openModal(nodes, titleText, imgSrc, imgAlt, triggerEl) {
            restoreMovedNodes();
            modalBody.innerHTML = "";

            if (imgSrc) {
                const imgWrap = document.createElement("div");
                imgWrap.className = "detail-modal-img";
                const img = document.createElement("img");
                img.src = imgSrc;
                img.alt = imgAlt || "";
                imgWrap.appendChild(img);
                modalBody.appendChild(imgWrap);
            }

            if (titleText) {
                const h3 = document.createElement("h3");
                h3.className = "detail-modal-title";
                h3.textContent = titleText;
                modalBody.appendChild(h3);
            }

            nodes.forEach(function (node) {
                movedNodes.push({ node: node, parent: node.parentNode, next: node.nextSibling });
                modalBody.appendChild(node);
                node.classList.add("show-text");
            });

            activeReadMoreEl = triggerEl || null;
            overlay.classList.add("active");
            document.body.classList.add("modal-open");
            closeBtn.focus({ preventScroll: true });
        }

        closeBtn.addEventListener("click", closeModal);
        overlay.addEventListener("click", function (e) {
            if (e.target === overlay) closeModal();
        });
        document.addEventListener("keydown", function (e) {
            if (e.key === "Escape" && overlay.classList.contains("active")) closeModal();
        });

        function truncate(text, maxLen) {
            const clean = text.replace(/\s+/g, " ").trim();
            if (clean.length <= maxLen) return clean;
            return clean.slice(0, maxLen).replace(/\s+\S*$/, "") + "\u2026";
        }

        /* ---- Project cards ---- */
        document.querySelectorAll(".project-card").forEach(function (card) {
            const content = card.querySelector(".project-content");
            if (!content) return;
            const titleEl = content.querySelector(".project-title");
            const descEl = content.querySelector("p");
            if (!descEl || descEl.dataset.modalReady) return;
            descEl.dataset.modalReady = "1";

            const badges = content.querySelector(".project-badges");
            const rating = content.querySelector(".rating-widget");
            const actions = content.querySelector(".mt-3");

            descEl.classList.add("detail-only");
            [badges, rating, actions].forEach(function (el) {
                if (el) el.classList.add("detail-only");
            });

            const preview = document.createElement("p");
            preview.className = "card-preview-text";
            preview.textContent = truncate(descEl.textContent, 110);
            descEl.parentNode.insertBefore(preview, descEl);

            const btn = document.createElement("button");
            btn.type = "button";
            btn.className = "card-read-more";
            btn.innerHTML = '<span>Read More</span><i class="fas fa-arrow-right"></i>';
            preview.insertAdjacentElement("afterend", btn);

            btn.addEventListener("click", function (e) {
                e.stopPropagation();
                const nodes = [descEl];
                if (badges) nodes.push(badges);
                if (rating) nodes.push(rating);
                if (actions) nodes.push(actions);
                const imgEl = card.querySelector(".project-img img");
                openModal(
                    nodes,
                    titleEl ? titleEl.textContent.trim() : "",
                    imgEl ? imgEl.getAttribute("src") : "",
                    imgEl ? imgEl.getAttribute("alt") : "",
                    btn
                );
            });
        });

        /* ---- My Learning cards ---- */
        document.querySelectorAll(".learning-card").forEach(function (card) {
            const content = card.querySelector(".learning-content");
            if (!content) return;
            const oldBtn = content.querySelector(".read-more-btn");
            const fullText = content.querySelector(".full-text");
            if (!oldBtn || !fullText || oldBtn.dataset.modalReady) return;
            oldBtn.dataset.modalReady = "1";

            const titleEl = content.querySelector(".learning-title");
            const linkWrap = oldBtn.nextElementSibling; // wrapper div holding the LinkedIn/GitHub link
            if (linkWrap) linkWrap.classList.add("detail-only");

            // Replace the old expand-in-place button with a fresh one so no
            // stale toggle listeners remain, then wire it to open the modal.
            const btn = oldBtn.cloneNode(true);
            btn.className = "read-more-btn card-read-more";
            btn.innerHTML = '<span>Read More</span><i class="fas fa-arrow-right"></i>';
            oldBtn.parentNode.replaceChild(btn, oldBtn);

            btn.addEventListener("click", function (e) {
                e.preventDefault();
                e.stopPropagation();
                const nodes = [fullText];
                if (linkWrap) nodes.push(linkWrap);
                const imgEl = card.querySelector(".learning-img img");
                openModal(
                    nodes,
                    titleEl ? titleEl.textContent.trim() : "",
                    imgEl ? imgEl.getAttribute("src") : "",
                    imgEl ? imgEl.getAttribute("alt") : "",
                    btn
                );
            });
        });
    }
})();
