r"""
SPIKE STEP 9 - The chatbot: a conversation layer on top of the RAG steps in 08.

08_answer.py answers ONE question and forgets it. This file turns it into a chat:

  1. UNDERSTAND  One small LLM call reads the new message together with the last
                 few messages and decides what it is:
                   chat       "salam", "sağ ol", "sən kimsən?"   -> reply directly
                   offtopic   nothing to do with the programme -> polite redirect
                   programme  a real question                  -> steps 2 and 3
                 For a programme question it also writes a complete stand-alone
                 version ("bəs bakalavr üçün?" -> "Bakalavriat üçün ...?") and
                 3 search versions.
  2. SEARCH + PICK   exactly as in 08_answer.py (reused, so it lives in one place).
  3. ANSWER      warm tone, simple words, programme facts only from the documents.
                 If the documents do not cover the question, the model writes
                 NO_ANSWER and the code swaps in a friendly message + the email.
  4. CHECK       A second call lists the programme facts in the answer that the text
                 does not support. If there is even one, the friendly message + the email
                 is sent instead. Eval baseline: 16% of answers had a made-up fact.

THE RULE THAT MUST NOT BREAK: the rewritten question is used for SEARCHING only.
The answer model reads the user's OWN message plus the conversation. In the first
version of this file the answer model got the rewrite instead, and the rewrite had
turned "ortalama" (GPA) into "ortalama xərclər" (average costs) - so a question that
08 answered correctly 3 times out of 3 got an answer about money.

Why a NO_ANSWER marker instead of letting the model write the refusal: a fixed
marker is easy for code to detect and count later, and the email address can
never be mistyped by the model.

Run:  .venv\Scripts\python.exe spike\09_chat.py               (chat - type "çıx" to stop)
      .venv\Scripts\python.exe spike\09_chat.py "sualınız"    (one question)
      add --debug to either to see what happened inside
"""
import importlib.util
import json
import pathlib
import re
import sys
import time

# Reuse the search steps from 08_answer.py. Python cannot write "import 08_answer"
# because module names may not start with a digit, so we load it by file path.
_spec = importlib.util.spec_from_file_location(
    "rag", pathlib.Path(__file__).with_name("08_answer.py"))
rag = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(rag)

HISTORY_TURNS = 3                     # previous question/answer pairs the bot remembers
CONTACT = "dp22-28@edu.gov.az"
CHECK = True                          # check the answer against the text before sending it. False = old behaviour
CHECK_MODEL = "gpt-4.1-mini"
READ_BIG = True                       # search small, read big (D-010). False = old behaviour
PAGE_LIMIT = 4000                     # pages up to this many characters are given whole
NEIGHBOURS = 1                        # longer pages: the chosen chunk plus this many on each side

WELCOME = (
    "Salam! Mən Xaricdə təhsil üzrə Dövlət Proqramı ilə bağlı suallarınıza cavab "
    "verən köməkçiyəm.\n"
    "Tələblər, xərclər, müraciət qaydaları - nə maraqlandırır, soruşun.\n\n"
    "Qeyd: bu, rəsmi olmayan tələbə layihəsidir. Vacib qərarlardan əvvəl məlumatı "
    "dp.edu.az saytında yoxlayın."
)

OFFTOPIC_NOTE = (
    "QEYD: ilk addım bu mesajın proqramla əlaqəsiz ola biləcəyini təxmin etdi, amma bu, "
    "yalnız təxmindir. Mesaj Dövlət Proqramı, xaricdə təhsil, xaricdə yaşayış xərcləri (kirayə, "
    "yemək, nəqliyyat), ölkələr, universitetlər, sənədlər və ya tələblər haqqında HƏR HANSI "
    "sualdırsa, adi qaydada cavab ver. Yalnız mesaj ümumiyyətlə sual deyilsə (bota deyilən söz, "
    "təhqir, zarafat, anlaşılmaz mətn) və ya açıq-aydın başqa mövzudadırsa (idman, hava, filmlər, "
    "kafe və restoran tövsiyəsi), mətndə oxşar söz olsa belə yalnız NO_ANSWER yaz."
)


NO_ANSWER_REPLY = (
    "Təəssüf ki, bu barədə rəsmi sənədlərdə məlumat tapa bilmədim. Dəqiq cavab üçün "
    f"Dövlət Proqramı İdarəetmə Qrupuna yazmağınızı tövsiyə edirəm: {CONTACT}"
)

CHECK_PROMPT = """Aşağıda istifadəçinin SUALI, çat-botun CAVABI və botun oxuduğu MƏTN var.
Cavabdakı hər proqram faktını (qayda, tələb, tarix, məbləğ, sənəd, kvota, siyahı, öhdəlik,
"bəli" və ya "xeyr" hökmü) MƏTN ilə yoxla.

Fakt DƏSTƏKLƏNİR: MƏTN-də yazılıbsa və ya MƏTN-dən birbaşa çıxırsa. Sözlər fərqli ola bilər.
Fakt DƏSTƏKLƏNMİR:
- MƏTN-də yoxdursa;
- MƏTN onu bir qrup üçün deyir, cavab isə başqa qrupa və ya hamıya aid edirsə (məsələn,
  doktorantura qaydası hamı üçün deyilirsə);
- cavab "bəli" və ya "xeyr" deyir, amma MƏTN sualın özünə bu cavabı vermirsə.
Bunları yoxlama: "(ümumi məlumat, rəsmi sənəddən deyil)" ilə işarələnmiş hissə, "Mənbə:" sətri,
əlaqə e-poçtu, "Bu məlumat ... tarixinə olan vəziyyətdir" cümləsi.

YALNIZ JSON qaytar: {{"unsupported": ["dəstəklənməyən fakt", "..."]}}
Hər fakt dəstəklənirsə: {{"unsupported": []}}

SUAL: {message}

CAVAB:
{reply}

MƏTN:
{context}"""

UNDERSTAND_PROMPT = """Sən Xaricdə təhsil üzrə Dövlət Proqramı haqqında çat-botun ilk addımısan.
İstifadəçinin SON MESAJINI söhbətin kontekstində başa düş və YALNIZ JSON qaytar.

Mesajın növləri:
- "chat": salamlaşma, təşəkkür, sağollaşma, botun özü haqqında sual ("sən kimsən?"), bota
  deyilən söz, tərif, təhqir və ya zarafat, heç bir sual olmayan anlaşılmaz mətn. Bunlara
  qısa, sakit, nəzakətli cavab ver və proqramla bağlı sual verməyə dəvət et.
- "programme": Dövlət Proqramı, xaricdə təhsil, müraciət, tələblər, xərclər, imtahanlar,
  sertifikatlar, universitetlər, siyahılar, elanlar, tarixlər, nəyin dərc olunub-olunmadığı
  və ya bunlarla bağlı anlayışlar haqqında istənilən sual - qısa və ya qeyri-müəyyən olsa
  belə (məsələn, "elan çıxıb?"). Şübhə edirsənsə, "programme" seç.
- "offtopic": yalnız Dövlət Proqramı və xaricdə təhsillə AÇIQ-AYDIN heç bir əlaqəsi olmayan
  mövzu (məsələn, idman, hava, filmlər). Xaricdə yaşayış xərcləri - yemək, kirayə, nəqliyyat,
  ölkələr üzrə məbləğlər - haqqında suallar offtopic DEYİL, proqramın maliyyələşdirməsinə aiddir.

JSON sahələri:
- "type": yuxarıdakı növlərdən biri.
- "reply": yalnız "chat" və "offtopic" üçün - qısa, səmimi cavab, istifadəçinin dilində.
  "offtopic" üçün nəzakətlə bildir ki, yalnız Dövlət Proqramı ilə bağlı kömək edirsən, və
  proqramla bağlı sual verməyə dəvət et. Proqram haqqında HEÇ BİR fakt yazma.
  "programme" üçün boş saxla.
- "question": yalnız "programme" üçün - tam, müstəqil sual. İstifadəçinin ÖZ SÖZLƏRİNİ
  saxla: sözləri başqa mənalı sözlərlə əvəz etmə. Yalnız söhbətdən aydın olan çatışmayan
  hissəni əlavə et (məsələn, əvvəl magistratura soruşulubsa, "bəs bakalavr üçün?" -> eyni
  mövzunu bakalavriat üçün soruşan sual). Söhbət yoxdursa və ya mesaj özü tamdırsa, onu
  olduğu kimi saxla, yalnız yazı səhvlərini düzəlt.
  Qısa davam sualında ("bəs ...?", "nə vaxt?", "harada?") mövzu mesajın özündə deyilmirsə,
  mövzunu söhbətdən götürüb sualda ADI İLƏ yaz (məsələn, əvvəl aylıq yaşayış xərcindən
  danışılıbsa, "bəs nə qədərdir?" -> "Aylıq yaşayış xərci nə qədərdir?").
- "search": yalnız "programme" üçün - sualın 3 fərqli yazılışı: (1) dövlət sənədlərinin
  rəsmi dilində, (2) sadə dildə, (3) ən çox ehtimal olunan mənanı açıq göstərməklə
  (hansı təhsil səviyyəsi, hansı xərc və s.).

Nümunə: {{"type": "programme", "reply": "", "question": "...", "search": ["...", "...", "..."]}}

SÖHBƏT:
{history}

SON MESAJ: {message}"""

ANSWER_PROMPT = """Sən Xaricdə təhsil üzrə Dövlət Proqramı haqqında suallara cavab verən səmimi köməkçisən.

NECƏ DANIŞMALISAN:
- Təcrübəli, mehriban bir məsləhətçi kimi danış. İstifadəçiyə "siz" deyə müraciət et.
- Sadə sözlərlə izah et. Uzun hüquqi cümlələri olduğu kimi köçürmə - mənasını qısa və
  aydın çatdır.
- Qısa yaz: adətən 2-5 cümlə. Siyahı lazımdırsa, qısa siyahı işlət.
- Faktlarda dəqiq ol: rəqəmləri və şərtləri mətndəki kimi saxla.

İKİ NÖV MƏLUMAT VAR:
1) PROQRAM MƏLUMATI - Dövlət Proqramının qaydaları, tələbləri, tarixləri, məbləğləri,
   sənədləri, kvotaları, universitetləri və öhdəlikləri.
   Bunları YALNIZ aşağıdakı MƏTN-dən götür. Mətndə yoxdursa, öz biliyinlə heç vaxt doldurma.
2) ÜMUMİ MƏLUMAT - beynəlxalq standartların qısa izahı (beynəlxalq imtahanlar,
   sertifikatlar, dil səviyyələri) və standart beynəlxalq şkalaların çevrilməsi. Bunu öz
   biliyinlə 1-2 cümlə ilə verə bilərsən, amma həmin hissənin sonuna mütləq
   "(ümumi məlumat, rəsmi sənəddən deyil)" yaz. Məsləhət vermə.
   Azərbaycana və ya Dövlət Proqramına xas termin və qısaltmaları yalnız MƏTN-dən izah et;
   mətndə izahı yoxdursa, izah etmə.

QAYDALAR:
- Cavabı istifadəçinin SON MESAJINA ver, söhbəti nəzərə al. "Botun anladığı sual" yalnız
  köməkçi təxmindir; istifadəçinin öz sözləri ilə uyğun gəlmirsə, istifadəçinin sözlərinə əsaslan.
- İstifadəçi gündəlik sözlər, sinonimlər, qısaltmalar və ya səhv yazılış işlədə bilər.
  Sözlərə yox, MƏNAYA bax.
- Rəqəmi yalnız sualın soruşduğu tələbə aid olduqda işlət. Başqa təhsil səviyyəsinin və
  ya başqa imtahanın rəqəmini cavab kimi vermə.
- İstifadəçi öz nəticəsini deyib bəs edib-etmədiyini soruşursa: bəs edirsə "Bəli", bəs
  etmirsə "Xeyr" ilə başla, sonra tələbi göstər. Şkala çevrilməsi lazımdırsa, ümumi
  məlumatdan istifadə et və onu işarələ.
- Sual aydın deyilsə (məsələn, təhsil səviyyəsi deyilməyib) və mətndə bir neçə hal üçün
  cavab varsa, hər hal üçün ayrıca qısa cavab ver.
- Mətndə sualın mövzusu haqqında heç nə yoxdursa, "bəli" və ya "xeyr" deyərək cavab
  uydurma. Proqram məlumatı mətndə yoxdursa, yalnız NO_ANSWER yaz, başqa heç nə yazma.
  Cavabının bütün mənası "bu barədə məlumat yoxdur" olacaqsa, onu öz sözlərinlə yazma -
  yalnız NO_ANSWER yaz.
- Siyahının və ya elanın dərc olunub-olunmadığı soruşulursa: mətndəki tədris ilini
  istifadəçinin soruşduğu tədris ili ilə müqayisə et. İstifadəçi il deməyibsə, mətndəki ən
  son ili götür. Dərc olunubsa, bunu de və linki ver. Soruşulan il üçün mətndə dərc
  olunduğu yazılmayıbsa, hələ dərc olunmadığını, saytda hansı ilin siyahısı olduğunu de və
  dp.edu.az saytını bir müddət sonra yoxlamağı tövsiyə et. YALNIZ dərc olunma vəziyyəti haqqında cavabların sonunda mütləq
  ayrıca cümlə yaz: "Bu məlumat <mətndəki yoxlanılma tarixi> tarixinə olan vəziyyətdir."
- Konkret ölkənin siyahıda olub-olmadığı soruşulursa: mətndə siyahıdakı ölkələr sadalanıbsa,
  ona əsasən "Bəli" (neçə proqram olduğunu da de) və ya "Xeyr" de və siyahının linkini ver.
  Mətndə ölkələr sadalanmayıbsa, "bəli", "xeyr" və ya "ola bilər" demə - yalnız linki ver.
- Konkret universitetin və ya proqramın siyahıda olub-olmadığı soruşulursa və həmin ad
  mətndə yoxdursa: "bəli", "xeyr" və ya "ola bilər" demə. Siyahının linkini ver və adı
  həmin siyahıda axtarmağı tövsiyə et.
- İstifadəçinin son mesajının dilində cavab ver.
- Proqram məlumatı istifadə etmisənsə, sonda ayrıca sətirdə yaz: Mənbə: <istifadə etdiyin
  səhifənin linki>. Linki mötərizəsiz, sadə yaz.

BUGÜNKÜ TARİX: {today}

MƏTN:
{context}

SÖHBƏTİN SONU:
{history}

İSTİFADƏÇİNİN SON MESAJI: {message}
(Botun anladığı sual, təxmini: {question})
{offtopic_note}

CAVAB:"""


def _cost(usage):
    return sum(i / 1e6 * rag.PRICES.get(m, (0, 0))[0] + o / 1e6 * rag.PRICES.get(m, (0, 0))[1]
               for m, (i, o) in usage.items())


def _format_history(history):
    recent = history[-2 * HISTORY_TURNS:]
    return "\n".join(f"{'İstifadəçi' if m['role'] == 'user' else 'Bot'}: {m['content']}"
                     for m in recent) or "(söhbət yeni başlayır)"


def understand(message, history, usage):
    """Step 1: what kind of message is this, and what is the full question?"""
    r = rag._setup()["llm"].chat.completions.create(
        model=rag.SEARCH_MODEL, temperature=0, response_format={"type": "json_object"},
        messages=[{"role": "user", "content": UNDERSTAND_PROMPT.format(
            history=_format_history(history), message=message)}])
    tokens = usage.setdefault(rag.SEARCH_MODEL, [0, 0])
    tokens[0] += r.usage.prompt_tokens
    tokens[1] += r.usage.completion_tokens
    try:
        data = json.loads(r.choices[0].message.content)
    except (json.JSONDecodeError, TypeError):
        data = {}
    kind = data.get("type")
    if kind not in ("chat", "offtopic", "programme"):
        kind = "programme"            # when unsure, search - never answer from memory
    return kind, data


def _says_only_no_info(text):
    """Safety net: the model sometimes writes "məlumat mətndə yoxdur" in its own words
    instead of the NO_ANSWER marker. A SHORT reply that only says "there is no
    information" - with no "amma/lakin", so it is not a partial answer - is treated as
    a refusal, so the user still gets the friendly message and the email."""
    body = "\n".join(line for line in text.splitlines()
                     if not line.strip().lower().startswith("mənbə"))
    no_info = re.search(r"(məlumat|informasiya)[^.]{0,40}(yoxdur|tapılmadı|göstərilməyib|qeyd olunmayıb)",
                        body, re.IGNORECASE)
    partial = re.search(r"\b(amma|lakin|ancaq|bununla belə)\b", body, re.IGNORECASE)
    return bool(no_info) and not partial and len(body.strip()) < 220


def check(message, reply, context, usage):
    """Step 4: which programme facts in the reply does the text NOT support?
    The answer prompt already says "only from the text", but the model breaks that rule:
    asked about paying bank debt from the stipend, it invented two different rules in two runs."""
    r = rag._setup()["llm"].chat.completions.create(
        model=CHECK_MODEL, temperature=0, response_format={"type": "json_object"},
        messages=[{"role": "user", "content": CHECK_PROMPT.format(
            message=message, reply=reply, context=context)}])
    tokens = usage.setdefault(CHECK_MODEL, [0, 0])
    tokens[0] += r.usage.prompt_tokens
    tokens[1] += r.usage.completion_tokens
    try:
        found = json.loads(r.choices[0].message.content).get("unsupported", [])
    except (json.JSONDecodeError, TypeError, AttributeError):
        found = []                    # a broken check reply: send the answer as before
    return [str(f).strip() for f in found if str(f).strip()] if isinstance(found, list) else []


_corpus = {}


def _load_corpus():
    """The chunk and page files, loaded once. Chroma ids are "chunk-N" = position N in
    spike_chunks.json, because 06_index_chroma.py numbers them in that order."""
    if not _corpus:
        base = rag.ROOT / "data" / "processed"
        _corpus["chunks"] = json.loads((base / "spike_chunks.json").read_text(encoding="utf-8"))
        _corpus["pages"] = {d["doc_id"]: d for d in
                            json.loads((base / "spike_docs.json").read_text(encoding="utf-8"))}
    return _corpus


def read_big(chosen):
    """SEARCH SMALL, READ BIG. Search finds small chunks because they match precisely, but
    a small chunk can miss the sentence right next to it. Content/70 says "the participant
    pays the visa fee" in one chunk and "and gets it refunded" in the next one; given only
    the first, the bot answered that visa costs are NOT covered.

    So the model reads more than the chunk that matched:
      - a page up to PAGE_LIMIT characters -> the whole page
      - a longer page (the FAQ)            -> the chosen chunk plus its neighbours
    Returns (url, text) blocks, each short page at most once."""
    corpus = _load_corpus()
    chunks, pages = corpus["chunks"], corpus["pages"]
    blocks, whole_pages, used_chunks = [], set(), set()
    for cid, doc, meta in chosen:
        doc_id = meta["doc_id"]
        page = pages.get(doc_id)
        if doc_id in whole_pages:
            continue
        if page and len(page["text"]) <= PAGE_LIMIT:
            whole_pages.add(doc_id)
            blocks.append((meta["url"], page["text"]))
            continue
        n = int(cid.rsplit("-", 1)[1])
        if not (0 <= n < len(chunks)) or chunks[n]["doc_id"] != doc_id:
            blocks.append((meta["url"], doc))            # index and chunk file out of step
            continue
        ids = [i for i in range(n - NEIGHBOURS, n + NEIGHBOURS + 1)
               if 0 <= i < len(chunks) and chunks[i]["doc_id"] == doc_id and i not in used_chunks]
        used_chunks.update(ids)
        if ids:
            opening = " ".join(page["text"][:300].split()) if page else ""
            body = "\n".join(chunks[i]["body"] for i in ids)
            blocks.append((meta["url"], f"{opening}\n---\n{body}" if opening else body))
    return blocks


def chat(message, history=None):
    """One message in, one reply out. `history` is updated in place."""
    history = [] if history is None else history
    rag._setup()
    t0, usage = time.time(), {}
    kind, data = understand(message, history, usage)
    info = {"type": kind}

    if kind == "chat" and str(data.get("reply", "")).strip():
        reply = data["reply"].strip()
    else:
        # "offtopic" is only a suggestion (D-012). Search runs anyway, and the polite off-topic
        # reply is used only if the documents have nothing. It used to skip search entirely, so
        # one wrong label ("ABŞ-da aylıq xərc norması" -> offtopic) meant a guaranteed wrong answer.
        suggested_offtopic = kind == "offtopic"
        info["type"] = "programme"
        question = str(data.get("question") or message).strip()
        searches = [s for s in data.get("search", []) if isinstance(s, str) and s.strip()]
        # SEARCH with the user's own words AND the rewrites; the rewrites never reach the answer.
        previous = next((m["content"] for m in reversed(history) if m["role"] == "user"), "")
        extra = [f"{previous} {message}"] if previous else []   # a follow-up keeps its topic in search
        queries = list(dict.fromkeys([message, question] + searches[:rag.N_REWRITES] + extra))
        pick_question = message if question == message else f"{message}\n(tam sual: {question})"
        if previous:
            pick_question += f"\n(əvvəlki sual: {previous})"
        chosen = rag.pick(pick_question, rag.search(queries), usage)
        blocks = read_big(chosen) if READ_BIG else [(meta["url"], doc) for _, doc, meta in chosen]
        context = "\n\n".join(f"[mənbə {n}] {url}\n{body}" for n, (url, body) in enumerate(blocks, 1))
        info["read_chars"] = len(context)
        info["context"] = context         # the eval judge checks the reply against this text
        text = rag._chat(rag.ANSWER_MODEL, ANSWER_PROMPT.format(
            context=context, history=_format_history(history), message=message, question=question,
            today=time.strftime("%d.%m.%Y"),
            offtopic_note=OFFTOPIC_NOTE if suggested_offtopic else ""), usage)
        refused = "NO_ANSWER" in text or _says_only_no_info(text)
        if CHECK and not refused:
            info["unsupported"] = check(message, text, context, usage)
            refused = bool(info["unsupported"])
        if refused and suggested_offtopic and str(data.get("reply", "")).strip():
            reply, info["type"] = data["reply"].strip(), "offtopic"
        else:
            reply = NO_ANSWER_REPLY if refused else text
        info.update(question=question, searches=searches, refused=refused,
                    chosen=[(cid, meta["doc_id"]) for cid, _, meta in chosen])

    history += [{"role": "user", "content": message}, {"role": "assistant", "content": reply}]
    info["seconds"] = time.time() - t0
    info["cost"] = _cost(usage)
    return reply, info


def _show_debug(info):
    print(f"   [type: {info['type']}]")
    if info["type"] == "programme":
        print(f"   [bot understood: {info['question']}]")
        for s in info["searches"]:
            print(f"   [search: {s}]")
        print(f"   [pages given to the model: {', '.join(d for _, d in info['chosen'])}]")
        if info["refused"]:
            print("   [NO_ANSWER -> friendly refusal]")
    print(f"   [{info['seconds']:.1f}s, ~${info['cost']:.5f}]")


if __name__ == "__main__":
    debug = "--debug" in sys.argv
    args = [a for a in sys.argv[1:] if a != "--debug"]

    print("Yüklənir, bir az gözləyin...")
    rag._setup()                      # the ~20 s model load happens once, here

    if args:                          # one question, then exit
        reply, info = chat(args[0])
        print("\n" + reply)
        if debug:
            _show_debug(info)
        sys.exit()

    print("\n" + WELCOME)
    history = []
    while True:
        try:
            message = input("\nSiz: ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not message:
            continue
        if message.lower() in ("çıx", "cix", "exit", "quit"):
            break
        reply, info = chat(message, history)
        print("\nBot: " + reply)
        if debug:
            _show_debug(info)
    print("\nSağ olun, uğurlar!")
