"""Metric registry system for extensibility."""

from typing import Dict, Callable, Any, List
from dataclasses import dataclass
from loguru import logger


@dataclass
class MetricDefinition:
    """Definition of a metric."""
    name: str
    version: str
    category: str  # 'call', 'speaker', 'quality'
    compute_func: Callable
    description: str
    inputs: List[str]
    outputs: List[str]
    units: Dict[str, str]


class MetricRegistry:
    """Registry for metric computation functions."""
    
    def __init__(self):
        self._metrics: Dict[str, MetricDefinition] = {}
    
    def register(
        self,
        name: str,
        version: str,
        category: str,
        compute_func: Callable,
        description: str,
        inputs: List[str],
        outputs: List[str],
        units: Dict[str, str] = None
    ) -> None:
        """
        Register a metric.
        
        Args:
            name: Metric name (unique identifier)
            version: Metric version (for tracking changes)
            category: Category (call, speaker, quality)
            compute_func: Function that computes the metric
            description: Human-readable description
            inputs: Required input data (e.g., 'utterances_df', 'timeline_stats')
            outputs: Output field names
            units: Units for each output field
        """
        if name in self._metrics:
            logger.warning(f"Overwriting existing metric: {name}")
        
        metric_def = MetricDefinition(
            name=name,
            version=version,
            category=category,
            compute_func=compute_func,
            description=description,
            inputs=inputs,
            outputs=outputs,
            units=units or {}
        )
        
        self._metrics[name] = metric_def
        logger.debug(f"Registered metric: {name} v{version}")
    
    def get(self, name: str) -> MetricDefinition:
        """Get metric definition by name."""
        if name not in self._metrics:
            raise KeyError(f"Metric not found: {name}")
        return self._metrics[name]
    
    def list_metrics(self, category: str = None) -> List[MetricDefinition]:
        """
        List registered metrics.
        
        Args:
            category: Filter by category (optional)
            
        Returns:
            List of metric definitions
        """
        metrics = list(self._metrics.values())
        
        if category:
            metrics = [m for m in metrics if m.category == category]
        
        return metrics
    
    def compute(
        self,
        name: str,
        **kwargs
    ) -> Any:
        """
        Compute a metric by name.
        
        Args:
            name: Metric name
            **kwargs: Input data for metric computation
            
        Returns:
            Metric result
        """
        metric_def = self.get(name)
        
        # Validate inputs
        missing = set(metric_def.inputs) - set(kwargs.keys())
        if missing:
            raise ValueError(
                f"Missing required inputs for metric '{name}': {missing}"
            )
        
        # Compute
        try:
            result = metric_def.compute_func(**kwargs)
            return result
        except Exception as e:
            logger.error(f"Error computing metric '{name}': {e}")
            raise


# Global registry instance
_global_registry = MetricRegistry()


def get_global_registry() -> MetricRegistry:
    """Get the global metric registry."""
    return _global_registry


def register_core_metrics():
    """Register all core metrics."""
    from .call_level import compute_call_metrics
    from .speaker_level import compute_speaker_metrics
    from .quality import compute_quality_metrics
    from .text_analysis import compute_text_statistics, compute_filler_words
    from .interaction_patterns import compute_interaction_metrics
    
    registry = get_global_registry()
    
    # Call-level metrics
    registry.register(
        name='call_metrics',
        version='1.0.0',
        category='call',
        compute_func=compute_call_metrics,
        description='Comprehensive call-level metrics',
        inputs=['call_id', 'utterances_df', 'timeline_stats'],
        outputs=[
            'total_duration', 'speech_time', 'silence_time', 'overlap_time',
            'silence_ratio', 'speech_ratio', 'overlap_ratio',
            'total_utterances', 'valid_utterances', 'speaker_switches',
            'interruptions_total'
        ],
        units={
            'total_duration': 's',
            'speech_time': 's',
            'silence_time': 's',
            'overlap_time': 's',
            'silence_ratio': 'ratio',
            'speech_ratio': 'ratio',
            'overlap_ratio': 'ratio'
        }
    )
    
    # Speaker-level metrics
    registry.register(
        name='speaker_metrics',
        version='1.0.0',
        category='speaker',
        compute_func=compute_speaker_metrics,
        description='Speaker-level metrics',
        inputs=['call_id', 'utterances_df', 'timeline_stats'],
        outputs=[
            'raw_speaking_time', 'apportioned_speaking_time',
            'turn_count', 'words_per_minute', 'dialog_balance_gini'
        ],
        units={
            'raw_speaking_time': 's',
            'apportioned_speaking_time': 's',
            'words_per_minute': 'wpm',
            'dialog_balance_gini': 'ratio'
        }
    )
    
    # Quality metrics
    registry.register(
        name='quality_metrics',
        version='1.0.0',
        category='quality',
        compute_func=compute_quality_metrics,
        description='Data quality and health metrics',
        inputs=['call_id', 'utterances_df', 'call_duration_meta', 'timeline_stats'],
        outputs=[
            'invalid_time_ratio', 'unknown_speaker_ratio',
            'empty_text_ratio', 'quality_score'
        ],
        units={
            'invalid_time_ratio': 'ratio',
            'unknown_speaker_ratio': 'ratio',
            'empty_text_ratio': 'ratio',
            'quality_score': 'score'
        }
    )
    
    # Text analysis metrics
    registry.register(
        name='text_statistics',
        version='1.0.0',
        category='text',
        compute_func=compute_text_statistics,
        description='Text-based statistics and linguistic patterns',
        inputs=['utterances_df', 'call_id'],
        outputs=[
            'unique_words_count', 'vocabulary_richness', 'avg_sentence_length',
            'question_count', 'exclamation_count', 'agent_questions', 'customer_questions'
        ],
        units={
            'vocabulary_richness': 'ratio',
            'avg_sentence_length': 'words'
        }
    )
    
    registry.register(
        name='filler_words',
        version='1.0.0',
        category='text',
        compute_func=compute_filler_words,
        description='Filler word detection and analysis',
        inputs=['utterances_df', 'call_id'],
        outputs=[
            'filler_words_total', 'filler_words_rate',
            'agent_filler_rate', 'customer_filler_rate'
        ],
        units={
            'filler_words_rate': 'ratio',
            'agent_filler_rate': 'ratio',
            'customer_filler_rate': 'ratio'
        }
    )
    
    # Interaction pattern metrics
    registry.register(
        name='interaction_metrics',
        version='1.0.0',
        category='interaction',
        compute_func=compute_interaction_metrics,
        description='Conversation flow and interaction patterns',
        inputs=['utterances_df', 'call_id'],
        outputs=[
            'long_pauses_count', 'interruption_rate', 'agent_avg_response_delay',
            'customer_avg_response_delay', 'monologue_segments', 'turn_taking_balance'
        ],
        units={
            'interruption_rate': 'ratio',
            'agent_avg_response_delay': 's',
            'customer_avg_response_delay': 's',
            'turn_taking_balance': 'ratio'
        }
    )
    
    logger.info(f"Registered {len(registry.list_metrics())} core metrics")
