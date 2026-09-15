# Eval report: 2026-09-15_145820

Bot: answer model `gpt-4.1-mini`, search model `gpt-4o-mini`, check model `gpt-4.1-mini`, read big = True. Judge: `gpt-5.4 / prompt f0fa4f`.  
34 questions x 2 runs = 68 answers.

## Scores (judge)

| | correct | partly | wrong |
|---|---|---|---|
| should answer (in_documents = yes) | 19 (50%) | 6 (16%) | 13 (34%) |
| should refuse (in_documents = no) | 20 (67%) | 1 (3%) | 9 (30%) |
| all | 39 (57%) | 7 (10%) | 22 (32%) |

## Simple checks

- answers that answered or declined as expected (no LLM): 48/68
- questions answered in another language (no LLM): 9  q21 (en -> az), q22 (en -> az), q23 (en -> az), q29 (en -> az), q30 (ru -> az), q31 (ru -> az), q32 (ru -> az), q33 (ru -> az), q34 (ru -> az)
- questions with a made-up programme fact (judge): 5  q06, q07, q22, q24, q31
- questions graded differently in different runs: 10  q01, q02, q09, q11, q12, q15, q18, q26, q31, q33
- bot errors: 0
- bot cost: $0.216, 4.6 s per answer
- judge cost: $0.574

## Check the label

in_documents = no, but the bot answered and the judge found every fact in the text it read. Maybe a page does answer these: q04, q06, q15, q26

## Failures

Every question with at least one answer that is not correct. All runs are shown, so you can see when a question flips.

### q01: neleri qarsilayir?

- in_documents: yes
- your answer: təhsil xərcləri, viza və təhsil aldığı ölkədə qeydiyyat xərcləri, aylıq yaşayış xərcləri; tibbi sığorta xərcləri; beynəlxalq nəqliyyat xərcləri; bank və plastik kart xərcləri
- **run 1: partly**
  - bot: Dövlət Proqramı xarici ölkələrin nüfuzlu ali təhsil müəssisələrində bakalavriat, magistratura və doktorantura səviyyələrində təhsil almaq üçün imkan yaradır. Proqram çərçivəsində təhsil xərcləri Dövlət Neft Fondunun vəsaiti ilə maliyyələşdirilir. Hər il 500 nəfərədək, ümumilikdə isə 2000 nəfərədək tələbənin təhsili təmin olunur. Təhsil alanlarla 3 tərəfli müqavilə imzalanır və maliyyə öhdəliyi bu ...
  - judge: IN_DOCUMENTS is yes, so the bot should answer what expenses the programme covers. The reference answer lists several covered cost categories, but the bot only mentions that education costs are financed and adds unrelated facts about programme scope, quotas, and the tripartite contract. It misses most key covered items, so the answer is incomplete in an important way, but it does not clearly invent unsupported coverage details.
  - pages read: dp-content-78, pdf-secim-meyarlari-2026
- **run 2: correct**
  - bot: Dövlət Proqramı aşağıdakı xərcləri qarşılayır: təhsil haqqı, viza və qeydiyyat xərcləri, aylıq yaşayış xərcləri, tibbi sığorta, beynəlxalq nəqliyyat və bank/plastik kart xərcləri. Ailə üzvlərinin xərcləri isə maliyyələşdirilmir. Mənbə: dp.edu.az/az/content/68
  - judge: IN_DOCUMENTS is yes, and the bot's reply matches the listed covered expenses in the source: tuition/education, visa and registration, monthly living, medical insurance, international transport, and bank/card costs. It also adds that family members' expenses are not financed, which is supported by the FAQ text and is not misleading in this context.
  - pages read: dp-faq, dp-content-78, pdf-secim-meyarlari-2026, dp-content-68

### q02: qayitmasaq nolar?

- in_documents: no
- your answer: tədris müddəti bitdikdən sonra ən geci 2 (iki) ay ərzində Azərbaycan Respublikasına qayıtmaq, qayıtdıqdan sonra 10 (on) təqvim günü müddətində Nazirliyə bu barədə məlumat vermək və Azərbaycan Respublikasında 5 (beş) il (öhdəlik müddəti) əmək fəaliyyəti göstərmək
- **run 1: partly**
  - bot: Salam! Sualınız varsa, Dövlət Proqramı ilə bağlı kömək etməyə hazıram.
  - judge: IN_DOCUMENTS is no, so the expected behavior is to decline or say the information is not available. The bot did not answer the question and instead gave a generic greeting, which is not a proper refusal but also does not invent any programme facts. Since it neither answers nor clearly declines, this is only partially acceptable.
  - pages read: none
- **run 2: wrong**
  - bot: Salam! Mən Xaricdə təhsil üzrə Dövlət Proqramı haqqında məlumat vermək üçün buradayam. Proqramla bağlı sualınız varsa, məmnuniyyətlə kömək edərəm!
  - judge: IN_DOCUMENTS is no, so the correct behavior is to decline or say the information is not available from the programme materials. The bot did not answer the question, but it also did not clearly refuse or direct the user to the official contact; it only gave a generic greeting. It did not invent any programme facts.
  - pages read: none

### q03: kesilsek ne olur?

- in_documents: yes
- your answer: Kesrinizi duzeldene qeder teqaud almirsiniz ve teqaudunuz bloklanir. Duzeltdikden sonra ise teqaudunuz blok hesabdan cixir
- **run 1: wrong**
  - bot: Salam! Sualınız varsa, Dövlət Proqramı ilə bağlı kömək etməyə hazıram.
  - judge: IN_DOCUMENTS is yes, so the documents do contain an answer and a refusal or non-answer is automatically wrong. The bot did not answer the question at all; it only gave a generic greeting and offer to help, missing the key fact about the stipend being blocked until the academic issue is fixed. It also did not make up any programme fact.
  - pages read: none
- **run 2: wrong**
  - bot: Salam! Sualınız varsa, Dövlət Proqramı ilə bağlı kömək etməyə hazıram.
  - judge: IN_DOCUMENTS is yes, so the programme documents do contain the answer and a refusal or non-answer is not acceptable. The bot did not answer the question at all; it only gave a generic greeting and offer to help, missing the key fact about the scholarship being blocked until the academic failure is corrected. It also did not invent any unsupported programme fact.
  - pages read: none

### q04: is verirler sonra?

- in_documents: no
- your answer: Dövlət Proqramı çərçivəsində nüfuzlu xarici ali təhsil müəssisələrində təhsilini uğurla bitirmiş gənclərin Azərbaycan Respublikasının dayanıqlı inkişafını təmin edəcək prioritet sahələrdə məşğulluğunun təmin edilməsi xüsusi əhəmiyyət kəsb edir. Bu prioritet istiqamətin reallaşdırılması üçün ehtiyac duyulan sahələr üzrə iş təkliflərinin verilməsi və karyerada yüksəliş mexanizmi hazırlanacaqdır. Dövlət orqanlarında bu Dövlət Proqramı çərçivəsində məzun olmuş şəxslərin işlə təminatına üstünlük veriləcəkdir.
- **run 1: wrong**
  - bot: Bəli, Dövlət Proqramı çərçivəsində xaricdə təhsilini başa vurduqdan sonra Azərbaycan Respublikasının ali təhsil müəssisəsində əsas iş yeri olmaqla ən azı 5 il müddətinə əmək fəaliyyətinə cəlb edilmək üçün əmək müqaviləsi bağlanmalıdır. Bu, proqramın əsas şərtlərindən biridir. Mənbə: dp.edu.az/uploads/fileuploads/2026/05/4ec0f92d30d04271886e0bc82fcae744.pdf
  - judge: IN_DOCUMENTS is no, so the expected behavior was to decline and say the programme texts do not provide the answer. Instead, the bot gave a definite programme-specific answer about a 5-year employment contract after graduation. That is a substantive answer rather than a refusal, so it is wrong under the rubric; the cited fact appears in the text, so it is not made up.
  - pages read: pdf-secim-meyarlari-2026, dp-content-66, dp-faq
- **run 2: wrong**
  - bot: Bəli, Dövlət Proqramı çərçivəsində xaricdə təhsilini başa vurduqdan sonra Azərbaycan Respublikasının ali təhsil müəssisəsində əsas iş yeri olmaqla ən azı 5 il müddətinə əmək fəaliyyətinə cəlb edilmək tələb olunur. Bu, proqramın əsas öhdəliklərindən biridir. Mənbə: dp.edu.az/uploads/fileuploads/2026/05/4ec0f92d30d04271886e0bc82fcae744.pdf
  - judge: IN_DOCUMENTS is no, so the bot should have declined instead of answering. It gave a specific programme rule about a 5-year work obligation after graduation; while that rule appears in the provided text, the grading instruction says any substantive answer is wrong when the documents do not answer this question. The reply is not made up, but it fails because it did not refuse.
  - pages read: pdf-secim-meyarlari-2026, dp-content-69

### q06: ne elesem qebul sansim artar?

- in_documents: no
- your answer: Qəbul aldığınız və müraciət etdiyiniz universitetin DP-in universitetlər və ixtisaslar siyahısında olduğundan əmin olun. Müsahibəyə erkəndən hazırlaşmağa başlayın. İxtisas mövzularını yaxşı təkrar edin və ümumi dünyagörüşü suallarına hazırlıqlı olun. Müsahibə zamanı özünüzü ağıllı göstərmək üçün mövzunu bilmədiyiniz yerlərə çəkməyin. Həyəcanlanmayın
- **run 1: wrong**
  - bot: Qəbul şansınızı artırmaq üçün: - Təhsil almaq istədiyiniz ixtisasın prioritet sahələrdən olmasına diqqət edin. - Xarici universitetdən rəsmi qəbul sənədi alın. - Tədris dilini ən azı C1 səviyyəsində beynəlxalq sertifikatla təsdiqləyin (məsələn, IELTS, TOEFL). - Qəbul imtahanında tələb olunan balı toplayın (texniki sahələrdə ən azı 400, digər sahələrdə 550 bal). - Məntiqi mühakimə, kommunikasiya və...
  - judge: IN_DOCUMENTS is no, so the bot should have declined and said the documents do not provide an answer, ideally giving the contact email. Instead, it answered with concrete programme-based tips and framed them as ways to increase acceptance chances. Those facts may come from the text, but answering instead of refusing is still wrong when the documents do not answer this question directly.
  - pages read: pdf-secim-meyarlari-2026, dp-faq, dp-content-65
- **run 2: wrong** (made up)
  - bot: Qəbul şansınızı artırmaq üçün: 1. Sənədlərinizi tam və düzgün təqdim edin, uyğunsuzluq olmasın. 2. Beynəlxalq səviyyəli dil sertifikatınızı (ən az C1 səviyyəsində) hazırlayın. 3. Müsahibəyə ciddi hazırlaşın, elmi tədqiqat, məntiqi mühakimə və kommunikasiya bacarıqlarınızı inkişaf etdirin. 4. “Yüksəliş” müsabiqəsinin qalibi olsanız, müsahibədən azad ola bilərsiniz, bu üstünlükdür. Unutmayın, müsahi...
  - judge: IN_DOCUMENTS is no, so the bot should decline and say the programme documents do not provide this kind of answer. Instead, it gives actionable tips as if they were official guidance, including claims about increasing chances and presenting them as sourced from the FAQ. Several of these are unsupported as general advice in the provided text, even if some related facts exist separately.
  - pages read: dp-faq, pdf-doktorantura, pdf-secim-meyarlari-2026

### q07: hansi senedler lazimdi? bakalavr ucun

- in_documents: yes
- your answer: Ümumi təhsil müəssisələrinin buraxılış sinfində təhsil aldığına dair arayış və ya tam orta təhsil haqqında attestatın surəti; qəbul sənədi (bakalavriat səviyyəsi üzrə); beynəlxalq səviyyəli dil sertifikatının surəti; hərbi bilet və ya ASAN xidmətdən əldə olunan hərbi xidmətdən möhlət hüququ haqqında arayış; DİM qəbul imtahanının nəticəsi; sağlamlıq haqqında arayış (AZS-086/1); olduğu təqdirdə beynəlxalq təhsil proqramının (IB, Alevel, AP) göstəricisini təsdiq edən arayışın surəti; olduğu təqdirdə beynəlxalq olimpiada qalibi olduğunu təsdiq edən sənədin surəti; SAT və ya ACT nəticəsini təsdiq edən arayışın surəti.
- **run 1: partly**
  - bot: Bakalavr üçün lazım olan sənədlər: 1. Ümumitəhsil müəssisələrinin buraxılış sinfində təhsil aldığını təsdiq edən arayış və ya tam orta təhsilə dair attestatın surəti (orta ixtisas təhsili varsa, diplom və ya arayış). 2. Xarici universitetdən qəbul sənədi (təhsil aldığını təsdiq edən arayış da ola bilər). 3. Təhsil dilini C1 səviyyəsində bildiyini göstərən beynəlxalq dil sertifikatı. 4. Hərbi bilet...
  - judge: IN_DOCUMENTS is yes, so the bot should provide the documented list. The reply matches several key items from the documents and reference answer: school certificate/attestat, admission document, language certificate, military document, and DİM result, plus the translation note. However, it omits important listed documents such as the health certificate, optional IB/A-level/AP proof, olympiad proof, and SAT/ACT proof, and it adds wording like 'xarici universitetdən' and 'təhsil aldığını təsdiq edən arayış da ola bilər' without clearly limiting that note as in the source.
  - pages read: pdf-secim-meyarlari-2026, dp-content-65
- **run 2: partly** (made up)
  - bot: Bakalavr səviyyəsi üçün tələb olunan sənədlər: 1. Ümumitəhsil müəssisələrinin buraxılış sinfində təhsil aldığına dair arayış və ya tam orta təhsil haqqında attestatın surəti (orta ixtisas təhsili varsa, diplom və ya arayış). 2. Xarici universitetdən qəbul sənədi (hazırda təhsil alırsınızsa, arayış). 3. C1 səviyyəsində beynəlxalq dil sertifikatının surəti. 4. Hərbi bilet və ya ASAN xidmətdən möhlət...
  - judge: IN_DOCUMENTS is yes, and the bot reply matches the listed bachelor documents that appear in the provided text: school certificate/attestat, admission document, language certificate at C1, military document, and DİM result, plus the note about translation requirements. However, it adds 'bəzən azadlıq şərtləri ola bilər' about exemption from the DİM requirement, which is not supported by the specific text the bot read for this answer. It also omits several optional documents present in the reference answer, so the answer is incomplete.
  - pages read: pdf-secim-meyarlari-2026, dp-faq

### q08: sonra master/phd oxuya bilerem?

- in_documents: yes
- your answer: Beli
- **run 1: wrong**
  - bot: Təəssüf ki, bu barədə rəsmi sənədlərdə məlumat tapa bilmədim. Dəqiq cavab üçün Dövlət Proqramı İdarəetmə Qrupuna yazmağınızı tövsiyə edirəm: dp22-28@edu.gov.az
  - judge: IN_DOCUMENTS is yes, and the documents do contain the key fact relevant to this short question: a candidate can proceed to a later level, e.g. apply for PhD while still in the final year of master's, which supports the reference answer 'Bəli.' The bot instead refused and said no information was available. A refusal is always wrong when the answer exists in the documents, and there is no made-up programme fact here.
  - pages read: pdf-doktorantura
- **run 2: wrong**
  - bot: Təəssüf ki, bu barədə rəsmi sənədlərdə məlumat tapa bilmədim. Dəqiq cavab üçün Dövlət Proqramı İdarəetmə Qrupuna yazmağınızı tövsiyə edirəm: dp22-28@edu.gov.az
  - judge: IN_DOCUMENTS is yes, so the bot should answer from the documents rather than refuse. The reference answer says the correct answer is simply yes, and the documents discuss progression to doctoral study after/while finishing master's, so a refusal is not acceptable here. The bot did not invent any programme fact; it only said it could not find the information and gave the contact email.
  - pages read: pdf-doktorantura

### q09: bakalavr dp ile oxudumsa master dp ile oxuya bilerem yene?

- in_documents: yes
- your answer: Beli, her tehsil pillesi uzre 1 defe DP iistifade ede bilersiniz
- **run 1: wrong**
  - bot: Təəssüf ki, bu barədə rəsmi sənədlərdə məlumat tapa bilmədim. Dəqiq cavab üçün Dövlət Proqramı İdarəetmə Qrupuna yazmağınızı tövsiyə edirəm: dp22-28@edu.gov.az
  - judge: IN_DOCUMENTS is yes, so a refusal is automatically wrong. The reference answer says a person may use the State Programme once at each education level, and the bot failed to provide that key fact despite the documents containing the answer according to the human setting. The reply does not invent unsupported programme facts; it only declines and gives the contact email.
  - pages read: dp-faq, pdf-doktorantura, dp-content-81
- **run 2: correct**
  - bot: Xeyr, əgər bakalavr səviyyəsində Dövlət Proqramı ilə təhsil almısınızsa, eyni təhsil səviyyəsi üzrə yenidən müraciət edə bilməzsiniz. Amma magistratura səviyyəsi üçün müraciət etmək mümkündür. Mənbə: dp.edu.az/az/faq
  - judge: IN_DOCUMENTS is yes, and the key fact in the reference answer is that DP can be used once per education level, so someone who used it for bachelor may still use it for master's. The bot reply matches that substance: it says not again at the same level, but master's is possible. It is slightly worded as 'Xeyr' at the start, but overall the final meaning is correct and not misleading here.
  - pages read: dp-faq, pdf-doktorantura, pdf-secim-meyarlari-2026

### q11: viza xərcini qarşılayır?

- in_documents: yes
- your answer: Beli, ilk once odenisi ozunuz edirsiniz daha sonra lazimi senedler istenilerek sizin bank hesabiniza geri odeme edilir
- **run 1: partly**
  - bot: Xeyr, viza xərcləri proqram iştirakçıları tərəfindən ödənilir. Dövlət Proqramı isə bu xərclərin təsdiqedici sənədlər əsasında geri ödənməsini təmin edir. Bu məlumat 15.09.2026 tarixinə olan vəziyyətdir. Mənbə: dp.edu.az/az/content/70
  - judge: IN_DOCUMENTS is yes, so the bot should answer from the documents. The key fact is that visa costs are covered by the programme, but the participant first pays them and then is reimbursed upon submitting supporting documents. The bot reply starts with "No," which is misleading and contradicts the core answer, even though the rest correctly explains reimbursement; therefore the key facts are not stated correctly overall.
  - pages read: dp-content-70, dp-content-68
- **run 2: correct**
  - bot: Bəli, Dövlət Proqramı viza xərclərini qarşılayır. Bu xərclərə vizanın rəsmiləşdirilməsi üçün tutulan rüsum, tibbi müayinə və təhsil ölkəsində qeydiyyat xərcləri daxildir. Lakin viza xərcləri əvvəlcə siz tərəfindən ödənilir, sonra təsdiqedici sənədlərlə geri qaytarılır. Mənbə: dp.edu.az/az/content/70
  - judge: The documents clearly support that visa-related costs are covered, but first paid by the participant and then reimbursed upon submission of supporting documents. The bot reply matches these key facts and correctly includes the covered sub-items from the cited rule, including visa fee, medical examination related to visa processing, and registration in the study country. Nothing important is wrong or misleading.
  - pages read: dp-faq, dp-content-70, dp-content-68

### q12: bəs nə vaxt qaytarırlar?

- in_documents: yes
- your answer: kruatorunuz size bununla bagli melumat verir ve siz lazimi subutlari (invoice, ticket price, bank statement ve s ola biler), bank rekvizitleriniz ile birlikde ona gonderirsiniz
- **run 1: correct**
  - bot: Viza xərcləri ödənildikdən sonra təsdiqedici sənədlərlə birlikdə müvafiq ərizə Dövlət Proqramı İdarəetmə Qrupuna təqdim olunmalıdır. Ödəniş həmin sənədlərin təqdim olunduğu tarixə qüvvədə olan rəsmi məzənnə ilə proqram iştirakçısının bank hesabına qaytarılır. Bu məlumat 15.09.2026 tarixinə olan vəziyyətdir. Mənbə: dp.edu.az/az/content/74
  - judge: IN_DOCUMENTS is yes, so the bot should answer from the documents. The reply correctly says reimbursement happens after the participant submits the application and supporting documents, and that payment is made to the bank account at the official exchange rate effective on the processing/formalization date. It does not mention the curator detail from the reference, but that is not necessary for the key fact asked ('when do they return it?'), and it does not add unsupported facts.
  - pages read: dp-content-74, pdf-doktorantura, dp-faq, dp-content-68
- **run 2: wrong**
  - bot: Təəssüf ki, bu barədə rəsmi sənədlərdə məlumat tapa bilmədim. Dəqiq cavab üçün Dövlət Proqramı İdarəetmə Qrupuna yazmağınızı tövsiyə edirəm: dp22-28@edu.gov.az
  - judge: IN_DOCUMENTS is yes, and the documents do answer the question: reimbursement is paid to the participant's bank account based on submitted supporting documents, at the time the Ministry's payment order is formalized. The bot incorrectly refused and said it could not find information, which is always wrong when the answer exists in the documents. It did not add unsupported facts, only a refusal and contact email.
  - pages read: pdf-doktorantura, dp-content-74, dp-content-70, dp-content-68

### q14: 2026-da neçə nəfər qəbul olunacaq?

- in_documents: yes
- your answer: Dövlət Proqramı üzrə illik kvota 500 nəfər təşkil edir. Bu kvota çərçivəsində rəqabət mühitinin tənzimlənməsi məqsədilə müraciət sayından asılı olaraq prioritet ixtisas istiqamətləri üzrə keçid balları tətbiq edilə bilər
- **run 1: wrong**
  - bot: Təəssüf ki, bu barədə rəsmi sənədlərdə məlumat tapa bilmədim. Dəqiq cavab üçün Dövlət Proqramı İdarəetmə Qrupuna yazmağınızı tövsiyə edirəm: dp22-28@edu.gov.az
  - judge: IN_DOCUMENTS is yes, so a refusal is automatically wrong. The reference answer says the annual quota is 500 people, but the bot said it could not find official information and redirected the user instead, missing the key fact entirely. The reply does not invent unsupported programme facts, aside from giving advice/contact, so made_up is false.
  - pages read: pdf-secim-meyarlari-2026, dp-status-university-list
- **run 2: wrong**
  - bot: Təəssüf ki, bu barədə rəsmi sənədlərdə məlumat tapa bilmədim. Dəqiq cavab üçün Dövlət Proqramı İdarəetmə Qrupuna yazmağınızı tövsiyə edirəm: dp22-28@edu.gov.az
  - judge: IN_DOCUMENTS is yes, so a refusal is automatically wrong. The reference answer says the annual quota is 500 people, while the bot says it could not find information and redirects by email instead of answering. The reply does not invent programme facts, so it is not made up.
  - pages read: pdf-secim-meyarlari-2026, dp-status-university-list

### q15: Nece nefer phd olacaq?

- in_documents: no
- your answer: 2026 ucun  Dövlət Proqramına aid 500 nəfərlik kvotanın 20 faizindən çox olmayan hissəsi doktorantura səviyyəsini əhatə edir.
- **run 1: correct**
  - bot: Təəssüf ki, bu barədə rəsmi sənədlərdə məlumat tapa bilmədim. Dəqiq cavab üçün Dövlət Proqramı İdarəetmə Qrupuna yazmağınızı tövsiyə edirəm: dp22-28@edu.gov.az
  - judge: IN_DOCUMENTS is no, so the bot should decline rather than answer from the programme documents. The reply clearly says it could not find official information and directs the user to the official contact email, which matches the expected behavior. It does not assert unsupported programme facts.
  - pages read: dp-content-78, pdf-secim-meyarlari-2026, pdf-doktorantura
- **run 2: wrong**
  - bot: PhD (doktorantura) səviyyəsi üzrə müraciət üçün xarici ali təhsil müəssisəsinə şərtsiz qəbul sənədiniz olmalıdır. Təhsil haqqı depoziti və əvvəlki diplom və ya transkript təqdim edilməlidir. Müraciət yalnız elektron sistem (portal.edu.az) üzərindən qəbul olunur və sənədlər tam olmalıdır, yoxsa müsahibəyə buraxılmırsınız. Son müraciət tarixi 05.06.2026 saat 18:00-dır. Mənbə: dp.edu.az/uploads/fileu...
  - judge: IN_DOCUMENTS is no, so the bot should have declined and said the documents do not provide this information. Instead, it answered with unrelated programme details about PhD application requirements and deadlines as if responding to the question. Those facts may exist in the text, but they do not answer 'How many PhD spots will there be?', so the reply is still wrong rather than a refusal.
  - pages read: pdf-doktorantura, pdf-secim-meyarlari-2026

### q18: Musahibe nece qiymetledirilir?

- in_documents: yes
- your answer: Gənclərin xarici ölkələrin nüfuzlu universitetlərində təhsil alması üçün 2022–2028-ci illər Dövlət Proqramı (DP) çərçivəsində müsahibə mərhələsi 50 ballıq sistemlə qiymətləndirilir və minimum 40 bal keçid balı müəyyən edilib. İxtisas və Sahə Üzrə Biliklər, məntiqi Mühakimə və Düşüncə: Kommunikasiya və Özünəinam, Dil Bilikləri yoxlanilir
- **run 1: correct**
  - bot: Müsahibə 50 bal üzərindən qiymətləndirilir. Minimum 40 bal toplayan namizədlər müsabiqədə iştirak hüququ qazanır. Qiymətləndirmədə namizədin ixtisas bilikləri, məntiqi mühakimə, kommunikasiya və özünəinamı nəzərə alınır. Mənbə: dp.edu.az/az/faq
  - judge: IN_DOCUMENTS is yes, so the reply should match the documented facts. The bot correctly states the 50-point scale, the 40-point minimum, and the interview criteria such as subject knowledge, logical reasoning, communication, and self-confidence. It omits 'language skills' from the reference answer, but the provided text the bot read does not support that item, so the reply stays within the documents and is not misleading.
  - pages read: dp-faq, pdf-secim-meyarlari-2026
- **run 2: partly**
  - bot: Müsahibədə maksimum 50 bal verilir. Minimum 40 bal toplayan namizədlər müsabiqədə iştirak hüququ qazanır. Qiymətləndirmədə ixtisas bilikləri, məntiqi mühakimə, kommunikasiya və özünəinam kimi bacarıqlar nəzərə alınır. Mənbə: dp.edu.az/az/faq
  - judge: IN_DOCUMENTS is yes, and the bot reply matches the documented facts that the interview is scored out of 50 and requires at least 40 points. It also correctly summarizes the assessed areas as subject knowledge, logical reasoning, communication, and self-confidence. However, it omits the reference answer's mention of language skills, which makes it slightly incomplete rather than wrong.
  - pages read: dp-faq, pdf-doktorantura

### q19: Koreyayadan qebulum var muraciet ede bilerem?

- in_documents: yes
- your answer: Ixtisaslar ve olkeler ucun listi  yoxlamaginiz xahis olununr
- **run 1: wrong**
  - bot: Təəssüf ki, bu barədə rəsmi sənədlərdə məlumat tapa bilmədim. Dəqiq cavab üçün Dövlət Proqramı İdarəetmə Qrupuna yazmağınızı tövsiyə edirəm: dp22-28@edu.gov.az
  - judge: IN_DOCUMENTS is yes, and the documents do contain relevant information about a Korea-related programme: the INHA University–BMU dual degree and the list of eligible specialities. The user asks if they can apply with an admission from Korea, and the reference answer says they should check the list of specialities/countries; instead, the bot wrongly refuses and says no information was found. A refusal is always wrong when the answer exists in the documents.
  - pages read: dp-content-56, dp-content-53
- **run 2: wrong**
  - bot: Təəssüf ki, bu barədə rəsmi sənədlərdə məlumat tapa bilmədim. Dəqiq cavab üçün Dövlət Proqramı İdarəetmə Qrupuna yazmağınızı tövsiyə edirəm: dp22-28@edu.gov.az
  - judge: IN_DOCUMENTS is yes, so the bot should answer from the documents rather than refuse. The reference answer’s key point is to check the list of countries/specialties, and the documents do contain a Korea-related programme (INHA-BMU) under specific fields. The bot instead says no information was found and refers away, which is a refusal and therefore wrong here; it does not invent facts.
  - pages read: dp-content-56, dp-content-53, dp-content-73

### q20: Kecen il Queen Mary University of London siyahida var idi indi hani bes?

- in_documents: yes
- your answer: Ixtisas siyahisi her il yenilenir
- **run 1: wrong**
  - bot: Təəssüf ki, bu barədə rəsmi sənədlərdə məlumat tapa bilmədim. Dəqiq cavab üçün Dövlət Proqramı İdarəetmə Qrupuna yazmağınızı tövsiyə edirəm: dp22-28@edu.gov.az
  - judge: IN_DOCUMENTS is yes, and the documents do contain the needed idea: the university/programme list is published for 2026/2027, 2027/2028 is not yet published, and the list is updated by year, so a university that was on last year's list may differ now. The bot wrongly refused instead of giving that key fact, which is always wrong when the answer exists in the documents. It did not add unsupported programme facts, so there is no fabrication.
  - pages read: dp-status-university-list, pdf-secim-meyarlari-2026
- **run 2: wrong**
  - bot: Təəssüf ki, bu barədə rəsmi sənədlərdə məlumat tapa bilmədim. Dəqiq cavab üçün Dövlət Proqramı İdarəetmə Qrupuna yazmağınızı tövsiyə edirəm: dp22-28@edu.gov.az
  - judge: IN_DOCUMENTS is yes, and the documents do contain the key point that the university/program list is published for each academic year and that 2027/2028 has not yet been published. The reference answer's key fact is that the list is updated every year. The bot wrongly refused instead of giving that answer, so this is wrong. It did not add unsupported programme facts, only a refusal and contact email.
  - pages read: dp-status-university-list, pdf-secim-meyarlari-2026

### q24: Dovlet proqramini bitirenden sonra harda isleye bilerem?

- in_documents: no
- your answer: (unreleated)
- **run 1: wrong** (made up)
  - bot: Dövlət Proqramı bitirəndən sonra iş yeri ilə bağlı konkret məhdudiyyət yoxdur. Siz xaricdə aldığınız təhsilin sahəsinə və ixtisasınıza uyğun olaraq Azərbaycanda və ya xaricdə işləyə bilərsiniz. Proqramın məqsədi sizi rəqabətqabiliyyətli və yüksəkixtisaslı kadr kimi hazırlamaqdır. Mənbə: dp.edu.az/az/faq
  - judge: IN_DOCUMENTS is no, so the bot should have declined and said the programme documents do not provide this information. Instead, it gave a concrete answer about where the applicant may work after finishing the programme, presenting it as if supported by the source. The cited text only states the programme's general goal of preparing competitive specialists, not that there are no work-location restrictions or that graduates may work in Azerbaijan or abroad.
  - pages read: dp-faq, dp-content-70, dp-content-78, pdf-secim-meyarlari-2026
- **run 2: wrong** (made up)
  - bot: Dövlət Proqramı bitirəndən sonra işləmək üçün konkret yer proqramda göstərilməyib. Amma məqsədiniz Azərbaycan Respublikasının gələcək inkişafını təmin edən, müasir texnologiyaları mənimsəyən və rəqabətqabiliyyətli peşəkar olmaqdır. Yəni, proqram sizi ölkədə və ya beynəlxalq səviyyədə ixtisasınıza uyğun sahələrdə işləməyə hazırlayır. Mənbə: dp.edu.az/az/content/78
  - judge: IN_DOCUMENTS is no, so the bot should decline and say the programme documents do not provide this information. Instead, it gave a substantive answer about where the applicant may work after finishing, using general purpose language from the programme aim and adding an unsupported interpretation about working in-country or internationally. That is an answer-as-if-known, not a refusal, and it includes made-up programme facts.
  - pages read: dp-faq, dp-content-78, dp-content-70, dp-content-74

### q26: Hansi bank riskleri var?

- in_documents: no
- your answer: (unreleated)
- **run 1: wrong**
  - bot: Dövlət Proqramına görə, bank riskləri proqram iştirakçılarının təqaüd kartlarına görə tələb olunan illik xidmət haqqı və bank xidmətləri haqqının ödənilməsi ilə bağlıdır. Bu xərclər proqram çərçivəsində maliyyələşdirilir və proqram iştirakçısının bank və plastik kart xərclərini əhatə edir. Digər risklər və ya bank problemləri barədə məlumat mətndə yoxdur. Mənbə: dp.edu.az/az/content/75
  - judge: IN_DOCUMENTS is no, so the bot should have declined and said the programme documents do not answer this question. Instead, it answered as if 'bank risks' meant bank/card costs, which is not the same as the user's question, and presented programme facts rather than refusing. Those cited facts are supported by the text, so there is no fabrication, but the response is still wrong because it does not decline.
  - pages read: dp-content-75, dp-content-74, dp-content-70
- **run 2: correct**
  - bot: Bağışlayın, yalnız Dövlət Proqramı ilə bağlı kömək edirəm. Proqramla bağlı sual verməyə dəvət edirəm.
  - judge: IN_DOCUMENTS is no, so the expected behavior is to decline rather than answer. The bot correctly says it only helps with the State Programme and invites the user to ask a programme-related question. It does not invent any unsupported programme facts.
  - pages read: dp-content-75, dp-content-74, dp-content-70

### q31: Сколько баллов ГЭЦ нужно для бакалавриата?

- in_documents: yes
- your answer: At least 400 for agriculture, health, welfare, basic medical and special groups; at least 550 for other fields
- **run 1: partly** (made up)
  - bot: Bakalavriat səviyyəsi üzrə müraciət etmək üçün GƏT imtahanında aşağıdakı bal tələbləri var: - Texniki, təbiət, səhiyyə və bəzi digər prioritet ixtisaslar üzrə ən azı 400 bal; - Digər sahələr üzrə ən azı 550 bal. Mənbə: dp.edu.az/az/faq
  - judge: IN_DOCUMENTS is yes, and the bot should answer from the programme text. It gives the main threshold split correctly as 400 for certain priority groups and 550 for other fields, but it changes the official list of 400-point groups: the documents say agriculture, health, welfare and service, basic medical education, and special-purpose groups, while the bot says 'technical, natural sciences, health and some other priority fields,' which is incomplete and partly inaccurate.
  - pages read: dp-faq, dp-content-65, pdf-secim-meyarlari-2026, dp-content-66
- **run 2: correct**
  - bot: Bakalavriat səviyyəsi üzrə müraciət üçün DİM imtahanında sahəyə görə aşağıdakı bal tələbləri var: - Texniki, təbiət, kənd təsərrüfatı, səhiyyə, rifah və xidmət, baza ali tibb və xüsusi ixtisaslar üzrə ən azı 400 bal; - Digər sahələr üzrə ən azı 550 bal. Mənbə: dp.edu.az/az/faq, dp.edu.az/az/content/65, dp.edu.az/uploads/fileuploads/2026/05/4ec0f92d30d04271886e0bc82fcae744.pdf
  - judge: IN_DOCUMENTS is yes, and the bot gives the required bachelor DİM score thresholds directly from the provided documents. The key facts match the reference answer: minimum 400 for agriculture/health/welfare/basic medical/special groups and 550 for other fields; it also includes technical and natural sciences, which are indeed in the source text. Nothing important is wrong or misleading.
  - pages read: dp-faq, dp-content-65, pdf-secim-meyarlari-2026

### q33: Как оценивается собеседование?

- in_documents: yes
- your answer: Out of 50 points, minimum 40 to pass
- **run 1: correct**
  - bot: Müsahibədə maksimum 50 bal verilir. Minimum 40 bal toplayan namizədlər müsabiqədə iştirak hüququ qazanır. Qiymətləndirmədə ixtisas üzrə bilik, məntiqi mühakimə, kommunikasiya bacarıqları, özünəinam və inandırma qabiliyyəti nəzərə alınır. Bu məlumat 15.09.2026 tarixinə olan vəziyyətdir. Mənbə: dp.edu.az/az/faq
  - judge: IN_DOCUMENTS is yes, and the bot’s answer matches the key facts in the documents: the interview is graded out of 50 points, and 40 is the minimum to qualify for the competition stage. It also correctly adds the evaluation criteria listed in the FAQ, which fits the question about how the interview is assessed. No unsupported programme fact is introduced.
  - pages read: dp-faq, pdf-doktorantura
- **run 2: wrong**
  - bot: Müsahibədə namizədin ixtisas üzrə bilik və bacarıqları, məntiqi mühakimə, kommunikasiya, özünəinam və inandırma qabiliyyəti qiymətləndirilir. Ekspertlər bu sahələrdə namizədin səviyyəsini yoxlayır. Bu mərhələ Dövlət Proqramına qəbul üçün vacibdir. Mənbə: dp.edu.az/az/faq
  - judge: IN_DOCUMENTS is yes, and the reference answer says the interview is scored out of 50 points with a minimum of 40 to pass. The bot reply instead describes what competencies are assessed during the interview, which is a different FAQ item and does not answer how it is evaluated. It also omits the key scoring facts entirely, but the facts it states are supported by the text.
  - pages read: dp-faq, pdf-doktorantura
