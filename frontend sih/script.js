const translations = {
  en: {
    tagline: "every drop counts",
    home: "Home",
    contact: "Contact",
    featuresHeading: "EXPLORE POWERFUL FEATURES",
    feature1Title: "Harvesting Feasibility 🏠💧",
    feature1Text: "Check if your rooftop is ready for rainwater harvesting — get a clear YES/NO with tips to improve your setup.",
    feature2Title: "Money Matters 💸",
    feature2Text: "Understand costs, savings, and funding options for water projects.",
    feature3Title: "Groundwater Depth 📏",
    feature3Text: "Check the groundwater levels in your area with updated data.",
    feature4Title: "Rain Check ☔",
    feature4Text: "Provides local rainfall data and trends.",
    feature5Title: "Runoff Meter ⚡",
    feature5Text: "Measure and predict water runoff during rains for better planning.",
    feature6Title: "Red Alert Meter ⚠️",
    feature6Text: "Real-time Red Alert system notifies users of rising water-borne disease risks in their area.",
    feature7Title: "👷📞 Contact a Contractor",
    feature7Text: "Need professional help? Instantly connect with verified local contractors to install or maintain your harvesting system.",
    plansHeading: "Subscription Plans",
    freePlan: "BOOND — Free (7 day pro trial included)",
    proPlan: "BOOND Pro — 99 INR/month",
    premiumPlan: "BOOND Premium — 200 INR/month",
    address: "Address:",
    call: "Call:",
    email: "Email:",
    followers: "Followers:"
  },
  hi: {
    tagline: "हर बूंद मायने रखती है",
    home: "होम",
    contact: "संपर्क",
    featuresHeading: "प्रमुख सुविधाएँ देखें",
    feature1Title: "वर्षा जल संचयन की व्यवहार्यता 🏠💧",
    feature1Text: "जाँचें कि आपकी छत वर्षा जल संचयन के लिए उपयुक्त है या नहीं, और व्यवस्था सुधारने के सुझाव पाएँ।",
    feature2Title: "लागत और बचत 💸",
    feature2Text: "जल परियोजनाओं की लागत, बचत और वित्तीय सहायता के विकल्प जानें।",
    feature3Title: "भूजल की गहराई 📏",
    feature3Text: "अपने क्षेत्र के भूजल स्तर की उपलब्ध जानकारी देखें।",
    feature4Title: "वर्षा की जानकारी ☔",
    feature4Text: "अपने क्षेत्र की वर्षा के आँकड़े और रुझान देखें।",
    feature5Title: "जल बहाव मापक ⚡",
    feature5Text: "बेहतर योजना के लिए वर्षा के दौरान जल बहाव का मापन और अनुमान करें।",
    feature6Title: "जोखिम सूचना ⚠️",
    feature6Text: "यह सुविधा क्षेत्र में जलजनित रोगों के जोखिम की सूचना देती है।",
    feature7Title: "👷📞 ठेकेदार से संपर्क",
    feature7Text: "वर्षा जल संचयन प्रणाली लगाने या उसकी देखभाल के लिए स्थानीय ठेकेदार से संपर्क करें।",
    plansHeading: "सदस्यता योजनाएँ",
    freePlan: "BOOND — निःशुल्क (7 दिन का प्रो परीक्षण शामिल)",
    proPlan: "BOOND Pro — 99 रुपये/माह",
    premiumPlan: "BOOND Premium — 200 रुपये/माह",
    address: "पता:",
    call: "फ़ोन:",
    email: "ईमेल:",
    followers: "सोशल मीडिया:"
  }
};

function setLanguage(language) {
  const copy = translations[language];
  if (!copy) return;

  document.documentElement.lang = language;
  document.querySelectorAll("[data-i18n]").forEach((element) => {
    const translatedText = copy[element.dataset.i18n];
    if (translatedText) element.textContent = translatedText;
  });

  document.querySelectorAll("[data-lang]").forEach((button) => {
    const selected = button.dataset.lang === language;
    button.setAttribute("aria-pressed", String(selected));
    button.classList.toggle("active", selected);
    button.style.backgroundColor = selected ? "#0a6fb3" : "#ffffff";
    button.style.color = selected ? "#ffffff" : "#242323";
  });

  try {
    localStorage.setItem("boond_language", language);
  } catch (_) {
    // The page still works if the browser blocks local storage.
  }
}

document.addEventListener("DOMContentLoaded", () => {
  let savedLanguage = "en";
  try {
    savedLanguage = localStorage.getItem("boond_language") || "en";
  } catch (_) {
    // Use English when local storage is unavailable.
  }

  document.querySelectorAll("[data-lang]").forEach((button) => {
    button.addEventListener("click", () => setLanguage(button.dataset.lang));
  });

  setLanguage(savedLanguage);
});
