"""
KY-039 심박 센서 고급 분석 예제
ESP32 S3용 마이크로파이썬
원 저작자: COMPASS (만드는 놀이터 블로그)

이 예제는 심박수 분석기와 신호 처리 기능을 사용하여
고급 심박수 분석을 수행합니다.
"""

from ky039_heartbeat import KY039Heartbeat
from heartbeat_analyzer import HeartbeatAnalyzer, SignalProcessor
import time

def advanced_heart_rate_analysis():
    """
    고급 심박수 분석 예제
    """
    print("=== 고급 심박수 분석 예제 ===")
    
    # 센서 및 분석기 초기화
    heartbeat_sensor = KY039Heartbeat(
        analog_pin=34,
        led_pin=2,
        sample_rate=100
    )
    
    analyzer = HeartbeatAnalyzer(window_size=5)
    
    print("고급 심박수 분석을 시작합니다...")
    print("손가락을 센서에 올려놓고 15초간 기다려주세요.")
    
    # 심박수 측정
    heart_rate = heartbeat_sensor.start_measurement(duration=15)
    
    if heart_rate > 0:
        # 분석기에 데이터 추가
        analyzer.add_heart_rate(heart_rate)
        
        # 통계 정보 출력
        stats = analyzer.get_statistics()
        print(f"\n=== 심박수 분석 결과 ===")
        print(f"현재 심박수: {heart_rate:.1f} BPM")
        print(f"이동 평균: {analyzer.get_moving_average():.1f} BPM")
        print(f"심박 변이도: {analyzer.get_heart_rate_variability():.1f}")
        
        # 심박수 구간 분석
        current_zone = analyzer.get_current_zone(heart_rate, age=30)
        zones = analyzer.get_heart_rate_zone(age=30)
        
        print(f"\n=== 심박수 구간 분석 (30세 기준) ===")
        print(f"현재 구간: {current_zone}")
        print("구간별 심박수 범위:")
        for zone_name, (min_hr, max_hr) in zones.items():
            print(f"  {zone_name}: {min_hr:.0f} - {max_hr:.0f} BPM")
        
        # 불규칙 리듬 감지
        if analyzer.detect_irregular_rhythm():
            print("\n경고: 불규칙한 심박 리듬이 감지되었습니다!")
        else:
            print("\n심박 리듬이 정상입니다.")
    
    else:
        print("심박수를 측정할 수 없습니다.")

def signal_processing_demo():
    """
    신호 처리 기능 데모
    """
    print("\n=== 신호 처리 데모 ===")
    
    # 센서 초기화
    heartbeat_sensor = KY039Heartbeat(
        analog_pin=34,
        led_pin=2,
        sample_rate=200
    )
    
    print("신호 처리를 위한 데이터 수집을 시작합니다...")
    print("손가락을 센서에 올려놓고 8초간 기다려주세요.")
    
    # 데이터 수집
    heart_rate = heartbeat_sensor.start_measurement(duration=8)
    
    # 원시 데이터 가져오기
    raw_data = heartbeat_sensor.get_raw_data()
    filtered_data = heartbeat_sensor.get_filtered_data()
    
    if raw_data:
        print(f"\n=== 신호 처리 결과 ===")
        print(f"원시 데이터 샘플 수: {len(raw_data)}")
        
        # 이동 평균 적용
        moving_avg = SignalProcessor.moving_average(raw_data, window_size=5)
        print(f"이동 평균 적용 완료 (윈도우 크기: 5)")
        
        # 중간값 필터 적용
        median_filtered = SignalProcessor.median_filter(raw_data, window_size=3)
        print(f"중간값 필터 적용 완료 (윈도우 크기: 3)")
        
        # 신호 정규화
        normalized = SignalProcessor.normalize_signal(raw_data)
        print(f"신호 정규화 완료")
        
        # 고급 피크 감지
        peaks = SignalProcessor.find_peaks_advanced(
            filtered_data, 
            min_distance=10
        )
        print(f"고급 피크 감지: {len(peaks)}개 피크 발견")
        
        # 미분 계산
        derivative_data = SignalProcessor.derivative(filtered_data)
        print(f"신호 미분 계산 완료")
        
        # 결과 요약
        print(f"\n=== 처리된 데이터 통계 ===")
        print(f"원시 데이터 범위: {min(raw_data)} - {max(raw_data)}")
        print(f"정규화된 데이터 범위: {min(normalized):.3f} - {max(normalized):.3f}")
        print(f"미분 데이터 범위: {min(derivative_data):.1f} - {max(derivative_data):.1f}")

def continuous_analysis():
    """
    연속 심박수 분석 및 모니터링
    """
    print("\n=== 연속 심박수 분석 모니터링 ===")
    
    # 센서 및 분석기 초기화
    heartbeat_sensor = KY039Heartbeat(
        analog_pin=34,
        led_pin=2,
        sample_rate=50
    )
    
    analyzer = HeartbeatAnalyzer(window_size=10)
    
    print("연속 분석을 시작합니다. Ctrl+C로 중단하세요.")
    print("각 측정마다 5초간 데이터를 수집합니다.")
    
    measurement_count = 0
    
    try:
        while True:
            measurement_count += 1
            print(f"\n--- 측정 #{measurement_count} ---")
            
            # 심박수 측정
            heart_rate = heartbeat_sensor.start_measurement(duration=5)
            
            if heart_rate > 0:
                # 분석기에 데이터 추가
                analyzer.add_heart_rate(heart_rate)
                
                # 현재 상태 출력
                print(f"현재 심박수: {heart_rate:.1f} BPM")
                print(f"이동 평균: {analyzer.get_moving_average():.1f} BPM")
                print(f"심박 변이도: {analyzer.get_heart_rate_variability():.1f}")
                
                # 구간 분석
                zone = analyzer.get_current_zone(heart_rate, age=30)
                print(f"현재 구간: {zone}")
                
                # 통계 정보
                stats = analyzer.get_statistics()
                print(f"통계 - 최소: {stats['min']:.1f}, 최대: {stats['max']:.1f}, 평균: {stats['average']:.1f}")
                
                # 불규칙 리듬 경고
                if analyzer.detect_irregular_rhythm():
                    print("⚠️  불규칙한 심박 리듬 감지!")
                
            else:
                print("심박수 측정 실패")
            
            # 3초 대기
            time.sleep(3)
    
    except KeyboardInterrupt:
        print(f"\n모니터링이 중단되었습니다. 총 {measurement_count}회 측정했습니다.")
        
        # 최종 통계
        final_stats = analyzer.get_statistics()
        if final_stats['count'] > 0:
            print(f"\n=== 최종 통계 ===")
            print(f"총 측정 횟수: {final_stats['count']}")
            print(f"평균 심박수: {final_stats['average']:.1f} BPM")
            print(f"최소 심박수: {final_stats['min']:.1f} BPM")
            print(f"최대 심박수: {final_stats['max']:.1f} BPM")
            print(f"심박 변이도: {final_stats['variability']:.1f}")

def filter_optimization_demo():
    """
    필터 최적화 데모
    """
    print("\n=== 필터 최적화 데모 ===")
    
    # 센서 초기화
    heartbeat_sensor = KY039Heartbeat(
        analog_pin=34,
        led_pin=2,
        sample_rate=100
    )
    
    print("다양한 필터 설정으로 측정을 비교합니다...")
    print("손가락을 센서에 올려놓고 6초간 기다려주세요.")
    
    # 다양한 알파 값으로 테스트
    alpha_values = [0.5, 0.7, 0.8, 0.9]
    results = {}
    
    for alpha in alpha_values:
        print(f"\n알파 값 {alpha}로 측정 중...")
        heartbeat_sensor.set_filter_alpha(alpha)
        
        heart_rate = heartbeat_sensor.start_measurement(duration=6)
        results[alpha] = heart_rate
        
        print(f"알파 {alpha}: {heart_rate:.1f} BPM")
        time.sleep(1)
    
    # 결과 비교
    print(f"\n=== 필터 최적화 결과 ===")
    for alpha, hr in results.items():
        print(f"알파 {alpha}: {hr:.1f} BPM")
    
    # 최적 알파 값 추천
    valid_results = {k: v for k, v in results.items() if v > 0}
    if valid_results:
        avg_hr = sum(valid_results.values()) / len(valid_results)
        best_alpha = min(valid_results.keys(), 
                        key=lambda x: abs(valid_results[x] - avg_hr))
        print(f"\n추천 알파 값: {best_alpha} (평균에 가장 가까운 결과)")

if __name__ == "__main__":
    print("KY-039 심박 센서 고급 분석 예제")
    print("=" * 50)
    
    # 사용자 선택
    print("실행할 예제를 선택하세요:")
    print("1. 고급 심박수 분석")
    print("2. 신호 처리 데모")
    print("3. 연속 분석 모니터링")
    print("4. 필터 최적화 데모")
    print("5. 모든 예제 실행")
    
    try:
        choice = input("선택하세요 (1-5): ")
        
        if choice == "1":
            advanced_heart_rate_analysis()
        elif choice == "2":
            signal_processing_demo()
        elif choice == "3":
            continuous_analysis()
        elif choice == "4":
            filter_optimization_demo()
        elif choice == "5":
            advanced_heart_rate_analysis()
            signal_processing_demo()
            filter_optimization_demo()
        else:
            print("잘못된 선택입니다.")
    
    except KeyboardInterrupt:
        print("\n프로그램이 중단되었습니다.")
    except Exception as e:
        print(f"오류가 발생했습니다: {e}")
    
    print("\n프로그램을 종료합니다.")
