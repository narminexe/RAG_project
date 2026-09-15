# Eval report: 2026-09-15_002138

Bot: answer model `gpt-4.1-mini`, search model `gpt-4o-mini`, read big = True. Judge: `gpt-5.4 / prompt f0fa4f`.  
34 questions x 2 runs = 68 answers.

## Scores (judge)

| | correct | partly | wrong |
|---|---|---|---|
| should answer (in_documents = yes) | 25 (66%) | 6 (16%) | 7 (18%) |
| should refuse (in_documents = no) | 11 (37%) | 5 (17%) | 14 (47%) |
| all | 36 (53%) | 11 (16%) | 21 (31%) |

## Simple checks

- answers that answered or declined as expected (no LLM): 47/68
- questions answered in another language (no LLM): 9  q21 (en -> az), q22 (en -> az), q23 (en -> az), q29 (en -> az), q30 (ru -> az), q31 (ru -> az), q32 (ru -> az), q33 (ru -> az), q34 (ru -> az)
- questions with a made-up programme fact (judge): 9  q06, q07, q08, q09, q12, q16, q17, q24, q29
- questions graded differently in different runs: 7  q09, q11, q12, q13, q20, q29, q32
- bot errors: 0
- bot cost: $0.162, 4.2 s per answer
- judge cost: $0.583

## Check the label

in_documents = no, but the bot answered and the judge found every fact in the text it read. Maybe a page does answer these: q04, q15, q17, q24, q26, q32

## Failures

Every question with at least one answer that is not correct. All runs are shown, so you can see when a question flips.

### q02: qayitmasaq nolar?

- in_documents: no
- your answer: tədris müddəti bitdikdən sonra ən geci 2 (iki) ay ərzində Azərbaycan Respublikasına qayıtmaq, qayıtdıqdan sonra 10 (on) təqvim günü müddətində Nazirliyə bu barədə məlumat vermək və Azərbaycan Respublikasında 5 (beş) il (öhdəlik müddəti) əmək fəaliyyəti göstərmək
- **run 1: partly**
  - bot: Salam! Mən Xaricdə təhsil üzrə Dövlət Proqramı haqqında məlumat vermək üçün buradayam. Proqramla bağlı sualınız varsa, məmnuniyyətlə cavab verərəm!
  - judge: IN_DOCUMENTS is no, so the expected behavior is to decline or say the information is not available. The bot did not answer the question, but it also did not clearly refuse or direct the user to the programme contact; instead it gave a generic greeting and invitation to ask a question. Since it failed to provide the expected decline/helpful limitation message, this is only partially acceptable.
  - pages read: none
- **run 2: partly**
  - bot: Salam! Sualınız varsa, Dövlət Proqramı ilə bağlı kömək etməyə hazıram.
  - judge: IN_DOCUMENTS is no, so the expected behavior is to decline or say the information is not available. The bot did not answer the question, but it also did not clearly refuse or direct the user to the official contact; it only gave a generic greeting. Since it did not invent any programme facts, there is no made-up content.
  - pages read: none

### q03: kesilsek ne olur?

- in_documents: yes
- your answer: Kesrinizi duzeldene qeder teqaud almirsiniz ve teqaudunuz bloklanir. Duzeltdikden sonra ise teqaudunuz blok hesabdan cixir
- **run 1: wrong**
  - bot: Salam! Sualınız varsa, Dövlət Proqramı ilə bağlı kömək etməyə hazıram.
  - judge: IN_DOCUMENTS is yes, so the answer is in the programme documents and the bot was expected to answer it. Instead, it gave a generic greeting and did not address the question at all. Since a refusal or non-answer is always wrong when IN_DOCUMENTS is yes, this must be graded wrong.
  - pages read: none
- **run 2: wrong**
  - bot: Salam! Sualınız varsa, Dövlət Proqramı ilə bağlı kömək etməyə hazıram.
  - judge: IN_DOCUMENTS is yes, so the programme documents do contain an answer and a refusal or non-answer is automatically wrong. The bot did not answer the question at all; it only sent a generic greeting, missing the key fact that the stipend is blocked until the failed grade is corrected and then unblocked. It also did not invent any unsupported programme facts.
  - pages read: none

### q04: is verirler sonra?

- in_documents: no
- your answer: Dövlət Proqramı çərçivəsində nüfuzlu xarici ali təhsil müəssisələrində təhsilini uğurla bitirmiş gənclərin Azərbaycan Respublikasının dayanıqlı inkişafını təmin edəcək prioritet sahələrdə məşğulluğunun təmin edilməsi xüsusi əhəmiyyət kəsb edir. Bu prioritet istiqamətin reallaşdırılması üçün ehtiyac duyulan sahələr üzrə iş təkliflərinin verilməsi və karyerada yüksəliş mexanizmi hazırlanacaqdır. Dövlət orqanlarında bu Dövlət Proqramı çərçivəsində məzun olmuş şəxslərin işlə təminatına üstünlük veriləcəkdir.
- **run 1: wrong**
  - bot: Bəli, Dövlət Proqramı çərçivəsində xaricdə təhsilini başa vurduqdan sonra Azərbaycan Respublikasının ali təhsil müəssisəsində əsas iş yeri olmaqla ən azı 5 il müddətinə əmək fəaliyyətinə cəlb edilmək tələb olunur. Bu, proqramın əsas öhdəliklərindən biridir. Mənbə: dp.edu.az/uploads/fileuploads/2026/05/4ec0f92d30d04271886e0bc82fcae744.pdf
  - judge: IN_DOCUMENTS is no, so the expected behavior is to decline and say the documents do not answer the question. Instead, the bot gave a concrete programme-specific answer about a 5-year work obligation after graduation. That fact is in the provided text, but because the question is not answerable from the programme documents according to IN_DOCUMENTS, answering instead of refusing makes the reply wrong; it is not made up since the stated fact is supported by the text.
  - pages read: pdf-secim-meyarlari-2026, dp-content-69
- **run 2: wrong**
  - bot: Bəli, Dövlət Proqramı çərçivəsində xaricdə təhsilini başa vurduqdan sonra Azərbaycan Respublikasının ali təhsil müəssisəsində əsas iş yeri olmaqla ən azı 5 il müddətinə əmək fəaliyyətinə cəlb edilmək tələb olunur. Bu, proqramın əsas öhdəliklərindən biridir. Mənbə: dp.edu.az/uploads/fileuploads/2026/05/4ec0f92d30d04271886e0bc82fcae744.pdf
  - judge: IN_DOCUMENTS is no, so the bot should have declined rather than answering. Instead, it gave a definite programme rule about a 5-year employment obligation after graduation. That fact does appear in the provided text, so it is not made up, but answering instead of refusing is still wrong under the grading rule for IN_DOCUMENTS=no.
  - pages read: pdf-secim-meyarlari-2026, dp-content-69

### q06: ne elesem qebul sansim artar?

- in_documents: no
- your answer: Qəbul aldığınız və müraciət etdiyiniz universitetin DP-in universitetlər və ixtisaslar siyahısında olduğundan əmin olun. Müsahibəyə erkəndən hazırlaşmağa başlayın. İxtisas mövzularını yaxşı təkrar edin və ümumi dünyagörüşü suallarına hazırlıqlı olun. Müsahibə zamanı özünüzü ağıllı göstərmək üçün mövzunu bilmədiyiniz yerlərə çəkməyin. Həyəcanlanmayın
- **run 1: wrong** (made up)
  - bot: Qəbul şansınızı artırmaq üçün: - Sənədlərinizi tam və düzgün təqdim edin, xüsusilə ÜOMG 81+ olmalıdır. - Ən azı 2 tövsiyə məktubu təqdim edin, biri akademik olmalıdır. - C1 səviyyəsində beynəlxalq dil sertifikatı təqdim edin. - Sağlamlıq arayışınızın AZS-086/1 formasında və etibarlı olmasına diqqət edin. - “Yüksəliş” müsabiqəsinin qalibi olsanız, müsahibədən azad olursunuz, bu üstünlükdür. - Müsah...
  - judge: IN_DOCUMENTS is no, so the bot should have declined and said the programme documents do not answer how to increase acceptance chances. Instead, it gave concrete programme-specific tips and even used facts that are only for a specific group while presenting them as general advice. It did not refuse or provide the contact email.
  - pages read: pdf-secim-meyarlari-2026, pdf-doktorantura
- **run 2: wrong** (made up)
  - bot: Qəbul şansınızı artırmaq üçün: - Beynəlxalq fənn olimpiadalarından ən azı birində medal qazanmağa çalışın (qızıl, gümüş və ya bürünc). - Müsahibəyə yaxşı hazırlaşın: ixtisas bilikləri, məntiqi mühakimə və kommunikasiya bacarıqlarınızı inkişaf etdirin. - Dil sertifikatınızı C1 səviyyəsində təmin edin. - Sənədlərinizi tam və düzgün təqdim edin, vaxtında elektron ərizəni təsdiq edin. Bu addımlar şans...
  - judge: IN_DOCUMENTS is no, so the bot should have declined and said the documents do not provide this kind of acceptance-improving advice. Instead, it gives concrete programme-related recommendations as if known, including a C1 certificate requirement and document/timing advice, and it even applies the olympiad rule as general advice rather than stating the actual exception. These are unsupported or misapplied facts for this question, so the reply is incorrect and contains made-up programme facts.
  - pages read: dp-faq, pdf-doktorantura, pdf-secim-meyarlari-2026

### q07: hansi senedler lazimdi? bakalavr ucun

- in_documents: yes
- your answer: Ümumi təhsil müəssisələrinin buraxılış sinfində təhsil aldığına dair arayış və ya tam orta təhsil haqqında attestatın surəti; qəbul sənədi (bakalavriat səviyyəsi üzrə); beynəlxalq səviyyəli dil sertifikatının surəti; hərbi bilet və ya ASAN xidmətdən əldə olunan hərbi xidmətdən möhlət hüququ haqqında arayış; DİM qəbul imtahanının nəticəsi; sağlamlıq haqqında arayış (AZS-086/1); olduğu təqdirdə beynəlxalq təhsil proqramının (IB, Alevel, AP) göstəricisini təsdiq edən arayışın surəti; olduğu təqdirdə beynəlxalq olimpiada qalibi olduğunu təsdiq edən sənədin surəti; SAT və ya ACT nəticəsini təsdiq edən arayışın surəti.
- **run 1: partly**
  - bot: Bakalavr səviyyəsi üçün tələb olunan sənədlər: 1. Ümumitəhsil müəssisələrinin buraxılış sinfində təhsil aldığına dair arayış və ya tam orta təhsil haqqında attestatın surəti (orta ixtisas təhsili varsa, diplomun surəti). 2. Qəbul sənədi (hazırda təhsil alanlar üçün arayış). 3. Beynəlxalq səviyyəli dil sertifikatının surəti (C1 səviyyəsində). 4. Hərbi bilet və ya ASAN xidmətdən möhlət haqqında aray...
  - judge: IN_DOCUMENTS is yes, and the bot mostly matches the bachelor document list in the provided text: school certificate/attestat, admission document, language certificate, military document, DİM result, and health certificate. However, it omits important listed items from the reference answer such as the optional IB/A-level/AP proof and international olympiad document, and it weakens SAT/ACT by saying only 'üstünlükdür' instead of presenting it as an application document 'olduğu təqdirdə'. It also adds wording like 'orta ixtisas tehsili varsa' and 'C1 səviyyəsində' that are supported by the text, so not made up.
  - pages read: pdf-secim-meyarlari-2026
- **run 2: partly** (made up)
  - bot: Bakalavr səviyyəsi üçün tələb olunan sənədlər: 1. Ümumitəhsil müəssisələrinin buraxılış sinfində təhsil aldığına dair arayış və ya tam orta təhsil haqqında attestatın surəti (orta ixtisas təhsili varsa, diplomun surəti). 2. Qəbul sənədi (hazırda təhsil alanlar üçün arayış). 3. Beynəlxalq səviyyəli dil sertifikatının surəti (C1 səviyyəsində). 4. Hərbi bilet və ya ASAN xidmətdən möhlət haqqında aray...
  - judge: The bot includes several correct bachelor-level items from the document: school certificate/attestat, acceptance document, language certificate at C1, military document, DIM result, health form, and the translation note. However, it omits the optional IB/A-level/AP proof and instead adds unsupported or mixed-up facts such as transcript with ÜOMG 81+, SAT/ACT being merely a preference without framing it as a document copy, and an олимпиада exemption statement not tied to the required document copy as in the reference. Because it states programme facts that are not supported for bachelor documents in the shown text, this is made up.
  - pages read: pdf-secim-meyarlari-2026

### q09: bakalavr dp ile oxudumsa master dp ile oxuya bilerem yene?

- in_documents: yes
- your answer: Beli, her tehsil pillesi uzre 1 defe DP iistifade ede bilersiniz
- **run 1: wrong** (made up)
  - bot: Xeyr, eyni təhsil səviyyəsi üzrə Dövlət Proqramına namizəd olmaq olmaz. Yəni, bakalavr səviyyəsində Dövlət Proqramı ilə təhsil almış şəxs magistratura səviyyəsində də proqramda iştirak edə bilməz. Mənbə: dp.edu.az/az/faq
  - judge: IN_DOCUMENTS is yes, so the bot should answer using the programme documents. The reference says a person may use the State Programme once per education level, so someone who used it for bachelor's may still use it for master's. The bot replied the opposite and incorrectly extended an 'same level' restriction to a different level.
  - pages read: dp-faq
- **run 2: partly**
  - bot: Xeyr, eyni təhsil səviyyəsi üzrə Dövlət Proqramına yenidən müraciət etmək olmaz. Bakalavr səviyyəsində Dövlət Proqramı ilə təhsil almış şəxs magistratura səviyyəsi üzrə müraciət edə bilər. Amma magistraturada Dövlət Proqramı və ya digər dövlət proqramları çərçivəsində təhsil almış şəxslər eyni səviyyə üçün yenidən müraciət edə bilməzlər. Mənbə: dp.edu.az/az/faq
  - judge: IN_DOCUMENTS is yes, and the key rule in the documents is that people who already studied under state support at the master's level cannot apply again for the same level. That implies a person funded for bachelor can still apply for master, so the bot's main conclusion matches the reference. However, it starts with "Xeyr," which is misleading for this user's exact question, even though the following sentences correct it.
  - pages read: dp-faq, pdf-doktorantura, pdf-secim-meyarlari-2026

### q11: viza xərcini qarşılayır?

- in_documents: yes
- your answer: Beli, ilk once odenisi ozunuz edirsiniz daha sonra lazimi senedler istenilerek sizin bank hesabiniza geri odeme edilir
- **run 1: correct**
  - bot: Bəli, Dövlət Proqramı viza xərclərini qarşılayır. Lakin viza rüsumu və qeydiyyat xərcləri əvvəlcə proqram iştirakçısı tərəfindən ödənilir, sonra təqdim olunan sənədlər əsasında həmin məbləğ geri qaytarılır. Bu məlumat 15.09.2026 tarixinə olan vəziyyətdir. Mənbə: dp.edu.az/az/content/70
  - judge: The bot reply matches the key facts in the documents and the reference: visa costs are covered by the programme, but the participant pays first and is later reimbursed upon submitting supporting documents. Nothing important is incorrect or misleading; the extra date/source note does not change the substance. All stated programme facts are supported by the provided text.
  - pages read: dp-faq, dp-content-70, dp-content-68
- **run 2: partly**
  - bot: Xeyr, viza xərcləri proqram iştirakçıları tərəfindən ödənilir. Dövlət Proqramı isə bu xərclərin təsdiqedici sənədlər əsasında geri ödənməsini təmin edir. Bu məlumat 15.09.2026 tarixinə olan vəziyyətdir. Mənbə: dp.edu.az/az/content/70
  - judge: IN_DOCUMENTS is yes, so the bot should answer from the documents. The key fact is that visa costs are covered by the programme, but paid upfront by the participant and later reimbursed upon submission of supporting documents. The bot reply is misleading because it starts with "No" and says participants pay, without clearly answering that the programme does cover and reimburse these costs.
  - pages read: dp-content-70, dp-content-68

### q12: bəs nə vaxt qaytarırlar?

- in_documents: yes
- your answer: kruatorunuz size bununla bagli melumat verir ve siz lazimi subutlari (invoice, ticket price, bank statement ve s ola biler), bank rekvizitleriniz ile birlikde ona gonderirsiniz
- **run 1: correct**
  - bot: Viza xərclərinin geri qaytarılması üçün sənədləri təqdim etdikdən sonra, Nazirliyin maliyyələşdirən qurumu təqdim olunan sənədlərin rəsmiləşdirildiyi tarixə qüvvədə olan rəsmi məzənnəyə uyğun Azərbaycan manatı ilə ödənişi proqram iştirakçısının bank hesabına köçürür. Konkret vaxt mətndə göstərilməyib, amma sənədlər tam və düzgün təqdim olunmalıdır. Bu məlumat 15.09.2026 tarixinə olan vəziyyətdir. ...
  - judge: IN_DOCUMENTS is yes, so the bot needed to answer from the programme text. The reply correctly says the reimbursement is made after supporting documents are submitted and that no specific timeline is stated in the text; this matches the available source better than the reference's extra procedural detail. It does not materially mislead, though it adds a mild interpretation about documents being complete/correct, which is consistent with the document requirement.
  - pages read: dp-content-74, pdf-doktorantura, dp-faq, dp-content-70
- **run 2: partly** (made up)
  - bot: Viza xərcləri ödənildikdən sonra təsdiqedici sənədləri (ərizə, pasport və viza səhifəsi, qəbz və s.) Dövlət Proqramı İdarəetmə Qrupuna təqdim etdikdə, xərclər rəsmi məzənnəyə uyğun bank hesabınıza geri ödənilir. Ödənişlərin geri qaytarılması üçün ərizə və sənədlər tam olmalıdır. Bu məlumat 15.09.2026 tarixinə olan vəziyyətdir. Mənbə: dp.edu.az/az/content/74
  - judge: IN_DOCUMENTS is yes, so the bot should answer from the documents. The reply correctly says reimbursement happens after the participant submits the required supporting documents electronically and that payment is made to the participant's bank account in AZN at the official exchange rate effective when the Ministry's order is formalized. However, it adds a concrete document list for visa reimbursement that is incomplete/inexact versus the source and does not mention the key timing wording from the document, so it is not fully precise.
  - pages read: dp-content-74, pdf-doktorantura, dp-faq, dp-content-68

### q13: kruatoum kimdir?

- in_documents: no
- your answer: Dovlet proqramini qazandiginiz teqdirde assign olunacaqdir
- **run 1: correct**
  - bot: Salam! Mən Xaricdə təhsil üzrə Dövlət Proqramı haqqında məlumat vermək üçün buradayam. Proqramla bağlı sualınız varsa, məmnuniyyətlə kömək edərəm!
  - judge: IN_DOCUMENTS is no, so the expected behavior is to decline or say the information is not available from the programme materials. The bot did not answer the question and instead gave a generic prompt about asking a programme-related question; this functions as a polite decline rather than inventing facts. It contains no unsupported programme facts beyond a generic description.
  - pages read: none
- **run 2: partly**
  - bot: Salam! Mən Xaricdə təhsil üzrə Dövlət Proqramı haqqında məlumat vermək üçün buradayam. Proqramla bağlı sualınız varsa, məmnuniyyətlə cavab verərəm!
  - judge: IN_DOCUMENTS is no, so the expected behavior is to decline or say the information is not available from the programme documents. The bot did not answer the question, but it also did not clearly refuse or direct the user to the programme contact; it only gave a generic greeting asking for a programme-related question. It did not invent any unsupported programme fact.
  - pages read: none

### q14: 2026-da neçə nəfər qəbul olunacaq?

- in_documents: yes
- your answer: Dövlət Proqramı üzrə illik kvota 500 nəfər təşkil edir. Bu kvota çərçivəsində rəqabət mühitinin tənzimlənməsi məqsədilə müraciət sayından asılı olaraq prioritet ixtisas istiqamətləri üzrə keçid balları tətbiq edilə bilər
- **run 1: wrong**
  - bot: Təəssüf ki, bu barədə rəsmi sənədlərdə məlumat tapa bilmədim. Dəqiq cavab üçün Dövlət Proqramı İdarəetmə Qrupuna yazmağınızı tövsiyə edirəm: dp22-28@edu.gov.az
  - judge: IN_DOCUMENTS is yes, so a refusal is automatically wrong. The reference answer says the annual quota is 500 people, but the bot replied that it could not find information and redirected the user instead. The reply does not introduce unsupported programme facts, so it is not made up.
  - pages read: pdf-secim-meyarlari-2026, dp-status-university-list, dp-faq, dp-content-81
- **run 2: wrong**
  - bot: Təəssüf ki, bu barədə rəsmi sənədlərdə məlumat tapa bilmədim. Dəqiq cavab üçün Dövlət Proqramı İdarəetmə Qrupuna yazmağınızı tövsiyə edirəm: dp22-28@edu.gov.az
  - judge: IN_DOCUMENTS is yes, so a refusal is automatically wrong. The reference answer says the annual quota is 500 people, while the bot said it could not find the information and redirected the user instead. The reply does not add unsupported programme facts, so it is not made up.
  - pages read: pdf-secim-meyarlari-2026, dp-content-81, dp-status-university-list

### q15: Nece nefer phd olacaq?

- in_documents: no
- your answer: 2026 ucun  Dövlət Proqramına aid 500 nəfərlik kvotanın 20 faizindən çox olmayan hissəsi doktorantura səviyyəsini əhatə edir.
- **run 1: wrong**
  - bot: Dövlət Proqramı çərçivəsində ümumilikdə 2000 nəfərədək tələbə xaricdə bakalavriat, magistratura və doktorantura səviyyələrində təhsil alacaq. Hər il isə 500 nəfərdən çox olmayacaq. PhD (doktorantura) səviyyəsində olanların sayı bu ümumi rəqəmə daxildir, amma ayrıca neçə nəfər doktorantura səviyyəsində olacağı mətndə göstərilməyib. Mənbə: dp.edu.az/az/content/78
  - judge: IN_DOCUMENTS is no, so the bot should decline rather than answer from the documents. Instead, it gives a substantive answer claiming the PhD number is not specified, even though the expected behavior here is refusal; this is therefore wrong. It does not appear to invent unsupported programme facts beyond the quoted overall 2000/500 figures, so made_up is false.
  - pages read: dp-content-78, pdf-secim-meyarlari-2026, dp-faq, pdf-doktorantura
- **run 2: wrong**
  - bot: Dövlət Proqramı çərçivəsində ümumilikdə 2000 nəfərədək Azərbaycan vətəndaşı xaricdə ali təhsil alacaq, bunların içində bakalavriat, magistratura və doktorantura (PhD) səviyyələri var. Hər il 500 nəfərdən çox olmayaraq qəbul edilir, amma PhD səviyyəsi üçün ayrıca konkret say göstərilməyib. Mənbə: dp.edu.az/az/content/78
  - judge: IN_DOCUMENTS is no, so the bot should have declined instead of answering. It gave a substantive programme answer claiming there is no separate PhD count, but the expected behavior here is refusal because the documents available to the bot are treated as not answering this exact question. The stated facts about 2000 total and 500 per year are supported by the text, so there is no made-up fact.
  - pages read: dp-content-78, pdf-secim-meyarlari-2026, dp-content-65

### q16: Waitliste dusdum ne olacaq?

- in_documents: no
- your answer: DP qazananlardan kimse proqramda istirak etmekden imtina ederse, waitlistden namizedler cagirilir
- **run 1: wrong** (made up)
  - bot: Waitlistə düşmək o deməkdir ki, siz hələ təhsil yerinə qəbul olunmamısınız, amma ehtiyat siyahısındasınız. Əgər ayrılmış yerlər dolmazsa və ya bəzi namizədlər imtina edərsə, waitlistdə olanlar sıralama üzrə çağırıla bilər. Bu halda, proqramdan əlavə məlumat və ya çağırış gözləmək lazımdır. Mənbə: dp.edu.az/uploads/fileuploads/2025/08/1715512f051845178834ccda81b368fc.pdf
  - judge: IN_DOCUMENTS is no, so the correct behavior would be to decline and say the programme documents do not provide this information. Instead, the bot gives a substantive explanation about what being on a waitlist means and how candidates may be called if places remain or others decline. That is an answer-as-if-known, so it is wrong here; these waitlist facts are not supported by the provided text.
  - pages read: pdf-doktorantura, dp-faq, dp-content-66
- **run 2: wrong** (made up)
  - bot: Waitlistə düşmək o deməkdir ki, siz hələ təhsil yerinə qəbul olunmamısınız, amma ehtiyat siyahısındasınız. Əgər əsas namizədlərdən kimlərsə imtina edərsə, sizin növbəniz gələ bilər. Bu halda proqramdan əlavə məlumat və ya dəvət ala bilərsiniz. Müsahibə və sənədlərinizin vəziyyətini diqqətlə izləyin. Bu məlumat 15.09.2026 tarixinə olan vəziyyətdir. Mənbə: dp.edu.az/az/faq
  - judge: IN_DOCUMENTS is no, so the expected behavior is to decline and say the programme documents do not provide this information. Instead, the bot gives a substantive answer about what waitlist means and what may happen next, presenting programme-specific information as if known. That makes the reply wrong, and the waitlist claim is unsupported by the provided text.
  - pages read: pdf-doktorantura, dp-faq, dp-content-66

### q17: 98 ortalama, 8 ielts ile nece olduki waitliste dusdum?

- in_documents: no
- your answer: ortalama ve dil senedi size musahibe merhelesine qeder komek edir. Musahibe merhelesi tamamile sizin suallara cavab vermeyinizden, ozunuzu musahibe boyunca yaxsi ifade etmeyinizden ve diger namizedlerden daha yaxsi oldugunuzu subut etmeyinizden asili olacaq
- **run 1: wrong** (made up)
  - bot: Xeyr, 98 ortalama və 8 IELTS ilə waitlistə düşməyinizin səbəbi müsahibə balının 40-dan aşağı olması və ya digər seçim meyarlarında çatışmazlıq ola bilər. Dövlət Proqramında müsahibədə minimum keçid balı 40-dır və müsahibə nəticələri əsas rol oynayır. IELTS 8 səviyyəsi dil tələbinə uyğundur, amma müsahibə və digər meyarlar da vacibdir. Mənbə: dp.edu.az/az/faq
  - judge: IN_DOCUMENTS is no, so the correct behavior would be to decline and say the programme documents do not provide this exact answer. Instead, the bot gives a specific explanation for the waitlist result, including stating that the interview score may have been below 40 and implying causes not established for this individual by the provided text. Although some cited facts about interview scoring exist in the documents, the reply still answers as if it knows the applicant's case, so it is unsupported.
  - pages read: dp-content-73, dp-faq, dp-content-66
- **run 2: wrong**
  - bot: Xeyr, 98 ortalama və 8 IELTS ilə waitlistə düşməyiniz mümkündür, çünki müsahibə balı da önəmlidir və müsahibədə ən az 40 bal toplamaq lazımdır. Təhsil sahəniz və müsahibə nəticələriniz də yer seçimində rol oynayır. Yəni, dil və qəbul balları kifayət qədər olsa da, müsahibə və digər meyarlar nəticəyə təsir edir. Mənbə: dp.edu.az/az/faq
  - judge: IN_DOCUMENTS is no, so the bot should have declined instead of answering. It gave a substantive explanation using programme facts such as the 40-point interview threshold and ranking by interview outcomes, which counts as answering when the documents are deemed not to contain the answer. Those facts may appear in the provided text, so this is not made up, but the response is still wrong because it did not refuse.
  - pages read: dp-faq, dp-content-66, dp-content-65

### q19: Koreyayadan qebulum var muraciet ede bilerem?

- in_documents: yes
- your answer: Ixtisaslar ve olkeler ucun listi  yoxlamaginiz xahis olununr
- **run 1: wrong**
  - bot: Bəli, Koreyada xarici ali təhsil müəssisəsinə qəbulunuz varsa, Dövlət Proqramına müraciət edə bilərsiniz. Proqrama qəbul olmadan müraciət etmək mümkün deyil. Mənbə: dp.edu.az/az/faq
  - judge: IN_DOCUMENTS is yes, and the key point in the reference is that the applicant should check the approved countries/specialties list. The bot instead gives a blanket 'yes' based only on having admission, which is misleading because admission alone does not establish eligibility for South Korea under the programme. It uses a supported fact about needing prior admission, but misses the essential restriction tied to the list.
  - pages read: dp-faq
- **run 2: wrong**
  - bot: Bəli, müraciət edə bilərsiniz. Koreya Respublikasının İNHA Universiteti ilə Bakı Mühəndislik Universitetinin mühəndislik ixtisasları üzrə bakalavriat səviyyəsində beynəlxalq ikili diplom proqramına sənəd qəbulu 5 iyun - 9 avqust 2023-cü tarixləri arasında olub. Yeni qəbul üçün məlumatları dp.edu.az saytından izləməyiniz məsləhətdir. Bu məlumat 15.09.2026 tarixinə olan vəziyyətdir. Mənbə: dp.edu.az...
  - judge: The documents do contain relevant information: South Korea appears only for the BMU–INHA dual degree programme, so the key response should direct the applicant to check the programme/country-specialty list rather than broadly say they can apply. The bot incorrectly says 'Bəli, müraciət edə bilərsiniz' and adds unsupported advice wording; it also treats a specific 2023 INHA/BMU announcement as a general yes to the user's question, which is misleading. The factual details about the INHA programme dates are supported, so this is not made up, but the main answer does not match the reference's key point.
  - pages read: dp-content-56, dp-content-53

### q20: Kecen il Queen Mary University of London siyahida var idi indi hani bes?

- in_documents: yes
- your answer: Ixtisas siyahisi her il yenilenir
- **run 1: correct**
  - bot: Queen Mary University of London-un 2026/2027 tədris ili üçün siyahıda olub-olmadığını PDF faylında yoxlamaq lazımdır. Siyahı dp.edu.az saytında dərc olunub, link: https://dp.edu.az/uploads/fileuploads/2026/04/7a8f23b3d5e94312af0b99da8ceadac8.pdf 2027/2028 tədris ili üçün siyahı hələ dərc olunmayıb. Bu məlumat 13.09.2026 tarixinə olan vəziyyətdir. Mənbə: dp.edu.az/uploads/fileuploads/2026/04/7a8f23...
  - judge: IN_DOCUMENTS is yes, and the key point in the reference is that the list is updated every year. The bot reply does not state that directly, but it does convey the same practical fact by saying the 2026/2027 list is published and 2027/2028 is not yet published, implying year-by-year renewal. It stays within the provided documents and does not invent unsupported programme facts.
  - pages read: dp-status-university-list, dp-content-67, pdf-secim-meyarlari-2026
- **run 2: partly**
  - bot: Bəli, Queen Mary University of London 2026/2027 tədris ili üzrə siyahıda var. Bu universitet Birləşmiş Krallıq ölkəsi altında qeyd olunub. Siyahını buradan yoxlaya bilərsiniz: https://dp.edu.az/uploads/fileuploads/2026/04/7a8f23b3d5e94312af0b99da8ceadac8.pdf Bu məlumat 13.09.2026 tarixinə olan vəziyyətdir. Mənbə: dp.edu.az/uploads/fileuploads/2026/04/7a8f23b3d5e94312af0b99da8ceadac8.pdf
  - judge: IN_DOCUMENTS is yes, and the key point in the reference answer is that the specialty/university list is updated every year. The bot instead answers a different question by claiming Queen Mary is on the 2026/2027 list and gives a link, but it does not convey the essential fact about annual renewal. That makes the key answer missing/misleading, though the specific claim appears supported by the provided text source.
  - pages read: dp-status-university-list, dp-content-57, pdf-secim-meyarlari-2026

### q24: Dovlet proqramini bitirenden sonra harda isleye bilerem?

- in_documents: no
- your answer: (unreleated)
- **run 1: wrong**
  - bot: Dövlət Proqramını bitirdikdən sonra siz ən azı 5 il müddətinə Azərbaycan Respublikasının ali təhsil müəssisəsində əsas iş yeri olmaqla əmək fəaliyyətinə cəlb olunmalısınız. Bu, proqramın şərtlərindən biridir və əmək müqaviləsi bağlamağa razılıq tələb olunur. Yəni, proqramı bitirəndən sonra Azərbaycanda ali təhsil müəssisəsində işləmək öhdəliyiniz var. Mənbə: dp.edu.az/az/content/78
  - judge: IN_DOCUMENTS is no, so the expected behavior is to refuse or say the documents do not provide this exact information. Instead, the bot gave a definite programme-specific answer about a 5-year work obligation at an Azerbaijani higher education institution. That is a substantive answer rather than a refusal, so it must be graded wrong under the rubric, even though the cited text may mention similar conditions.
  - pages read: dp-content-78, pdf-secim-meyarlari-2026, dp-content-70
- **run 2: wrong** (made up)
  - bot: Dövlət Proqramı xaricdə nüfuzlu ali təhsil müəssisələrində təhsil almaq üçün imkan yaradır. Proqramı bitirdikdən sonra, aldığınız bilik və bacarıqlara əsasən, Azərbaycan və ya xarici ölkələrdə müvafiq sahədə işləyə bilərsiniz. Proqramın məqsədi sizi əmək bazarının tələblərinə cavab verən rəqabətqabiliyyətli mütəxəssis kimi hazırlamaqdır. Mənbə: dp.edu.az/az/content/78
  - judge: IN_DOCUMENTS is no, so the bot should have declined and said the programme documents do not provide this information, ideally with the contact email. Instead, it gave a substantive answer about being able to work in Azerbaijan or abroad after finishing, which is not supported by the provided text. It also cited the programme purpose page as if it answered the employment-location question.
  - pages read: dp-faq, pdf-secim-meyarlari-2026, dp-content-78, dp-content-69

### q26: Hansi bank riskleri var?

- in_documents: no
- your answer: (unreleated)
- **run 1: wrong**
  - bot: Dövlət Proqramına görə, proqram iştirakçılarının bank və plastik kart xərcləri maliyyələşdirilir. Bu xərclərə illik xidmət haqqı və bank xidmətləri haqqı daxildir. Proqram çərçivəsində saxtakarlıq və qanunsuz sənəd istifadəsi aşkar edilərsə, ciddi cəzalar tətbiq olunur. Mənbə: dp.edu.az/az/content/75
  - judge: IN_DOCUMENTS is no, so the bot should have declined or said the documents do not answer the question. Instead, it answered with programme facts about bank/plastic card expenses and penalties, which does not address the unclear question about "bank risks" as a refusal. The cited facts are supported by the text, so there is no fabrication, but giving a substantive answer here is still the wrong behavior.
  - pages read: dp-content-75, dp-content-74, dp-content-70
- **run 2: wrong**
  - bot: Dövlət Proqramına görə, proqram iştirakçılarının bank və plastik kart xərcləri maliyyələşdirilir. Bu xərclərə illik xidmət haqqı və bank xidmətləri haqqı daxildir. Proqram çərçivəsində saxtakarlıq və qanunsuz sənəd istifadəsi aşkar edilərsə, ciddi cəzalar tətbiq olunur. Mənbə: dp.edu.az/az/content/75
  - judge: The question asks about 'bank risks', but the provided documents only mention bank and plastic card expenses being covered, plus reimbursement mechanics and fraud penalties. The bot did not refuse; instead it answered with related facts that do not address the asked question. Its statements are supported by the text, so this is not made up, but it is still the wrong behavior when IN_DOCUMENTS is no.
  - pages read: dp-content-75, dp-content-74, dp-content-70

### q29: Can I work part-time while studying abroad?

- in_documents: no
- your answer: Refusal with dp22-28@edu.gov.az
- **run 1: correct**
  - bot: Təəssüf ki, bu barədə rəsmi sənədlərdə məlumat tapa bilmədim. Dəqiq cavab üçün Dövlət Proqramı İdarəetmə Qrupuna yazmağınızı tövsiyə edirəm: dp22-28@edu.gov.az
  - judge: IN_DOCUMENTS is no, so the expected behavior is to refuse rather than answer the policy question. The bot clearly says it could not find information in the official documents and directs the user to the official contact email. It does not add unsupported programme facts.
  - pages read: pdf-secim-meyarlari-2026, dp-content-65, dp-content-66
- **run 2: partly** (made up)
  - bot: Xaricdə təhsil zamanı yarı-zamanlı işləmək barədə Dövlət Proqramında xüsusi məlumat yoxdur. Bu məsələ təhsil aldığınız ölkənin qanunları və universitetin qaydalarından asılıdır. Əlavə məlumat üçün təhsil alacağınız ölkənin müvafiq qaydalarını yoxlamağınız məsləhətdir. Mənbə: dp.edu.az/uploads/fileuploads/2026/05/4ec0f92d30d04271886e0bc82fcae744.pdf
  - judge: IN_DOCUMENTS is no, so the expected behavior is to refuse and direct the user to the official contact. The bot does say the programme has no specific information, which is a refusal, but it also adds unsupported statements about the matter depending on the host country's laws/university rules and gives advice to check them instead of providing the required contact email. That makes it only partly correct, and those extra statements count as made up relative to the programme text.
  - pages read: pdf-secim-meyarlari-2026, dp-content-65

### q32: Сколько мест выделено на докторантуру?

- in_documents: no
- your answer: Refusal with dp22-28@edu.gov.az
- **run 1: correct**
  - bot: Mətndə doktorantura səviyyəsi üzrə ayrılmış yerlərin sayı göstərilməyib. Yalnız ümumi olaraq hər il 500 nəfərdən çox olmamaqla, 2022-2028-ci illər ərzində 2000 nəfərə qədər tələbənin xaricdə təhsil alacağı qeyd olunub. Bu məlumat 15.09.2026 tarixinə olan vəziyyətdir. Mənbə: dp.edu.az/az/content/78
  - judge: IN_DOCUMENTS is no, so the expected behavior is to refuse and point out that the programme documents do not provide the exact answer. The bot clearly says the number of places for doctoral level is not specified, which is a valid refusal. It also mentions a related supported fact from the text about the overall annual and total participant caps, and does not invent a doctorate-specific quota.
  - pages read: dp-content-78, pdf-secim-meyarlari-2026, pdf-doktorantura, dp-content-5, dp-content-81
- **run 2: partly**
  - bot: Dövlət Proqramı üzrə hər il ümumilikdə 500 nəfərdən çox olmamaqla, 2022-2028-ci illərdə 2000 nəfərədək tələbə xaricdə təhsil alacaq. Bu yerlər bakalavriat, magistratura və doktorantura səviyyələrini əhatə edir, amma doktorantura üçün ayrıca ayrılmış yer sayı mətndə göstərilməyib. Bu məlumat 15.09.2026 tarixinə olan vəziyyətdir. Mənbə: dp.edu.az/az/content/78
  - judge: IN_DOCUMENTS is no, so the expected behavior is a refusal or clear statement that the documents do not provide the exact answer. The bot does say that a separate number for doctoral places is not stated, but it also gives programme facts about total annual and overall places instead of refusing and does not provide the contact email. Those extra facts are supported by the text, so they are not made up.
  - pages read: dp-content-78, dp-content-5, pdf-doktorantura, pdf-secim-meyarlari-2026
