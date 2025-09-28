"""
심박수 신호 분석을 위한 고급 알고리즘 모듈
ESP32 S3용 KY-039 심박 센서와 함께 사용
원 저작자: COMPASS (만드는 놀이터 블로그)
"""

import math
import time

class HeartbeatAnalyzer:
    """
    심박수 신호 분석을 위한 고급 클래스
    
    이 클래스는 심박 센서 데이터를 분석하고
    다양한 통계 정보를 제공합니다.
    """
    
    def __init__(self, window_size=10):
        """
        HeartbeatAnalyzer 초기화
        
        Args:
            window_size (int): 이동 평균 윈도우 크기
        """
        self.window_size = window_size
        self.heart_rate_history = []
        self.timestamp_history = []
        
    def add_heart_rate(self, heart_rate, timestamp=None):
        """
        심박수 데이터를 히스토리에 추가합니다.
        
        Args:
            heart_rate (float): 심박수 (BPM)
            timestamp (float, optional): 타임스탬프
        """
        if timestamp is None:
            timestamp = time.time()
        
        self.heart_rate_history.append(heart_rate)
        self.timestamp_history.append(timestamp)
        
        # 윈도우 크기 유지
        if len(self.heart_rate_history) > self.window_size:
            self.heart_rate_history.pop(0)
            self.timestamp_history.pop(0)
    
    def get_moving_average(self):
        """
        이동 평균 심박수를 계산합니다.
        
        Returns:
            float: 이동 평균 심박수
        """
        if not self.heart_rate_history:
            return 0
        
        return sum(self.heart_rate_history) / len(self.heart_rate_history)
    
    def get_heart_rate_variability(self):
        """
        심박 변이도(HRV)를 계산합니다.
        
        Returns:
            float: 심박 변이도
        """
        if len(self.heart_rate_history) < 2:
            return 0
        
        # 연속된 심박수 간의 차이 계산
        differences = []
        for i in range(1, len(self.heart_rate_history)):
            diff = abs(self.heart_rate_history[i] - self.heart_rate_history[i-1])
            differences.append(diff)
        
        # 평균 차이 계산
        if differences:
            return sum(differences) / len(differences)
        return 0
    
    def detect_irregular_rhythm(self, threshold=10):
        """
        불규칙한 심박 리듬을 감지합니다.
        
        Args:
            threshold (float): 불규칙성 임계값
            
        Returns:
            bool: 불규칙한 리듬이 감지되면 True
        """
        hrv = self.get_heart_rate_variability()
        return hrv > threshold
    
    def get_heart_rate_zone(self, age=30):
        """
        심박수 구간을 계산합니다.
        
        Args:
            age (int): 나이
            
        Returns:
            dict: 각 구간별 심박수 범위
        """
        max_hr = 220 - age
        
        zones = {
            'recovery': (max_hr * 0.5, max_hr * 0.6),
            'aerobic': (max_hr * 0.6, max_hr * 0.7),
            'threshold': (max_hr * 0.7, max_hr * 0.8),
            'lactate': (max_hr * 0.8, max_hr * 0.9),
            'neuromuscular': (max_hr * 0.9, max_hr * 1.0)
        }
        
        return zones
    
    def get_current_zone(self, current_hr, age=30):
        """
        현재 심박수가 속하는 구간을 반환합니다.
        
        Args:
            current_hr (float): 현재 심박수
            age (int): 나이
            
        Returns:
            str: 현재 구간 이름
        """
        zones = self.get_heart_rate_zone(age)
        
        for zone_name, (min_hr, max_hr) in zones.items():
            if min_hr <= current_hr <= max_hr:
                return zone_name
        
        return 'unknown'
    
    def get_statistics(self):
        """
        심박수 통계 정보를 반환합니다.
        
        Returns:
            dict: 통계 정보 딕셔너리
        """
        if not self.heart_rate_history:
            return {
                'count': 0,
                'average': 0,
                'min': 0,
                'max': 0,
                'variability': 0
            }
        
        return {
            'count': len(self.heart_rate_history),
            'average': sum(self.heart_rate_history) / len(self.heart_rate_history),
            'min': min(self.heart_rate_history),
            'max': max(self.heart_rate_history),
            'variability': self.get_heart_rate_variability()
        }
    
    def clear_history(self):
        """심박수 히스토리를 초기화합니다."""
        self.heart_rate_history = []
        self.timestamp_history = []
        print("심박수 히스토리가 초기화되었습니다")

class SignalProcessor:
    """
    신호 처리를 위한 유틸리티 클래스
    """
    
    @staticmethod
    def moving_average(data, window_size):
        """
        이동 평균을 계산합니다.
        
        Args:
            data (list): 입력 데이터
            window_size (int): 윈도우 크기
            
        Returns:
            list: 이동 평균 결과
        """
        if len(data) < window_size:
            return data
        
        result = []
        for i in range(len(data)):
            start = max(0, i - window_size + 1)
            window_data = data[start:i+1]
            result.append(sum(window_data) / len(window_data))
        
        return result
    
    @staticmethod
    def median_filter(data, window_size=3):
        """
        중간값 필터를 적용합니다.
        
        Args:
            data (list): 입력 데이터
            window_size (int): 윈도우 크기
            
        Returns:
            list: 필터링된 데이터
        """
        if len(data) < window_size:
            return data
        
        result = []
        for i in range(len(data)):
            start = max(0, i - window_size // 2)
            end = min(len(data), i + window_size // 2 + 1)
            window_data = sorted(data[start:end])
            median = window_data[len(window_data) // 2]
            result.append(median)
        
        return result
    
    @staticmethod
    def derivative(data):
        """
        데이터의 미분을 계산합니다.
        
        Args:
            data (list): 입력 데이터
            
        Returns:
            list: 미분 결과
        """
        if len(data) < 2:
            return [0]
        
        result = [0]  # 첫 번째 값은 0
        for i in range(1, len(data)):
            result.append(data[i] - data[i-1])
        
        return result
    
    @staticmethod
    def find_peaks_advanced(data, min_height=None, min_distance=1):
        """
        고급 피크 감지 알고리즘
        
        Args:
            data (list): 입력 데이터
            min_height (float, optional): 최소 피크 높이
            min_distance (int): 피크 간 최소 거리
            
        Returns:
            list: 피크 인덱스 리스트
        """
        if len(data) < 3:
            return []
        
        # 동적 임계값 설정
        if min_height is None:
            max_val = max(data)
            min_val = min(data)
            min_height = min_val + (max_val - min_val) * 0.3
        
        peaks = []
        for i in range(1, len(data) - 1):
            if (data[i] > data[i-1] and 
                data[i] > data[i+1] and 
                data[i] > min_height):
                
                # 최소 거리 확인
                if not peaks or i - peaks[-1] >= min_distance:
                    peaks.append(i)
        
        return peaks
    
    @staticmethod
    def normalize_signal(data):
        """
        신호를 정규화합니다 (0-1 범위).
        
        Args:
            data (list): 입력 데이터
            
        Returns:
            list: 정규화된 데이터
        """
        if not data:
            return data
        
        min_val = min(data)
        max_val = max(data)
        
        if max_val == min_val:
            return [0.5] * len(data)
        
        return [(x - min_val) / (max_val - min_val) for x in data]
