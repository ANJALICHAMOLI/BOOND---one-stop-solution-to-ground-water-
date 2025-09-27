const $ = (q, el=document)=>el.querySelector(q);
const $$ = (q, el=document)=>Array.from(el.querySelectorAll(q));

/* Language (simple demo: English & Hindi) */
const i18n = {
  en: {
    title: "BOOND :Turning Every Drop into Sustainable Potential",
    subtitle: "On-Spot Evaluation of Rainwater Harvesting & Recharge",
    login: "Login",
    next: "Next",
    getStarted: "Get Started",
    heroCta: "Open Tool",

    // Login page
    welcome: "Welcome back",
    loginSubtitle: "Log in to access the on-spot assessment tool.",
    emailPh: "Email",
    passwordPh: "Password",
    loginBtn: "LOGIN",
    notReg: "Not registered?",
    createAcc: "Create an account",
    signupBtn: "Sign up",

    // Signup page
    createTitle: "Create your account",
    signupSubtitle: "Sign up to start assessing rainwater harvesting potential.",
    passwordPh2: "Password (6+ chars)",
    confirmPh: "Confirm password",
    createBtn: "Create account",
    alreadyAcc: "Already have an account?",
    loginLink: "Log in"
  },
  hi: {
    title: "बूंद : हर बूंद बने सतत् सम्भावना",
    subtitle: "वर्षा जल संचयन एवं रिचार्ज का तात्कालिक मूल्यांकन।",
    login: "लॉगिन",
    next: "आगे",
    getStarted: "शुरू करें",
    heroCta: "उपकरण खोलें",

    // Login page
    welcome: "वापसी पर स्वागत है",
    loginSubtitle: "ऑन-स्पॉट आकलन टूल का उपयोग करने के लिए लॉगिन करें।",
    emailPh: "ईमेल",
    passwordPh: "पासवर्ड",
    loginBtn: "लॉगिन",
    notReg: "पंजीकृत नहीं हैं?",
    createAcc: "खाता बनाएं",
    signupBtn: "साइन अप",

    // Signup page
    createTitle: "अपना खाता बनाएँ",
    signupSubtitle: "वर्षा जल संचयन क्षमता का आकलन शुरू करने के लिए साइन अप करें।",
    passwordPh2: "पासवर्ड (6+ अक्षर)",
    confirmPh: "पासवर्ड की पुष्टि करें",
    createBtn: "खाता बनाएं",
    alreadyAcc: "क्या आपके पास पहले से खाता है?",
    loginLink: "लॉगिन करें"
  }
};

function setLang(lang){
  localStorage.setItem('lang', lang);
  $$('[data-i18n]').forEach(el=>{
    const key = el.getAttribute('data-i18n');
    if(i18n[lang] && i18n[lang][key]) el.textContent = i18n[lang][key];
  });
  // Handle placeholders
  $$('[data-i18n-placeholder]').forEach(el=>{
    const key = el.getAttribute('data-i18n-placeholder');
    if(i18n[lang] && i18n[lang][key]) el.placeholder = i18n[lang][key];
  });
  const sel = $('.lang-switch select');
  if(sel) sel.value = lang;
}

function initLang(){
  const saved = localStorage.getItem('lang') || 'en';
  const sel = $('.lang-switch select');
  if(sel){
    sel.value = saved;
    sel.addEventListener('change', e=> setLang(e.target.value));
  }
  setLang(saved);
}

/* Carousel */
function initCarousel(){
  const track = $('.track');
  if(!track) return;
  const slides = $$('.slide', track);
  const dotsWrap = $('.dots');
  let idx = 0;
  function go(i){
    idx = (i+slides.length) % slides.length;
    track.style.transform = `translateX(-${idx*100}%)`;
    if(dotsWrap){
      $$('.dot', dotsWrap).forEach((d,di)=> d.classList.toggle('active', di===idx));
    }
  }
  $('.next')?.addEventListener('click', ()=>go(idx+1));
  $('.prev')?.addEventListener('click', ()=>go(idx-1));
  if(dotsWrap){
    dotsWrap.innerHTML = slides.map((_,i)=>`<button class="dot ${i===0?'active':''}" aria-label="Go to slide ${i+1}"></button>`).join('');
    $$('.dot', dotsWrap).forEach((d,i)=> d.addEventListener('click', ()=>go(i)));
  }
  // Auto-play (optional)
  let timer = setInterval(()=>go(idx+1), 5000);
  ['mouseenter','focusin'].forEach(ev=> track.addEventListener(ev, ()=>clearInterval(timer)));
  ['mouseleave','focusout'].forEach(ev=> track.addEventListener(ev, ()=> timer = setInterval(()=>go(idx+1), 5000)));
}


/* Login with FastAPI backend */
console.log("app.js loaded");

async function handleLogin(e) {
  e.preventDefault();
  console.log("handleLogin called");

  const email = document.getElementById('email')?.value?.trim();
  const password = document.getElementById('password')?.value || '';
  const flash = document.getElementById('flash');

  if (!email || !password) {
    console.log("Empty fields");
    if (flash) {
      flash.textContent = 'Please enter email & password.';
      flash.style.color = 'red';
    }
    return;
  }

  try {
    const res = await fetch("http://127.0.0.1:8000/login", {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    });

    const data = await res.json();
    console.log("Response:", data);

    if (!res.ok) {
      throw new Error(data.detail || 'Login failed');
    }

    localStorage.setItem('boond_token', data.access_token);
    window.location.href = 'feature.html';
  } catch (err) {
    console.error("Error:", err.message);
    if (flash) {
      flash.textContent = err.message;
      flash.style.color = 'red';
    }
  }
}

document.addEventListener("DOMContentLoaded", () => {
  console.log("Form handler attaching...");
  const form = document.getElementById("loginForm");
  if (form) {
    form.addEventListener("submit", handleLogin);
    console.log("Form handler attached ✅");
  } else {
    console.log("Form not found ❌");
  }
});




/* Signup with FastAPI backend */
async function handleSignup(e){
  e?.preventDefault();

  const name = $('#sname')?.value?.trim();
  const email = $('#semail')?.value?.trim();
  const pass = $('#spassword')?.value || '';
  const cpass = $('#scpassword')?.value || '';
  const flash = $('#sflash');

  if(!name || !email || !pass || pass.length < 6 || pass !== cpass){
    if(flash){
      flash.textContent = 'Fill all fields; passwords must match & be 6+ chars.';
      flash.style.color = 'var(--danger)';
    }
    return;
  }

  try {
    const res = await fetch("http://127.0.0.1:8000/users/", {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, email, password: pass })
    });

    const data = await res.json();
    console.log("Signup response:", data);

    if (!res.ok) {
      // Display backend error message if any
      throw new Error(data.detail || 'Signup failed');
    }

    // Signup successful: save minimal profile and redirect to login
    localStorage.setItem('profile', JSON.stringify({email, name}));
    window.location.href = 'login.html';

  } catch (err) {
    console.error("Error:", err.message);
    if(flash){
      flash.textContent = err.message; // show exact backend error
      flash.style.color = 'var(--danger)';
    }
  }
}


/* Check auth for protected pages */
function checkAuth(){
  const token = localStorage.getItem('boond_token');
  if(!token){
    window.location.href = 'login.html';
  }
}

function logout(){
  localStorage.removeItem('boond_token');
  window.location.href = 'index.html';
}

// Init per page
document.addEventListener('DOMContentLoaded', ()=>{
  initLang();
  if($('.track')) initCarousel();
  if($('#loginForm')) $('#loginForm').addEventListener('submit', handleLogin);
  if($('#signupForm')) $('#signupForm').addEventListener('submit', handleSignup);
  if($('#logoutBtn')) $('#logoutBtn').addEventListener('click', logout);
  if(document.body.dataset.page==='main'){ checkAuth(); }
});

