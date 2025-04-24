// File: script.js (Lengkap - Dengan Guest Quiz Start AKTIF)

// --- Konfigurasi & State ---
const API_BASE_URL = "http://localhost:8000/api/v1";
let currentQuizSessionId = null;
let questions = [];
let currentQuestionIndex = 0;
let userAnswers = [];
let isLoggedIn = false;
let authToken = localStorage.getItem('authToken');
let currentUserEmail = null;
let isGuestMode = false;
let guestInfo = { name: null, status: null, institution: null };

// --- Referensi Elemen DOM ---
const setupDiv = document.getElementById('quiz-setup'); /* ... dan semua elemen lain ... */
const quizActiveDiv = document.getElementById('quiz-active'); const resultsDiv = document.getElementById('quiz-results'); const loadingIndicator = document.getElementById('loading-indicator'); const historySection = document.getElementById('history-section'); const historyListDiv = document.getElementById('history-list'); const authArea = document.getElementById('auth-area'); const loggedOutView = document.getElementById('logged-out-view'); const loggedInView = document.getElementById('logged-in-view'); const userEmailSpan = document.getElementById('user-email'); const showLoginBtn = document.getElementById('show-login-btn'); const showRegisterBtn = document.getElementById('show-register-btn'); const logoutBtn = document.getElementById('logout-btn'); const showHistoryBtn = document.getElementById('show-history-btn'); const closeHistoryBtn = document.getElementById('close-history-btn'); const loginFormSection = document.getElementById('login-form-section'); const registerFormSection = document.getElementById('register-form-section'); const loginForm = document.getElementById('login-form'); const registerForm = document.getElementById('register-form'); const loginEmailInput = document.getElementById('login-email'); const loginPasswordInput = document.getElementById('login-password'); const loginErrorDiv = document.getElementById('login-error'); const registerEmailInput = document.getElementById('register-email'); const registerPasswordInput = document.getElementById('register-password'); const registerErrorDiv = document.getElementById('register-error'); const cancelLoginBtn = document.getElementById('cancel-login-btn'); const cancelRegisterBtn = document.getElementById('cancel-register-btn'); const categorySelectorDiv = document.getElementById('category-selector'); const categoryLoadingP = document.getElementById('category-loading'); const selectAllButton = document.getElementById('select-all-btn'); const deselectAllButton = document.getElementById('deselect-all-btn'); const startFeedbackDiv = document.getElementById('start-feedback'); const startButton = document.getElementById('start-quiz-btn'); const questionCategorySpan = document.getElementById('question-category'); const questionTextP = document.getElementById('question-text'); const optionsContainer = document.getElementById('options-container'); const questionCounterSpan = document.getElementById('question-counter'); const feedbackDiv = document.getElementById('feedback'); const nextButton = document.getElementById('next-question-btn'); const finalScoreSpan = document.getElementById('final-score'); const correctCountSpan = document.getElementById('correct-count'); const totalCountSpan = document.getElementById('total-count'); const categoryAnalysisDiv = document.getElementById('category-analysis'); const recommendationsDiv = document.getElementById('recommendations'); const recommendationsLoadingP = document.getElementById('recommendations-loading'); const resetButton = document.getElementById('reset-quiz-btn'); const guestPromptModal = document.getElementById('guest-prompt-modal'); const guestInfoModal = document.getElementById('guest-info-modal'); const promptLoginBtn = document.getElementById('prompt-login-btn'); const promptRegisterBtn = document.getElementById('prompt-register-btn'); const promptGuestBtn = document.getElementById('prompt-guest-btn'); const promptCancelBtn = document.getElementById('prompt-cancel-btn'); const guestInfoForm = document.getElementById('guest-info-form'); const guestNameInput = document.getElementById('guest-name'); const guestStatusSelect = document.getElementById('guest-status'); const guestSchoolInputDiv = document.getElementById('guest-school-input'); const guestSchoolInput = document.getElementById('guest-school'); const guestUniversityInputDiv = document.getElementById('guest-university-input'); const guestUniversityInput = document.getElementById('guest-university'); const guestInfoErrorDiv = document.getElementById('guest-info-error'); const cancelGuestInfoBtn = document.getElementById('cancel-guest-info-btn');

// --- Fungsi Utilitas UI ---
function showLoading() { loadingIndicator.classList.remove('hidden'); loadingIndicator.classList.add('flex'); }
function hideLoading() { loadingIndicator.classList.add('hidden'); loadingIndicator.classList.remove('flex'); }

// function showView(viewToShow) { setupDiv.classList.add('hidden'); quizActiveDiv.classList.add('hidden'); resultsDiv.classList.add('hidden'); loginFormSection.classList.add('hidden'); registerFormSection.classList.add('hidden'); historySection.classList.add('hidden'); guestPromptModal.classList.add('hidden'); guestInfoModal.classList.add('hidden'); guestPromptModal.classList.remove('flex'); guestInfoModal.classList.remove('flex'); if (viewToShow === 'setup') setupDiv.classList.remove('hidden'); else if (viewToShow === 'quiz') quizActiveDiv.classList.remove('hidden'); else if (viewToShow === 'results') resultsDiv.classList.remove('hidden'); else if (viewToShow === 'login') loginFormSection.classList.remove('hidden'); else if (viewToShow === 'register') registerFormSection.classList.remove('hidden'); else if (viewToShow === 'history') historySection.classList.remove('hidden'); else if (viewToShow === 'guestPrompt') guestPromptModal.classList.remove('hidden'); guestPromptModal.classList.add('flex'); else if (viewToShow === 'guestInfo') guestInfoModal.classList.remove('hidden'); guestInfoModal.classList.add('flex'); }

// File: script.js (Ganti fungsi showView yang lama dengan ini)

function showView(viewToShow) {
    console.log(`Attempting to show view: ${viewToShow}`); // Tambah log untuk debug

    // Daftar semua elemen view/modal yang bisa ditampilkan/disembunyikan
    const allViews = [
        setupDiv, quizActiveDiv, resultsDiv,
        loginFormSection, registerFormSection,
        historySection, guestPromptModal, guestInfoModal
    ];

    // Sembunyikan semua view terlebih dahulu
    allViews.forEach(view => {
        if (view) { // Pastikan elemen tidak null
            view.classList.add('hidden');
            view.classList.remove('flex'); // Hapus flex jika ada (untuk modal)
        } else {
            // Jika ada view yang null, mungkin ada typo di getElementById atau ID di HTML
            // console.warn("Warning: One view element is null during hide all.");
        }
    });

    // Tampilkan view yang diminta
    let viewElementToShow = null;
    switch (viewToShow) {
        case 'setup':
            viewElementToShow = setupDiv;
            break;
        case 'quiz':
            viewElementToShow = quizActiveDiv;
            break;
        case 'results':
            viewElementToShow = resultsDiv;
            break;
        case 'login':
            viewElementToShow = loginFormSection;
            break;
        case 'register':
            viewElementToShow = registerFormSection;
            break;
        case 'history':
            viewElementToShow = historySection;
            break;
        case 'guestPrompt':
            viewElementToShow = guestPromptModal;
            // Modal perlu 'flex' untuk tampil di tengah overlay
            if (viewElementToShow) viewElementToShow.classList.add('flex');
            break;
        case 'guestInfo':
            viewElementToShow = guestInfoModal;
            // Modal perlu 'flex' untuk tampil di tengah overlay
            if (viewElementToShow) viewElementToShow.classList.add('flex');
            break;
        default:
            console.warn(`showView called with unknown view: ${viewToShow}. Defaulting to setup.`);
            viewElementToShow = setupDiv; // Default ke setup jika nama tidak dikenal
    }

    // Tampilkan elemen yang dipilih jika elemennya ada
    if (viewElementToShow) {
        viewElementToShow.classList.remove('hidden');
        console.log(`Successfully displayed view: ${viewToShow}`);
    } else {
        console.error(`Element for view '${viewToShow}' not found! Check getElementById references.`);
        // Jika elemen penting tidak ditemukan, mungkin fallback ke setup
        if (setupDiv) setupDiv.classList.remove('hidden');
    }
}

// --- Fungsi Update UI Auth ---

function updateAuthUI() { if (isLoggedIn) { loggedOutView.classList.add('hidden'); loggedInView.classList.remove('hidden'); userEmailSpan.textContent = currentUserEmail || 'User'; userEmailSpan.title = currentUserEmail || 'Logged In User'; if(showHistoryBtn) showHistoryBtn.classList.remove('hidden'); } else { loggedOutView.classList.remove('hidden'); loggedInView.classList.add('hidden'); userEmailSpan.textContent = ''; userEmailSpan.title = ''; if(historySection) historySection.classList.add('hidden'); if(showHistoryBtn) showHistoryBtn.classList.add('hidden'); } if(isLoggedIn){ loginFormSection.classList.add('hidden'); registerFormSection.classList.add('hidden'); } }


// async function handleRegister(event) {

// --- Fungsi Auth API Calls ---
async function handleRegister(event) { event.preventDefault(); registerErrorDiv.textContent = ''; showLoading(); const email = registerEmailInput.value; const password = registerPasswordInput.value; try { const response = await fetch(`${API_BASE_URL}/auth/register`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ email, password }), }); const data = await response.json(); if (!response.ok) { throw new Error(data.detail || `Registrasi gagal (Status: ${response.status})`); } console.log('Registrasi berhasil:', data); alert('Registrasi berhasil! Silakan login.'); showView('login'); registerForm.reset(); } catch (error) { console.error("Error registering:", error); registerErrorDiv.textContent = error.message; } finally { hideLoading(); } }
async function handleLogin(event) { event.preventDefault(); loginErrorDiv.textContent = ''; showLoading(); const email = loginEmailInput.value; const password = loginPasswordInput.value; try { const formData = new FormData(); formData.append('username', email); formData.append('password', password); const response = await fetch(`${API_BASE_URL}/auth/login`, { method: 'POST', body: formData, }); const data = await response.json(); if (!response.ok) { throw new Error(data.detail || `Login gagal (Status: ${response.status}).`); } console.log('Login berhasil:', data); authToken = data.access_token; if (!authToken) throw new Error("Token tidak diterima."); localStorage.setItem('authToken', authToken); isLoggedIn = true; currentUserEmail = email; await fetchUserInfo(); showView('setup'); loginForm.reset(); } catch (error) { console.error("Error logging in:", error); loginErrorDiv.textContent = error.message; isLoggedIn = false; authToken = null; localStorage.removeItem('authToken'); updateAuthUI(); } finally { hideLoading(); } }
function handleLogout() { showLoading(); console.log("Logging out..."); authToken = null; localStorage.removeItem('authToken'); isLoggedIn = false; currentUserEmail = null; isGuestMode = false; guestInfo = { name: null, status: null, institution: null }; updateAuthUI(); showView('setup'); console.log("Logged out."); hideLoading(); }
async function fetchUserInfo() { authToken = localStorage.getItem('authToken'); if (!authToken) { console.log("No auth token."); isLoggedIn = false; currentUserEmail = null; updateAuthUI(); return; } console.log("Found token, fetching user info..."); if (!isLoggedIn) showLoading(); try { const response = await fetch(`${API_BASE_URL}/users/me`, { method: 'GET', headers: { 'Authorization': `Bearer ${authToken}` } }); if (response.status === 401) { throw new Error('Sesi tidak valid.'); } if (!response.ok) { const errorData = await response.json().catch(() => ({detail: `Gagal ambil data user (${response.status})`})); throw new Error(errorData.detail); } const userData = await response.json(); currentUserEmail = userData.email; isLoggedIn = true; console.log("User info fetched:", userData); } catch (error) { console.error("Error fetching user info:", error.message); handleLogout(); } finally { updateAuthUI(); hideLoading(); } }

// --- Fungsi Memuat Kategori ---
async function fetchAndDisplayCategories() { categoryLoadingP.classList.remove('hidden'); try { const response = await fetch(`${API_BASE_URL}/quiz/categories`); if (!response.ok) throw new Error(`Gagal memuat kategori: ${response.statusText}`); const categories = await response.json(); categoryLoadingP.classList.add('hidden'); categorySelectorDiv.innerHTML = ''; if (categories && categories.length > 0) { categories.sort((a, b) => a.name.localeCompare(b.name)); categories.forEach(cat => { const div = document.createElement('div'); div.classList.add('flex', 'items-center', 'mb-2'); const checkbox = document.createElement('input'); checkbox.type = 'checkbox'; checkbox.id = `cat-${cat.id}`; checkbox.value = cat.id; checkbox.name = 'category'; checkbox.classList.add('mr-2', 'h-4', 'w-4', 'text-blue-600', 'bg-gray-100', 'border-gray-300', 'rounded', 'focus:ring-blue-500'); const label = document.createElement('label'); label.htmlFor = `cat-${cat.id}`; label.textContent = cat.name; label.classList.add('ms-2', 'text-sm', 'font-medium', 'text-gray-900'); div.appendChild(checkbox); div.appendChild(label); categorySelectorDiv.appendChild(div); }); } else { categorySelectorDiv.innerHTML = '<p class="text-red-500 italic">Tidak ada kategori.</p>'; } } catch (error) { console.error("Error fetching categories:", error); categoryLoadingP.classList.add('hidden'); categorySelectorDiv.innerHTML = `<p class="text-red-500 italic">${error.message || 'Gagal hubungi server.'}</p>`; } }

// --- Fungsi Logika Kuis ---
async function fetchQuizQuestions() { // Hanya untuk user login
    // Cek login sudah di event listener
    showLoading(); startFeedbackDiv.textContent = '';
    const selectedCategoryCheckboxes = document.querySelectorAll('#category-selector input[name="category"]:checked'); const selectedCategoryIds = Array.from(selectedCategoryCheckboxes).map(cb => cb.value);
    const amount = 10; console.log("Selected Category IDs:", selectedCategoryIds);
    let apiUrl = `${API_BASE_URL}/quiz/start?amount=${amount}`;
    if (selectedCategoryIds.length > 0) { const categoryParams = selectedCategoryIds.map(id => `category_id=${encodeURIComponent(id)}`).join('&'); apiUrl += `&${categoryParams}`; }
    console.log("Fetching URL:", apiUrl);
    try {
        const headers = {}; if (isLoggedIn && authToken) { headers['Authorization'] = `Bearer ${authToken}`; } else { throw new Error("Otentikasi diperlukan."); }
        const response = await fetch(apiUrl, { headers: headers });
        if (response.status === 401) { throw new Error('Sesi tidak valid.'); } if (!response.ok) { const errorData = await response.json().catch(() => ({ detail: `Gagal memuat soal (${response.status})` })); throw new Error(errorData.detail || response.statusText); }
        const data = await response.json(); if (data && data.session_id && Array.isArray(data.questions)) { currentQuizSessionId = data.session_id; questions = data.questions; console.log("Received session ID:", currentQuizSessionId); } else { console.error("Struktur data kuis tidak sesuai:", data); throw new Error("Format data kuis tidak dikenali."); }
        if (questions.length === 0) { startFeedbackDiv.textContent = "Tidak ada soal ditemukan."; showView('setup'); hideLoading(); return; }
        currentQuestionIndex = 0; userAnswers = []; isGuestMode = false; showView('quiz'); displayQuestion(currentQuestionIndex);
    } catch (error) { console.error("Error fetching quiz:", error); startFeedbackDiv.textContent = `Gagal memulai kuis: ${error.message}`; if (error.message.includes("Sesi tidak valid")) { handleLogout(); } showView('setup'); hideLoading(); }
}

// --- Fungsi BARU untuk memulai kuis sebagai TAMU (MEMANGGIL ENDPOINT BARU) ---
async function fetchGuestQuizQuestions() {
    showLoading();
    startFeedbackDiv.textContent = ''; // Hapus pesan error lama
    const selectedCategoryCheckboxes = document.querySelectorAll('#category-selector input[name="category"]:checked');
    const selectedCategoryIds = Array.from(selectedCategoryCheckboxes).map(cb => cb.value);
    const amount = 10;
    console.log("Attempting to start quiz as GUEST. Selected Category IDs:", selectedCategoryIds);
    console.log("Guest Info:", guestInfo);

    // Bangun URL untuk endpoint tamu BARU
    let apiUrl = `${API_BASE_URL}/quiz/start-guest?amount=${amount}`; // Panggil endpoint guest
    if (selectedCategoryIds.length > 0) {
        const categoryParams = selectedCategoryIds.map(id => `category_id=${encodeURIComponent(id)}`).join('&');
        apiUrl += `&${categoryParams}`;
    }
    console.log("Fetching Guest URL:", apiUrl);

    try {
        // Panggil endpoint tamu (TANPA header Authorization)
        const response = await fetch(apiUrl);

        // Tidak perlu cek 401 di sini
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({ detail: `Gagal memuat soal tamu (Status: ${response.status})` }));
            throw new Error(errorData.detail || response.statusText);
        }
        const data = await response.json();
        if (data && data.session_id && Array.isArray(data.questions)) {
            currentQuizSessionId = data.session_id; // Tetap simpan session ID tamu
            questions = data.questions;
            console.log("Received GUEST session ID:", currentQuizSessionId);
        } else {
            console.error("Struktur data kuis tamu tidak sesuai:", data);
            throw new Error("Format data kuis tamu tidak dikenali.");
        }

        if (questions.length === 0) {
            startFeedbackDiv.textContent = "Tidak ada soal ditemukan untuk filter yang dipilih.";
            showView('setup'); // Kembali ke setup jika tidak ada soal
            hideLoading();
            return;
        }

        currentQuestionIndex = 0; userAnswers = [];
        isGuestMode = true; // Tandai ini adalah sesi tamu
        showView('quiz'); // Tampilkan kuis
        displayQuestion(currentQuestionIndex); // Tampilkan soal pertama

    } catch (error) {
        console.error("Error fetching guest quiz:", error);
        startFeedbackDiv.textContent = `Gagal memulai kuis tamu: ${error.message}`;
        showView('setup'); // Kembali ke setup jika gagal
        hideLoading();
    }
    // hideLoading() dipanggil oleh displayQuestion jika sukses
}
// ----------------------------------------------------


// displayQuestion, selectAnswer, nextQuestion (Tidak Berubah)
function displayQuestion(index) { hideLoading(); if (index >= questions.length) { submitQuiz(); return; } const q = questions[index]; questionCategorySpan.textContent = q.category_name; questionTextP.textContent = q.question; optionsContainer.innerHTML = ''; feedbackDiv.textContent = ''; nextButton.disabled = true; q.options.forEach(option => { const button = document.createElement('button'); button.textContent = option; button.classList.add( 'quiz-option', 'block', 'w-full', 'text-left', 'p-3', 'border', 'border-gray-300', 'rounded-md', 'text-gray-800', 'hover:bg-blue-100', 'focus:outline-none', 'focus:ring-2', 'focus:ring-blue-400', 'focus:border-transparent', 'transition', 'duration-150'); button.onclick = () => selectAnswer(q.id, option, button); optionsContainer.appendChild(button); }); questionCounterSpan.textContent = `Soal ${index + 1} dari ${questions.length}`; if (index === questions.length - 1) nextButton.textContent = "Lihat Hasil"; else nextButton.textContent = "Selanjutnya"; }
function selectAnswer(questionId, selectedOption, selectedButton) { const existingAnswerIndex = userAnswers.findIndex(ans => ans.question_id === questionId); if (existingAnswerIndex > -1) userAnswers[existingAnswerIndex].user_answer = selectedOption; else userAnswers.push({ question_id: questionId, user_answer: selectedOption }); document.querySelectorAll('.quiz-option').forEach(btn => { btn.classList.remove('selected', 'bg-blue-400', 'text-white', 'border-blue-500'); btn.classList.add('text-gray-800', 'border-gray-300'); }); selectedButton.classList.add('selected', 'bg-blue-400', 'text-white', 'border-blue-500'); selectedButton.classList.remove('text-gray-800'); feedbackDiv.textContent = ''; nextButton.disabled = false; }
function nextQuestion() { const currentQuestionId = questions[currentQuestionIndex].id; const currentAnswer = userAnswers.find(ans => ans.question_id === currentQuestionId); if (!currentAnswer) { feedbackDiv.textContent = "Pilih jawaban dulu!"; return; } showLoading(); currentQuestionIndex++; if (currentQuestionIndex < questions.length) setTimeout(() => displayQuestion(currentQuestionIndex), 100); else submitQuiz(); }

// Modifikasi submitQuiz: Jangan kirim jika mode tamu
async function submitQuiz() {
    // CEK MODE TAMU
    if (isGuestMode) {
        alert("Mode Tamu: Hasil kuis tidak disimpan ke riwayat. Terima kasih sudah mencoba!");
        console.log("Guest mode quiz finished. Answers:", userAnswers);
        // TODO: Idealnya hitung skor lokal jika jawaban benar ada (tapi fetch_questions tidak kirim jawaban benar)
        // Untuk sekarang, langsung reset saja.
        resetQuiz();
        return;
    }

    // Logika submit untuk user login (Sama seperti sebelumnya)
    if (!currentQuizSessionId) { console.error("Tidak ada ID sesi kuis."); feedbackDiv.textContent = "Error: Sesi kuis tidak valid."; hideLoading(); return; } if (!isLoggedIn || !authToken) { feedbackDiv.textContent = "Login diperlukan untuk submit."; hideLoading(); showView('login'); return; } const lastQuestionId = questions[currentQuestionIndex].id; const lastAnswer = userAnswers.find(ans => ans.question_id === lastQuestionId); if (!lastAnswer && currentQuestionIndex === questions.length -1) { feedbackDiv.textContent = "Jawab soal terakhir dulu!"; hideLoading(); return; } showLoading();
    try { const headers = {'Content-Type': 'application/json', 'Authorization': `Bearer ${authToken}`}; const response = await fetch(`${API_BASE_URL}/quiz/${currentQuizSessionId}/submit`, { method: 'POST', headers: headers, body: JSON.stringify({ answers: userAnswers }) }); if (response.status === 401) { throw new Error('Sesi tidak valid.'); } if (!response.ok) { const errorData = await response.json().catch(() => ({ detail: `Gagal submit (${response.status})` })); throw new Error(errorData.detail || response.statusText); } const results = await response.json(); displayResults(results); } catch (error) { console.error("Error submitting quiz:", error); feedbackDiv.textContent = `Gagal submit: ${error.message}`; if (error.message.includes("Sesi tidak valid")) { handleLogout(); } hideLoading(); }
}

// displayResults (Tidak Berubah)
function displayResults(results) { /* ... kode SAMA seperti sebelumnya ... */ showView('results'); finalScoreSpan.textContent = results.score_percentage; correctCountSpan.textContent = results.correct_answers_count; totalCountSpan.textContent = results.total_questions; categoryAnalysisDiv.innerHTML = ''; if (results.analysis && results.analysis.length > 0) { results.analysis.forEach(cat => { const div = document.createElement('div'); div.classList.add('p-3', 'border', 'rounded', 'bg-gray-50'); const scoreColor = cat.score_percentage < 60 ? 'text-red-600' : 'text-green-600'; div.innerHTML = `<span class="font-medium text-gray-800">${cat.category_name}:</span> <span class="${scoreColor} font-bold">${cat.score_percentage}%</span> <span class="text-sm text-gray-600"> (${cat.correct_count}/${cat.total_questions} benar)</span>`; categoryAnalysisDiv.appendChild(div); }); } else { categoryAnalysisDiv.innerHTML = '<p class="text-gray-500 italic">Tidak ada data analisis kategori.</p>'; } recommendationsDiv.innerHTML = ''; recommendationsLoadingP.classList.remove('hidden'); recommendationsDiv.appendChild(recommendationsLoadingP); fetchRecommendations(results.analysis); }

// fetchRecommendations (Kirim token jika login)
async function fetchRecommendations(analysisData) { /* ... kode SAMA seperti sebelumnya ... */ showLoading(); try { const headers = {'Content-Type': 'application/json'}; if (isLoggedIn && authToken) { headers['Authorization'] = `Bearer ${authToken}`; } const response = await fetch(`${API_BASE_URL}/recommendations/`, { method: 'POST', headers: headers, body: JSON.stringify(analysisData) }); if (response.status === 401 && isLoggedIn) { throw new Error('Sesi tidak valid.'); } if (!response.ok) { const errorData = await response.json().catch(() => ({ detail: `Gagal memuat rekomendasi (${response.status})` })); throw new Error(errorData.detail || response.statusText); } const recommendations = await response.json(); recommendationsLoadingP.classList.add('hidden'); recommendationsDiv.innerHTML = ''; if (recommendations && recommendations.length > 0) { recommendations.forEach(rec => { const div = document.createElement('div'); div.classList.add('border-b', 'pb-3', 'mb-3'); let content = `<h4 class="font-semibold text-blue-700">${rec.title}</h4><p class="text-sm text-gray-700 mt-1">${rec.summary}</p>`; if (rec.url) content += `<a href="${rec.url}" target="_blank" rel="noopener noreferrer" class="text-sm text-blue-500 hover:underline">Baca lebih lanjut...</a>`; div.innerHTML = content; recommendationsDiv.appendChild(div); }); } else { recommendationsDiv.innerHTML = '<p class="text-gray-500 italic">Tidak ada rekomendasi spesifik.</p>'; } } catch (error) { console.error("Error fetching recommendations:", error); recommendationsLoadingP.classList.add('hidden'); recommendationsDiv.innerHTML = `<p class="text-red-500 italic">Gagal memuat rekomendasi: ${error.message}</p>`; if (error.message.includes("Sesi tidak valid")) { handleLogout(); } } finally { hideLoading(); } }

// --- Fungsi History ---
async function fetchAndDisplayHistory() { /* ... kode SAMA seperti sebelumnya ... */ if (!isLoggedIn || !authToken) { alert("Login untuk melihat riwayat."); showView('login'); return; } showLoading(); historyListDiv.innerHTML = '<p class="text-gray-500 p-4 text-center">Memuat riwayat...</p>'; showView('history'); try { const headers = { 'Authorization': `Bearer ${authToken}` }; const response = await fetch(`${API_BASE_URL}/history`, { headers: headers }); if (response.status === 401) { throw new Error('Sesi tidak valid.'); } if (!response.ok) { const errorData = await response.json().catch(() => ({detail: `Gagal memuat riwayat (${response.status})`})); throw new Error(errorData.detail); } const historyData = await response.json(); historyListDiv.innerHTML = ''; if (historyData && historyData.length > 0) { historyData.forEach(attempt => { const div = document.createElement('div'); div.classList.add('p-3', 'border-b'); const date = new Date(attempt.timestamp).toLocaleString('id-ID', { dateStyle: 'medium', timeStyle: 'short' }); const categories = attempt.categories_played ? attempt.categories_played.split(',').map(c=>c.trim()).join(', ') : 'Semua'; const scoreClass = attempt.score < 60 ? 'text-red-600' : 'text-green-600'; div.innerHTML = ` <div class="flex justify-between items-center mb-1"> <span class="text-sm font-medium text-gray-700">${date}</span> <span class="font-bold ${scoreClass}">${attempt.score.toFixed(1)}%</span> </div> <p class="text-xs text-gray-500">(${attempt.correct_answers} / ${attempt.total_questions} benar) - Kategori: ${categories}</p> `; historyListDiv.appendChild(div); }); } else { historyListDiv.innerHTML = '<p class="text-gray-500 p-4 text-center">Belum ada riwayat kuis.</p>'; } } catch (error) { console.error("Error fetching history:", error); historyListDiv.innerHTML = `<p class="text-red-500 p-4 text-center">Gagal memuat riwayat: ${error.message}</p>`; if (error.message.includes("Sesi tidak valid")) { handleLogout(); } } finally { hideLoading(); } }

// --- Fungsi Reset Kuis ---
function resetQuiz() {
    currentQuizSessionId = null; questions = []; currentQuestionIndex = 0; userAnswers = [];
    startFeedbackDiv.textContent = ''; feedbackDiv.textContent = ''; categoryAnalysisDiv.innerHTML = ''; recommendationsDiv.innerHTML = '';
    isGuestMode = false; // Selalu reset guest mode
    guestInfo = { name: null, status: null, institution: null };
    showView('setup');
}

// --- Event Listeners ---
// Auth & Modal Tamu
showLoginBtn?.addEventListener('click', () => { showView('login'); loginErrorDiv.textContent = ''; });
showRegisterBtn?.addEventListener('click', () => { showView('register'); registerErrorDiv.textContent = ''; });
cancelLoginBtn?.addEventListener('click', () => { showView('setup'); loginForm.reset(); loginErrorDiv.textContent = ''; });
cancelRegisterBtn?.addEventListener('click', () => { showView('setup'); registerForm.reset(); registerErrorDiv.textContent = ''; });
loginForm?.addEventListener('submit', handleLogin);
registerForm?.addEventListener('submit', handleRegister);
logoutBtn?.addEventListener('click', handleLogout);
showHistoryBtn?.addEventListener('click', fetchAndDisplayHistory);
closeHistoryBtn?.addEventListener('click', () => { showView('setup'); });
promptLoginBtn?.addEventListener('click', () => showView('login'));
promptRegisterBtn?.addEventListener('click', () => showView('register'));
promptGuestBtn?.addEventListener('click', () => showView('guestInfo'));
promptCancelBtn?.addEventListener('click', () => showView('setup'));
guestStatusSelect?.addEventListener('change', (event) => { const status = event.target.value; guestSchoolInputDiv.classList.add('hidden'); guestUniversityInputDiv.classList.add('hidden'); guestSchoolInput.required = false; guestUniversityInput.required = false; if (status === 'Siswa') { guestSchoolInputDiv.classList.remove('hidden'); guestSchoolInput.required = true; } else if (status === 'Mahasiswa') { guestUniversityInputDiv.classList.remove('hidden'); guestUniversityInput.required = true; } });
guestInfoForm?.addEventListener('submit', (event) => { event.preventDefault(); guestInfoErrorDiv.textContent = ''; const name = guestNameInput.value.trim(); const status = guestStatusSelect.value; let institution = null; if (!name || !status) { guestInfoErrorDiv.textContent = 'Nama & Status wajib.'; return; } if (status === 'Siswa') { institution = guestSchoolInput.value.trim(); if (!institution) { guestInfoErrorDiv.textContent = 'Nama Sekolah wajib.'; return; } } else if (status === 'Mahasiswa') { institution = guestUniversityInput.value.trim(); if (!institution) { guestInfoErrorDiv.textContent = 'Nama Universitas wajib.'; return; } } guestInfo = { name, status, institution }; console.log("Melanjutkan sebagai tamu:", guestInfo); isGuestMode = true; guestInfoModal.classList.add('hidden'); fetchGuestQuizQuestions(); });
cancelGuestInfoBtn?.addEventListener('click', () => { showView('guestPrompt'); guestInfoForm.reset(); guestInfoErrorDiv.textContent = ''; guestSchoolInputDiv.classList.add('hidden'); guestUniversityInputDiv.classList.add('hidden'); });

// Kuis Setup
selectAllButton?.addEventListener('click', () => { document.querySelectorAll('#category-selector input[type="checkbox"]').forEach(cb => { cb.checked = true; }); });
deselectAllButton?.addEventListener('click', () => { document.querySelectorAll('#category-selector input[type="checkbox"]').forEach(cb => { cb.checked = false; }); });
startButton?.addEventListener('click', () => { startFeedbackDiv.textContent = ''; if (isLoggedIn) { fetchQuizQuestions(); } else { showView('guestPrompt'); } });

// Kuis Aktif
nextButton?.addEventListener('click', () => { if (currentQuestionIndex === questions.length - 1) { const lastQuestionId = questions[currentQuestionIndex].id; const lastAnswer = userAnswers.find(ans => ans.question_id === lastQuestionId); if (!lastAnswer) { feedbackDiv.textContent = "Jawab soal terakhir dulu!"; return; } submitQuiz(); } else { nextQuestion(); } });

// Hasil
resetButton?.addEventListener('click', resetQuiz);

// --- Inisialisasi ---
document.addEventListener('DOMContentLoaded', () => {
    // Tambahkan null checks untuk elemen opsional saat init
    if (document.getElementById('loading-indicator')) { // Cek elemen utama ada
        fetchUserInfo(); // Cek status login
        showView('setup'); // Tampilkan view awal
        fetchAndDisplayCategories(); // Muat kategori
    } else {
        console.error("Elemen UI utama tidak ditemukan! Periksa HTML Anda.");
    }
});