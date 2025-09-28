"""
KY-039 심박 센서 라이브러리 테스트 스크립트
ESP32 S3용 마이크로파이썬
원 저작자: COMPASS (만드는 놀이터 블로그)

이 스크립트는 라이브러리의 기본 기능들을 테스트합니다.
"""

def test_imports():
    """라이브러리 임포트 테스트"""
    print("=== 라이브러리 임포트 테스트 ===")
    
    try:
        from ky039_heartbeat import KY039Heartbeat
        print("✅ KY039Heartbeat 클래스 임포트 성공")
    except ImportError as e:
        print(f"❌ KY039Heartbeat 임포트 실패: {e}")
        return False
    
    try:
        from heartbeat_analyzer import HeartbeatAnalyzer, SignalProcessor
        print("✅ HeartbeatAnalyzer, SignalProcessor 클래스 임포트 성공")
    except ImportError as e:
        print(f"❌ 분석 모듈 임포트 실패: {e}")
        return False
    
    return True

def test_sensor_initialization():
    """센서 초기화 테스트"""
    print("\n=== 센서 초기화 테스트 ===")
    
    try:
        from ky039_heartbeat import KY039Heartbeat
        
        # 센서 초기화 (실제 하드웨어 없이도 테스트 가능)
        sensor = KY039Heartbeat(
            analog_pin=34,
            led_pin=2,
            sample_rate=100
        )
        print("✅ 센서 초기화 성공")
        
        # 설정값 확인
        print(f"  아날로그 핀: {sensor.analog_pin}")
        print(f"  LED 핀: {sensor.led_pin}")
        print(f"  샘플링 주파수: {sensor.sample_rate}Hz")
        print(f"  샘플 간격: {sensor.sample_interval:.3f}초")
        
        return True
        
    except Exception as e:
        print(f"❌ 센서 초기화 실패: {e}")
        return False

def test_analyzer_initialization():
    """분석기 초기화 테스트"""
    print("\n=== 분석기 초기화 테스트 ===")
    
    try:
        from heartbeat_analyzer import HeartbeatAnalyzer, SignalProcessor
        
        # 분석기 초기화
        analyzer = HeartbeatAnalyzer(window_size=5)
        print("✅ HeartbeatAnalyzer 초기화 성공")
        print(f"  윈도우 크기: {analyzer.window_size}")
        
        # 신호 처리기 테스트
        test_data = [1, 2, 3, 4, 5, 4, 3, 2, 1]
        
        # 이동 평균 테스트
        moving_avg = SignalProcessor.moving_average(test_data, 3)
        print(f"✅ 이동 평균 계산 성공: {moving_avg[:3]}...")
        
        # 중간값 필터 테스트
        median_filtered = SignalProcessor.median_filter(test_data, 3)
        print(f"✅ 중간값 필터 계산 성공: {median_filtered[:3]}...")
        
        # 정규화 테스트
        normalized = SignalProcessor.normalize_signal(test_data)
        print(f"✅ 신호 정규화 성공: {normalized[:3]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ 분석기 초기화 실패: {e}")
        return False

def test_heart_rate_zones():
    """심박수 구간 계산 테스트"""
    print("\n=== 심박수 구간 계산 테스트 ===")
    
    try:
        from heartbeat_analyzer import HeartbeatAnalyzer
        
        analyzer = HeartbeatAnalyzer()
        
        # 30세 기준 심박수 구간 계산
        zones = analyzer.get_heart_rate_zone(age=30)
        print("✅ 심박수 구간 계산 성공")
        
        print("  구간별 심박수 범위 (30세 기준):")
        for zone_name, (min_hr, max_hr) in zones.items():
            print(f"    {zone_name}: {min_hr:.0f} - {max_hr:.0f} BPM")
        
        # 현재 구간 테스트
        test_heart_rates = [60, 100, 120, 150, 180]
        print("\n  테스트 심박수별 구간:")
        for hr in test_heart_rates:
            zone = analyzer.get_current_zone(hr, age=30)
            print(f"    {hr} BPM → {zone}")
        
        return True
        
    except Exception as e:
        print(f"❌ 심박수 구간 계산 실패: {e}")
        return False

def test_signal_processing():
    """신호 처리 기능 테스트"""
    print("\n=== 신호 처리 기능 테스트 ===")
    
    try:
        from heartbeat_analyzer import SignalProcessor
        
        # 테스트 데이터 생성 (사인파 + 노이즈)
        import math
        test_data = []
        for i in range(50):
            value = 1000 + 200 * math.sin(i * 0.2) + (i % 3 - 1) * 10
            test_data.append(int(value))
        
        print(f"✅ 테스트 데이터 생성 완료 ({len(test_data)}개 샘플)")
        
        # 피크 감지 테스트
        peaks = SignalProcessor.find_peaks_advanced(test_data, min_distance=5)
        print(f"✅ 피크 감지 성공: {len(peaks)}개 피크 발견")
        
        # 미분 계산 테스트
        derivative_data = SignalProcessor.derivative(test_data)
        print(f"✅ 미분 계산 성공: {len(derivative_data)}개 값")
        
        # 통계 계산
        print(f"  원시 데이터 범위: {min(test_data)} - {max(test_data)}")
        print(f"  미분 데이터 범위: {min(derivative_data):.1f} - {max(derivative_data):.1f}")
        
        return True
        
    except Exception as e:
        print(f"❌ 신호 처리 테스트 실패: {e}")
        return False

def test_analyzer_functions():
    """분석기 기능 테스트"""
    print("\n=== 분석기 기능 테스트 ===")
    
    try:
        from heartbeat_analyzer import HeartbeatAnalyzer
        
        analyzer = HeartbeatAnalyzer(window_size=5)
        
        # 가상의 심박수 데이터 추가
        test_heart_rates = [70, 75, 72, 78, 80, 76, 74, 79, 77, 75]
        
        for i, hr in enumerate(test_heart_rates):
            analyzer.add_heart_rate(hr)
            print(f"  데이터 {i+1}: {hr} BPM 추가")
        
        # 통계 계산
        stats = analyzer.get_statistics()
        print(f"\n✅ 통계 계산 성공:")
        print(f"  측정 횟수: {stats['count']}")
        print(f"  평균: {stats['average']:.1f} BPM")
        print(f"  최소: {stats['min']:.1f} BPM")
        print(f"  최대: {stats['max']:.1f} BPM")
        print(f"  변이도: {stats['variability']:.1f}")
        
        # 이동 평균
        moving_avg = analyzer.get_moving_average()
        print(f"  이동 평균: {moving_avg:.1f} BPM")
        
        # 불규칙 리듬 감지
        is_irregular = analyzer.detect_irregular_rhythm(threshold=5)
        print(f"  불규칙 리듬: {'감지됨' if is_irregular else '정상'}")
        
        return True
        
    except Exception as e:
        print(f"❌ 분석기 기능 테스트 실패: {e}")
        return False

def run_all_tests():
    """모든 테스트 실행"""
    print("KY-039 심박 센서 라이브러리 테스트 시작")
    print("=" * 50)
    
    tests = [
        ("라이브러리 임포트", test_imports),
        ("센서 초기화", test_sensor_initialization),
        ("분석기 초기화", test_analyzer_initialization),
        ("심박수 구간 계산", test_heart_rate_zones),
        ("신호 처리 기능", test_signal_processing),
        ("분석기 기능", test_analyzer_functions)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                print(f"❌ {test_name} 테스트 실패")
        except Exception as e:
            print(f"❌ {test_name} 테스트 중 오류: {e}")
    
    print("\n" + "=" * 50)
    print(f"테스트 결과: {passed}/{total} 통과")
    
    if passed == total:
        print("🎉 모든 테스트가 성공적으로 완료되었습니다!")
        print("라이브러리가 정상적으로 작동합니다.")
    else:
        print("⚠️  일부 테스트가 실패했습니다.")
        print("라이브러리 설정을 확인해주세요.")
    
    return passed == total

if __name__ == "__main__":
    run_all_tests()
