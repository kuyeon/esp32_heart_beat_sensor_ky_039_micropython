"""
KY-039 심박 센서 기본 사용법 예제
ESP32 S3용 마이크로파이썬
원 저작자: COMPASS (만드는 놀이터 블로그)

이 예제는 KY-039 심박 센서를 사용하여 기본적인 심박수 측정을 수행합니다.
"""

from ky039_heartbeat import KY039Heartbeat
import time

def main():
    """
    기본 심박수 측정 예제
    """
    print("=== KY-039 심박 센서 기본 예제 ===")
    
    # 센서 초기화
    # GPIO 34번 핀을 아날로그 입력으로 사용
    # GPIO 2번 핀을 LED 제어용으로 사용 (선택사항)
    heartbeat_sensor = KY039Heartbeat(
        analog_pin=34,    # 아날로그 입력 핀
        led_pin=2,        # LED 핀 (선택사항)
        sample_rate=100   # 샘플링 주파수 100Hz
    )
    
    # 센서 캘리브레이션
    print("\n센서 캘리브레이션을 시작합니다...")
    print("손가락을 센서에 올려놓고 5초간 기다려주세요.")
    min_val, max_val, avg_val = heartbeat_sensor.calibrate_sensor(duration=5)
    
    # 심박수 측정
    print("\n심박수 측정을 시작합니다...")
    print("손가락을 센서에 올려놓고 10초간 기다려주세요.")
    
    heart_rate = heartbeat_sensor.start_measurement(duration=10)
    
    # 결과 출력
    print(f"\n=== 측정 결과 ===")
    print(f"심박수: {heart_rate:.1f} BPM")
    
    # 원시 데이터 및 필터링된 데이터 확인
    raw_data = heartbeat_sensor.get_raw_data()
    filtered_data = heartbeat_sensor.get_filtered_data()
    peak_times = heartbeat_sensor.get_peak_times()
    
    print(f"수집된 샘플 수: {len(raw_data)}")
    print(f"감지된 피크 수: {len(peak_times)}")
    
    if raw_data:
        print(f"원시 데이터 범위: {min(raw_data)} - {max(raw_data)}")
    
    if filtered_data:
        print(f"필터링된 데이터 범위: {min(filtered_data):.1f} - {max(filtered_data):.1f}")

def continuous_monitoring():
    """
    연속 심박수 모니터링 예제
    """
    print("\n=== 연속 심박수 모니터링 예제 ===")
    
    # 센서 초기화
    heartbeat_sensor = KY039Heartbeat(
        analog_pin=34,
        led_pin=2,
        sample_rate=50  # 낮은 샘플링 주파수로 배터리 절약
    )
    
    print("연속 모니터링을 시작합니다. Ctrl+C로 중단하세요.")
    
    try:
        while True:
            print("\n새로운 측정 시작...")
            heart_rate = heartbeat_sensor.start_measurement(duration=5)
            
            if heart_rate > 0:
                print(f"현재 심박수: {heart_rate:.1f} BPM")
                
                # 심박수 구간 판정
                if heart_rate < 60:
                    print("심박수 상태: 낮음 (휴식 상태)")
                elif heart_rate < 100:
                    print("심박수 상태: 정상 (일반 활동)")
                elif heart_rate < 120:
                    print("심박수 상태: 약간 높음 (가벼운 운동)")
                else:
                    print("심박수 상태: 높음 (강한 운동)")
            else:
                print("심박수를 측정할 수 없습니다. 센서를 확인해주세요.")
            
            # 5초 대기 후 다음 측정
            time.sleep(5)
    
    except KeyboardInterrupt:
        print("\n모니터링이 중단되었습니다.")
        heartbeat_sensor.stop_measurement()

def sensor_test():
    """
    센서 테스트 및 디버깅 예제
    """
    print("\n=== 센서 테스트 예제 ===")
    
    # 센서 초기화
    heartbeat_sensor = KY039Heartbeat(
        analog_pin=34,
        led_pin=2,
        sample_rate=200  # 높은 샘플링 주파수로 정밀 측정
    )
    
    print("센서 테스트를 시작합니다...")
    print("손가락을 센서에 올려놓고 3초간 기다려주세요.")
    
    # 짧은 측정으로 센서 상태 확인
    heart_rate = heartbeat_sensor.start_measurement(duration=3)
    
    # 데이터 분석
    raw_data = heartbeat_sensor.get_raw_data()
    filtered_data = heartbeat_sensor.get_filtered_data()
    
    print(f"\n=== 센서 테스트 결과 ===")
    print(f"측정된 심박수: {heart_rate:.1f} BPM")
    print(f"수집된 샘플 수: {len(raw_data)}")
    
    if raw_data:
        print(f"원시 데이터 통계:")
        print(f"  최소값: {min(raw_data)}")
        print(f"  최대값: {max(raw_data)}")
        print(f"  평균값: {sum(raw_data)/len(raw_data):.1f}")
        
        # 신호 변화량 확인
        if len(raw_data) > 1:
            changes = [abs(raw_data[i] - raw_data[i-1]) for i in range(1, len(raw_data))]
            avg_change = sum(changes) / len(changes)
            print(f"  평균 변화량: {avg_change:.1f}")
            
            if avg_change < 10:
                print("  경고: 신호 변화가 적습니다. 센서 연결을 확인하세요.")
            elif avg_change > 100:
                print("  경고: 신호 변화가 너무 큽니다. 센서를 안정화하세요.")
            else:
                print("  센서 신호가 정상입니다.")

if __name__ == "__main__":
    # 기본 예제 실행
    main()
    
    # 사용자 선택에 따른 추가 예제 실행
    print("\n추가 예제를 실행하시겠습니까?")
    print("1. 연속 모니터링")
    print("2. 센서 테스트")
    print("3. 종료")
    
    try:
        choice = input("선택하세요 (1-3): ")
        
        if choice == "1":
            continuous_monitoring()
        elif choice == "2":
            sensor_test()
        else:
            print("프로그램을 종료합니다.")
    
    except:
        print("프로그램을 종료합니다.")
