/* app.js */

document.addEventListener('DOMContentLoaded', () => {
    // ── Tab Management ────────────────────────────────────────────────
    const navItems = document.querySelectorAll('.nav-item');
    const tabContents = document.querySelectorAll('.tab-content');

    navItems.forEach(item => {
        item.addEventListener('click', () => {
            const targetTab = item.getAttribute('data-tab');
            
            navItems.forEach(nav => nav.classList.remove('active'));
            item.classList.add('active');
            
            tabContents.forEach(tab => {
                if (tab.id === targetTab) {
                    tab.classList.add('active');
                } else {
                    tab.classList.remove('active');
                }
            });
            
            // Lazy load data if needed
            if (targetTab === 'colleges' && !window.collegesLoaded) {
                fetchDataAndRender();
            }
            if (targetTab === 'checklist' && !window.checklistLoaded) {
                fetchDataAndRender();
            }
        });
    });

    // ── Chat Logic ────────────────────────────────────────────────────
    const chatForm = document.getElementById('chat-form');
    const chatInput = document.getElementById('chat-input');
    const chatHistory = document.getElementById('chat-history');
    const sendBtn = document.getElementById('send-btn');

    // Make sure marked.js handles breaks
    if (typeof marked !== 'undefined') {
        marked.setOptions({ breaks: true });
    }

    function addMessage(content, type, isHtml = false) {
        const div = document.createElement('div');
        div.className = type === 'user' ? 'chat-user' : 'chat-ai';
        
        let label = '';
        if (type === 'user') {
            label = `<div class="chat-label label-user"><i class="ph-fill ph-user"></i> You</div>`;
        } else {
            // For general AI messages without specific intent
            label = `<div class="chat-label label-ai"><i class="ph-fill ph-robot"></i> AI Counselor</div>`;
        }

        const msgBody = isHtml ? content : (typeof marked !== 'undefined' ? marked.parse(content) : content);

        div.innerHTML = `
            ${label}
            <div class="msg-body">${msgBody}</div>
        `;
        chatHistory.appendChild(div);
        chatHistory.scrollTop = chatHistory.scrollHeight;
        return div; // Return DOM element in case we want to append more (like intent/sources)
    }

    function addTypingIndicator() {
        const div = document.createElement('div');
        div.className = 'chat-ai typing-indicator-container';
        div.id = 'typing-indicator';
        div.innerHTML = `
            <div class="chat-label label-ai"><i class="ph-fill ph-robot"></i> AI Counselor</div>
            <div class="typing-indicator">
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
            </div>
        `;
        chatHistory.appendChild(div);
        chatHistory.scrollTop = chatHistory.scrollHeight;
        return div;
    }

    function removeTypingIndicator() {
        const ind = document.getElementById('typing-indicator');
        if (ind) ind.remove();
    }
    
    function intentToCssClass(intent) {
        return `intent-${intent.replace(/_/g, '-')}`;
    }
    function intentToLabel(intent) {
        const map = {
            "checklist": "📋 Checklist",
            "eligibility": "✅ Eligibility",
            "documents": "📄 Documents",
            "deadlines": "📅 Deadlines",
            "scholarships": "💰 Scholarships",
            "fees": "💳 Fees",
            "comparison": "⚖️ Comparison",
            "entrance_exam": "📝 Entrance Exam",
            "general": "💬 General"
        };
        return map[intent] || `💬 ${intent}`;
    }

    chatForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const query = chatInput.value.trim();
        if (!query) return;

        addMessage(query, 'user');
        chatInput.value = '';
        sendBtn.disabled = true;
        
        addTypingIndicator();

        try {
            const res = await fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ query })
            });

            const data = await res.json();
            removeTypingIndicator();

            if (!res.ok) {
                addMessage(`Error: ${data.error || 'Server error'}`, 'ai', false);
            } else {
                const aiMsgDom = addMessage(data.answer, 'ai', false);
                
                // Add Intent Badge
                if (data.intent && data.intent !== 'general') {
                    const labelDiv = aiMsgDom.querySelector('.chat-label');
                    const badge = document.createElement('span');
                    badge.className = `intent-badge ${intentToCssClass(data.intent)}`;
                    badge.textContent = intentToLabel(data.intent);
                    labelDiv.appendChild(badge);
                }

                // Add Sources
                if (data.sources && data.sources.length > 0) {
                    const sourceContainer = document.createElement('div');
                    sourceContainer.className = 'source-container';
                    
                    const toggleBtn = document.createElement('button');
                    toggleBtn.className = 'source-toggle';
                    toggleBtn.innerHTML = `📚 ${data.sources.length} source(s) used <i class="ph ph-caret-down"></i>`;
                    
                    const sourceList = document.createElement('div');
                    sourceList.className = 'source-list';
                    sourceList.innerHTML = data.sources.map(src => `<div class="source-doc">📄 ${src}</div>`).join('');
                    
                    toggleBtn.onclick = () => {
                        sourceList.classList.toggle('open');
                        const icon = toggleBtn.querySelector('i');
                        icon.className = sourceList.classList.contains('open') ? 'ph ph-caret-up' : 'ph ph-caret-down';
                    };
                    
                    sourceContainer.appendChild(toggleBtn);
                    sourceContainer.appendChild(sourceList);
                    aiMsgDom.appendChild(sourceContainer);
                    chatHistory.scrollTop = chatHistory.scrollHeight;
                }
            }
        } catch (err) {
            removeTypingIndicator();
            addMessage(`Connectivity Error: ${err.message}`, 'ai');
        } finally {
            sendBtn.disabled = false;
            chatInput.focus();
        }
    });

    // ── Data Loading Logic (Colleges & Checklist) ─────────────────────
    let globalData = null;

    async function fetchDataAndRender() {
        if (globalData) return; // already loaded
        try {
            const res = await fetch('/api/data');
            if (res.ok) {
                globalData = await res.json();
                renderColleges(globalData.colleges || []);
                renderChecklist(globalData.admission_checklist || []);
                window.collegesLoaded = true;
                window.checklistLoaded = true;
            } else {
                document.getElementById('colleges-grid').innerHTML = `<div class="loader">Error loading data.</div>`;
                document.getElementById('checklist-timeline').innerHTML = `<div class="loader">Error loading data.</div>`;
            }
        } catch (err) {
            console.error('Failed to fetch data', err);
        }
    }

    function renderColleges(colleges) {
        const grid = document.getElementById('colleges-grid');
        grid.innerHTML = '';
        
        if (colleges.length === 0) {
            grid.innerHTML = `<div class="loader">No colleges found.</div>`;
            return;
        }

        colleges.forEach(col => {
            const card = document.createElement('div');
            card.className = 'college-card';
            
            const metaTags = [];
            if(col.type) metaTags.push(`<span class="meta-tag"><i class="ph ph-buildings"></i> ${col.type}</span>`);
            if(col.location) metaTags.push(`<span class="meta-tag"><i class="ph ph-map-pin"></i> ${col.location}</span>`);
            if(col.ranking && col.ranking.NIRF_2024) metaTags.push(`<span class="meta-tag"><i class="ph ph-trophy"></i> NIRF: ${col.ranking.NIRF_2024}</span>`);
            
            let html = `
                <h3 class="college-name">${col.name}</h3>
                <div class="college-meta">${metaTags.join('')}</div>
            `;
            
            if (col.courses && col.courses.length > 0) {
                 html += `<div class="programs-list">`;
                 col.courses.slice(0, 3).forEach(c => {
                     html += `
                        <div class="program-item">
                            <div class="program-name">${c.name}</div>
                            <div class="program-details">
                                <span>${c.duration}</span>
                                <span>⭐ ${c.seats} seats</span>
                            </div>
                        </div>
                     `;
                 });
                 if(col.courses.length > 3) {
                     html += `<div style="font-size:0.8rem; color:var(--text-muted); text-align:center; margin-top:8px;">+ ${col.courses.length - 3} more programs</div>`;
                 }
                 html += `</div>`;
            }
            
            card.innerHTML = html;
            grid.appendChild(card);
        });

        // Search logic
        const searchInput = document.getElementById('college-search');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => {
                const term = e.target.value.toLowerCase();
                const cards = grid.querySelectorAll('.college-card');
                cards.forEach(card => {
                    const name = card.querySelector('.college-name').textContent.toLowerCase();
                    card.style.display = name.includes(term) ? 'flex' : 'none';
                });
            });
        }
    }

    function renderChecklist(checklist) {
        const timeline = document.getElementById('checklist-timeline');
        timeline.innerHTML = '';
        
        if(checklist.length === 0) {
            timeline.innerHTML = '<div class="loader">No checklist items found.</div>';
            return;
        }

        checklist.forEach((item, index) => {
            const div = document.createElement('div');
            div.className = 'timeline-item';
            
            const tasksHtml = item.tasks ? item.tasks.map(t => `<li>${t}</li>`).join('') : '';
            
            div.innerHTML = `
                <div class="timeline-dot"></div>
                <div class="timeline-header">
                    <h3 class="timeline-phase">Phase ${item.phase || (index+1)}: ${item.title || item.step || ''}</h3>
                    <span class="timeline-status">Pending</span>
                </div>
                <p style="color: var(--text-main); margin-bottom: 16px;">${item.description || ''}</p>
                ${tasksHtml ? `<ul class="timeline-tasks">${tasksHtml}</ul>` : ''}
                ${item.deadline ? `<div class="timeline-deadline"><i class="ph ph-clock"></i> Deadline: ${item.deadline}</div>` : ''}
            `;
            timeline.appendChild(div);
        });
    }
});
