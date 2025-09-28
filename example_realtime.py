"""
KY-039 심박 센서 실시간 모니터링 예제
ESP32 S3용 마이크로파이썬
원 저작자: COMPASS (만드는 놀이터 블로그)

이 예제는 실시간으로 심박수를 모니터링하고
시각적 피드백을 제공합니다.
"""

from ky039_heartbeat import KY039Heartbeat
from heartbeat_analyzer import HeartbeatAnalyzer
import time

class RealtimeHeartRateMonitor:
    """
    실시간 심박수 모니터링 클래스
    """
    
    def __init__(self, analog_pin=34, led_pin=2, status_led_pin=4):
        """
        실시간 모니터 초기화
        
        Args:
            analog_pin (int): 아날로그 입력 핀
            led_pin (int): 센서 LED 핀
            status_led_pin (int): 상태 표시 LED 핀
        """
        self.heartbeat_sensor = KY039Heartbeat(
            analog_pin=analog_pin,
            led_pin=led_pin,
            sample_rate=100
        )
        
        self.analyzer = HeartbeatAnalyzer(window_size=10)
        
        # 상태 LED 초기화
        self.status_led = None
        if status_led_pin:
            from machine import Pin
            self.status_led = Pin(status_led_pin, Pin.OUT)
            self.status_led.off()
        
        self.is_monitoring = False
        self.measurement_count = 0
        
        print("실시간 심박수 모니터가 초기화되었습니다")
    
    def start_monitoring(self, measurement_interval=5):
        """
        실시간 모니터링 시작
        
        Args:
            measurement_interval (int): 측정 간격 (초)
        """
        self.is_monitoring = True
        self.measurement_count = 0
        
        print(f"실시간 모니터링을 시작합니다 (측정 간격: {measurement_interval}초)")
        print("Ctrl+C로 중단하세요.")
        
        try:
            while self.is_monitoring:
                self.measurement_count += 1
                
                # 상태 LED 깜빡임 (측정 시작)
                self._blink_status_led(2, 0.1)
                
                print(f"\n--- 측정 #{self.measurement_count} ---")
                print("측정 중...")
                
                # 심박수 측정
                heart_rate = self.heartbeat_sensor.start_measurement(duration=3)
                
                if heart_rate > 0:
                    # 분석기에 데이터 추가
                    self.analyzer.add_heart_rate(heart_rate)
                    
                    # 결과 표시
                    self._display_measurement_result(heart_rate)
                    
                    # 상태 LED로 심박수 구간 표시
                    self._indicate_heart_rate_zone(heart_rate)
                    
                else:
                    print("❌ 심박수 측정 실패")
                    self._blink_status_led(5, 0.2)  # 오류 표시
                
                # 다음 측정까지 대기
                if self.is_monitoring:
                    print(f"다음 측정까지 {measurement_interval}초 대기...")
                    time.sleep(measurement_interval)
        
        except KeyboardInterrupt:
            print("\n모니터링이 중단되었습니다.")
            self.stop_monitoring()
    
    def stop_monitoring(self):
        """모니터링 중단"""
        self.is_monitoring = False
        self.heartbeat_sensor.stop_measurement()
        
        # 최종 통계 출력
        self._display_final_statistics()
        
        # 상태 LED 끄기
        if self.status_led:
            self.status_led.off()
    
    def _display_measurement_result(self, heart_rate):
        """
        측정 결과를 표시합니다
        
        Args:
            heart_rate (float): 측정된 심박수
        """
        # 기본 정보
        print(f"💓 심박수: {heart_rate:.1f} BPM")
        
        # 이동 평균
        moving_avg = self.analyzer.get_moving_average()
        if moving_avg > 0:
            print(f"📊 이동 평균: {moving_avg:.1f} BPM")
        
        # 심박 변이도
        hrv = self.analyzer.get_heart_rate_variability()
        print(f"📈 심박 변이도: {hrv:.1f}")
        
        # 구간 분석
        zone = self.analyzer.get_current_zone(heart_rate, age=30)
        zone_emoji = self._get_zone_emoji(zone)
        print(f"{zone_emoji} 현재 구간: {zone}")
        
        # 상태 평가
        status = self._evaluate_heart_rate_status(heart_rate)
        print(f"🔍 상태: {status}")
        
        # 불규칙 리듬 감지
        if self.analyzer.detect_irregular_rhythm():
            print("⚠️  경고: 불규칙한 심박 리듬 감지!")
    
    def _get_zone_emoji(self, zone):
        """구간에 따른 이모지 반환"""
        zone_emojis = {
            'recovery': '😴',
            'aerobic': '🚶',
            'threshold': '🏃',
            'lactate': '💪',
            'neuromuscular': '🔥',
            'unknown': '❓'
        }
        return zone_emojis.get(zone, '❓')
    
    def _evaluate_heart_rate_status(self, heart_rate):
        """심박수 상태 평가"""
        if heart_rate < 60:
            return "낮음 (휴식 상태)"
        elif heart_rate < 100:
            return "정상 (일반 활동)"
        elif heart_rate < 120:
            return "약간 높음 (가벼운 운동)"
        elif heart_rate < 150:
            return "높음 (중간 강도 운동)"
        else:
            return "매우 높음 (고강도 운동)"
    
    def _indicate_heart_rate_zone(self, heart_rate):
        """
        LED로 심박수 구간을 표시합니다
        
        Args:
            heart_rate (float): 심박수
        """
        if not self.status_led:
            return
        
        # 구간별 LED 패턴
        if heart_rate < 60:
            # 휴식 구간: 천천히 깜빡임
            self._blink_status_led(1, 0.5)
        elif heart_rate < 100:
            # 정상 구간: 보통 깜빡임
            self._blink_status_led(2, 0.3)
        elif heart_rate < 120:
            # 가벼운 운동: 빠른 깜빡임
            self._blink_status_led(3, 0.2)
        elif heart_rate < 150:
            # 중간 강도: 매우 빠른 깜빡임
            self._blink_status_led(4, 0.1)
        else:
            # 고강도: 연속 깜빡임
            self._blink_status_led(5, 0.05)
    
    def _blink_status_led(self, count, interval):
        """
        상태 LED를 깜빡입니다
        
        Args:
            count (int): 깜빡임 횟수
            interval (float): 깜빡임 간격 (초)
        """
        if not self.status_led:
            return
        
        for _ in range(count):
            self.status_led.on()
            time.sleep(interval)
            self.status_led.off()
            time.sleep(interval)
    
    def _display_final_statistics(self):
        """최종 통계를 표시합니다"""
        stats = self.analyzer.get_statistics()
        
        if stats['count'] > 0:
            print(f"\n=== 최종 통계 ===")
            print(f"총 측정 횟수: {stats['count']}")
            print(f"평균 심박수: {stats['average']:.1f} BPM")
            print(f"최소 심박수: {stats['min']:.1f} BPM")
            print(f"최대 심박수: {stats['max']:.1f} BPM")
            print(f"심박 변이도: {stats['variability']:.1f}")
            
            # 전체적인 평가
            avg_hr = stats['average']
            if avg_hr < 60:
                print("📊 전체 평가: 휴식 상태가 많았습니다")
            elif avg_hr < 100:
                print("📊 전체 평가: 정상적인 활동 수준입니다")
            elif avg_hr < 120:
                print("📊 전체 평가: 가벼운 운동을 하셨습니다")
            else:
                print("📊 전체 평가: 활발한 운동을 하셨습니다")
        else:
            print("통계 데이터가 없습니다.")

def quick_measurement():
    """
    빠른 심박수 측정
    """
    print("=== 빠른 심박수 측정 ===")
    
    monitor = RealtimeHeartRateMonitor()
    
    print("손가락을 센서에 올려놓고 5초간 기다려주세요.")
    
    # 상태 LED로 준비 신호
    monitor._blink_status_led(3, 0.2)
    
    heart_rate = monitor.heartbeat_sensor.start_measurement(duration=5)
    
    if heart_rate > 0:
        print(f"\n💓 측정된 심박수: {heart_rate:.1f} BPM")
        
        # 구간 표시
        zone = monitor.analyzer.get_current_zone(heart_rate, age=30)
        emoji = monitor._get_zone_emoji(zone)
        print(f"{emoji} 구간: {zone}")
        
        # LED로 구간 표시
        monitor._indicate_heart_rate_zone(heart_rate)
    else:
        print("❌ 심박수 측정에 실패했습니다")

def calibration_and_test():
    """
    센서 캘리브레이션 및 테스트
    """
    print("=== 센서 캘리브레이션 및 테스트 ===")
    
    monitor = RealtimeHeartRateMonitor()
    
    # 캘리브레이션
    print("센서 캘리브레이션을 시작합니다...")
    print("손가락을 센서에 올려놓고 5초간 기다려주세요.")
    
    min_val, max_val, avg_val = monitor.heartbeat_sensor.calibrate_sensor(duration=5)
    
    print(f"캘리브레이션 완료:")
    print(f"  최소값: {min_val}")
    print(f"  최대값: {max_val}")
    print(f"  평균값: {avg_val:.1f}")
    
    # 신호 품질 확인
    signal_range = max_val - min_val
    if signal_range < 100:
        print("⚠️  경고: 신호 범위가 작습니다. 센서 연결을 확인하세요.")
    elif signal_range > 1000:
        print("⚠️  경고: 신호 범위가 너무 큽니다. 센서를 안정화하세요.")
    else:
        print("✅ 신호 품질이 양호합니다.")
    
    # 테스트 측정
    print("\n테스트 측정을 시작합니다...")
    heart_rate = monitor.heartbeat_sensor.start_measurement(duration=3)
    
    if heart_rate > 0:
        print(f"✅ 테스트 성공: {heart_rate:.1f} BPM")
    else:
        print("❌ 테스트 실패: 심박수를 측정할 수 없습니다")

if __name__ == "__main__":
    print("KY-039 심박 센서 실시간 모니터링")
    print("=" * 50)
    
    print("실행할 모드를 선택하세요:")
    print("1. 실시간 모니터링")
    print("2. 빠른 측정")
    print("3. 캘리브레이션 및 테스트")
    
    try:
        choice = input("선택하세요 (1-3): ")
        
        if choice == "1":
            # 측정 간격 설정
            try:
                interval = int(input("측정 간격을 입력하세요 (초, 기본값 5): ") or "5")
            except ValueError:
                interval = 5
            
            monitor = RealtimeHeartRateMonitor()
            monitor.start_monitoring(measurement_interval=interval)
            
        elif choice == "2":
            quick_measurement()
            
        elif choice == "3":
            calibration_and_test()
            
        else:
            print("잘못된 선택입니다.")
    
    except KeyboardInterrupt:
        print("\n프로그램이 중단되었습니다.")
    except Exception as e:
        print(f"오류가 발생했습니다: {e}")
    
    print("\n프로그램을 종료합니다.")
