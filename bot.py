"""Sahayak avatar bot: guided conversation with slot-filling.
No typing needed — taps + numbers. State machine per chat session."""
from calculators import front_open_space, rear_open_space, building_fee

STEPS = ["greet", "plot", "road", "height", "use", "done"]

GREET = {
    "en": "🙏 Namaste! Main **Sahayak** hu. Aapke plot ka hisaab 1 minute me nikal dunga. Plot kitne sq m ka hai?",
    "hi": "🙏 नमस्ते! मैं **सहायक** हूं। आपके प्लॉट का हिसाब 1 मिनट में निकाल दूंगा। प्लॉट कितने वर्ग मीटर का है?",
}

QUICK_PLOTS = [100, 150, 200, 300, 500, 1000]


def bot_reply(state: dict, message: str | None) -> tuple[str, dict, bool]:
    """Return (reply_markdown, updated_state, finished). Pure function of state+message."""
    step = state.get("step", "greet")
    lang = state.get("lang", "en" if not (message and any("\u0900" <= c <= "\u097F" for c in message)) else state.get("lang", "en"))
    if message and any("\u0900" <= c <= "\u097F" for c in message):
        lang = "hi"
    state["lang"] = lang
    hi = lang == "hi"

    import re
    num = None
    if message:
        m = re.search(r"(\d+(?:\.\d+)?)", message.replace(",", ""))
        if m:
            num = float(m.group(1))

    if step == "greet":
        state["step"] = "plot"
        return GREET[lang], state, False

    if step == "plot":
        if num and 10 <= num <= 100000:
            state["plot"] = num
            state["step"] = "road"
            q = "✅ {p} sq m. {t}".format(p=num, t="सड़क कितनी चौड़ी है (मीटर में)?" if hi else "How wide is the road in front (in meters)?")
            return q, state, False
        return ("❓ " + ("Plot area (sq m) batayein, jaise 200।" if hi else "Tell me the plot area in sq m, e.g. 200.")), state, False

    if step == "road":
        if num and 1 <= num <= 60:
            state["road"] = num
            state["step"] = "height"
            q = "✅ {r} m. {t}".format(r=num, t="इमारत कितनी ऊंची होगी (मीटर)?" if hi else "How tall will the building be (in meters)?")
            return q, state, False
        return ("❓ " + ("सड़क की चौड़ाई मीटर में batayein।" if hi else "Tell me the road width in meters.")), state, False

    if step == "height":
        if num and 1 <= num <= 100:
            state["height"] = num
            state["step"] = "use"
            return ("✅ {h} m. {t}".format(h=num, t="उपयोग क्या है — आवासीय या दुकान/वाणिज्यिक?" if hi else "What is the use — residential or shop/commercial?")), state, False
        return ("❓ " + ("ऊंचाई मीटर में batayein।" if hi else "Tell me the height in meters.")), state, False

    if step == "use":
        use = "residential"
        if message and any(k in message.lower() for k in ("shop", "commercial", "business", "दुकान", "वाणिज्य")):
            use = "commercial"
        state["use"] = use
        state["step"] = "done"
        p, r = state["plot"], state["road"]
        f, re_ = front_open_space(r), rear_open_space(p)
        if hi:
            return (f"📋 **Aapka hisaab:**\n- सामने: **{f} मी** (नियम 56)\n- पीछे: **{'शून्य' if re_ == 0 else str(re_) + ' मी'}** (नियम 56)\n"
                    f"- ऊंचाई {state['height']} मी, उपयोग: {use}\nOperator se print-slip lein! 🙏"), state, True
        return (f"📋 **Your numbers:**\n- Front: **{f} m** (Rule 56)\n- Rear: **{'Nil' if re_ == 0 else str(re_) + ' m'}** (Rule 56)\n"
                f"- Height {state['height']} m, use: {use}\nAsk the operator for a print-slip! 🙏"), state, True

    # done -> restart on new input
    state.update({"step": "plot", "plot": None, "road": None, "height": None, "use": None})
    return GREET[lang], state, False
