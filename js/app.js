const API_URL = window.location.origin;

const FUN_FACTS = {
    "القلب البشري": "القلب يضخ ما يكفي من الدم في حياة الإنسان لملء حوض سباحة بطول 10 كيلومترات!",
    "الدماغ البشري": "الدماغ يستهلك حوالي 20% من طاقة الجسم رغم أنه لا يمثل سوى 2% من وزنه.",
    "العين البشرية": "العين البشرية تستطيع تمييز ما يزيد عن 10 ملايين لون مختلف!",
    "الرئتان البشريتان": "إذا فرشنا سطح الحويصلات الهوائية في الرئتين، سيغطي مساحة 70 متراً مربعاً!",
    "الكلية البشرية": "الكليتان تصفيان كامل دم الجسم (5 لترات) حوالي 40 مرة يومياً.",
};

// DOM refs
const heroSection = document.getElementById('hero');
const viewerSection = document.getElementById('viewerSection');
const promptInput = document.getElementById('promptInput');
const generateBtn = document.getElementById('generateBtn');
const backBtn = document.getElementById('backBtn');
const arBtn = document.getElementById('arBtn');
const modelViewer = document.getElementById('modelViewer');
const sketchfabViewer = document.getElementById('sketchfabViewer');
const loadingState = document.getElementById('loadingState');
const cancelSelection = document.getElementById('cancelSelection');
const selectionModal = document.getElementById('selectionModal');
const candidatesGrid = document.getElementById('candidatesGrid');
const infoPanel = document.querySelector('.info-panel');
const navTitle = document.getElementById('navTitle');
const organName = document.getElementById('organName');
const organDesc = document.getElementById('organDesc');
const partsList = document.getElementById('partsList');
const funFact = document.getElementById('funFact');
const suggestionsSection = document.getElementById('suggestionsSection');
const suggestionsList = document.getElementById('suggestionsList');

function quickSearch(query) {
    const hiddenSelect = document.getElementById('categorySelect');
    hiddenSelect.value = 'medical_anatomy';
    
    // Sync custom dropdown UI
    const dropdown = document.getElementById('categoryDropdown');
    const medicalOption = dropdown.querySelector('.dropdown-option[data-value="medical_anatomy"]');
    if (medicalOption) {
        selectDropdownOption(medicalOption);
    }

    promptInput.value = query;
    handleGenerate();
}

// Custom Dropdown Logic
function initCustomDropdown() {
    const dropdown = document.getElementById('categoryDropdown');
    if (!dropdown) return;

    const selectedDiv = dropdown.querySelector('.dropdown-selected');
    const optionsDiv = dropdown.querySelector('.dropdown-options');
    const hiddenInput = document.getElementById('categorySelect');

    selectedDiv.onclick = (e) => {
        e.stopPropagation();
        optionsDiv.classList.toggle('hidden');
        dropdown.classList.toggle('active');
        console.log("Dropdown Toggled");
    };

    dropdown.querySelectorAll('.dropdown-option').forEach(option => {
        option.onclick = (e) => {
            e.stopPropagation();
            console.log("Option selected:", option.getAttribute('data-value'));
            selectDropdownOption(option);
            optionsDiv.classList.add('hidden');
            dropdown.classList.remove('active');
        };
    });

    document.addEventListener('click', () => {
        optionsDiv.classList.add('hidden');
        dropdown.classList.remove('active');
    });
}

function selectDropdownOption(optionEl) {
    const dropdown = document.getElementById('categoryDropdown');
    const selectedDiv = dropdown.querySelector('.dropdown-selected');
    const hiddenInput = document.getElementById('categorySelect');
    
    // Remove selected class from others
    dropdown.querySelectorAll('.dropdown-option').forEach(opt => opt.classList.remove('selected'));
    optionEl.classList.add('selected');

    // Update hidden input
    const val = optionEl.getAttribute('data-value');
    hiddenInput.value = val;

    // Update displaying selected content (SVG + Text)
    selectedDiv.innerHTML = optionEl.innerHTML;
}

// Initialize on load
console.log("Initializing Custom Dropdown...");
initCustomDropdown();


async function handleGenerate() {
    const prompt = promptInput.value.trim();
    const category = document.getElementById('categorySelect').value;
    if (!prompt) {
        promptInput.focus();
        promptInput.style.borderColor = 'rgba(239, 68, 68, 0.5)';
        setTimeout(() => promptInput.style.borderColor = '', 2000);
        return;
    }
    
    generateBtn.disabled = true;
    const btnText = generateBtn.querySelector('.btn-text');
    btnText.textContent = 'جاري تحليل المجسم...';
    
    const loadingStages = [
        'جاري تحليل الفكرة...',
        'جاري نحت المجسم بواسطة الذكاء الاصطناعي...',
        'جاري تلوين الأنسجة وتدقيق التفاصيل...',
        'أوشكنا على الانتهاء... استعد للنتيجة'
    ];
    let currentStage = 0;
    const stageInterval = setInterval(() => {
        if (currentStage < loadingStages.length - 1) {
            currentStage++;
            btnText.textContent = loadingStages[currentStage];
        }
    }, 8000);
    
    try {
        const res = await fetch(`${API_URL}/generate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ prompt, category })
        });
        
        if (!res.ok) throw new Error(`HTTP Error: ${res.status}`);
        const data = await res.json();
        
        if (data.status === 'success') {
            if (data.candidates && data.candidates.length > 1) {
                showSelectionScreen(data);
                return;
            }
            displayOrgan(data);
        } else {
            console.error('Generation Error:', data);
            alert('حدث خطأ أثناء البحث، جرب كلمات أخرى.');
        }
    } catch (err) {
        console.error('API Error:', err);
        alert('حدث خطأ في الاتصال بالخادم. تأكد من تشغيل python backend/main.py');
    } finally {
        clearInterval(stageInterval);
        generateBtn.disabled = false;
        btnText.textContent = 'استكشف';
    }
}

function resetUI() {
    infoPanel.classList.remove('active');
    viewerSection.classList.add('hidden');
    heroSection.classList.remove('hidden');
    
    // Force visibility reset for animated elements
    const animatedElements = heroSection.querySelectorAll('.fade-in, .slide-up');
    animatedElements.forEach(el => {
        el.style.opacity = '1';
        el.style.transform = 'translateY(0)';
        el.style.animation = 'none';
    });

    if (suggestionsSection) suggestionsSection.classList.add('hidden');
}

function showSelectionScreen(data) {
    heroSection.classList.add('hidden');
    viewerSection.classList.remove('hidden');
    loadingState.style.display = 'none';
    candidatesGrid.innerHTML = '';
    selectionModal.classList.remove('hidden');

    data.candidates.forEach((cand) => {
        const card = document.createElement('div');
        card.className = 'selection-card';
        card.innerHTML = `
            <div class="card-image-bg" style="background-image: url('${cand.thumbnail || 'https://via.placeholder.com/300x200?text=No+Preview'}');"></div>
            <div class="card-info">
                <div style="font-size: 0.7rem; color: var(--primary); opacity: 0.5; margin-bottom: 5px;">DATA_STREAM: SUCCESS</div>
                <h3>${cand.name}</h3>
                <button class="btn-select">تحديد الهدف [SELECT]</button>
            </div>
        `;
        card.onclick = () => {
            selectionModal.classList.add('hidden');
            const selectedData = { ...data, sketchfab_id: cand.uid, name: cand.name };
            displayOrgan(selectedData);
        };
        candidatesGrid.appendChild(card);
    });
}

cancelSelection.onclick = () => {
    selectionModal.classList.add('hidden');
    resetUI(); // Use the new resetUI function
};

function displayOrgan(data) {
    heroSection.classList.add('hidden');
    viewerSection.classList.remove('hidden');
    
    loadingState.style.display = 'flex';
    navTitle.textContent = data.name;
    
    // Trigger Sidebar Slide-in
    setTimeout(() => infoPanel.classList.add('active'), 100);

    modelViewer.classList.add('hidden');
    sketchfabViewer.classList.add('hidden');
    modelViewer.removeAttribute('src');
    sketchfabViewer.src = '';
    
    if (data.sketchfab_id) {
        sketchfabViewer.classList.remove('hidden');
        sketchfabViewer.src = `https://sketchfab.com/models/${data.sketchfab_id}/embed?autostart=1&internal=1&tracking=0&ui_ar=1`;
        loadingState.style.display = 'none';
        
        // Show panel for Sketchfab
        infoPanel.classList.remove('hidden');
        setTimeout(() => infoPanel.classList.add('active'), 50);
    } else {
        modelViewer.classList.remove('hidden');
        requestAnimationFrame(() => {
            let finalUrl = data.model_url;
            if (finalUrl.startsWith('/')) finalUrl = API_URL + finalUrl;
            modelViewer.src = finalUrl;
        });
    }
    
    arBtn.onclick = () => modelViewer.activateAR();
    organName.textContent = data.name;
    organDesc.textContent = data.description;
    partsList.innerHTML = '';
    
    const existingHotspots = modelViewer.querySelectorAll('.hotspot');
    existingHotspots.forEach(hs => hs.remove());

    const anchorPoints = [
        "0.05m 0.08m 0.1m", "-0.05m 0.05m 0.12m", "0.0m -0.05m 0.1m", 
        "0.08m -0.02m 0.05m", "-0.06m 0.1m 0.05m"
    ];

    data.parts.forEach((part, i) => {
        const card = document.createElement('div');
        card.className = 'part-card';
        card.style.animationDelay = `${i * 0.06}s`;
        card.innerHTML = `<div class="part-name">${part.name}</div><div class="part-info">${part.info}</div>`;
        partsList.appendChild(card);

        if (i < anchorPoints.length) {
            const hotspot = document.createElement('button');
            hotspot.className = 'hotspot';
            hotspot.slot = `hotspot-${i}`;
            hotspot.setAttribute('data-position', anchorPoints[i]);
            hotspot.setAttribute('data-normal', "0m 1m 0m");
            hotspot.innerHTML = `
                <div class="annotation-label">
                    <strong>${part.name}</strong><br>
                    ${part.info.substring(0, 40)}${part.info.length > 40 ? '...' : ''}
                </div>
            `;
            hotspot.onclick = () => {
                card.scrollIntoView({ behavior: 'smooth', block: 'center' });
                card.style.borderColor = 'var(--accent)';
                setTimeout(() => card.style.borderColor = '', 2000);
            };
            modelViewer.appendChild(hotspot);
        }
    });
    
    funFact.innerHTML = '';
    const factsArray = (data.quick_facts && data.quick_facts.length > 0) ? data.quick_facts : ['جسم الإنسان يحتوي على أكثر من 37 تريليون خلية تعمل بتناسق مذهل!'];
    factsArray.forEach(factText => {
        const factDiv = document.createElement('div');
        factDiv.style.marginBottom = '8px';
        factDiv.textContent = '💡 ' + factText;
        funFact.appendChild(factDiv);
    });
    
    suggestionsList.innerHTML = '';
    if (data.suggestions && data.suggestions.length > 0) {
        suggestionsSection.classList.remove('hidden');
        data.suggestions.forEach(sug => {
            const chip = document.createElement('div');
            chip.className = 'suggestion-chip';
            chip.textContent = sug.name;
            chip.onclick = () => quickSearch(sug.query || sug.name);
            suggestionsList.appendChild(chip);
        });
    } else {
        suggestionsSection.classList.add('hidden');
    }
    
    let loadTimeout;
    const onModelLoad = () => {
        clearTimeout(loadTimeout);
        loadingState.style.display = 'none';
        infoPanel.classList.remove('hidden');
        infoPanel.classList.add('animate-in');
    };
    
    const onModelError = () => {
        clearTimeout(loadTimeout);
        loadingState.style.display = 'none';
        alert('⚠️ تعذر تحميل المجسم ثلاثي الأبعاد.');
        infoPanel.classList.remove('hidden');
        infoPanel.classList.add('animate-in');
    };
    
    if (!data.sketchfab_id) {
        loadTimeout = setTimeout(() => {
            modelViewer.removeEventListener('load', onModelLoad);
            modelViewer.removeEventListener('error', onModelError);
            loadingState.style.display = 'none';
            infoPanel.classList.remove('hidden');
            setTimeout(() => infoPanel.classList.add('active'), 50);
        }, 45000);
        modelViewer.addEventListener('load', onModelLoad, { once: true });
        modelViewer.addEventListener('error', onModelError, { once: true });
    }
}

backBtn.addEventListener('click', () => {
    viewerSection.classList.add('hidden');
    heroSection.classList.remove('hidden');
    modelViewer.src = '';
});

promptInput.addEventListener('keydown', e => {
    if (e.key === 'Enter') handleGenerate();
});

generateBtn.addEventListener('click', handleGenerate);
