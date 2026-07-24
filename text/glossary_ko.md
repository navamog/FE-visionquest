# VQ 한글패치 용어집 (canonical)

톤: 자연스러운 현대 구어체. UI/시스템은 간결한 표준어. 원본 말투 유지.
제어코드 `[X][NL][A][80xx]`와 `[..]` 형태는 **절대 변형 말 것** — 위치만 유지하고 그대로 출력.
숫자/이름이 삽입되는 조각 문자열(예: "Got " + 값 + " gold.")은 **조각 순서를 못 바꾸므로**
한국어가 조각 순서로 읽어도 자연스럽게: "Got "→"" / "gold."→"골드 획득" 처럼 배치.

## 스탯 (FE 표준)
HP=HP, Str=힘, Mag=마력, Skl=기술, Spd=속도, Lck=행운, Def=수비, Res=마방,
Mov=이동, Con=체격, Aid=원조, Level=레벨, EXP=경험치, Wexp=무기숙련,
Hit=명중, Crit=필살, Atk=공격, Avo=회피, Rng=사거리

## 메뉴/행동
Unit=유닛, Status=상황, Options=설정, Suspend=중단, Save=저장, End=턴종료,
Guide=도감, Attack=공격, Staff=지팡이, Item=도구, Trade=교환, Rescue=구출,
Drop=내리기, Take=받기, Give=건네기, Wait=대기, Talk=대화, Visit=방문,
Seize=점령, Steal=훔치기, Dance=춤, Shop=상점, Armory=무기점, Vendor=도구점,
Arena=투기장, Convoy=수송대, Restart=재시작, Yes=예, No=아니오,
Change=변경, Cancel=취소, Fight=전투, Escape=탈출, Discard=버리기, Use=사용

## 무기/아이템 (FE 표준)
Sword=검, Lance=창, Axe=도끼, Bow=활, Anima=자연마법, Light=빛마법, Dark=어둠마법,
Staff=지팡이, Iron=강철, Steel=강철(무거운 건 문맥따라), Slim=가는, Killer=킬러,
Vulnerary=상처약, Elixir=만능약, Antitoxin=해독제, Pure Water=성수,
Iron Sword=철검, Iron Lance=철창, Iron Axe=철도끼, Iron Bow=철궁,
Fire=파이어, Thunder=선더, Elfire=엘파이어, Lightning=라이트닝,
Heal=힐, Mend=멘드, Physic=피직, Torch=횃불, Chest Key=상자 열쇠, Door Key=문 열쇠,
Lockpick=만능열쇠, Hammerne=하마안, Fortify=포티파이

## 지형/기타
Plains=평원, Forest=숲, Fort=요새, Village=마을, Throne=옥좌, Gate=성문,
Turn=턴, Enemy=적, Ally=아군, Player Phase=아군 페이즈, Enemy Phase=적 페이즈,
Boss=보스, Chapter=챕터, Prologue=프롤로그, gold=골드

## VQ 고유명사 (인명 — 음역 통일)
Gradin=그라딘, Vaspasian=바스파시안, Storch=슈토르히, Waluyo=왈루요, Titus=티투스,
Lori=로리, Sigrid=시그리드, Timmonen=티모넨, Sjohstrom=쇼스트롬, Cajon=카욘,
Stroganoff=스트로가노프, Esfir=에스피르, Naia=나이아, Marlen=마를렌, Larisa=라리사,
Kusuma=쿠수마, Surya=수리아, Bulan=불란, Ketut=케툿, Anisa=아니사, Zakawat=자카왓,
Zuljalal=줄잘랄, Natsuko=나츠코, Michael=미하엘, Sarka=사르카, Erasmus=에라스무스,
Festan=페스탄, Kosuke=코스케, Kitozawa=키토자와, Hindrawan=힌드라완, Dewi=데위,
Belaro=벨라로, Nevan=네반, Lomsk=롬스크, Kuching=쿠칭, Mahala=마할라, Mostyn=모스틴,
Horschadt=호르샤트, Ofenloch=오펜로흐, Yaska=야스카, Balti=발티
