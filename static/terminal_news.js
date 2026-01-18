
function renderStudyNews(newsItems) {
    if (!newsItems || newsItems.length === 0) return;

    const container = document.getElementById('studyNewsContainer');
    if (!container) {
        // Create container if it doesn't exist, append to studyContent
        const studyContent = document.getElementById('studyContent');
        if (studyContent) {
            const newsDiv = document.createElement('div');
            newsDiv.id = 'studyNewsContainer';
            newsDiv.style.marginTop = '30px';
            newsDiv.style.padding = '20px';
            newsDiv.style.borderTop = '1px solid #333';
            studyContent.appendChild(newsDiv);

            // Recursively call to render
            renderStudyNews(newsItems);
        }
        return;
    }

    const newsHTML = newsItems.map(item => `
            <div style="padding: 10px; border-bottom: 1px solid #222; margin-bottom: 5px;">
                <div style="color: #10b981; font-size: 10px; font-weight:700;">${item.source.toUpperCase()} • ${item.published}</div>
                <div style="color: #eee; font-size: 14px; margin: 4px 0;">
                    <a href="${item.link}" target="_blank" style="color: #eee; text-decoration: none; hover: text-decoration: underline;">${item.title}</a>
                </div>
                <div style="display: flex; gap: 5px; margin-top: 5px;">
                    <span style="background: #1f2937; color: #9ca3af; padding: 2px 6px; border-radius: 4px; font-size: 9px;">${item.sentiment}</span>
                    <span style="background: #1f2937; color: #9ca3af; padding: 2px 6px; border-radius: 4px; font-size: 9px;">IMPACT: ${item.impact}</span>
                </div>
            </div>
        `).join('');

    container.innerHTML = `
            <div style="color: #fff; font-size: 16px; font-weight: 700; margin-bottom: 15px;">Live Market Intelligence</div>
            ${newsHTML}
        `;
}
