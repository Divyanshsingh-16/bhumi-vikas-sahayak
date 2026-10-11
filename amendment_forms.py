"""28-08-2026 amendment explainer + application form/checklist router.
Content grounded in pack sources; amendment text itself is a pointer (not in pack)."""

AMENDMENT = {
    "en": (
        "On 28-08-2026 the Government of Madhya Pradesh amended Rule 2(5)(c) "
        "for plots up to 500 sq m. Our rulebook data freezes at 06-03-2025, so for "
        "plots ≤500 sq m that match the Development Plan (e.g. a 300 sq m plot), "
        "confirm the August-2026 position with the Authority before deciding. "
        "See: teamleaseregtech article 59469 (read 10-10-2026)."
    ),
    "hi": (
        "28-08-2026 को मध्यप्रदेश सरकार ने 500 वर्ग मीटर तक के प्लॉट के लिए नियम 2(5)(c) "
        "में संशोधन किया। हमारा डेटा 06-03-2025 तक का है, इसलिए ≤500 वर्ग मीटर के प्लॉट "
        "(जैसे 300 वर्ग मीटर, विकास योजना के अनुरूप) पर निर्णय से पहले प्राधिकारी से "
        "अगस्त-2026 की स्थिति अवश्य जांचें।"
    ),
}

# application type -> form + key docs (Rules 12/14/16/18/26-B grounding in rule_text hint)
FORMS = {
    "development": {
        "label_en": "Development permission (land layout/sub-division)",
        "label_hi": "विकास अनुमति (भूमि विकास/ले-आउट)",
        "form": "Appendix A-1 (Rule 14)",
        "fee": "Rs 5,000/hectare or part thereof (Rule 21(2))",
        "docs_en": ["Key plan, site plan, sub-division/layout plan", "Service plans + project report",
                    "Ownership proof / legal right", "Application fee receipt (Rule 21)"],
        "docs_hi": ["मुख्य योजना, स्थल योजना, उप-विभाजन/ले-आउट योजना", "सेवा योजना + परियोजना रिपोर्ट",
                    "स्वामित्व प्रमाण / विधिक अधिकार", "आवेदन शुल्क रसीद (नियम 21)"],
    },
    "building": {
        "label_en": "Building permission (erect/re-erect/alter)",
        "label_hi": "भवन अनुमति (निर्माण/पुनर्निर्माण/परिवर्तन)",
        "form": "Appendix A-2 / A-2(1) (Rule 14); via authorised Architect/Structural Engineer (Rule 26-B)",
        "fee": "Rs 1 per sq m of proposed built-up + permission-fee slabs (Rule 21)",
        "docs_en": ["Floor plans + covered-area + stair/lift details", "Sections: footing, walls, slabs, openings",
                    "Ownership proof + fee receipt", "Earthquake certificate Rule 88 (if applicable)"],
        "docs_hi": ["मंजिल योजना + आच्छादित क्षेत्र + सीढ़ी/लिफ्ट विवरण", "काट-चित्र: नींव, दीवार, स्लैब, द्वार-खिड़की",
                    "स्वामित्व प्रमाण + शुल्क रसीद", "भूकंप प्रमाणपत्र नियम 88 (लागू हो तो)"],
    },
    "alteration": {
        "label_en": "Alteration of existing building",
        "label_hi": "मौजूदा भवन में परिवर्तन",
        "form": "Only necessary plans/statements (Rule 19); sanction change via Form-M App-K for Sec 29(3) cases",
        "fee": "Rs 500 for non-built-up changes; >10% change = fresh application (Rule 21)",
        "docs_en": ["Only affected plans/statements (Rule 19)", "Original sanction reference"],
        "docs_hi": ["केवल प्रभावित योजना/विवरण (नियम 19)", "मूल स्वीकृति संदर्भ"],
    },
    "revalidation": {
        "label_en": "Revalidation of expired permission",
        "label_hi": "समाप्त अनुमति का नवीनीकरण",
        "form": "Revalidation request (Rule 23: 2 × 1 yr, then fresh)",
        "fee": "10% of original building fee if applied after expiry; free if before expiry (Rule 21/23)",
        "docs_en": ["Original sanction copy", "Status of execution on site"],
        "docs_hi": ["मूल स्वीकृति प्रति", "स्थल पर कार्य की स्थिति"],
    },
}


def route_form(query: str) -> str | None:
    q = query.lower()
    if any(k in q for k in ("revalid", "renew", "नवीनीकरण", "expired")):
        return "revalidation"
    if any(k in q for k in ("alter", "change", "modify", "deviation", "परिवर्तन")):
        return "alteration"
    if any(k in q for k in ("develop", "layout", "sub-division", "subdivision", "colony", "विकास")):
        return "development"
    if any(k in q for k in ("build", "construct", "house", "shop", "floor", "भवन", "मकान", "घर")):
        return "building"
    return None
