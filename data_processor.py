import pandas as pd
import random

class DataProcessor:
    @staticmethod
    def process_daily_fluctuations(df):
        """
        Process daily prices to calculate top 5 fluctuations (rises/drops)
        """
        if df.empty:
            return df
            
        df = df.copy()
        
        # Handle NaN values (fill with 0 or drop depending on importance)
        df['Today_Price'] = df['Today_Price'].fillna(0)
        df['Yesterday_Price'] = df['Yesterday_Price'].fillna(0)
        
        # Filter out rows where yesterday price was 0 to avoid division by zero
        df = df[df['Yesterday_Price'] > 0]
        
        # Calculate percentage change
        df['Change_Rate'] = ((df['Today_Price'] - df['Yesterday_Price']) / df['Yesterday_Price']) * 100
        
        # Sort by absolute change rate (biggest changes)
        df['Abs_Change'] = df['Change_Rate'].abs()
        top_5 = df.sort_values(by='Abs_Change', ascending=False).head(5)
        
        return top_5.sort_values(by='Change_Rate') # Sort for charting

    @staticmethod
    def process_trend_data(df):
        """
        Process 7-day trend data
        """
        df = df.copy()
        # Ensure dates are sorted
        # Fill missing intermediate prices with forward fill
        df['Price'] = df['Price'].ffill().bfill()
        return df

    @staticmethod
    def analyze_market_context(daily_df, regional_df, trend_df, exclude_item=None):
        """
        Analyzes data to find 'Significant Indicators' and suggest Category C or E.
        """
        findings = []
        selected_item = None
        
        # 1. Detect significant fluctuations (>15%) -> Suggest Category E (Outlook)
        if not daily_df.empty:
            df_filtered = daily_df.copy()
            if exclude_item:
                print(f"Excluding previously posted item: {exclude_item}")
                df_filtered = df_filtered[df_filtered['Item'] != exclude_item]
                
            if not df_filtered.empty:
                df_filtered['Change_Rate'] = ((df_filtered['Today_Price'] - df_filtered['Yesterday_Price']) / df_filtered['Yesterday_Price']) * 100
                max_rise = df_filtered.loc[df_filtered['Change_Rate'].idxmax()]
                max_drop = df_filtered.loc[df_filtered['Change_Rate'].idxmin()]
                
                if max_rise['Change_Rate'] > 15:
                    findings.append(f"폭등주의: {max_rise['Item']} 가격이 {max_rise['Change_Rate']:.1f}% 상승함")
                    selected_item = max_rise['Item']
                elif max_drop['Change_Rate'] < -15:
                    findings.append(f"가격 급락: {max_drop['Item']} 가격이 {max_drop['Change_Rate']:.1f}% 하락함")
                    selected_item = max_drop['Item']

        # 2. Trends (Steady drop -> Suggest Category C Segment Tips)
        if not trend_df.empty and len(trend_df) >= 7:
            first_price = trend_df.iloc[0]['Price']
            last_price = trend_df.iloc[-1]['Price']
            if last_price < first_price * 0.9:
                findings.append("가격 안정세: 최근 일주일간 꾸준한 하락세 관찰")
                # Trend item is usually the one in trend_df, let's assume it's the main focus
                if hasattr(trend_df, 'Item'): selected_item = trend_df.iloc[0]['Item']
        
        # Determine Category between C and E
        if findings:
            suggested_category = "C" if "안정세" in findings[-1] else "E"
        else:
            suggested_category = random.choice(["C", "E"])

        return suggested_category, findings, selected_item

if __name__ == "__main__":
    from data_fetcher import KamisFetcher
    fetcher = KamisFetcher()
    mock_daily = fetcher.get_mock_daily_data()
    processed = DataProcessor.process_daily_fluctuations(mock_daily)
    print(processed)
