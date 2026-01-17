// GSAP Animations for Finance-X Landing Page

// Register GSAP plugins
gsap.registerPlugin(ScrollTrigger);

// Particle Animation
const canvas = document.getElementById('particleCanvas');
const ctx = canvas.getContext('2d');

canvas.width = window.innerWidth;
canvas.height = window.innerHeight;

class Particle {
    constructor() {
        this.x = Math.random() * canvas.width;
        this.y = Math.random() * canvas.height;
        this.size = Math.random() * 2 + 1;
        this.speedX = Math.random() * 0.5 - 0.25;
        this.speedY = Math.random() * 0.5 - 0.25;
        this.opacity = Math.random() * 0.5 + 0.2;
    }

    update() {
        this.x += this.speedX;
        this.y += this.speedY;

        if (this.x > canvas.width) this.x = 0;
        if (this.x < 0) this.x = canvas.width;
        if (this.y > canvas.height) this.y = 0;
        if (this.y < 0) this.y = canvas.height;
    }

    draw() {
        ctx.fillStyle = `rgba(16, 185, 129, ${this.opacity})`;
        ctx.beginPath();
        ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
        ctx.fill();
    }
}

const particles = [];
for (let i = 0; i < 100; i++) {
    particles.push(new Particle());
}

function animateParticles() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    particles.forEach(particle => {
        particle.update();
        particle.draw();
    });

    // Draw connections
    particles.forEach((p1, i) => {
        particles.slice(i + 1).forEach(p2 => {
            const dx = p1.x - p2.x;
            const dy = p1.y - p2.y;
            const distance = Math.sqrt(dx * dx + dy * dy);

            if (distance < 100) {
                ctx.strokeStyle = `rgba(16, 185, 129, ${0.2 * (1 - distance / 100)})`;
                ctx.lineWidth = 1;
                ctx.beginPath();
                ctx.moveTo(p1.x, p1.y);
                ctx.lineTo(p2.x, p2.y);
                ctx.stroke();
            }
        });
    });

    requestAnimationFrame(animateParticles);
}

animateParticles();

// Resize canvas on window resize
window.addEventListener('resize', () => {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
});

// GSAP Timeline for Page Load Animation
const tl = gsap.timeline({ defaults: { ease: 'power3.out' } });

// Animate logo
tl.to('.logo-container', {
    opacity: 1,
    y: 0,
    duration: 1,
    delay: 0.3
});

// Animate title lines
tl.to('.hero-title', {
    opacity: 1,
    y: 0,
    duration: 1
}, '-=0.5');

// Animate description
tl.to('.hero-description', {
    opacity: 1,
    y: 0,
    duration: 0.8
}, '-=0.5');

// Animate mode cards with stagger
tl.to('.mode-card', {
    opacity: 1,
    y: 0,
    duration: 1,
    stagger: 0.2
}, '-=0.5');

// Animate feature items
tl.to('.feature-item', {
    opacity: 1,
    y: 0,
    duration: 0.8,
    stagger: 0.15
}, '-=0.5');

// Hover animations for mode cards
const modeCards = document.querySelectorAll('.mode-card');

modeCards.forEach(card => {
    const icon = card.querySelector('.mode-icon');
    const button = card.querySelector('.mode-button');

    card.addEventListener('mouseenter', () => {
        gsap.to(icon, {
            scale: 1.2,
            rotation: 10,
            duration: 0.3,
            ease: 'back.out(1.7)'
        });
    });

    card.addEventListener('mouseleave', () => {
        gsap.to(icon, {
            scale: 1,
            rotation: 0,
            duration: 0.3,
            ease: 'back.out(1.7)'
        });
    });
});

// Parallax effect on mouse move
document.addEventListener('mousemove', (e) => {
    const mouseX = e.clientX / window.innerWidth - 0.5;
    const mouseY = e.clientY / window.innerHeight - 0.5;

    gsap.to('.mode-card', {
        x: mouseX * 20,
        y: mouseY * 20,
        duration: 1,
        ease: 'power2.out'
    });

    gsap.to('.feature-item', {
        x: mouseX * 10,
        y: mouseY * 10,
        duration: 1.5,
        ease: 'power2.out'
    });
});

// Glowing effect on enterprise card
const enterpriseCard = document.getElementById('enterpriseCard');
if (enterpriseCard) {
    gsap.to(enterpriseCard, {
        boxShadow: '0 0 40px rgba(59, 130, 246, 0.3)',
        duration: 2,
        repeat: -1,
        yoyo: true,
        ease: 'sine.inOut'
    });
}

// Button click animation
document.querySelectorAll('.mode-button').forEach(button => {
    button.addEventListener('click', function (e) {
        const ripple = document.createElement('span');
        const rect = this.getBoundingClientRect();
        const size = Math.max(rect.width, rect.height);
        const x = e.clientX - rect.left - size / 2;
        const y = e.clientY - rect.top - size / 2;

        ripple.style.width = ripple.style.height = size + 'px';
        ripple.style.left = x + 'px';
        ripple.style.top = y + 'px';
        ripple.classList.add('ripple');

        this.appendChild(ripple);

        setTimeout(() => ripple.remove(), 600);
    });
});

// Add ripple CSS dynamically
const style = document.createElement('style');
style.textContent = `
    .mode-button {
        position: relative;
        overflow: hidden;
    }
    
    .ripple {
        position: absolute;
        border-radius: 50%;
        background: rgba(255, 255, 255, 0.6);
        transform: scale(0);
        animation: ripple-animation 0.6s ease-out;
        pointer-events: none;
    }
    
    @keyframes ripple-animation {
        to {
            transform: scale(4);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);

console.log('%c🚀 Finance-X Loaded', 'color: #10b981; font-size: 20px; font-weight: bold;');
console.log('%cGSAP Animations Active', 'color: #3b82f6; font-size: 14px;');
