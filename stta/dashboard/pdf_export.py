"""PDF export functionality with Coworkers.ai branding."""

import pandas as pd
from datetime import datetime
from pathlib import Path
from typing import Dict, Any
import io
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, 
    Image, PageBreak, Frame, PageTemplate
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfgen import canvas


class CoworkersAIPDFReport:
    """PDF report generator with Coworkers.ai branding."""
    
    # Coworkers.ai colors
    CYAN = colors.HexColor('#7DD3D3')
    CYAN_LIGHT = colors.HexColor('#C5E8E8')
    MAGENTA = colors.HexColor('#E6458B')
    NAVY = colors.HexColor('#1A2B3C')
    GRAY = colors.HexColor('#6B7280')
    
    def __init__(self, filename: str):
        """Initialize PDF report."""
        self.filename = filename
        self.doc = SimpleDocTemplate(
            filename,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=3*cm,
            bottomMargin=2*cm
        )
        self.story = []
        self.styles = getSampleStyleSheet()
        self._setup_styles()
    
    def _setup_styles(self):
        """Setup custom styles with Coworkers.ai branding."""
        # Title style
        self.styles.add(ParagraphStyle(
            name='CoworkersTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=self.NAVY,
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Subtitle
        self.styles.add(ParagraphStyle(
            name='CoworkersSubtitle',
            parent=self.styles['Normal'],
            fontSize=12,
            textColor=self.GRAY,
            spaceAfter=20,
            alignment=TA_CENTER
        ))
        
        # Section heading
        self.styles.add(ParagraphStyle(
            name='SectionHeading',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=self.NAVY,
            spaceBefore=20,
            spaceAfter=10,
            borderPadding=5,
            borderColor=self.CYAN,
            borderWidth=2,
            fontName='Helvetica-Bold'
        ))
        
        # KPI style
        self.styles.add(ParagraphStyle(
            name='KPI',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=self.NAVY,
            alignment=TA_CENTER
        ))
    
    def add_header(self, title: str, date_range: str = None):
        """Add branded header."""
        # Title
        self.story.append(Paragraph(
            f"🤖 {title}",
            self.styles['CoworkersTitle']
        ))
        
        # Subtitle with branding
        subtitle = "by <b>Coworkers.ai</b> | Advanced Speech-to-Text Analytics"
        if date_range:
            subtitle += f"<br/>{date_range}"
        
        self.story.append(Paragraph(subtitle, self.styles['CoworkersSubtitle']))
        self.story.append(Spacer(1, 0.5*cm))
    
    def add_kpi_table(self, kpis: Dict[str, Any]):
        """Add KPI summary table."""
        self.story.append(Paragraph("Key Performance Indicators", self.styles['SectionHeading']))
        
        # Prepare data
        data = [['Metric', 'Value']]
        for key, value in kpis.items():
            data.append([key, str(value)])
        
        # Create table
        table = Table(data, colWidths=[8*cm, 6*cm])
        table.setStyle(TableStyle([
            # Header
            ('BACKGROUND', (0, 0), (-1, 0), self.CYAN),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            
            # Body
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('TEXTCOLOR', (0, 1), (-1, -1), self.NAVY),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, self.CYAN_LIGHT),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, self.CYAN_LIGHT]),
        ]))
        
        self.story.append(table)
        self.story.append(Spacer(1, 1*cm))
    
    def add_data_table(self, title: str, df: pd.DataFrame, max_rows: int = 20):
        """Add data table."""
        self.story.append(Paragraph(title, self.styles['SectionHeading']))
        
        # Limit rows
        if len(df) > max_rows:
            df = df.head(max_rows)
            note = f"<i>Showing top {max_rows} of {len(df)} records</i>"
            self.story.append(Paragraph(note, self.styles['Normal']))
        
        # Prepare data
        data = [df.columns.tolist()]
        for _, row in df.iterrows():
            data.append([str(v)[:50] for v in row.values])  # Truncate long values
        
        # Calculate column widths
        available_width = 17*cm
        col_width = available_width / len(df.columns)
        
        # Create table
        table = Table(data, colWidths=[col_width] * len(df.columns))
        table.setStyle(TableStyle([
            # Header
            ('BACKGROUND', (0, 0), (-1, 0), self.MAGENTA),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            
            # Body
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, self.GRAY),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, self.CYAN_LIGHT]),
        ]))
        
        self.story.append(table)
        self.story.append(Spacer(1, 1*cm))
    
    def add_section(self, title: str, content: str):
        """Add text section."""
        self.story.append(Paragraph(title, self.styles['SectionHeading']))
        self.story.append(Paragraph(content, self.styles['Normal']))
        self.story.append(Spacer(1, 0.5*cm))
    
    def add_page_break(self):
        """Add page break."""
        self.story.append(PageBreak())
    
    def build(self):
        """Build PDF document."""
        self.doc.build(self.story, onFirstPage=self._add_footer, onLaterPages=self._add_footer)
    
    def _add_footer(self, canvas_obj, doc):
        """Add footer to each page."""
        canvas_obj.saveState()
        canvas_obj.setFont('Helvetica', 8)
        canvas_obj.setFillColor(self.GRAY)
        
        # Page number
        page_num = canvas_obj.getPageNumber()
        text = f"Page {page_num}"
        canvas_obj.drawRightString(A4[0] - 2*cm, 1*cm, text)
        
        # Generated timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        canvas_obj.drawString(2*cm, 1*cm, f"Generated: {timestamp}")
        
        # Branding
        canvas_obj.drawCentredString(A4[0]/2, 1*cm, "Powered by Coworkers.ai")
        
        canvas_obj.restoreState()


def generate_summary_report(
    calls_df: pd.DataFrame,
    call_metrics_df: pd.DataFrame,
    quality_metrics_df: pd.DataFrame,
    text_stats_df: pd.DataFrame,
    filler_words_df: pd.DataFrame,
    interaction_metrics_df: pd.DataFrame,
    filename: str = "call_analytics_report.pdf"
) -> str:
    """
    Generate comprehensive summary PDF report.
    
    Returns:
        Path to generated PDF file
    """
    
    report = CoworkersAIPDFReport(filename)
    
    # Header
    date_range = f"{calls_df['call_start_meta'].min()} to {calls_df['call_start_meta'].max()}"
    report.add_header("Call Analytics Summary Report", date_range)
    
    # KPIs
    kpis = {
        "Total Calls": f"{len(calls_df):,}",
        "Total Duration": f"{call_metrics_df['total_duration'].sum() / 3600:.1f} hours",
        "Avg Call Duration": f"{call_metrics_df['total_duration'].mean() / 60:.1f} min",
        "Total Utterances": f"{call_metrics_df['total_utterances'].sum():,}",
        "Avg Quality Score": f"{quality_metrics_df['quality_score'].mean() * 100:.1f}%",
        "Avg Vocabulary Richness": f"{text_stats_df['vocabulary_richness'].mean() * 100:.1f}%",
        "Avg Filler Rate": f"{filler_words_df['filler_words_rate'].mean() * 100:.2f}%",
        "Avg Interruption Rate": f"{interaction_metrics_df['interruption_rate'].mean() * 100:.1f}%"
    }
    report.add_kpi_table(kpis)
    
    # Top performers
    report.add_page_break()
    report.add_data_table(
        "🏆 Longest Calls",
        call_metrics_df.nlargest(10, 'total_duration')[['call_id', 'total_duration', 'total_utterances']]
    )
    
    report.add_data_table(
        "💬 Most Talkative Calls",
        call_metrics_df.nlargest(10, 'total_utterances')[['call_id', 'total_utterances', 'total_words']]
    )
    
    # Quality insights
    report.add_page_break()
    report.add_section(
        "🔍 Quality Insights",
        f"Average data quality score across all calls is {quality_metrics_df['quality_score'].mean()*100:.1f}%. "
        f"{(quality_metrics_df['quality_score'] < 0.9).sum()} calls have quality issues that need attention."
    )
    
    # Language analytics
    report.add_section(
        "💬 Language Analytics",
        f"Average vocabulary richness is {text_stats_df['vocabulary_richness'].mean()*100:.1f}%, "
        f"indicating a {'good' if text_stats_df['vocabulary_richness'].mean() > 0.5 else 'limited'} variety of words used. "
        f"On average, calls contain {text_stats_df['question_count'].mean():.1f} questions."
    )
    
    # Build PDF
    report.build()
    
    return filename
