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

WELCOME = (
    "Salam! Mən Xaricdə təhsil üzrə Dövlət Proqramı ilə bağlı suallarınıza cavab "
    "verən köməkçiyəm.\n"
    "Tələblər, xərclər, müraciət qaydaları - nə maraqlandırır, soruşun.\n\n"
    "Qeyd: bu, rəsmi olmayan tələbə layihəsidir. Vacib qərarlardan əvvəl məlumatı "
    "dp.edu.az saytında yoxlayın."
)

NO_ANSWER_REPLY = (
    "Təəssüf ki, bu barədə rəsmi sənədlərdə məlumat tapa bilmədim. Dəqiq cavab üçün "
    f"Dövlət Proqramı İdarəetmə Qrupuna yazmağınızı tövsiyə edirəm: {CONTACT}"
)

UNDERSTAND_PROMPT = """Sən Xaricdə təhsil üzrə Dövlət Proqramı haqqında çat-botun ilk addımısan.
İstifadəçinin SON MESAJINI söhbətin kontekstində başa düş və YALNIZ JSON qaytar.

Mesajın növləri:
- "chat": salamlaşma, təşəkkür, sağollaşma, botun özü haqqında sual ("sən kimsən?").
- "programme": Dövlət Proqramı, xaricdə təhsil, müraciət, tələblər, xərclər, imtahanlar,
  sertifikatlar, universitetlər və ya bunlarla bağlı anlayışlar haqqında istənilən sual.
  Şübhə edirsənsə, "programme" seç.
- "offtopic": Dövlət Proqramı və xaricdə təhsillə heç bir əlaqəsi olmayan mövzu.

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
- İstifadəçinin son mesajının dilində cavab ver.
- Proqram məlumatı istifadə etmisənsə, sonda ayrıca sətirdə yaz: Mənbə: <istifadə etdiyin
  səhifənin linki>. Linki mötərizəsiz, sadə yaz.

MƏTN:
{context}

SÖHBƏTİN SONU:
{history}

İSTİFADƏÇİNİN SON MESAJI: {message}
(Botun anladığı sual, təxmini: {question})

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


def chat(message, history=None):
    """One message in, one reply out. `history` is updated in place."""
    history = [] if history is None else history
    rag._setup()
    t0, usage = time.time(), {}
    kind, data = understand(message, history, usage)
    info = {"type": kind}

    if kind in ("chat", "offtopic") and str(data.get("reply", "")).strip():
        reply = data["reply"].strip()
    else:
        info["type"] = "programme"
        question = str(data.get("question") or message).strip()
        searches = [s for s in data.get("search", []) if isinstance(s, str) and s.strip()]
        # SEARCH with the user's own words AND the rewrites; the rewrites never reach the answer.
        queries = list(dict.fromkeys([message, question] + searches[:rag.N_REWRITES]))
        pick_question = message if question == message else f"{message}\n(tam sual: {question})"
        chosen = rag.pick(pick_question, rag.search(queries), usage)
        context = "\n\n".join(f"[mənbə {n}] {meta['url']}\n{doc}"
                              for n, (_, doc, meta) in enumerate(chosen, 1))
        text = rag._chat(rag.ANSWER_MODEL, ANSWER_PROMPT.format(
            context=context, history=_format_history(history), message=message, question=question), usage)
        refused = "NO_ANSWER" in text
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
