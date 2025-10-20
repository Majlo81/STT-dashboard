"""
PDF Report Generation using ReportLab.

Generates professional PDF reports with:
- KPI summary
- Charts (exported from Plotly via kaleido)
- Data tables
- Narrative text
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import Dict, List
import plotly.graph_objects as go


class PDFReportGenerator:
    """Generate PDF reports for call analytics."""
    
    def __init__(self, output_path: Path):
        """
        Initialize PDF generator.
        
        Args:
            output_path: Path to output PDF file
        """
        self.output_path = output_path
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create document
        self.doc = SimpleDocTemplate(
            str(output_path),
            pagesize=A4,
            rightMargin=0.75*inch,
            leftMargin=0.75*inch,
            topMargin=1*inch,
            bottomMargin=0.75*inch
        )
        
        # Styles
        self.styles = getSampleStyleSheet()
        self._setup_styles()
        
        # Story (content elements)
        self.story = []
    
    def _setup_styles(self):
        """Setup custom paragraph styles."""
        
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#2E86AB'),
            spaceAfter=12,
            alignment=TA_CENTER
        ))
        
        # Section header
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#2E86AB'),
            spaceAfter=12,
            spaceBefore=12
        ))
        
        # KPI style
        self.styles.add(ParagraphStyle(
            name='KPI',
            parent=self.styles['Normal'],
            fontSize=12,
            spaceAfter=6
        ))
    
    def add_title(self, call_id: str):
        """Add report title."""
        title = Paragraph(
            f"Call Analytics Report<br/>{call_id}",
            self.styles['CustomTitle']
        )
        self.story.append(title)
        
        # Timestamp
        timestamp = Paragraph(
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            self.styles['Normal']
        )
        self.story.append(timestamp)
        self.story.append(Spacer(1, 0.3*inch))
    
    def add_section(self, title: str):
        """Add section header."""
        header = Paragraph(title, self.styles['SectionHeader'])
        self.story.append(header)
    
    def add_kpi_table(self, call_metrics: pd.Series):
        """Add KPI summary table."""
        
        kpis = [
            ['Metric', 'Value'],
            ['Total Duration', f"{call_metrics['total_duration']:.1f} s"],
            ['Speech Time', f"{call_metrics['speech_time']:.1f} s ({call_metrics['speech_ratio']:.1%})"],
            ['Silence Time', f"{call_metrics['silence_time']:.1f} s ({call_metrics['silence_ratio']:.1%})"],
            ['Overlap Time', f"{call_metrics['overlap_time']:.1f} s ({call_metrics['overlap_ratio']:.1%})"],
            ['Total Utterances', str(int(call_metrics['total_utterances']))],
            ['Speaker Switches', str(int(call_metrics['speaker_switches']))],
            ['Interruptions', str(int(call_metrics['interruptions_total']))],
        ]
        
        table = Table(kpis, colWidths=[3*inch, 3*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E86AB')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        
        self.story.append(table)
        self.story.append(Spacer(1, 0.2*inch))
    
    def add_speaker_table(self, speaker_metrics: pd.DataFrame):
        """Add speaker metrics table."""
        
        data = [['Speaker', 'Speaking Time', 'Turns', 'WPM', 'Words']]
        
        for _, row in speaker_metrics.iterrows():
            data.append([
                row['speaker'],
                f"{row['apportioned_speaking_time']:.1f} s",
                str(int(row['turn_count'])),
                f"{row['words_per_minute']:.1f}",
                str(int(row['total_words']))
            ])
        
        table = Table(data, colWidths=[1.5*inch, 1.5*inch, 1*inch, 1*inch, 1*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#A23B72')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        
        self.story.append(table)
        self.story.append(Spacer(1, 0.2*inch))
    
    def add_quality_table(self, quality_metrics: pd.Series):
        """Add quality metrics table."""
        
        data = [
            ['Quality Metric', 'Value'],
            ['Quality Score', f"{quality_metrics['quality_score']:.1%}"],
            ['Invalid Timestamps', f"{quality_metrics['invalid_time_ratio']:.1%}"],
            ['Unknown Speakers', f"{quality_metrics['unknown_speaker_ratio']:.1%}"],
            ['Empty Text', f"{quality_metrics['empty_text_ratio']:.1%}"],
        ]
        
        table = Table(data, colWidths=[3*inch, 2*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#F18F01')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightgoldenrodyellow),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        
        self.story.append(table)
        self.story.append(Spacer(1, 0.2*inch))
    
    def add_narrative(self, text: str):
        """Add narrative text."""
        # Split by paragraphs
        paragraphs = text.strip().split('\n\n')
        
        for para in paragraphs:
            if para.strip():
                p = Paragraph(para.replace('\n', '<br/>'), self.styles['Normal'])
                self.story.append(p)
                self.story.append(Spacer(1, 0.1*inch))
    
    def add_chart_image(self, image_path: Path, width: float = 6*inch):
        """
        Add chart image to report.
        
        Args:
            image_path: Path to PNG image
            width: Image width in inches
        """
        if not image_path.exists():
            return
        
        img = Image(str(image_path), width=width)
        self.story.append(img)
        self.story.append(Spacer(1, 0.2*inch))
    
    def add_page_break(self):
        """Add page break."""
        self.story.append(PageBreak())
    
    def build(self):
        """Build and save PDF."""
        self.doc.build(self.story)


def export_plotly_to_png(fig: go.Figure, output_path: Path, width: int = 1200, height: int = 600):
    """
    Export Plotly figure to PNG using kaleido.
    
    Args:
        fig: Plotly figure
        output_path: Output PNG path
        width: Image width in pixels
        height: Image height in pixels
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    fig.write_image(
        str(output_path),
        width=width,
        height=height,
        scale=2  # For higher resolution
    )


def generate_call_report(
    call_id: str,
    call_metrics: pd.Series,
    speaker_metrics: pd.DataFrame,
    quality_metrics: pd.Series,
    narrative: str,
    chart_paths: Dict[str, Path],
    output_path: Path
):
    """
    Generate complete call report.
    
    Args:
        call_id: Call identifier
        call_metrics: Call-level metrics
        speaker_metrics: Speaker-level metrics
        quality_metrics: Quality metrics
        narrative: Narrative text
        chart_paths: Dict mapping chart names to PNG paths
        output_path: Output PDF path
    """
    generator = PDFReportGenerator(output_path)
    
    # Title
    generator.add_title(call_id)
    
    # Executive Summary
    generator.add_section("Executive Summary")
    generator.add_narrative(narrative)
    
    # KPIs
    generator.add_section("Key Performance Indicators")
    generator.add_kpi_table(call_metrics)
    
    # Charts
    if 'timeline' in chart_paths:
        generator.add_section("Timeline Visualization")
        generator.add_chart_image(chart_paths['timeline'])
    
    if 'speaking_time' in chart_paths:
        generator.add_section("Speaking Time Distribution")
        generator.add_chart_image(chart_paths['speaking_time'])
    
    # Speaker metrics
    generator.add_page_break()
    generator.add_section("Speaker Analytics")
    generator.add_speaker_table(speaker_metrics)
    
    if 'wpm' in chart_paths:
        generator.add_chart_image(chart_paths['wpm'])
    
    # Quality
    generator.add_section("Data Quality")
    generator.add_quality_table(quality_metrics)
    
    if 'quality_flags' in chart_paths:
        generator.add_chart_image(chart_paths['quality_flags'])
    
    # Build PDF
    generator.build()
