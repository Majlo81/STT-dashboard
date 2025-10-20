"""Alert system for critical metrics and anomalies."""

import pandas as pd
from typing import List, Dict, Any
from datetime import datetime
from dataclasses import dataclass
from enum import Enum


class AlertSeverity(Enum):
    """Alert severity levels."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class Alert:
    """Alert data structure."""
    severity: AlertSeverity
    category: str
    message: str
    call_id: str = None
    metric_value: float = None
    threshold: float = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'severity': self.severity.value,
            'category': self.category,
            'message': self.message,
            'call_id': self.call_id,
            'metric_value': self.metric_value,
            'threshold': self.threshold,
            'timestamp': self.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        }


class AlertSystem:
    """Alert system for monitoring call quality and performance."""
    
    def __init__(self):
        """Initialize alert system with default thresholds."""
        self.thresholds = {
            # Quality thresholds
            'quality_score_min': 0.8,
            'invalid_time_ratio_max': 0.1,
            'unknown_speaker_ratio_max': 0.05,
            
            # Language thresholds
            'vocabulary_richness_min': 0.3,
            'filler_rate_max': 0.05,  # 5%
            'agent_filler_rate_max': 0.03,  # 3% for agents
            
            # Interaction thresholds
            'interruption_rate_max': 0.8,  # 80%
            'agent_response_delay_max': 3.0,  # seconds
            'long_pauses_count_max': 5,
            'turn_balance_min': 0.3,
            
            # Duration thresholds
            'call_duration_min': 30,  # seconds
            'call_duration_max': 3600,  # 1 hour
        }
        
        self.alerts: List[Alert] = []
    
    def set_threshold(self, metric: str, value: float):
        """Update threshold for a metric."""
        self.thresholds[metric] = value
    
    def check_quality_alerts(
        self,
        quality_df: pd.DataFrame,
        calls_df: pd.DataFrame
    ) -> List[Alert]:
        """Check for quality-related alerts."""
        alerts = []
        
        for _, row in quality_df.iterrows():
            call_id = row['call_id']
            
            # Low quality score
            if row['quality_score'] < self.thresholds['quality_score_min']:
                alerts.append(Alert(
                    severity=AlertSeverity.WARNING,
                    category="Data Quality",
                    message=f"Low quality score detected",
                    call_id=call_id,
                    metric_value=row['quality_score'],
                    threshold=self.thresholds['quality_score_min']
                ))
            
            # High invalid time ratio
            if row['invalid_time_ratio'] > self.thresholds['invalid_time_ratio_max']:
                alerts.append(Alert(
                    severity=AlertSeverity.ERROR,
                    category="Data Quality",
                    message=f"High invalid timestamp ratio",
                    call_id=call_id,
                    metric_value=row['invalid_time_ratio'],
                    threshold=self.thresholds['invalid_time_ratio_max']
                ))
            
            # Unknown speakers
            if row['unknown_speaker_ratio'] > self.thresholds['unknown_speaker_ratio_max']:
                alerts.append(Alert(
                    severity=AlertSeverity.WARNING,
                    category="Data Quality",
                    message=f"High unknown speaker ratio",
                    call_id=call_id,
                    metric_value=row['unknown_speaker_ratio'],
                    threshold=self.thresholds['unknown_speaker_ratio_max']
                ))
        
        return alerts
    
    def check_language_alerts(
        self,
        text_stats_df: pd.DataFrame,
        filler_words_df: pd.DataFrame
    ) -> List[Alert]:
        """Check for language-related alerts."""
        alerts = []
        
        # Merge dataframes
        lang_df = text_stats_df.merge(filler_words_df, on='call_id')
        
        for _, row in lang_df.iterrows():
            call_id = row['call_id']
            
            # Low vocabulary richness
            if row['vocabulary_richness'] < self.thresholds['vocabulary_richness_min']:
                alerts.append(Alert(
                    severity=AlertSeverity.INFO,
                    category="Language Quality",
                    message=f"Low vocabulary richness",
                    call_id=call_id,
                    metric_value=row['vocabulary_richness'],
                    threshold=self.thresholds['vocabulary_richness_min']
                ))
            
            # High filler rate
            if row['filler_words_rate'] > self.thresholds['filler_rate_max']:
                alerts.append(Alert(
                    severity=AlertSeverity.WARNING,
                    category="Language Quality",
                    message=f"High filler words rate",
                    call_id=call_id,
                    metric_value=row['filler_words_rate'],
                    threshold=self.thresholds['filler_rate_max']
                ))
            
            # High agent filler rate
            if row['agent_filler_rate'] > self.thresholds['agent_filler_rate_max']:
                alerts.append(Alert(
                    severity=AlertSeverity.WARNING,
                    category="Agent Performance",
                    message=f"Agent using too many filler words",
                    call_id=call_id,
                    metric_value=row['agent_filler_rate'],
                    threshold=self.thresholds['agent_filler_rate_max']
                ))
        
        return alerts
    
    def check_interaction_alerts(
        self,
        interaction_df: pd.DataFrame
    ) -> List[Alert]:
        """Check for interaction pattern alerts."""
        alerts = []
        
        for _, row in interaction_df.iterrows():
            call_id = row['call_id']
            
            # High interruption rate
            if row['interruption_rate'] > self.thresholds['interruption_rate_max']:
                alerts.append(Alert(
                    severity=AlertSeverity.WARNING,
                    category="Interaction Quality",
                    message=f"High interruption rate",
                    call_id=call_id,
                    metric_value=row['interruption_rate'],
                    threshold=self.thresholds['interruption_rate_max']
                ))
            
            # Slow agent response
            if row['agent_avg_response_delay'] > self.thresholds['agent_response_delay_max']:
                alerts.append(Alert(
                    severity=AlertSeverity.WARNING,
                    category="Agent Performance",
                    message=f"Slow agent response time",
                    call_id=call_id,
                    metric_value=row['agent_avg_response_delay'],
                    threshold=self.thresholds['agent_response_delay_max']
                ))
            
            # Too many long pauses
            if row['long_pauses_count'] > self.thresholds['long_pauses_count_max']:
                alerts.append(Alert(
                    severity=AlertSeverity.INFO,
                    category="Interaction Quality",
                    message=f"Too many long pauses (awkward silence)",
                    call_id=call_id,
                    metric_value=row['long_pauses_count'],
                    threshold=self.thresholds['long_pauses_count_max']
                ))
            
            # Poor turn-taking balance
            if row['turn_taking_balance'] < self.thresholds['turn_balance_min']:
                alerts.append(Alert(
                    severity=AlertSeverity.INFO,
                    category="Interaction Quality",
                    message=f"Poor conversation balance (one-sided)",
                    call_id=call_id,
                    metric_value=row['turn_taking_balance'],
                    threshold=self.thresholds['turn_balance_min']
                ))
        
        return alerts
    
    def check_duration_alerts(
        self,
        call_metrics_df: pd.DataFrame
    ) -> List[Alert]:
        """Check for duration-related alerts."""
        alerts = []
        
        for _, row in call_metrics_df.iterrows():
            call_id = row['call_id']
            
            # Very short call
            if row['total_duration'] < self.thresholds['call_duration_min']:
                alerts.append(Alert(
                    severity=AlertSeverity.INFO,
                    category="Call Duration",
                    message=f"Very short call",
                    call_id=call_id,
                    metric_value=row['total_duration'],
                    threshold=self.thresholds['call_duration_min']
                ))
            
            # Very long call
            if row['total_duration'] > self.thresholds['call_duration_max']:
                alerts.append(Alert(
                    severity=AlertSeverity.WARNING,
                    category="Call Duration",
                    message=f"Unusually long call",
                    call_id=call_id,
                    metric_value=row['total_duration'],
                    threshold=self.thresholds['call_duration_max']
                ))
        
        return alerts
    
    def run_all_checks(
        self,
        calls_df: pd.DataFrame,
        call_metrics_df: pd.DataFrame,
        quality_metrics_df: pd.DataFrame,
        text_stats_df: pd.DataFrame,
        filler_words_df: pd.DataFrame,
        interaction_metrics_df: pd.DataFrame
    ) -> List[Alert]:
        """Run all alert checks and return consolidated list."""
        
        all_alerts = []
        
        all_alerts.extend(self.check_quality_alerts(quality_metrics_df, calls_df))
        all_alerts.extend(self.check_language_alerts(text_stats_df, filler_words_df))
        all_alerts.extend(self.check_interaction_alerts(interaction_metrics_df))
        all_alerts.extend(self.check_duration_alerts(call_metrics_df))
        
        # Sort by severity and timestamp
        severity_order = {
            AlertSeverity.CRITICAL: 0,
            AlertSeverity.ERROR: 1,
            AlertSeverity.WARNING: 2,
            AlertSeverity.INFO: 3
        }
        all_alerts.sort(key=lambda x: (severity_order[x.severity], x.timestamp), reverse=True)
        
        self.alerts = all_alerts
        return all_alerts
    
    def get_alert_summary(self) -> Dict[str, int]:
        """Get summary of alerts by severity."""
        summary = {
            'critical': 0,
            'error': 0,
            'warning': 0,
            'info': 0,
            'total': len(self.alerts)
        }
        
        for alert in self.alerts:
            summary[alert.severity.value] += 1
        
        return summary
    
    def get_alerts_by_category(self) -> Dict[str, List[Alert]]:
        """Group alerts by category."""
        by_category = {}
        for alert in self.alerts:
            if alert.category not in by_category:
                by_category[alert.category] = []
            by_category[alert.category].append(alert)
        return by_category
    
    def get_critical_calls(self, min_alerts: int = 3) -> List[str]:
        """Get call IDs with multiple alerts."""
        call_alert_counts = {}
        for alert in self.alerts:
            if alert.call_id:
                call_alert_counts[alert.call_id] = call_alert_counts.get(alert.call_id, 0) + 1
        
        return [
            call_id for call_id, count in call_alert_counts.items()
            if count >= min_alerts
        ]
