# FE-visionquest
파이어 엠블렘 비전 퀘스트 한글패치

<img width="240" height="160" alt="image" src="https://github.com/user-attachments/assets/474e85f4-8a68-4311-bf40-0f1c842afa26" />

기술 노트

인코딩: EUC-KR 2바이트를 직접 인덱싱하는 글리프 뱅크(ROM 확장 영역)

렌더러: 텍스트 디스패처 4곳(0x4004/0x4180/0x3EDC/0x3F3C)과ASCII 변형 4곳(0x4504/0x44C8/0x4538/0x4568)에 THUMB 훅 원본 ASCII는 그대로, 한글은 2바이트 경로로 렌더

Vision Quest 원작: Pandan & friends / Pushwall (v3). 본 패치는 비공식 팬 번역이며, 원본 ROM은 포함하지 않습니다.

이 패치는 팬 번역이며 비영리로 배포됩니다. 원본 롬은 포함되어 있지 않으며, 롬은 이용자가 정품으로 직접 준비해야 합니다. 

패치 파일의 재배포 시에는 이 README를 함께 첨부해 주세요.
