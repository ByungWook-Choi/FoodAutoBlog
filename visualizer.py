import os
import pandas as pd
from datetime import datetime
from config import IMAGES_DIR
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio

class KamisVisualizer:
    def __init__(self, theme='plotly_dark'):
        self.theme = 'plotly_dark' if theme == 'dark' else theme
        
    def _add_watermark_and_font(self, fig, title):
        """Standardizes font, theme and adds the KAMIS watermark."""
        fig.update_layout(
            template=self.theme,
            paper_bgcolor="#2D2D2D" if self.theme == 'plotly_dark' else None,
            plot_bgcolor="#2D2D2D" if self.theme == 'plotly_dark' else None,
            title={
                'text': title,
                'y': 0.95,
                'x': 0.5,
                'xanchor': 'center',
                'yanchor': 'top',
                'font': dict(size=22, color='#00d2ff', family="Malgun Gothic, 'Nanum Gothic', sans-serif")
            },
            font=dict(
                family="Malgun Gothic, 'Nanum Gothic', sans-serif",
                size=14,
                color="white" if self.theme == 'plotly_dark' else "#333333"
            ),
            annotations=[
                dict(
                    text='출처: KAMIS (농산물유통정보)',
                    x=1.0,
                    y=-0.15,
                    xref='paper',
                    yref='paper',
                    showarrow=False,
                    font=dict(size=11, color='gray'),
                    xanchor='right',
                    yanchor='bottom'
                )
            ]
        )
        return fig

    def _save_plot(self, fig, prefix):
        """Saves Plotly chart as high-resolution PNG."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{prefix}_{timestamp}.png"
        filepath = os.path.join(IMAGES_DIR, filename)
        
        # Save image utilizing kaleido under the hood
        fig.write_image(filepath, scale=2.5, width=1000, height=600)
        return filepath

    def plot_0900_daily_fluctuation(self, df):
        """[09:00] Daily Top 5 Fluctuation Horizontal Bar Chart"""
        df = df.copy()
        
        # Color conditional
        colors = ['#ff0055' if x > 0 else '#08f7fe' for x in df['Change_Rate']]

        fig = go.Figure()
        fig.add_trace(go.Bar(
            y=df['Item'],
            x=df['Change_Rate'],
            orientation='h',
            marker_color=colors,
            text=[f"{v:+.1f}%" for v in df['Change_Rate']],
            textposition='outside',
            textfont=dict(size=14, color='white' if self.theme == 'plotly_dark' else 'black')
        ))
        
        fig.update_layout(
            xaxis_title="등락률 (%)",
            yaxis_title=None,
            xaxis=dict(zeroline=True, zerolinewidth=2, zerolinecolor='#f5d300')
        )
        self._add_watermark_and_font(fig, "🚀 오늘의 농축산물 가격 등락률 TOP 5")
        
        return self._save_plot(fig, "0900_fluctuation")

    def plot_1300_regional_comparison(self, df):
        """[13:00] Regional Price Comparison Chart"""
        fig = px.bar(df, x='Region', y='Price', color='Region', text='Price', 
                     color_discrete_sequence=['#08f7fe', '#09FBD3', '#FE53BB', '#F5D300', '#FF0055'])
        
        fig.update_traces(texttemplate='%{text:,.0f}원', textposition='outside')
        fig.update_layout(
            xaxis_title="지역",
            yaxis_title="가격 (원)",
            showlegend=False
        )
        self._add_watermark_and_font(fig, "🌟 오늘의 지역별 주요 품목 가격 비교")
        
        return self._save_plot(fig, "1300_regional")

    def plot_1700_trend_line(self, df):
        """[17:00] 7-Day Trend Line Chart"""
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=df['Date'],
            y=df['Price'],
            mode='lines+markers+text',
            text=[f"{v:,.0f}" for v in df['Price']],
            textposition='top center',
            marker=dict(size=12, color='#08f7fe', line=dict(width=2, color='white')),
            line=dict(width=4, color='#08f7fe', shape='spline'),
            fill='tozeroy', 
            fillcolor='rgba(8, 247, 254, 0.2)' # Cyan gradient fill logic imitation
        ))
        
        fig.update_layout(
            xaxis_title="날짜",
            yaxis_title="가격 (원)",
            xaxis=dict(
                tickformat="%m월 %d일",
                dtick="D1" # Every day
            )
        )
        # Add dynamic y-axis range margin so text isn't cut off
        fig.update_yaxes(range=[df['Price'].min() * 0.9, df['Price'].max() * 1.1])
        
        self._add_watermark_and_font(fig, "🔥 최근 7일간 가격 흐름 (Trend Line)")
        return self._save_plot(fig, "1700_trend")

    def plot_2100_yoy_comparison(self, df):
        """[21:00] YoY Price Change Comparison Chart"""
        df_melted = df.melt(id_vars='Month', value_vars=['This_Year', 'Last_Year'], 
                            var_name='Year', value_name='Price')
        df_melted['Year'] = df_melted['Year'].map({'This_Year': '올해', 'Last_Year': '작년'})
        
        fig = px.bar(df_melted, x="Month", y="Price", color="Year", barmode="group",
                     color_discrete_sequence=['#ff9f43', '#00cfce'], text="Price")
        
        fig.update_traces(texttemplate='%{text:,.0f}', textposition='outside')
        fig.update_layout(
            xaxis_title="월",
            yaxis_title="가격 (원)",
            legend_title=None,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        
        # Add dynamic buffer internally
        fig.update_yaxes(range=[0, df_melted['Price'].max() * 1.15])
        
        self._add_watermark_and_font(fig, "⚡ 전년 대비 가격 흐름 비교")
        return self._save_plot(fig, "2100_yoy")
