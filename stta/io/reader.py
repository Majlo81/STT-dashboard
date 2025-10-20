"""
Robust CSV reader with encoding detection and error handling.

Handles:
- Multiple encodings (UTF-8-sig, CP1250, Latin-1)
- Semicolon delimiter
- Two-tier structure (metadata row + utterance rows)
- Missing/malformed data
"""

import pandas as pd
from pathlib import Path
from typing import Tuple, List, Dict, Any, Optional
from loguru import logger
from datetime import datetime
import yaml

from ..utils.timecode import parse_timecode, validate_time_range
from ..utils.text import count_words, count_chars, normalize_text, is_empty_text


class CSVReader:
    """Robust CSV reader with deterministic fallback logic."""
    
    def __init__(
        self,
        encodings: List[str] = None,
        delimiter: str = ";",
        speaker_mapping: Dict[str, str] = None
    ):
        """
        Initialize CSV reader.
        
        Args:
            encodings: List of encodings to try (in order)
            delimiter: CSV delimiter
            speaker_mapping: Mapping of raw speaker labels to normalized
        """
        self.encodings = encodings or ["utf-8-sig", "cp1250", "latin-1"]
        self.delimiter = delimiter
        self.speaker_mapping = speaker_mapping or {}
        self.default_speaker = "UNKNOWN"
    
    def read_csv_file(
        self,
        file_path: Path,
        config: Dict[str, Any]
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Read CSV file and split into calls and utterances.
        
        Args:
            file_path: Path to CSV file
            config: Configuration dict with field mappings
            
        Returns:
            (calls_df, utterances_df) tuple
            
        Raises:
            ValueError: If file cannot be parsed
        """
        logger.info(f"Reading CSV: {file_path}")
        
        # Try encodings in order
        df_raw = None
        encoding_used = None
        
        for encoding in self.encodings:
            try:
                df_raw = pd.read_csv(
                    file_path,
                    sep=self.delimiter,
                    dtype=str,
                    keep_default_na=False,
                    encoding=encoding,
                    on_bad_lines='warn'
                )
                encoding_used = encoding
                logger.debug(f"Successfully read with encoding: {encoding}")
                break
            except UnicodeDecodeError:
                logger.debug(f"Failed with encoding: {encoding}")
                continue
            except Exception as e:
                logger.error(f"Unexpected error with encoding {encoding}: {e}")
                continue
        
        if df_raw is None:
            raise ValueError(f"Could not read CSV with any encoding: {file_path}")
        
        # Validate non-empty
        if df_raw.empty:
            raise ValueError(f"CSV file is empty: {file_path}")
        
        logger.info(f"Read {len(df_raw)} rows with encoding {encoding_used}")
        
        # Apply column mapping if configured
        column_mapping = config.get('column_mapping', {})
        if column_mapping:
            df_raw = df_raw.rename(columns=column_mapping)
            logger.debug(f"Applied column mapping: {len(column_mapping)} columns renamed")
        
        # Detect multi-call format: rows with metadata = new calls, empty rows = utterances
        # Check if we have a timestamp column that indicates call boundaries
        timestamp_col = df_raw.columns[0] if len(df_raw.columns) > 0 else None
        
        # Detect if this is a multi-call CSV (metadata rows + utterance rows pattern)
        # Note: empty values are '' (empty strings), not NaN
        if timestamp_col:
            filled_rows = (df_raw[timestamp_col] != '') & (df_raw[timestamp_col].notna())
            empty_rows = (df_raw[timestamp_col] == '') | (df_raw[timestamp_col].isna())
            has_metadata_pattern = (filled_rows.sum() > 1 and empty_rows.sum() > 0)
        else:
            has_metadata_pattern = False
        
        if has_metadata_pattern:
            logger.debug("Detected multi-call CSV format (metadata rows separate calls)")
            return self._parse_multi_call_csv(df_raw, file_path, config)
        else:
            logger.debug("Detected single-call CSV format")
            # Traditional format: single call
            if len(df_raw) < 2:
                logger.warning(f"CSV has only {len(df_raw)} row(s), treating as metadata only")
                calls_df = self._extract_call_metadata(df_raw.iloc[[0]], file_path, config)
                utterances_df = pd.DataFrame()  # Empty
            else:
                calls_df = self._extract_call_metadata(df_raw.iloc[[0]], file_path, config)
                utterances_df = self._extract_utterances(
                    df_raw.iloc[1:],
                    calls_df.iloc[0]['call_id'],
                    config
                )
        
            return calls_df, utterances_df
    
    def _parse_multi_call_csv(
        self,
        df_raw: pd.DataFrame,
        source_file: Path,
        config: Dict[str, Any]
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Parse CSV with multiple calls where:
        - Rows with timestamp = call metadata (start of new call)
        - Rows without timestamp = utterances belonging to previous call
        """
        timestamp_col = df_raw.columns[0]
        
        # Identify call boundary rows (rows with non-empty timestamp)
        # Note: empty values are '' strings, not NaN
        is_call_start = (df_raw[timestamp_col] != '') & (df_raw[timestamp_col].notna())
        
        # Assign call group ID to each row
        df_raw['_call_group'] = is_call_start.cumsum()
        
        logger.info(f"Detected {is_call_start.sum()} calls in CSV")
        
        all_calls = []
        all_utterances = []
        
        # Process each call group
        for call_idx, group_df in df_raw.groupby('_call_group'):
            # First row is metadata
            meta_row = group_df.iloc[[0]]
            
            # Generate unique call_id from metadata
            call_id = self._generate_call_id(meta_row.iloc[0], call_idx, source_file)
            
            # Extract call metadata
            call_metadata = self._extract_call_metadata_from_row(
                meta_row.iloc[0],
                call_id,
                source_file,
                config
            )
            all_calls.append(call_metadata)
            
            # Extract utterances (all rows in group)
            if len(group_df) > 0:
                utterances = self._extract_utterances(
                    group_df,
                    call_id,
                    config
                )
                if not utterances.empty:
                    all_utterances.append(utterances)
        
        # Combine all calls and utterances
        calls_df = pd.concat(all_calls, ignore_index=True)
        utterances_df = pd.concat(all_utterances, ignore_index=True) if all_utterances else pd.DataFrame()
        
        logger.info(f"Extracted {len(calls_df)} calls with {len(utterances_df)} total utterances")
        
        return calls_df, utterances_df
    
    def _generate_call_id(
        self,
        meta_row: pd.Series,
        call_idx: int,
        source_file: Path
    ) -> str:
        """Generate unique call_id from metadata."""
        import hashlib
        
        # Use timestamp + agent + customer + index for uniqueness
        timestamp = str(meta_row.get(meta_row.index[0], ''))  # First column (timestamp)
        agent = str(meta_row.get('agent_name', ''))
        customer = str(meta_row.get('customer_id', ''))
        
        # Create hash from combination
        unique_str = f"{timestamp}_{agent}_{customer}_{call_idx}"
        call_hash = hashlib.md5(unique_str.encode()).hexdigest()[:8]
        
        return f"call_{call_hash}"
    
    def _extract_call_metadata_from_row(
        self,
        row: pd.Series,
        call_id: str,
        source_file: Path,
        config: Dict[str, Any]
    ) -> pd.DataFrame:
        """Extract call metadata from a single row."""
        
        # Extract optional metadata
        direction_raw = str(row.get('direction', 'UNKNOWN')).strip().upper()
        if 'IN' in direction_raw:
            direction = 'INBOUND'
        elif 'OUT' in direction_raw:
            direction = 'OUTBOUND'
        else:
            direction = 'UNKNOWN'
        
        # Parse call duration from metadata (if present)
        call_duration_meta = None
        if 'call_duration' in row:
            try:
                call_duration_meta = parse_timecode(row['call_duration'])
            except (ValueError, Exception) as e:
                logger.debug(f"Could not parse call_duration: {e}")
        
        # Convert source_file to relative path if possible
        try:
            source_file_str = str(source_file.relative_to(Path.cwd()))
        except ValueError:
            source_file_str = str(source_file.resolve())
        
        # Parse call start timestamp
        call_start_meta = None
        timestamp_col = row.index[0]
        if timestamp_col in row and row[timestamp_col]:
            try:
                call_start_meta = pd.to_datetime(row[timestamp_col])
            except:
                pass
        
        call_data = {
            'call_id': call_id,
            'source_file': source_file_str,
            'call_start_meta': call_start_meta,
            'call_duration_meta': call_duration_meta,
            'direction': direction,
            'agent_id': row.get('agent_id', None),
            'agent_name': row.get('agent_name', None),
            'customer_id': row.get('customer_id', None),
            'language': row.get('language', None),
            'ingested_at': datetime.now()
        }
        
        return pd.DataFrame([call_data])
    
    def _extract_call_metadata(
        self,
        meta_row: pd.DataFrame,
        source_file: Path,
        config: Dict[str, Any]
    ) -> pd.DataFrame:
        """Extract call metadata from first row."""
        
        row = meta_row.iloc[0]
        
        # Extract call_id (required)
        call_id_field = config.get('call_id_field', 'call_id')
        call_id = row.get(call_id_field, '').strip()
        
        # Fallback to filename if missing
        if not call_id:
            call_id = source_file.stem
            logger.warning(f"No call_id found, using filename: {call_id}")
        
        # Extract optional metadata
        direction = row.get('direction', 'UNKNOWN').strip().upper()
        if direction not in ['INBOUND', 'OUTBOUND']:
            direction = 'UNKNOWN'
        
        # Parse call duration from metadata (if present)
        call_duration_meta = None
        if 'call_duration' in row:
            try:
                call_duration_meta = parse_timecode(row['call_duration'])
            except (ValueError, Exception) as e:
                logger.warning(f"Could not parse call_duration metadata: {e}")
        
        # Build metadata dict
        # Convert source_file to relative path if possible, otherwise use name
        try:
            source_file_str = str(source_file.relative_to(Path.cwd()))
        except ValueError:
            # If file is not relative to cwd, use absolute path
            source_file_str = str(source_file.resolve())
        
        call_data = {
            'call_id': call_id,
            'source_file': source_file_str,
            'call_start_meta': None,  # Could parse if available
            'call_duration_meta': call_duration_meta,
            'direction': direction,
            'agent_id': row.get('agent_id', None),
            'agent_name': row.get('agent_name', None),
            'customer_id': row.get('customer_id', None),
            'language': row.get('language', None),
            'ingested_at': datetime.now()
        }
        
        return pd.DataFrame([call_data])
    
    def _extract_utterances(
        self,
        utter_rows: pd.DataFrame,
        call_id: str,
        config: Dict[str, Any]
    ) -> pd.DataFrame:
        """Extract and normalize utterances."""
        
        utterances = []
        
        # Field names from config
        speaker_field = config.get('speaker_field', 'speaker')
        text_field = config.get('text_field', 'text')
        start_field = config.get('start_time_field', 'start_time')
        end_field = config.get('end_time_field', 'end_time')
        
        for idx, row in utter_rows.iterrows():
            # Extract raw values
            raw_speaker = row.get(speaker_field, '').strip()
            text = normalize_text(row.get(text_field, ''))
            raw_start = row.get(start_field, '').strip()
            raw_end = row.get(end_field, '').strip()
            
            # Normalize speaker
            speaker = self.speaker_mapping.get(raw_speaker, self.default_speaker)
            if speaker == self.default_speaker and raw_speaker:
                logger.debug(f"Unknown speaker label: {raw_speaker}")
            
            # Parse times
            start_sec = None
            end_sec = None
            duration_sec = None
            valid_time = False
            invalid_reason = None
            
            try:
                if raw_start and raw_end:
                    start_sec = parse_timecode(raw_start)
                    end_sec = parse_timecode(raw_end)
                    
                    # Validate range
                    is_valid, reason = validate_time_range(start_sec, end_sec)
                    if is_valid:
                        duration_sec = end_sec - start_sec
                        valid_time = True
                    else:
                        invalid_reason = reason
                        valid_time = False
                else:
                    invalid_reason = "missing_time"
                    valid_time = False
            except (ValueError, Exception) as e:
                logger.debug(f"Invalid timecode in row {idx}: {e}")
                invalid_reason = "parse_error"
                valid_time = False
            
            # Text metrics
            char_count = count_chars(text)
            word_count = count_words(text)
            
            utterance = {
                'call_id': call_id,
                'utt_id': f"{call_id}-{len(utterances):05d}",
                'utterance_index': len(utterances),  # Will be re-sorted later
                'speaker': speaker,
                'start_sec': start_sec,
                'end_sec': end_sec,
                'duration_sec': duration_sec,
                'text': text,
                'char_count': char_count,
                'word_count': word_count,
                'valid_time': valid_time,
                'invalid_reason': invalid_reason
            }
            
            utterances.append(utterance)
        
        df = pd.DataFrame(utterances)
        
        # Sort by time (valid times first, then by start_sec)
        if not df.empty:
            df = df.sort_values(
                by=['valid_time', 'start_sec'],
                ascending=[False, True],
                na_position='last'
            ).reset_index(drop=True)
            
            # Re-assign utterance_index after sorting
            df['utterance_index'] = range(len(df))
            
            # Regenerate utt_id with sorted index
            df['utt_id'] = df.apply(
                lambda row: f"{row['call_id']}-{row['utterance_index']:05d}",
                axis=1
            )
        
        logger.info(f"Extracted {len(df)} utterances ({df['valid_time'].sum()} valid)")
        
        return df


def load_speaker_mapping(config_path: Path) -> Dict[str, str]:
    """
    Load speaker mapping from YAML config.
    
    Args:
        config_path: Path to speakers.yml
        
    Returns:
        Mapping dict
    """
    if not config_path.exists():
        logger.warning(f"Speaker config not found: {config_path}, using defaults")
        return {}
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    mapping = config.get('map', {})
    logger.info(f"Loaded {len(mapping)} speaker mappings")
    
    return mapping
