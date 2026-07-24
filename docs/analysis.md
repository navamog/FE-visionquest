# FE Vision Quest 한글패치 — ROM 분석 결과

**공식 대상: `Fire Emblem - Vision Quest v3.0.GBA` (28,947,180 bytes / 0x1B9B2EC)** — 사용자 결정(2026-07-24)으로 v3 기준.
- v3: CRC32 `2BCFEC83`, MD5 `39050BD4B968B5CB1CD3067E9290CEA2`, SHA1 `16D772195BD3B6A561595ECB71BE7BEF1185E7EA`
- FE8U 원본(보유, 검증됨): CRC32 `A47246AE` (No-Intro 일치)
- (구판 v2.3: SHA1 `E9E80928...`, 최초 분석에 사용 — 엔진 영역 0x2BA4/0x3C00-0x4700/0xA1C0/허프만트리 **v3와 바이트 동일** 확인)
- FE8U(BE8E) 기반, FEBuilderGBA로 제작된 롬핵. GBA ROM 한도 32MB까지 ~4.4MB 확장 여유.
- 아래 모든 오프셋은 v2.3에서 역공학 후 v3에서 재검증됨. 텍스트 테이블 위치 동일(0x1024D7C, `p32(0xA2A0)`으로 확인).

## 1. 텍스트 시스템 (완전 해석)

| 항목 | 값 |
|---|---|
| 텍스트 테이블 | ROM `0x1024D7C`, 4바이트 포인터 × `0x7FFF` 항목 |
| 테이블 참조 리터럴 | `0x0800A284`의 `ldr r1, =0x09024D7C` |
| 안티허프만 규약 | 포인터 bit31 set = **비압축 평문** (FEBuilder 방식) |
| 디코더 분기 | `0x08002BA4`: `lsrs r2,r0,#31` → set이면 `0x0800A274`→`0x08464470`(비압축 복사), 아니면 허프만 |
| 허프만 트리 | 노드 배열 `0x15A72C` (4바이트 노드 {u16 a,b}, b==0xFFFF=리프), 루트 `0x15D484`, 루트포인터 `0x15D488` |
| 문자열 포스트프로세서 | `0x0800A1C8` (후행 0x1F 제거), `0x0800A2A4` (`0x80 xx` 특수코드 전개) |

- **평문(스토리) 문자열: v3 기준 2,566개, 1,276,595바이트** — `text/script_dump.txt` (v2.3은 2,433개였음; git 히스토리에 보존)
- **허프만(시스템) 문자열: v3 기준 2,741개** — 인덱스 0x1..0x143F대 (아이템/클래스/메뉴) / `text/system_dump.txt`
- 더미 필러: `0x080E8414`를 가리키는 27,582개 항목 (미사용 ID)
- 제어코드: `0x00`끝, `0x01`줄바꿈, `0x03`[A], `0x04-0x1F` 제어(초상화 로드 0x10 등), `0x80 xx` 2바이트 특수(이름 치환 등, 0x12-0x22 점프테이블 @0x0800A2E0)

## 2. 폰트/렌더러 (완전 해석)

### Glyph 구조체 (0x48바이트)
```c
struct Glyph {
    struct Glyph* next;   // +0  같은 슬롯의 체인 (SJIS용)
    u8  sjisByte;         // +4  리드 바이트 (ASCII 글리프는 0)
    u8  width;            // +5  전진폭(px)
    u16 pad;              // +6
    u32 bitmap[16];       // +8  16행 × u32(16px, 2bpp, LSB-first)
};
```

### 폰트 테이블
- 대화 폰트: `0x58C7EC` (0x100 포인터, 코드 참조 `0x08003CFE`)
- 메뉴 폰트: `0x58F6F4` (0x100 포인터, 아이콘 포함, 코드 참조 `0x08003D10`)
- Font 구조체(RAM, 기본 인스턴스 `0x02028E58`, 현재 폰트 포인터 `0x02028E70`):
  `+0` VRAM dest, `+4` glyphs 테이블, `+8` 글리프 드로우 함수ptr, `+0xC` dest 계산 함수ptr(`0x080041E9`), `+0x10` tileref, `+0x12` x커서, `+0x14` palid, `+0x16` 모드플래그
- 모드 플래그 전역: `0x02028E74` (Text init 시 `0x08003C7C`로 읽어 text+0x16에 저장)

### 문자 드로우 경로 (`0x08004180` Text_DrawCharacter)
- **모드≠0 (영문 경로) `0x08004504`**: `glyph = glyphs[str[0]]`, null이면 `glyphs[0x3F]`('?'), 1바이트 전진
- **모드=0 (2바이트 SJIS 경로, 온전히 잔존!)**: `b1=str[0], b2=str[1]`; `g = glyphs[b2-0x40]`에서 `next` 체인을 `g->sjisByte==b1`까지 걷기; 실패 시 0x81A7('？') 폴백; 2바이트 전진
- 폭 계산: 1문자 `0x08004538`, 문자열 `0x08004568` (바이트당 glyph->width 합산 — 2바이트 미고려, 패치 필요)
- 2bpp→4bpp 블리터: `0x08004268`+, 색 LUT `0x08588240`

## 3. 한글 렌더링 설계 (초안)

**전략: 영문 경로에 2바이트 한글 훅 추가 + 직접 인덱스 글리프 뱅크**

- 인코딩: 리드 `0x81..0x93`(예약 0x80 제외), 세컨드 `0x40..0xFF` → 19×192=3,648 슬롯 ≥ 2,350 완성형
- 글리프 뱅크: 확장 영역에 `Glyph[N]` 배열, 주소 = `BANK + ((b1-0x81)*192 + (b2-0x40)) * 0x48` — 링크드리스트 불필요, asm 몇 줄로 계산
- 훅 지점:
  1. `0x08004504` 드로우: `str[0] >= 0x81`이면 2바이트 룩업 후 기존 블리터 호출, +2 전진
  2. `0x08004538` / `0x08004568` 폭 계산: 동일 분기
  3. 자동 줄바꿈/스킵 등 바이트 단위 순회 코드 점검 필요
- 한글 폰트: 16×16 셀에 12~13px 픽셀폰트 (Windows 굴림체 비트맵 스트라이크 또는 둥근모꼴/Galmuri) → 2bpp (ink=1, shadow=2는 영문 글리프 관례 확인 후)
- 용량: 2,350자 × 0x48 = ~170KB (여유 충분)
- 시스템(허프만) 문자열도 전부 비압축+bit31로 교체 삽입 가능 (테이블 포인터만 교체)

## 3.5 기술 리서치 요약 (2026-07-24, decomp/커뮤니티 소스 교차 확인)

- 제 역공학 결과가 fe8u decomp 심볼과 전부 일치: `Text_DrawCharacter`=0x4180(SJIS 2바이트), `Text_DrawCharacterAscii`=0x4504, `GetCharTextLenASCII`=0x4538, `GetStringTextLenASCII`=0x4568, `Text_DrawString`=0x4004, `GetStringTextLen`=0x3EDC, `GetCharTextLen`=0x3F3C, `Text_DrawStringASCII`=0x44C8, 폰트테이블 `TextGlyphs_System`=0x58C7EC/`TextGlyphs_Talk`=0x58F6F4/`TextGlyphs_Special`=0x590B44
- **검증된 선행 프레임워크: MokhaLeee의 [FE8U-UTF8InstallerCN](https://github.com/MokhaLeee/FE8U-UTF8InstallerCN)** (중국어 번역 실제 사용) — UTF-8 디코드 + `glyphs[코드포인트 하위바이트]` 버킷 연결리스트(sjisByte1=상위바이트), LynJump 훅 0x3EDC/0x3F3C/0x4004/0x4180, ASCII 경로 훅 0x44D2/0x450C/0x4540/0x4574. FEBuilder 호환 시그니처: `ORG 0x44D2; BYTE 00 00 00 4B 18 47` (DrawUTF8 모드 인식)
- SkillSystem_FE8 저장소에 안티허프만 원본 EA 코드 + CN 폰트 인스톨러 포함 (`EngineHacks/ExternalHacks/Fonts/`)
- **제약: 디코드 버퍼 `sMsgString` @0x0202A6AC buffer1 = 0x555바이트/메시지.** UTF-8 한글(3B/자)이면 ~450자 상한 → 장문 대사 위험. 커스텀 2바이트 인코딩이면 ~680자로 여유. 인코딩 선택 시 고려(또는 버퍼 리포인트 패치)
- FEBuilderGBA 내부: 텍스트 테이블 주소는 `p32(0xA2A0)`, 저장 시 비압축+MSB로 기록, 복구용 바닐라 주소 0x15D48C
- 한글패치 선례: FE6/FE8 (WindowsTiger팀, FEBuilder 개조 + 32MB 확장), FE7 (Del Lab, 12×12 비트맵 글꼴) — 완성형 방식 실증
- laqieer FEHRR: 대본에 실제 등장하는 글자만 빈도 스캔해 글리프 삽입하는 접근 (한글 용량 최적화에 적용 가능)

## 4. 리서치 확인 사항 (2026-07-24)

- VQ는 FEBuilderGBA 제작 — 공개 텍스트/빌드파일 소스 없음. ROM 추출이 정공법 (완료)
- **최신판은 v3 (2022-10-01, Pushwall 마감 패치)** — v2.3(2021-05)은 구판. 배포는 FE8U 대상 UPS
- 중국어 번역판 존재(2022-04, CRC32 92B99FD6) — CJK 폰트 삽입 실증 사례
- 일본어 번역 진행 중 (FEBuilder 개발자 7743 본인)
- 한국어 번역: 전무
- FEU 스레드: https://feuniverse.us/t/3815 / RA 패치 미러: RetroAchievements RAPatches GitHub
- FE8U 원본 베이스: CRC32 A47246AE / SHA1 C25B145E37456171ADA4B0D440BF88A19F4D509F

## 4.5 ★ 파이프라인 실기 검증 완료 (2026-07-24)

**`tools/build_korean.py`로 빌드한 `out/vq3kr.gba`를 Mesen2(emucap)에서 실행 → 한글 렌더링 성공.**

- 오프닝 대사(텍스트 ID 0xF9F)를 한국어로 교체 → 인게임에서 초상화·자동 줄바꿈·[A] 프롬프트와 함께 **완벽히 한글 표시**됨. 2개 대사 화면 육안 확인.
- 맵 커맨드 메뉴(Unit/Status/Guide/Options/Suspend/End) 영문이 **교체 함수를 통해 깨짐 없이** 렌더 → 훅이 ASCII 경로를 보존함을 확인.
- 즉 **인코딩(EUC-KR 2바이트) + 글리프 뱅크 + asm 훅 4곳**이 end-to-end로 동작 입증.

### 확정된 구현 방식 (build_korean.py)
- **인코딩: EUC-KR (KS X 1001 완성형 2,350자)**. 뱅크 인덱스 = `(b1-0xB0)*94 + (b2-0xA1)`. 리드바이트 0xB0–0xC8은 제어(0x00–0x1F)·특수(0x80)와 겹치지 않아 메시지 VM이 인쇄용 런으로 그대로 통과시킴.
- **글리프 뱅크**: ROM 확장영역(원본 끝 0x1B9B2F0~)에 `Glyph[2350] × 0x48B`. 굴림 12px, 잉크=3/그림자=2(x+1), YOFF=2. 폭=우측 잉크+2.
- **asm 훅 (keystone THUMB, 확장영역 0x1BC47E0~)**: 트램펄린 `ldr r3,[pc,#0]; bx r3; .word target|1`을 4개 ASCII 텍스트 함수에 설치:
  - 0x4504 `Text_DrawCharacterAscii` → kr_drawchar (대사 경로가 이걸 호출)
  - 0x44C8 `Text_DrawStringASCII` → kr_drawstring (메뉴/한 줄 경로)
  - 0x4538 `GetCharTextLenASCII` → kr_charlen
  - 0x4568 `GetStringTextLenASCII` → kr_strlen
  - 공통 서브루틴 `kr_lookup`: 첫 바이트 0xB0–0xC8 & 둘째 ≥0xA1이면 뱅크 인덱스로 글리프 반환(2바이트 소비), 아니면 기존 ASCII 글리프 폴백(1바이트).
- **텍스트 재삽입**: 테이블 항목을 `확장영역주소 | 0x80000000`(비압축 플래그)으로 교체, 문자열은 EUC-KR 바이트 + `0x00`(대사는 제어코드 보존).

### 남은 과제 (실무)
- keystone가 로컬 라벨(`1:`)·`ldr =imm` 미지원 → 명명 라벨 + `.word` 리터럴로 우회 완료.
- 폭 계산 kr_charlen/kr_strlen은 완성형 한글 폭을 glyph->width로 합산(정상). 다만 한글 고정폭(예: 13px)이 자연스러운지 문장부호 혼용 시 재확인 필요.
- 시스템(허프만) 문자열의 메뉴 라벨은 별도 text ID 사용 — 0x0592/0x0601은 맵 메뉴가 아니었음. 실제 사용 ID 매핑 필요(번역 단계에서 인게임 대조).
- 장문 대사: 디코드 버퍼 0x555B/메시지 한도 유의.

## 4.6 ★ 데모 완역 + 인게임 검증 완료 (2026-07-24)

**`out/vq3kr.gba` (패치 CRC32 `CBD62B00`) — Mesen2 인게임 검증에서 전 UI 한글 확인:**

| 화면 | 한글 렌더 |
|---|---|
| 오프닝 대사(0xF9F/0xFA1) | ✅ 왕좌 대결 씬 완역, 초상화·[A] 정상 |
| 난이도 설명(0x149-14B) | ✅ "적이 약합니다 (오토레벨 -5)..." 다중 줄 |
| 맵 커맨드 메뉴 | ✅ 유닛·상황·도감·설정·중단·턴종료 |
| 유닛 이름 | ✅ 슈토르히(Storch) |
| 지형 | ✅ 길(Road) |
| 챕터 목표(0x1A8) | ✅ 표시된 칸에서 탈출 |

- **번역 규모**: 스토리 2개(오프닝 씬) + 시스템 UI 1,320개(0x01–0x6DF: 메뉴/아이템/무기/클래스/스탯/전투/메시지) + UI 63개(챕터 제목·목표·난이도) = **약 1,382개**
- 병렬 서브에이전트 4개로 시스템 문자열 번역, `verify_tl.py`로 제어토큰 무결성(0 불일치)·EUC-KR(0 오류) 검증
- **세이브스테이트**: `out/prologue_map_kr.mss` (프롤로그 맵, 재검증용)
- **컷신 스킵**: START 버튼으로 이벤트 씬 스킵 가능(FE8 기본) — 긴 오프닝 우회에 유용

### 미번역/한계 (그래픽 타일 — 텍스트 아님)
- "New Game/Extras", "Select Mode", "Easy/Normal/Hard", "Objective/Turn/Funds/PLAYER/ENEMY" 라벨 = 사전렌더 그래픽 → 텍스트 패치 대상 아님(그래픽 편집 별도 작업)
- 청크 02/03(0x6E0–0x14BD): 스킬 설명 + 바닐라 FE8 잔존 대사 → 저우선(R버튼 도움말/미사용). 다음 반복에서 보강
- 프롤로그 전투 중 대사·엔딩 씬: 추가 story ID 수집 필요(텍스트 속도 최대화 후 일괄 로깅 예정)

## 5. 산출물/도구

- `text/script_dump.txt` + `script_meta.json` — 스토리 평문 덤프
- `text/system_dump.txt` + `system_meta.json` — 시스템(허프만) 덤프
- `tools/dumptext2.py`, `tools/dumphuff2.py` — 덤퍼 (재실행 가능)
- `tools/disrom.py` — capstone THUMB 디스어셈블러 (리터럴 주석 포함)
- `tools/fontdump.py` — 폰트 테이블 → PNG 렌더 (비트맵 +8 보정 필요: 현재 +0xC로 1행 밀림)
