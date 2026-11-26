# sutradhar — हिंदी क्विकस्टार्ट

**एक धागा: रिसर्च से रिटेंशन तक।** वीडियो एडिटिंग कोड में, अपने ही ब्रांड में, और हर चीज़ नापी हुई — अंदाज़े से नहीं।

सब कुछ फ्री है: MIT लाइसेंस, कोई सब्सक्रिप्शन नहीं, कोई क्लाउड नहीं। कोर हिस्सा सिर्फ़ Python standard library
पर चलता है — `git clone` ही पूरा इंस्टॉल है।

---

## 1. इंस्टॉल (5 मिनट)

```bash
git clone https://github.com/<you>/sutradhar && cd sutradhar
make test          # 57 टेस्ट, इंटरनेट के बिना
make doctor        # क्या मिसिंग है, और उसका ठीक कमांड
```

ज़रूरी: Python 3.10+
वीडियो रेंडर के लिए: Node 22+, HyperFrames, ffmpeg
(Windows: `winget install Gyan.FFmpeg` · Mac: `brew install ffmpeg`)

अगर सिर्फ़ ffmpeg की कमी है तो `pip install imageio-ffmpeg` भी चल जाएगा — लाउडनेस गेट उसी से काम करता है।

## 2. Antigravity या Claude Code में खोलें

```bash
make sync          # .claude/skills -> .agents/skills (Antigravity इसी फ़ोल्डर को पढ़ता है)
```

Antigravity में **`sutradhar` फ़ोल्डर** खोलें (कोई सब-फ़ोल्डर नहीं), फिर पहला मैसेज:

> `read AGENTS.md first, then list the 8 skills you can see in .agents/skills.`

## 3. तीन कमांड जो सब तय करते हैं

```bash
sutra pack list                    # 10 कैटेगरी: tutorial, comedy, story, gaming...
sutra resolve --pack tutorial --locale hi --format long-16x9
sutra init my-video --pack tutorial --locale hi
```

`sutra resolve` ये भी बताता है कि **हर नंबर कहाँ से आया** — पैक से, भाषा से, या फ़ॉर्मैट से। इसीलिए "कैप्शन 28
अक्षर क्यों" का जवाब एक लुकअप में मिलता है, बहस में नहीं।

## 4. हिंदी/हिंग्लिश में जो अलग है (और सबसे ज़्यादा गड़बड़ होती है)

| चीज़ | क्या होता है | यहाँ क्या है |
|---|---|---|
| whisper मॉडल | `small.en` हिंदी ऑडियो पर भरोसे से गलत शब्द देता है | `hi`/`hinglish` → **large-v3** |
| बड़े अक्षर | देवनागरी में अपरकेस होता ही नहीं | caps बंद, ज़ोर वज़न और रंग से |
| लाइन हाइट | ऊपर की मात्रा कट जाती है | `1.06–1.08` |
| कैप्शन चौड़ाई | 42 अक्षर कभी फ़िट नहीं होंगे | 28–30 अक्षर |
| हिंग्लिश | जैसा बोला, वैसा लिखो | Roman रोमन रहता है, देवनागरी में नहीं बदलता |
| फ़ॉन्ट | Inter में देवनागरी नहीं है | Baloo Bhai 2 या Mukta + Latin fallback |

`sutra doctor` बताता है कि इस मशीन पर कौन-सी स्क्रिप्ट का फ़ॉन्ट नहीं है।

## 5. पहला वीडियो — क्रम यही है

```
brand (एक बार) → plan → research → script → timeline → storyboard ✋ रुको → render → 7 गेट ✋ रुको → publish
                                                                              |
                                                    7 दिन बाद: retention curve → loop → 1 नियम लॉक, 1 डिलीट
```

सिर्फ़ **दो जगह** इंसान चाहिए: स्टोरीबोर्ड मंज़ूरी, और गेट रिव्यू। बाकी एजेंट ख़ुद पूरा करे।

```bash
sutra build plan/timeline.json --out renders/project   # ब्राउज़र में खुलने वाला शॉट-शीट प्लेयर
sutra gate --timeline plan/timeline.json --render renders/v01.mp4
```

`index.html` खोलो, स्पेस दबाओ — पूरी टाइमलाइन चलेगी। रेंडर से पहले पेसिंग आँख से देख लो।

## 6. सात गेट (पब्लिश से पहले)

हुक · पेस · मोबाइल (पढ़ने लायक) · लाइसेंस · ऑडियो (−14 LUFS, true peak ≤ −1 dB) · शब्द कवरेज · फ़्लैश (≤3/सेकंड)

जो गेट फ़ेल हो, वो **टाइमस्टैम्प** देता है। जो चेक नहीं हो सका, वो `SKIP` लिखता है — चुपचाप पास नहीं होता।

## 7. ईमानदार बातें

- **10 में से 0 पैक "measured" हैं।** नंबर शुरुआती डिफ़ॉल्ट हैं, नापे हुए नहीं। `sutra evidence` स्कोरबोर्ड है।
- टूल आपकी जगह **taste** नहीं दे सकता। वो आपको ख़ुद बनाना है।
- बाकी सब मशीन पर मुफ़्त है; ख़र्च सिर्फ़ समय का है। पहला वीडियो ~2 घंटे, दूसरा ~40 मिनट।

पूरा रोडमैप और कमियों की सूची: [`ROADMAP.md`](../ROADMAP.md) · कैटेगरी गाइड: [`CATEGORIES.md`](CATEGORIES.md) ·
भाषाओं की गहराई: [`LOCALES.md`](LOCALES.md)
