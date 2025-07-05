# 드럼 MIDI 생성기 & 피아노 키보드 매퍼

이 저장소는 음악 관련 도구들을 포함하고 있습니다:
1. **드럼 MIDI 생성기** - 음악 파일에서 드럼 패턴을 추출하여 MIDI 파일로 생성
2. **피아노 키보드 매퍼** - MIDI 파일을 키보드로 연주

## 드럼 MIDI 생성기

### 주요 기능

- **기본 드럼 패턴 생성**: Rock, Pop, Latin, Funk, Ballad 스타일
- **음악 파일 분석**: librosa를 사용한 오디오 분석
- **🆕 Demucs 통합**: Facebook AI의 고품질 드럼 분리
- **커스텀 패턴 생성**: 사용자 정의 드럼 패턴
- **MIDI 출력**: mido 라이브러리를 사용한 MIDI 파일 생성

### Demucs란?

Demucs는 Facebook AI Research에서 개발한 최첨단 음악 소스 분리 도구입니다:
- AI 기반 고품질 음악 트랙 분리
- 드럼, 베이스, 보컬, 기타 등으로 분리
- 기존 방법보다 훨씬 정확한 분리 성능
- 분리된 드럼 트랙으로 더 정확한 패턴 분석 가능

### 설치 및 설정

1. 기본 의존성 설치:
```bash
pip install mido librosa numpy scipy
```

2. Demucs 설치 (선택사항, 고품질 분리용):
```bash
pip install demucs
```

3. 프로그램 실행:
```bash
python drum_midi_creator.py
```

### 사용법

#### 인터랙티브 모드
```bash
python drum_midi_creator.py
```

#### 프로그래밍 방식
```python
# 기본 패턴 생성
from drum_midi_creator import create_drum_midi_with_mido, create_basic_rock_pattern

pattern = create_basic_rock_pattern()
create_drum_midi_with_mido("rock", pattern, "rock_drums.mid", bpm=120, measures=8)

# 음악 파일에서 드럼 추출 (기본)
from drum_midi_creator import create_drum_from_audio_file
create_drum_from_audio_file("song.mp3", "extracted_drums.mid")

# Demucs로 고품질 드럼 추출
from drum_midi_creator import create_drum_midi_from_audio_with_demucs
create_drum_midi_from_audio_with_demucs("song.mp3", "demucs_drums.mid", bpm=120, measures=8)
```

## 피아노 키보드 매퍼

## 기능

- MIDI CSV 파일에서 노트 이벤트 로드
- 피아노 건반을 키보드 키로 매핑 (흰건반/검은건반)
- 실시간 키보드 입력 시뮬레이션 (PyAutoGUI 사용)
- 다양한 재생 속도 옵션
- 노트 분석 및 키 매핑 정보 표시

## 키보드 매핑

### 흰건반 (White Keys)
```
z x c v b n m , . / Q W E R T Y U I O P [ ]
C D E F G A B C D E F G A B C D E F G A B C
```

### 검은건반 (Black Keys)
```
S D   G H J   L ;     2 3   4   6 7   9 0 -
C# D# F# G# A#     C# D# F#  G# A#  C# D# F#
```

## 설치

1. Python 3.6 이상이 필요합니다.
2. 필요한 패키지를 설치합니다:

```bash
pip install -r requirements.txt
```

또는 직접 설치:

```bash
pip install pyautogui
```

## 사용법

1. MIDI 파일을 CSV로 변환한 파일이 필요합니다. (예: SamuraiHeart.csv)
2. 프로그램을 실행합니다:

```bash
python piano_keyboard_mapper.py
```

3. 메뉴에서 원하는 옵션을 선택합니다:
   - 1: 정상 속도 (키 누르기/떼기 시뮬레이션)
   - 2: 절반 속도 (키 누르기/떼기 시뮬레이션)
   - 3: 2배 속도 (키 누르기/떼기 시뮬레이션)
   - 4: 정상 속도 (탭 모드 - 짧은 키 누르기)
   - 5: 키 표시만 (타이밍 없음, 시뮬레이션 없음)
   - 6: 종료

## 주의사항

⚠️ **중요**: 이 프로그램은 실제 키보드 입력을 시뮬레이션합니다!

- 텍스트 에디터나 대상 애플리케이션이 포커스된 상태에서 실행하세요
- 긴급 정지: 마우스를 화면 왼쪽 상단 모서리로 이동하면 중단됩니다 (PyAutoGUI FAILSAFE)
- 프로그램 실행 전에 중요한 작업을 저장하세요
- Ctrl+C로 재생을 중단할 수 있습니다

## 파일 구조

- `piano_keyboard_mapper.py`: 메인 프로그램
- `SamuraiHeart.csv`: MIDI CSV 데이터 파일 (예시)
- `requirements.txt`: 필요한 Python 패키지 목록
- `README.md`: 이 문서

## 기술적 세부사항

- MIDI 틱을 시간으로 변환: 480 ticks/quarter note, 500000 μs/quarter note
- PyAutoGUI를 사용한 실제 키보드 입력 시뮬레이션
- 안전 기능: FAILSAFE, 짧은 대기 시간 설정
- 두 가지 모드: 지속적 키 누르기 vs 탭 모드

## 문제 해결

### PyAutoGUI 설치 오류
Windows에서 PyAutoGUI 설치 시 문제가 있다면:
```bash
pip install --upgrade pip
pip install pyautogui
```

### 키 입력이 작동하지 않음
- 대상 애플리케이션이 포커스되어 있는지 확인
- 관리자 권한으로 실행 시도
- 보안 소프트웨어가 키 입력을 차단하지 않는지 확인

### 속도 조절
- 템포 스케일을 조정하여 재생 속도 변경 가능
- PyAutoGUI.PAUSE 값을 조정하여 키 입력 간격 조절 가능

- `piano_keyboard_mapper.py`: 메인 프로그램
- `SamuraiHeart.csv`: MIDI 데이터 (CSV 형식)
- `requirements.txt`: 필요한 라이브러리 목록

## 주의사항

- `keyboard` 라이브러리는 관리자 권한이 필요할 수 있습니다
- 프로그램 실행 중 Ctrl+C로 중지할 수 있습니다
- CSV 파일은 프로그램과 같은 폴더에 있어야 합니다
