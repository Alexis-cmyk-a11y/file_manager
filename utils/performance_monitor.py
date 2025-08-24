"""
性能监控模块
提供函数性能监控、性能分析和优化建议
"""

import time
import functools
import statistics
from typing import Dict, List, Any, Optional, Callable
from collections import defaultdict, deque
from datetime import datetime, timedelta
from utils.logger import get_logger

logger = get_logger(__name__)

class PerformanceMonitor:
    """性能监控器"""
    
    def __init__(self):
        self.metrics = defaultdict(list)
        self.function_stats = defaultdict(lambda: {
            'calls': 0,
            'total_time': 0.0,
            'min_time': float('inf'),
            'max_time': 0.0,
            'recent_times': deque(maxlen=100)  # 最近100次调用的时间
        })
        self.slow_threshold = 1.0  # 慢函数阈值（秒）
        self.enabled = True
    
    def record_metric(self, function_name: str, duration: float, success: bool = True, **kwargs):
        """记录性能指标"""
        if not self.enabled:
            return
        
        try:
            # 记录基本指标
            self.metrics[function_name].append({
                'timestamp': datetime.now(),
                'duration': duration,
                'success': success,
                **kwargs
            })
            
            # 更新函数统计
            stats = self.function_stats[function_name]
            stats['calls'] += 1
            stats['total_time'] += duration
            stats['min_time'] = min(stats['min_time'], duration)
            stats['max_time'] = max(stats['max_time'], duration)
            stats['recent_times'].append(duration)
            
            # 记录慢函数
            if duration > self.slow_threshold:
                logger.warning(
                    f"检测到慢函数: {function_name}",
                    function=function_name,
                    duration_seconds=round(duration, 3),
                    threshold_seconds=self.slow_threshold,
                    **kwargs
                )
            
            # 记录失败的函数调用
            if not success:
                logger.error(
                    f"函数执行失败: {function_name}",
                    function=function_name,
                    duration_seconds=round(duration, 3),
                    **kwargs
                )
                
        except Exception as e:
            logger.error(f"记录性能指标失败: {function_name}, 错误: {e}")
    
    def get_function_stats(self, function_name: str) -> Dict[str, Any]:
        """获取函数统计信息"""
        if function_name not in self.function_stats:
            return {}
        
        stats = self.function_stats[function_name]
        if stats['calls'] == 0:
            return {}
        
        recent_times = list(stats['recent_times'])
        
        return {
            'function_name': function_name,
            'total_calls': stats['calls'],
            'total_time': stats['total_time'],
            'average_time': stats['total_time'] / stats['calls'],
            'min_time': stats['min_time'] if stats['min_time'] != float('inf') else 0,
            'max_time': stats['max_time'],
            'recent_average': statistics.mean(recent_times) if recent_times else 0,
            'recent_median': statistics.median(recent_times) if recent_times else 0,
            'recent_std': statistics.stdev(recent_times) if len(recent_times) > 1 else 0,
            'calls_per_minute': self._calculate_calls_per_minute(function_name)
        }
    
    def get_all_stats(self) -> Dict[str, Any]:
        """获取所有函数统计信息"""
        all_stats = {}
        for function_name in self.function_stats:
            all_stats[function_name] = self.get_function_stats(function_name)
        return all_stats
    
    def get_slow_functions(self, threshold: Optional[float] = None) -> List[Dict[str, Any]]:
        """获取慢函数列表"""
        if threshold is None:
            threshold = self.slow_threshold
        
        slow_functions = []
        for function_name, stats in self.function_stats.items():
            if stats['calls'] > 0:
                avg_time = stats['total_time'] / stats['calls']
                if avg_time > threshold:
                    slow_functions.append({
                        'function_name': function_name,
                        'average_time': avg_time,
                        'total_calls': stats['calls'],
                        'total_time': stats['total_time']
                    })
        
        # 按平均时间排序
        slow_functions.sort(key=lambda x: x['average_time'], reverse=True)
        return slow_functions
    
    def get_performance_report(self) -> Dict[str, Any]:
        """生成性能报告"""
        try:
            all_stats = self.get_all_stats()
            slow_functions = self.get_slow_functions()
            
            # 计算总体统计
            total_calls = sum(stats['total_calls'] for stats in all_stats.values())
            total_time = sum(stats['total_time'] for stats in all_stats.values())
            
            report = {
                'timestamp': datetime.now().isoformat(),
                'summary': {
                    'total_functions': len(all_stats),
                    'total_calls': total_calls,
                    'total_time': total_time,
                    'average_time_per_call': total_time / total_calls if total_calls > 0 else 0
                },
                'slow_functions': slow_functions,
                'function_details': all_stats,
                'recommendations': self._generate_recommendations(all_stats, slow_functions)
            }
            
            return report
            
        except Exception as e:
            logger.error(f"生成性能报告失败: {e}")
            return {'error': str(e)}
    
    def _calculate_calls_per_minute(self, function_name: str) -> float:
        """计算每分钟调用次数"""
        try:
            recent_metrics = [m for m in self.metrics[function_name] 
                            if m['timestamp'] > datetime.now() - timedelta(minutes=1)]
            return len(recent_metrics)
        except Exception:
            return 0.0
    
    def _generate_recommendations(self, all_stats: Dict, slow_functions: List) -> List[str]:
        """生成性能优化建议"""
        recommendations = []
        
        # 基于慢函数的建议
        for func in slow_functions:
            if func['average_time'] > 5.0:
                recommendations.append(f"函数 {func['function_name']} 平均执行时间过长({func['average_time']:.2f}s)，建议优化算法或添加缓存")
            elif func['average_time'] > 1.0:
                recommendations.append(f"函数 {func['function_name']} 执行时间较长({func['average_time']:.2f}s)，建议检查是否有优化空间")
        
        # 基于调用频率的建议
        for func_name, stats in all_stats.items():
            if stats['calls_per_minute'] > 100:
                recommendations.append(f"函数 {func_name} 调用频率很高({stats['calls_per_minute']}/分钟)，建议检查是否有重复调用")
        
        # 基于时间分布的建议
        for func_name, stats in all_stats.items():
            if stats['recent_std'] > stats['recent_average'] * 0.5:
                recommendations.append(f"函数 {func_name} 执行时间波动较大，建议检查输入数据的一致性")
        
        return recommendations
    
    def reset_stats(self, function_name: Optional[str] = None):
        """重置统计信息"""
        if function_name:
            if function_name in self.function_stats:
                self.function_stats[function_name] = {
                    'calls': 0,
                    'total_time': 0.0,
                    'min_time': float('inf'),
                    'max_time': 0.0,
                    'recent_times': deque(maxlen=100)
                }
            if function_name in self.metrics:
                self.metrics[function_name].clear()
        else:
            self.function_stats.clear()
            self.metrics.clear()
        
        logger.info(f"性能统计已重置: {function_name or '所有函数'}")

# 全局性能监控器实例
_performance_monitor = None

def get_performance_monitor() -> PerformanceMonitor:
    """获取性能监控器实例"""
    global _performance_monitor
    if _performance_monitor is None:
        _performance_monitor = PerformanceMonitor()
    return _performance_monitor

def performance_monitor(func: Optional[Callable] = None, 
                       slow_threshold: Optional[float] = None,
                       log_args: bool = False,
                       log_result: bool = False):
    """性能监控装饰器
    
    Args:
        func: 被装饰的函数
        slow_threshold: 慢函数阈值（秒）
        log_args: 是否记录函数参数
        log_result: 是否记录函数结果
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            monitor = get_performance_monitor()
            
            # 记录开始时间
            start_time = time.time()
            
            # 记录函数参数（如果需要）
            extra_info = {}
            if log_args:
                try:
                    # 只记录前几个参数，避免记录过大的对象
                    args_repr = [repr(arg)[:100] for arg in args[:3]]
                    kwargs_repr = {k: repr(v)[:100] for k, v in list(kwargs.items())[:5]}
                    extra_info['args'] = args_repr
                    extra_info['kwargs'] = kwargs_repr
                except Exception:
                    pass
            
            try:
                # 执行函数
                result = func(*args, **kwargs)
                
                # 计算执行时间
                duration = time.time() - start_time
                
                # 记录成功指标
                monitor.record_metric(
                    func.__name__, 
                    duration, 
                    success=True,
                    **extra_info
                )
                
                # 记录函数结果（如果需要）
                if log_result:
                    try:
                        result_repr = repr(result)[:200]
                        extra_info['result'] = result_repr
                    except Exception:
                        pass
                
                return result
                
            except Exception as e:
                # 计算执行时间
                duration = time.time() - start_time
                
                # 记录失败指标
                monitor.record_metric(
                    func.__name__, 
                    duration, 
                    success=False,
                    error=str(e),
                    error_type=type(e).__name__,
                    **extra_info
                )
                
                # 重新抛出异常
                raise
        
        return wrapper
    
    # 处理装饰器的不同使用方式
    if func is None:
        return decorator
    else:
        return decorator(func)

def monitor_performance(func_name: Optional[str] = None, 
                       slow_threshold: Optional[float] = None,
                       log_args: bool = False,
                       log_result: bool = False):
    """性能监控装饰器的别名，用于更清晰的语义"""
    return performance_monitor(
        func=func_name,
        slow_threshold=slow_threshold,
        log_args=log_args,
        log_result=log_result
    )

# 便捷的装饰器函数
def monitor_slow_functions(threshold: float = 1.0):
    """监控慢函数的装饰器"""
    return performance_monitor(slow_threshold=threshold)

def monitor_with_args():
    """监控函数参数和结果的装饰器"""
    return performance_monitor(log_args=True, log_result=True)

def monitor_critical_functions():
    """监控关键函数的装饰器"""
    return performance_monitor(log_args=True, log_result=True, slow_threshold=0.1)
