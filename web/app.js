// Telegram Web App initialization
let tg = window.Telegram.WebApp;
let currentSlide = 0;
let totalSlides = 13;
let userStats = null;
const API_BASE = 'http://localhost:5000/api';

// Initialize app
document.addEventListener('DOMContentLoaded', function() {
    console.log('App loaded');
    initTelegramApp();
    loadUserStats();
    
    // Simulate fingerprint detection after 2 seconds
    setTimeout(showSlides, 2000);
});

function initTelegramApp() {
    // Expand app to full height
    tg.expand();
    tg.setHeaderColor('transparent');
    tg.setBackgroundColor('#000000');
    
    // Log user data
    console.log('User:', tg.initDataUnsafe.user);
    
    // Enable close button
    tg.enableClosingConfirmation();
    
    // Set header color
    if (tg.setHeaderColor) {
        tg.setHeaderColor('#000000');
    }
}

function showSlides() {
    document.getElementById('loadingScreen').style.display = 'none';
    document.getElementById('slidesContainer').style.display = 'flex';
    document.getElementById('navButtons').style.display = 'flex';
    document.getElementById('slideIndicator').style.display = 'block';
    
    showSlide(0);
}

function loadUserStats() {
    // Get user ID from Telegram
    const userId = tg.initDataUnsafe?.user?.id || 12345;
    
    // Fetch stats from backend
    fetch(`/api/stats/${userId}`)
        .then(response => response.json())
        .then(data => {
            console.log('Stats loaded:', data);
            userStats = data;
            updateSlideStats();
        })
        .catch(error => {
            console.error('Error loading stats:', error);
            // Use mock data on error
            userStats = getMockStats(userId);
            updateSlideStats();
        });
}

function getMockStats(userId) {
    return {
        user_id: userId,
        join_date: '1,345 days ago',
        messages_count: 1531,
        voice_messages_count: 40734,
        round_videos_count: 4492,
        last_message_date: '2 December, 2025',
        most_used_time: 'Daytime 🌤',
        fastest_reply: '< 0.6 seconds',
        longest_reply: '68 hours',
        hidden_online_count: 2942,
        unsent_messages_count: 6648,
        longest_session: '16 days in a row',
        longest_ignore_period: '3 days in a row'
    };
}

function updateSlideStats() {
    if (!userStats) return;
    
    // Map stats to slides
    const statsMap = {
        1: userStats.join_date,
        2: userStats.messages_count.toLocaleString(),
        3: userStats.voice_messages_count.toLocaleString(),
        4: userStats.round_videos_count.toLocaleString(),
        5: userStats.most_used_time,
        6: userStats.last_message_date,
        7: userStats.fastest_reply,
        8: userStats.longest_reply,
        9: userStats.hidden_online_count.toLocaleString(),
        10: userStats.unsent_messages_count.toLocaleString(),
        11: userStats.longest_session,
        12: userStats.longest_ignore_period
    };
    
    // Update slide content
    for (let slideNum in statsMap) {
        const element = document.getElementById(`stat-${slideNum}`);
        if (element) {
            element.textContent = statsMap[slideNum];
        }
    }
}

function showSlide(slideNumber) {
    // Validate slide number
    if (slideNumber < 0) slideNumber = 0;
    if (slideNumber >= totalSlides) slideNumber = totalSlides - 1;
    
    currentSlide = slideNumber;
    
    // Remove all active classes
    document.querySelectorAll('.slide').forEach(slide => {
        slide.classList.remove('active', 'prev');
    });
    
    // Add active class to current slide
    const currentSlideElement = document.querySelector(`[data-slide="${slideNumber}"]`);
    if (currentSlideElement) {
        currentSlideElement.classList.add('active');
    }
    
    // Update buttons visibility
    const backBtn = document.getElementById('backBtn');
    const continueBtn = document.getElementById('continueBtn');
    
    backBtn.disabled = slideNumber === 0;
    continueBtn.textContent = slideNumber === totalSlides - 1 ? 'Start Over' : 'Continue';
    
    // Update slide indicator
    document.getElementById('currentSlide').textContent = slideNumber + 1;
    document.getElementById('totalSlides').textContent = totalSlides;
    
    // Animate emoji
    const emoji = currentSlideElement?.querySelector('.emoji-large');
    if (emoji) {
        emoji.style.animation = 'none';
        setTimeout(() => {
            emoji.style.animation = '';
        }, 10);
    }
    
    // Haptic feedback
    if (tg.HapticFeedback) {
        tg.HapticFeedback.impactOccurred('light');
    }
}

function nextSlide() {
    if (currentSlide === totalSlides - 1) {
        // Restart
        showSlide(0);
    } else {
        showSlide(currentSlide + 1);
    }
}

function previousSlide() {
    showSlide(currentSlide - 1);
}

// Keyboard navigation
document.addEventListener('keydown', function(event) {
    if (event.key === 'ArrowRight') {
        nextSlide();
    } else if (event.key === 'ArrowLeft') {
        previousSlide();
    }
});

// Swipe navigation
let touchStartX = 0;
let touchEndX = 0;

document.querySelector('.slides-container').addEventListener('touchstart', e => {
    touchStartX = e.changedTouches[0].screenX;
});

document.querySelector('.slides-container').addEventListener('touchend', e => {
    touchEndX = e.changedTouches[0].screenX;
    handleSwipe();
});

function handleSwipe() {
    if (touchEndX < touchStartX - 50) {
        // Swiped left
        nextSlide();
    } else if (touchEndX > touchStartX + 50) {
        // Swiped right
        previousSlide();
    }
}

// Log when app is closed
window.addEventListener('beforeunload', () => {
    console.log('App closed');
});

// Handle Telegram back button
tg.onEvent('backButtonClicked', function() {
    if (currentSlide > 0) {
        previousSlide();
    } else {
        tg.close();
    }
});

// Show back button if not on first slide
tg.BackButton.hide();
