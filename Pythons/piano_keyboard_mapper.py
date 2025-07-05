import csv
import time
import threading
from collections import defaultdict
import sys

# pyautogui 라이브러리 사용 (pip install pyautogui로 설치 가능)
try:
    import pyautogui
    PYAUTOGUI_AVAILABLE = True
    # pyautogui 안전 설정
    pyautogui.FAILSAFE = True  # 마우스를 화면 왼쪽 상단 모서리로 이동하면 중단
    pyautogui.PAUSE = 0.01     # 각 함수 호출 사이의 짧은 대기 시간
except ImportError:
    PYAUTOGUI_AVAILABLE = False
    print("Note: 'pyautogui' library not found. Install with 'pip install pyautogui' for actual key simulation.")

class PianoKeyboardMapper:
    def __init__(self, csv_file_path, use_minecraft_optimization=False):
        self.csv_file_path = csv_file_path
        self.use_minecraft_optimization = use_minecraft_optimization
        
        # 기본 피아노 건반 매핑
        # 흰건반: C, D, E, F, G, A, B (옥타브마다 반복)
        self.white_keys = ['z', 'x', 'c', 'v', 'b', 'n', 'm', ',', '.', '/', 
                          'q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p', '[', ']']
        
        # 검은건반: C#, D#, F#, G#, A# (옥타브마다 반복)
        self.black_keys = ['s', 'd', 'g', 'h', 'j', 'l', ';',
                          '2', '3', '4', '6', '7', '9', '0', '-']
        
        # MIDI 노트를 키보드 키로 매핑
        self.note_to_key = {}
        self.setup_note_mapping()
        
        # 마인크래프트 최적화 적용
        if use_minecraft_optimization:
            self.apply_minecraft_optimization()
        
        # 현재 연주 중인 노트들
        self.active_notes = set()
        
        # 이벤트 리스트
        self.events = []
        self.load_midi_events()
        
    def apply_minecraft_optimization(self):
        """마인크래프트 instrument keyboard 음역대에 맞게 최적화
        l:c3 (Low/Left hand 시작: C3, MIDI 36)
        m:f4:g4 (Middle 영역: F4~G4, MIDI 53~55)  
        R:c6 (High/Right hand 끝: C6, MIDI 84)
        """
        print("\nApplying Minecraft instrument keyboard optimization...")
        print("Range: C3 (MIDI 36) to C6 (MIDI 84)")
        print("Focus on F4-G4 (MIDI 53-55) middle range")
        
        # 마인크래프트에서 연주 가능한 음역대 (C3 ~ C6)
        minecraft_min_note = 36  # C3
        minecraft_max_note = 84  # C6
        minecraft_middle_start = 53  # F4
        minecraft_middle_end = 55   # G4
        
        # 기존 매핑에서 마인크래프트 범위 밖의 노트들을 범위 안으로 조정
        adjusted_mapping = {}
        
        for midi_note, key in self.note_to_key.items():
            if minecraft_min_note <= midi_note <= minecraft_max_note:
                # 범위 안에 있으면 그대로 사용
                adjusted_mapping[midi_note] = key
            else:
                # 범위 밖에 있으면 옥타브 조정해서 범위 안으로 이동
                adjusted_note = midi_note
                
                # 너무 낮은 음은 옥타브 올리기
                while adjusted_note < minecraft_min_note:
                    adjusted_note += 12
                
                # 너무 높은 음은 옥타브 내리기
                while adjusted_note > minecraft_max_note:
                    adjusted_note -= 12
                
                # 조정된 노트가 범위 안에 있으면 매핑
                if minecraft_min_note <= adjusted_note <= minecraft_max_note:
                    adjusted_mapping[adjusted_note] = key
        
        # 중간 영역 (F4~G4) 노트들은 우선순위를 높여서 더 접근하기 쉬운 키에 매핑
        middle_notes = [midi_note for midi_note in adjusted_mapping.keys() 
                       if minecraft_middle_start <= midi_note <= minecraft_middle_end]
        
        # 우선순위 높은 키들 (가운데 행의 접근하기 쉬운 키들)
        priority_keys = ['f', 'g', 'h', 'j', 'k', 'l', 'd', 's', 'a']
        
        # 중간 영역 노트들을 우선순위 키에 재매핑
        for i, note in enumerate(sorted(middle_notes)):
            if i < len(priority_keys):
                adjusted_mapping[note] = priority_keys[i]
        
        self.note_to_key = adjusted_mapping
        
        print(f"Optimized mapping created with {len(adjusted_mapping)} notes")
        print("Middle range (F4-G4) mapped to easy-access keys: f, g, h, j, k, l, d, s, a")
    
    def setup_note_mapping(self):
        """기존 피아노 건반 MIDI 노트 번호를 키보드 키로 매핑"""
        # C4 = MIDI note 60을 기준으로 매핑
        base_note = 48  # C3부터 시작 (더 낮은 옥타브 포함)
        
        # 흰건반 매핑
        white_note_offsets = [0, 2, 4, 5, 7, 9, 11]  # C, D, E, F, G, A, B
        for i, key in enumerate(self.white_keys):
            octave = i // 7
            note_in_octave = i % 7
            midi_note = base_note + (octave * 12) + white_note_offsets[note_in_octave]
            self.note_to_key[midi_note] = key
            
        # 검은건반 매핑
        black_note_offsets = [1, 3, 6, 8, 10]  # C#, D#, F#, G#, A#
        for i, key in enumerate(self.black_keys):
            octave = i // 5
            note_in_octave = i % 5
            midi_note = base_note + (octave * 12) + black_note_offsets[note_in_octave]
            self.note_to_key[midi_note] = key
    
    def load_midi_events(self):
        """CSV 파일에서 MIDI 이벤트를 로드"""
        print(f"Loading MIDI events from {self.csv_file_path}...")
        
        with open(self.csv_file_path, 'r', encoding='utf-8') as file:
            csv_reader = csv.reader(file)
            for row in csv_reader:
                if len(row) >= 6:
                    track = int(row[0])
                    timestamp = int(row[1])
                    event_type = row[2].strip()
                    
                    if event_type in ['Note_on_c', 'Note_off_c']:
                        channel = int(row[3])
                        note = int(row[4])
                        velocity = int(row[5])
                        
                        self.events.append({
                            'track': track,
                            'timestamp': timestamp,
                            'type': event_type,
                            'note': note,
                            'velocity': velocity
                        })
        
        # 타임스탬프 순으로 정렬
        self.events.sort(key=lambda x: x['timestamp'])
        print(f"Loaded {len(self.events)} note events")
    
    def get_key_for_note(self, note):
        """MIDI 노트에 해당하는 키보드 키 반환"""
        return self.note_to_key.get(note, None)
    
    def press_key(self, key):
        """키를 눌러서 시뮬레이트"""
        if key and key not in self.active_notes:
            self.active_notes.add(key)
            print(f"Press: {key}")
            # 실제 키보드 입력 시뮬레이션 (pyautogui 라이브러리가 있을 때만)
            if PYAUTOGUI_AVAILABLE:
                try:
                    pyautogui.keyDown(key)
                except Exception as e:
                    print(f"Key press error for {key}: {e}")
    
    def release_key(self, key):
        """키를 떼어서 시뮬레이트"""
        if key and key in self.active_notes:
            self.active_notes.remove(key)
            print(f"Release: {key}")
            # 실제 키보드 입력 시뮬레이션 (pyautogui 라이브러리가 있을 때만)
            if PYAUTOGUI_AVAILABLE:
                try:
                    pyautogui.keyUp(key)
                except Exception as e:
                    print(f"Key release error for {key}: {e}")
    
    def tap_key(self, key):
        """키를 짧게 눌렀다 떼기 (옵션)"""
        if key:
            print(f"Tap: {key}")
            if PYAUTOGUI_AVAILABLE:
                try:
                    pyautogui.press(key)
                except Exception as e:
                    print(f"Key tap error for {key}: {e}")
    
    def play_midi(self, tempo_scale=1.0, use_tap=False):
        """MIDI 이벤트를 키보드 입력으로 재생"""
        print(f"Starting playback... (tempo scale: {tempo_scale}, tap mode: {use_tap})")
        print("Press Ctrl+C to stop")
        
        if PYAUTOGUI_AVAILABLE:
            print("PyAutoGUI is available - actual key simulation enabled")
        else:
            print("PyAutoGUI not available - only showing key presses")
        
        try:
            start_time = time.time()
            last_timestamp = 0
            
            for event in self.events:
                # 타이밍 계산 (MIDI ticks를 초로 변환)
                # 480 ticks per quarter note, 500000 microseconds per quarter note
                current_timestamp = event['timestamp']
                delta_ticks = current_timestamp - last_timestamp
                delta_seconds = (delta_ticks / 480.0) * (500000 / 1000000.0) / tempo_scale
                
                if delta_seconds > 0:
                    time.sleep(delta_seconds)
                
                # 키 매핑 확인
                key = self.get_key_for_note(event['note'])
                
                if key:
                    if event['type'] == 'Note_on_c' and event['velocity'] > 0:
                        if use_tap:
                            # 탭 모드: 짧게 누르고 바로 떼기
                            self.tap_key(key)
                        else:
                            # 일반 모드: 누르기만 (나중에 Note_off에서 떼기)
                            self.press_key(key)
                    elif event['type'] == 'Note_off_c' or (event['type'] == 'Note_on_c' and event['velocity'] == 0):
                        if not use_tap:
                            # 탭 모드가 아닐 때만 키를 떼기
                            self.release_key(key)
                else:
                    # 매핑되지 않은 노트는 무시
                    pass
                
                last_timestamp = current_timestamp
                
        except KeyboardInterrupt:
            print("\nPlayback stopped by user")
        except Exception as e:
            print(f"Error during playback: {e}")
        finally:
            # 모든 키를 해제
            for key in list(self.active_notes):
                self.release_key(key)
    
    def show_key_mapping(self):
        """키 매핑 정보를 출력"""
        if self.use_minecraft_optimization:
            print("\n=== Minecraft Optimized Piano Keyboard Mapping ===")
            print("Optimized for instrument keyboard range: C3 to C6")
            print("Priority on middle range (F4-G4) with easy-access keys")
            
            # 마인크래프트 범위 내의 매핑만 표시
            minecraft_mappings = [(note, key) for note, key in self.note_to_key.items() 
                                if 36 <= note <= 84]  # C3 to C6
            
            for note, key in sorted(minecraft_mappings):
                note_name = self.midi_note_to_name(note)
                priority_indicator = " (PRIORITY)" if 53 <= note <= 55 else ""
                print(f"  {key} -> {note_name} (MIDI {note}){priority_indicator}")
        else:
            print("\n=== Full Piano Keyboard Mapping ===")
            print("White Keys (low to high):")
            for i, key in enumerate(self.white_keys):
                octave = i // 7
                note_names = ['C', 'D', 'E', 'F', 'G', 'A', 'B']
                note_name = note_names[i % 7] + str(3 + octave)
                print(f"  {key} -> {note_name}")
            
            print("\nBlack Keys (low to high):")
            for i, key in enumerate(self.black_keys):
                octave = i // 5
                note_names = ['C#', 'D#', 'F#', 'G#', 'A#']
                note_name = note_names[i % 5] + str(3 + octave)
                print(f"  {key} -> {note_name}")
    
    def analyze_notes(self):
        """사용된 노트들을 분석"""
        used_notes = set()
        for event in self.events:
            if event['type'] == 'Note_on_c':
                used_notes.add(event['note'])
        
        print(f"\n=== Note Analysis ===")
        print(f"Total unique notes used: {len(used_notes)}")
        print(f"Note range: {min(used_notes)} - {max(used_notes)}")
        
        mapped_notes = 0
        for note in sorted(used_notes):
            key = self.get_key_for_note(note)
            note_name = self.midi_note_to_name(note)
            if key:
                mapped_notes += 1
                print(f"  MIDI {note} ({note_name}) -> Key '{key}'")
            else:
                print(f"  MIDI {note} ({note_name}) -> NOT MAPPED")
        
        print(f"Mapped notes: {mapped_notes}/{len(used_notes)}")
    
    def midi_note_to_name(self, midi_note):
        """MIDI 노트 번호를 노트 이름으로 변환"""
        note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        octave = (midi_note // 12) - 1
        note = note_names[midi_note % 12]
        return f"{note}{octave}"


def main():
    print("=== Piano MIDI to Keyboard Mapper ===")
    
    # CSV 파일 경로 입력받기
    print("\nEnter MIDI CSV file path:")
    print("(Press Enter for default: SamuraiHeart.csv)")
    csv_input = input("CSV file: ").strip()
    
    if not csv_input:
        csv_file = "SamuraiHeart.csv"
        print(f"Using default file: {csv_file}")
    else:
        csv_file = csv_input
        print(f"Using file: {csv_file}")
    
    # 파일 존재 확인
    import os
    if not os.path.exists(csv_file):
        print(f"Error: Could not find file '{csv_file}'")
        print("Make sure the file exists in the current directory or provide the full path.")
        return
    
    print("\nChoose mapping mode:")
    print("1. Minecraft optimized (C3-C6 range, F4-G4 priority)")
    print("2. Full piano keyboard")
    
    mapping_choice = input("Choose mapping mode (1-2): ").strip()
    use_minecraft = mapping_choice == '1'
    
    if use_minecraft:
        print("\nMinecraft optimized mode selected")
        print("Range: C3 to C6 (instrument keyboard compatible)")
        print("Middle range F4-G4 mapped to easy-access keys")
    else:
        print("\nFull piano keyboard mode selected")
    
    if PYAUTOGUI_AVAILABLE:
        print("PyAutoGUI is available for key simulation")
        print("WARNING: This program will simulate actual keyboard input!")
        print("Make sure to have a text editor or target application focused.")
        print("Move mouse to top-left corner to emergency stop (FAILSAFE)")
        response = input("Continue? (y/n): ").strip().lower()
        if response != 'y':
            print("Cancelled.")
            return
    else:
        print("PyAutoGUI not available - install with: pip install pyautogui")
        print("Running in display-only mode")
    
    try:
        # 매퍼 초기화
        mapper = PianoKeyboardMapper(csv_file, use_minecraft_optimization=use_minecraft)
        
        # 키 매핑 정보 출력
        mapper.show_key_mapping()
        
        # 노트 분석
        mapper.analyze_notes()
        
        # 재생 옵션 선택
        print("\n=== Playback Options ===")
        if use_minecraft:
            print("1. Normal speed (tap mode)")
            print("2. Half speed (tap mode)")
            print("3. Double speed (tap mode)")
            print("4. Just show key presses (no timing, no simulation)")
            print("5. Exit")
            
            choice = input("Choose an option (1-5): ").strip()
            
            if choice == '1':
                mapper.play_midi(1.0, use_tap=True)
            elif choice == '2':
                mapper.play_midi(0.5, use_tap=True)
            elif choice == '3':
                mapper.play_midi(2.0, use_tap=True)
            elif choice == '4':
                # 타이밍 없이 키 순서만 보여주기
                for event in mapper.events:
                    key = mapper.get_key_for_note(event['note'])
                    if key and event['type'] == 'Note_on_c' and event['velocity'] > 0:
                        print(f"Press: {key} (Note: {mapper.midi_note_to_name(event['note'])})")
            elif choice == '5':
                print("Goodbye!")
            else:
                print("Invalid choice")
        else:
            print("1. Normal speed (with key simulation)")
            print("2. Half speed (with key simulation)")
            print("3. Double speed (with key simulation)")
            print("4. Normal speed (tap mode - short key presses)")
            print("5. Just show key presses (no timing, no simulation)")
            print("6. Exit")
            
            choice = input("Choose an option (1-6): ").strip()
            
            if choice == '1':
                mapper.play_midi(1.0, use_tap=False)
            elif choice == '2':
                mapper.play_midi(0.5, use_tap=False)
            elif choice == '3':
                mapper.play_midi(2.0, use_tap=False)
            elif choice == '4':
                mapper.play_midi(1.0, use_tap=True)
            elif choice == '5':
                # 타이밍 없이 키 순서만 보여주기
                for event in mapper.events:
                    key = mapper.get_key_for_note(event['note'])
                    if key and event['type'] == 'Note_on_c' and event['velocity'] > 0:
                        print(f"Press: {key} (Note: {mapper.midi_note_to_name(event['note'])})")
            elif choice == '6':
                print("Goodbye!")
            else:
                print("Invalid choice")
            
    except FileNotFoundError:
        print(f"Error: Could not find file '{csv_file}'")
        print("Make sure the file is in the same directory as this script.")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
