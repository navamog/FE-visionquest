# -*- coding: utf-8 -*-
"""Korean translations for VQ story records (prologue opening scene).

Each entry mirrors the ORIGINAL control-code layout; only English runs are
swapped for Korean. Tone: natural modern Korean, keeping each speaker's register.
  Faces: 0x39 = Gradin (elder brother / ruler of Belaro, accusing, menacing)
         0xB1 = Vaspasian (younger brother, noble, defensive)
  Controls: 09=left speaks  0C=right speaks  01=NL  03=[A]  10 xx=LoadFace  11=ClearFace
"""

NL = b"\x01"
A = b"\x03"
L = b"\x09"   # left portrait active
R = b"\x0C"   # right portrait active


def _b(*parts):
    out = bytearray()
    for p in parts:
        out += p if isinstance(p, (bytes, bytearray)) else p.encode("euc-kr")
    return bytes(out)


# 0x0F9F — intro: dinner pleasantries (Gradin welcomes Vaspasian)
S0F9F = _b(
    L, b"\x10\x39", NL, R, b"\x10\xB1", NL,
    L, "바스파시안 경, 나의 형제이자", NL, "귀한 손님이여.", A,
    NL, "오늘 밤의 만찬과 연주가", NL, "마음에 드셨는지요?", A,
    R, "그라딘 경...", NL, "물론입니다.", A,
    NL, "포도주와 치즈가", NL, "참으로 훌륭했습니다.", A,
    NL, "이 드라이한 적포도주와", NL, "진한 체다의 조화는,", A,
    NL, "그야말로 천상의 즐거움이지요.", A,
    NL, "목관 합주단의 아름다운", NL, "연주까지 곁들여지니,", A,
    NL, "이 훌륭한 조화를 표현할", NL, "말을 찾기 어려울 정도입니다.", A,
    NL, "간단히 말하자면,", NL, "참으로 제 마음에 듭니다.", A,
    L, "과찬이십니다,", NL, "나의 형제여.", A,
    NL, "허나 오늘 밤 우리가 나눌", NL, "이야기가 아직 남아 있습니다.", A,
    NL, "이 지도를 봐 주시지요.", A,
    NL, "그대가 맡은 마을들을", NL, "표시해 두었소.", A,
    b"\x00\x00",
)

# 0x0FA1 — the confrontation (Gradin accuses Vaspasian of treason)
S0FA1 = _b(
    L, b"\x10\x39", NL, R, b"\x10\xB1", NL,
    L, "바스파시안 경...", NL, "내 인내심을 시험하는군.", A,
    NL, "지금이야말로 내가 알아낸 바를", NL, "털어놓기에", A,
    NL, "더없이 좋은 때인 듯하오.", A,
    NL, "그 소문을 처음 들었을 땐,", NL, "나는 애써 외면했소.", A,
    NL, "'내 아우가?", NL, "그럴 리가 있나?'", A,
    NL, "기녀와 노파들의 입방아쯤이야", NL, "한낱 우스갯소리라 여겼지!", A,
    NL, "헌데 그대가 감히", NL, "나를 폭군이라 몰아세워?", A,
    NL, "결국 내가 두려워하던 대로,", NL, "그 소문이 사실이었군.", A,
    R, "그 소문이란 게 무엇입니까,", NL, "그라딘 경.", A,
    NL, "형님이 무엇을 들으셨는지", NL, "저도 듣고 싶습니다.", A,
    NL, L, "그대가 도당을 규합해", NL, "왕좌를 노린다는 이야기다.", A,
    NL, "허나 바스파시안 경,", A,
    b" ", NL, "교활한 책략가라는 그대의 악명이", NL, "괜한 것은 아니나,", A,
    NL, "그대는 내게 충성하는 자들의", NL, "마음을 헤아리지 못했어!", A,
    NL, "이 몸을!", NL, "벨라로의 지배자를 말이다!", A,
    NL, R, "그라딘 경!", A,
    NL, "저는 왕좌를 찬탈할", NL, "뜻이 조금도 없습니다,", A,
    NL, "저속한 연극의 줄거리처럼 말이지요.", A,
    NL, "벨라로의 고귀한 신하로서,", NL, "저는 오직 번영을 바랄 뿐입니다.", A,
    NL, "우리와 혈족만이 아니라,", NL, "온 벨라로 백성을 위해서요.", A,
    NL, "그 소문은 거짓입니다.", NL, "무료한 아낙들이 지어낸 허언이자,", A,
    NL, "벨라로의 고귀한 가문이", NL, "무너지길 바라는 자들이,", A,
    NL, "닳고 해지고 약해지길 바라며", NL, "퍼뜨린 낭설입니다!", A,
    L, "언제나처럼 요지부동이군...", A,
    NL, "진실을 눈앞에 두고도,", NL, "그대는 거짓만 늘어놓아!", A,
    NL, "끔찍하고 끔찍한 거짓을!", NL, "안타깝게도, 나의 아우여...", A,
    NL, "이 반역의 죄는", NL, "결코 가벼이 넘기지 않을 것이다.", A,
    R, "이건 말도 안 됩니다!", A,
    NL, "형님의 집에서, 여기서", NL, "저를 죽이시겠다는 겁니까?", A,
    NL, "형님, 광기에", NL, "정신을 놓으셨군요!", A,
    NL, "이토록 변하시다니...", NL, "대체 무슨 일이 있었습니까? 말씀해 주십시오!", A,
    L, "닥쳐라!", A,
    NL, "그대에게 충고도 동정도", NL, "받지 않겠다.", A,
    NL, "내게서 왕좌를 훔치려는", NL, "나의 아우에게서는!", A,
    NL, L, b"\x11", R, b"\x11",
    b"\x00\x00",
)

STORY = {
    0x0F9F: S0F9F,
    0x0FA1: S0FA1,
}
