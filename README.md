# ESP32 S3용 KY-039 심박 센서 마이크로파이썬 라이브러리

ESP32 S3에서 KY-039 심박 센서를 사용하여 심박수를 측정하고 분석하는 마이크로파이썬 라이브러리입니다.

> **⚠️ 개발 상태**: 현재 라이브러리가 개발 중이며, 실제 하드웨어 테스트가 필요한 상태입니다.

**원 저작자**: COMPASS (만드는 놀이터 블로그)

## 📋 목차

- [특징](#특징)
- [하드웨어 요구사항](#하드웨어-요구사항)
- [설치 및 사용법](#설치-및-사용법)
- [API 문서](#api-문서)
- [예제](#예제)
- [라이브러리 구조](#라이브러리-구조)
- [문제 해결](#문제-해결)
- [기여하기](#기여하기)

## ✨ 특징

- **정확한 심박수 측정**: 고급 필터링 알고리즘으로 노이즈 제거
- **실시간 모니터링**: 연속적인 심박수 추적 및 분석
- **심박수 구간 분석**: 운동 강도별 심박수 구간 분류
- **심박 변이도(HRV) 계산**: 심장 건강 상태 분석
- **불규칙 리듬 감지**: 심박 리듬 이상 감지
- **시각적 피드백**: LED를 통한 상태 표시
- **캘리브레이션 기능**: 센서 자동 캘리브레이션
- **다양한 샘플링 주파수**: 용도에 따른 최적화된 설정

## 🔧 하드웨어 요구사항

### 필수 구성요소
- ESP32 S3 개발보드
- KY-039 심박 센서 모듈
- 점퍼 와이어
- 브레드보드 (선택사항)

### 핀 연결
```
KY-039 센서    ESP32 S3
VCC    →       3.3V
GND    →       GND
A0     →       GPIO 34 (아날로그 입력)
D0     →       GPIO 2  (디지털 출력, 선택사항)
```

### 추가 구성요소 (선택사항)
- LED (상태 표시용)
- 저항 (LED용, 220Ω)
- 버튼 (측정 시작/중단용)

## 🚀 설치 및 사용법

### 1. 파일 업로드
ESP32 S3에 다음 파일들을 업로드하세요:
```
ky039_heartbeat.py          # 메인 라이브러리
heartbeat_analyzer.py       # 분석 모듈
example_basic.py           # 기본 예제
example_advanced.py        # 고급 예제
example_realtime.py        # 실시간 모니터링 예제
```

### 2. 기본 사용법
```python
from ky039_heartbeat import KY039Heartbeat

# 센서 초기화
sensor = KY039Heartbeat(
    analog_pin=34,    # 아날로그 입력 핀
    led_pin=2,        # LED 핀 (선택사항)
    sample_rate=100   # 샘플링 주파수
)

# 심박수 측정
heart_rate = sensor.start_measurement(duration=10)
print(f"심박수: {heart_rate:.1f} BPM")
```

### 3. 예제 실행
```python
# 기본 예제
exec(open('example_basic.py').read())

# 고급 분석 예제
exec(open('example_advanced.py').read())

# 실시간 모니터링
exec(open('example_realtime.py').read())
```

## 📚 API 문서

### KY039Heartbeat 클래스

#### 생성자
```python
KY039Heartbeat(analog_pin, led_pin=None, sample_rate=100)
```

#### 주요 메서드

##### `start_measurement(duration=10)`
심박수 측정을 시작합니다.
- **매개변수**: `duration` (int) - 측정 지속 시간 (초)
- **반환값**: `float` - 측정된 심박수 (BPM)

##### `stop_measurement()`
심박수 측정을 중단합니다.

##### `calibrate_sensor(duration=5)`
센서를 캘리브레이션합니다.
- **매개변수**: `duration` (int) - 캘리브레이션 지속 시간 (초)
- **반환값**: `tuple` - (최소값, 최대값, 평균값)

##### `get_heart_rate()`
마지막으로 측정된 심박수를 반환합니다.
- **반환값**: `float` - 심박수 (BPM)

##### `set_filter_alpha(alpha)`
저역통과 필터의 알파 값을 설정합니다.
- **매개변수**: `alpha` (float) - 필터 계수 (0.0 ~ 1.0)

##### `set_sample_rate(rate)`
샘플링 주파수를 설정합니다.
- **매개변수**: `rate` (int) - 샘플링 주파수 (Hz)

### HeartbeatAnalyzer 클래스

#### 주요 메서드

##### `add_heart_rate(heart_rate, timestamp=None)`
심박수 데이터를 히스토리에 추가합니다.

##### `get_moving_average()`
이동 평균 심박수를 계산합니다.

##### `get_heart_rate_variability()`
심박 변이도(HRV)를 계산합니다.

##### `get_current_zone(current_hr, age=30)`
현재 심박수가 속하는 구간을 반환합니다.

##### `detect_irregular_rhythm(threshold=10)`
불규칙한 심박 리듬을 감지합니다.

## 📖 예제

### 1. 기본 심박수 측정
```python
from ky039_heartbeat import KY039Heartbeat

sensor = KY039Heartbeat(analog_pin=34, led_pin=2)
heart_rate = sensor.start_measurement(duration=10)
print(f"심박수: {heart_rate:.1f} BPM")
```

### 2. 연속 모니터링
```python
from ky039_heartbeat import KY039Heartbeat
from heartbeat_analyzer import HeartbeatAnalyzer

sensor = KY039Heartbeat(analog_pin=34)
analyzer = HeartbeatAnalyzer()

while True:
    hr = sensor.start_measurement(duration=5)
    analyzer.add_heart_rate(hr)
    print(f"현재: {hr:.1f} BPM, 평균: {analyzer.get_moving_average():.1f} BPM")
    time.sleep(5)
```

### 3. 심박수 구간 분석
```python
from heartbeat_analyzer import HeartbeatAnalyzer

analyzer = HeartbeatAnalyzer()
heart_rate = 120  # 측정된 심박수

zone = analyzer.get_current_zone(heart_rate, age=30)
zones = analyzer.get_heart_rate_zone(age=30)

print(f"현재 구간: {zone}")
print(f"구간별 범위: {zones}")
```

## 📁 라이브러리 구조

```
esp32_heart_beat_sensor_ky_039_micropython/
├── ky039_heartbeat.py          # 메인 라이브러리 클래스
├── heartbeat_analyzer.py       # 심박수 분석 모듈
├── example_basic.py           # 기본 사용법 예제
├── example_advanced.py        # 고급 분석 예제
├── example_realtime.py        # 실시간 모니터링 예제
└── README.md                  # 이 파일
```

### 파일 설명

- **`ky039_heartbeat.py`**: KY-039 센서를 제어하고 심박수를 측정하는 메인 클래스
- **`heartbeat_analyzer.py`**: 심박수 데이터 분석, HRV 계산, 구간 분석 기능
- **`example_basic.py`**: 기본적인 심박수 측정 예제
- **`example_advanced.py`**: 고급 신호 처리 및 분석 예제
- **`example_realtime.py`**: 실시간 모니터링 및 시각적 피드백 예제

## 🔧 문제 해결

### 일반적인 문제들

#### 1. 심박수를 측정할 수 없는 경우
- 센서 연결 상태 확인
- 손가락이 센서에 제대로 닿아 있는지 확인
- 센서 캘리브레이션 실행
- 샘플링 주파수 조정

#### 2. 측정값이 부정확한 경우
- 필터 알파 값 조정 (`set_filter_alpha()`)
- 측정 시간 증가
- 센서 위치 조정
- 환경 조명 확인

#### 3. 신호가 불안정한 경우
- 센서 연결부 확인
- 전원 공급 상태 확인
- 주변 전자기기 간섭 확인
- 샘플링 주파수 감소

### 디버깅 팁

```python
# 센서 상태 확인
sensor = KY039Heartbeat(analog_pin=34)
min_val, max_val, avg_val = sensor.calibrate_sensor(duration=5)
print(f"신호 범위: {max_val - min_val}")

# 원시 데이터 확인
sensor.start_measurement(duration=3)
raw_data = sensor.get_raw_data()
print(f"원시 데이터: {raw_data[:10]}")  # 처음 10개 값
```

## 🤝 기여하기

이 프로젝트에 기여하고 싶으시다면:

1. 이슈를 생성하여 버그나 개선사항을 보고해주세요
2. 새로운 기능이나 예제를 제안해주세요
3. 코드 개선이나 최적화를 제안해주세요
4. 문서화 개선을 도와주세요

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

## 📞 지원

문제가 있거나 질문이 있으시면 이슈를 생성해주세요.

---

**주의사항**: 이 라이브러리는 교육 및 프로토타이핑 목적으로 제작되었습니다. 의료 목적으로 사용하지 마세요. 정확한 심박수 측정이 필요한 경우 전문 의료 기기를 사용하시기 바랍니다.