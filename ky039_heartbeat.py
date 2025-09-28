"""
ESP32 S3용 심박 센서 KY-039 마이크로파이썬 라이브러리
원 저작자: COMPASS (만드는 놀이터 블로그)
작성자: ESP32 개발팀
버전: 1.0.0
"""

import time
import math
from machine import Pin, ADC

class KY039Heartbeat:
    """
    KY-039 심박 센서를 위한 마이크로파이썬 클래스
    
    이 클래스는 ESP32 S3에서 KY-039 심박 센서를 사용하여
    심박수를 측정하고 분석하는 기능을 제공합니다.
    """
    
    def __init__(self, analog_pin, led_pin=None, sample_rate=100):
        """
        KY039Heartbeat 클래스 초기화
        
        Args:
            analog_pin (int): 아날로그 입력 핀 번호
            led_pin (int, optional): LED 핀 번호 (센서 내장 LED 제어용)
            sample_rate (int): 샘플링 주파수 (Hz, 기본값: 100)
        """
        self.analog_pin = analog_pin
        self.led_pin = led_pin
        self.sample_rate = sample_rate
        self.sample_interval = 1.0 / sample_rate
        
        # ADC 초기화
        self.adc = ADC(Pin(analog_pin))
        self.adc.atten(ADC.ATTN_11DB)  # 0-3.3V 범위
        
        # LED 핀 초기화 (선택사항)
        if led_pin is not None:
            self.led = Pin(led_pin, Pin.OUT)
            self.led.off()
        else:
            self.led = None
        
        # 심박수 측정을 위한 변수들
        self.raw_values = []
        self.filtered_values = []
        self.peak_times = []
        self.heart_rate = 0
        self.is_measuring = False
        
        # 필터링을 위한 변수들
        self.alpha = 0.8  # 저역통과 필터 계수
        self.previous_filtered = 0
        
        print("KY-039 심박 센서 초기화 완료")
        print(f"아날로그 핀: {analog_pin}")
        print(f"샘플링 주파수: {sample_rate}Hz")
        if led_pin:
            print(f"LED 핀: {led_pin}")
    
    def read_raw_value(self):
        """
        센서에서 원시 아날로그 값을 읽어옵니다.
        
        Returns:
            int: 0-4095 범위의 ADC 값
        """
        return self.adc.read()
    
    def apply_low_pass_filter(self, raw_value):
        """
        저역통과 필터를 적용하여 노이즈를 제거합니다.
        
        Args:
            raw_value (int): 원시 센서 값
            
        Returns:
            float: 필터링된 값
        """
        filtered = self.alpha * self.previous_filtered + (1 - self.alpha) * raw_value
        self.previous_filtered = filtered
        return filtered
    
    def detect_peaks(self, values, threshold_factor=0.6):
        """
        신호에서 피크를 감지합니다.
        
        Args:
            values (list): 필터링된 신호 값들
            threshold_factor (float): 피크 감지 임계값 계수
            
        Returns:
            list: 피크 인덱스 리스트
        """
        if len(values) < 3:
            return []
        
        # 신호의 최대값과 최소값을 이용한 동적 임계값 설정
        max_val = max(values)
        min_val = min(values)
        threshold = min_val + (max_val - min_val) * threshold_factor
        
        peaks = []
        for i in range(1, len(values) - 1):
            if (values[i] > values[i-1] and 
                values[i] > values[i+1] and 
                values[i] > threshold):
                peaks.append(i)
        
        return peaks
    
    def calculate_heart_rate(self, peak_times, measurement_duration):
        """
        피크 시간들을 이용하여 심박수를 계산합니다.
        
        Args:
            peak_times (list): 피크 발생 시간들
            measurement_duration (float): 측정 지속 시간 (초)
            
        Returns:
            float: 분당 심박수 (BPM)
        """
        if len(peak_times) < 2:
            return 0
        
        # 연속된 피크들 사이의 평균 간격 계산
        intervals = []
        for i in range(1, len(peak_times)):
            interval = peak_times[i] - peak_times[i-1]
            if interval > 0.3:  # 최소 0.3초 간격 (최대 200 BPM)
                intervals.append(interval)
        
        if not intervals:
            return 0
        
        # 평균 간격으로 심박수 계산
        avg_interval = sum(intervals) / len(intervals)
        heart_rate = 60.0 / avg_interval
        
        return heart_rate
    
    def start_measurement(self, duration=10):
        """
        심박수 측정을 시작합니다.
        
        Args:
            duration (int): 측정 지속 시간 (초, 기본값: 10)
            
        Returns:
            float: 측정된 심박수 (BPM)
        """
        print(f"심박수 측정 시작 - {duration}초간 측정")
        
        self.is_measuring = True
        self.raw_values = []
        self.filtered_values = []
        self.peak_times = []
        
        start_time = time.time()
        sample_count = 0
        
        # LED 켜기 (센서 내장 LED가 있는 경우)
        if self.led:
            self.led.on()
        
        try:
            while time.time() - start_time < duration and self.is_measuring:
                # 원시 값 읽기
                raw_value = self.read_raw_value()
                self.raw_values.append(raw_value)
                
                # 필터링 적용
                filtered_value = self.apply_low_pass_filter(raw_value)
                self.filtered_values.append(filtered_value)
                
                sample_count += 1
                
                # 샘플링 주파수 유지
                time.sleep(self.sample_interval)
                
                # 진행 상황 표시 (매 1초마다)
                if sample_count % self.sample_rate == 0:
                    elapsed = time.time() - start_time
                    print(f"측정 진행: {elapsed:.1f}초 / {duration}초")
        
        except KeyboardInterrupt:
            print("측정이 중단되었습니다")
        
        finally:
            # LED 끄기
            if self.led:
                self.led.off()
            
            self.is_measuring = False
        
        print("측정 완료, 데이터 분석 중...")
        
        # 피크 감지
        peaks = self.detect_peaks(self.filtered_values)
        
        # 피크 시간 계산
        for peak_index in peaks:
            peak_time = peak_index * self.sample_interval
            self.peak_times.append(peak_time)
        
        # 심박수 계산
        self.heart_rate = self.calculate_heart_rate(self.peak_times, duration)
        
        print(f"감지된 피크 수: {len(peaks)}")
        print(f"측정된 심박수: {self.heart_rate:.1f} BPM")
        
        return self.heart_rate
    
    def stop_measurement(self):
        """심박수 측정을 중단합니다."""
        self.is_measuring = False
        print("측정 중단됨")
    
    def get_heart_rate(self):
        """
        마지막으로 측정된 심박수를 반환합니다.
        
        Returns:
            float: 심박수 (BPM)
        """
        return self.heart_rate
    
    def get_raw_data(self):
        """
        원시 센서 데이터를 반환합니다.
        
        Returns:
            list: 원시 센서 값 리스트
        """
        return self.raw_values
    
    def get_filtered_data(self):
        """
        필터링된 센서 데이터를 반환합니다.
        
        Returns:
            list: 필터링된 센서 값 리스트
        """
        return self.filtered_values
    
    def get_peak_times(self):
        """
        피크 발생 시간들을 반환합니다.
        
        Returns:
            list: 피크 시간 리스트
        """
        return self.peak_times
    
    def calibrate_sensor(self, duration=5):
        """
        센서를 캘리브레이션합니다.
        
        Args:
            duration (int): 캘리브레이션 지속 시간 (초)
            
        Returns:
            tuple: (최소값, 최대값, 평균값)
        """
        print(f"센서 캘리브레이션 시작 - {duration}초간")
        
        values = []
        start_time = time.time()
        
        while time.time() - start_time < duration:
            value = self.read_raw_value()
            values.append(value)
            time.sleep(0.1)
        
        min_val = min(values)
        max_val = max(values)
        avg_val = sum(values) / len(values)
        
        print(f"캘리브레이션 완료:")
        print(f"  최소값: {min_val}")
        print(f"  최대값: {max_val}")
        print(f"  평균값: {avg_val:.1f}")
        
        return min_val, max_val, avg_val
    
    def set_filter_alpha(self, alpha):
        """
        저역통과 필터의 알파 값을 설정합니다.
        
        Args:
            alpha (float): 필터 계수 (0.0 ~ 1.0)
        """
        if 0.0 <= alpha <= 1.0:
            self.alpha = alpha
            print(f"필터 알파 값이 {alpha}로 설정되었습니다")
        else:
            print("알파 값은 0.0과 1.0 사이여야 합니다")
    
    def set_sample_rate(self, rate):
        """
        샘플링 주파수를 설정합니다.
        
        Args:
            rate (int): 샘플링 주파수 (Hz)
        """
        if rate > 0:
            self.sample_rate = rate
            self.sample_interval = 1.0 / rate
            print(f"샘플링 주파수가 {rate}Hz로 설정되었습니다")
        else:
            print("샘플링 주파수는 0보다 커야 합니다")
