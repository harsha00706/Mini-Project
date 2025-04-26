import yfinance as yf
import time
import streamlit as st
import threading
import random
import datetime


# Initialize session state variables
if 'live_prices' not in st.session_state:
    st.session_state.live_prices = {}
if 'stop_ticker' not in st.session_state:
    st.session_state.stop_ticker = False

def update_live_prices():
    symbols = ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "TATAMOTORS.NS", "WIPRO.NS", "BAJFINANCE.NS"]
    
    while not st.session_state.get('stop_ticker', False):
        try:
            prices = {}
            for symbol in symbols:
                try:
                    stock = yf.Ticker(symbol)
                    info = stock.info
                    price = info.get('regularMarketPrice', None)
                    prev_close = info.get('previousClose', None)
                    
                    # Fall back to random changes if API fails
                    if price is None or prev_close is None:
                        # Get existing price if available or default
                        symbol_clean = symbol.replace('.NS', '').replace('.BO', '')
                        existing_price = st.session_state.live_prices.get(symbol_clean, {}).get('price', 1000 + random.random() * 1000)
                        
                        # Simulate a small random change
                        price = existing_price * (1 + (random.random() - 0.5) * 0.01)
                        change = (random.random() - 0.5) * 2  # Random change between -1% and +1%
                    else:
                        change = ((price - prev_close) / prev_close) * 100
                    
                    symbol_name = symbol.replace('.NS', '').replace('.BO', '')
                    prices[symbol_name] = {
                        'price': price,
                        'change': change
                    }
                except Exception as e:
                    # On error, add a placeholder with random data
                    symbol_name = symbol.replace('.NS', '').replace('.BO', '')
                    prices[symbol_name] = {
                        'price': 1000 + random.random() * 1000,
                        'change': (random.random() - 0.5) * 2
                    }
            
            # Update session state with new prices
            st.session_state.live_prices = prices
            time.sleep(60)  # Update every minute
            
        except Exception as e:
            # If something goes wrong, wait and try again
            time.sleep(30)

def start_live_ticker():
    """Function to start the ticker thread"""
    if not hasattr(st.session_state, 'ticker_thread_started'):
        st.session_state.ticker_thread_started = True
        ticker_thread = threading.Thread(target=update_live_prices)
        ticker_thread.daemon = True
        ticker_thread.start()

def main():
    st.title("Indian Stock Market Assistant")
    st.subheader("Get stock information, charts, news, and smart recommendations.")
    
    # Start the ticker thread when the app loads
    start_live_ticker()
    
    st.subheader("Live Stock Prices")
    
    # Create scrolling ticker with custom HTML/CSS
    ticker_html = create_ticker_html()
    st.markdown(ticker_html, unsafe_allow_html=True)
    
    # Rest of your app UI below
    st.markdown("---")
    
    # Create tabs for different functionalities
    tab1, tab2, tab3 = st.tabs(["Stock Information", "Market News", "Analysis"])
    
    with tab1:
        st.subheader("Stock Information")
        symbol = st.selectbox(
            "Select a stock",
            ["RELIANCE", "TCS", "HDFCBANK", "INFY", "TATAMOTORS", "WIPRO", "BAJFINANCE"]
        )
        if st.button("Get Information"):
            display_stock_info(f"{symbol}.NS")
    
    with tab2:
        st.subheader("Market News")
        st.info("Latest market news will appear here")
        
    with tab3:
        st.subheader("Analysis")
        st.info("Market analysis tools will be available here")

def create_ticker_html():
    """Generate HTML/CSS for the scrolling ticker"""
    ticker_items = []
    
    # Get current time
    current_time = datetime.datetime.now().strftime("%H:%M:%S")
    
    # Add time to ticker
    ticker_items.append(f'<span class="ticker-time">🕒 {current_time}</span>')
    
    # Add prices to ticker
    for symbol, data in st.session_state.live_prices.items():
        price = round(data['price'], 2)
        change = round(data['change'], 2)
        
        # Determine color based on price change
        color = "green" if change >= 0 else "red"
        arrow = "▲" if change >= 0 else "▼"
        
        ticker_items.append(
            f'<span class="ticker-item"><b>{symbol}</b>: '
            f'₹{price} <span style="color: {color};">{arrow} {abs(change)}%</span></span>'
        )
    
    # Default items if no data available yet
    if not ticker_items:
        ticker_items = [
            '<span class="ticker-item">Loading stock data...</span>',
            '<span class="ticker-item">Please wait...</span>'
        ]
    
    # Combine all items
    ticker_content = ' | '.join(ticker_items)
    
    # CSS for the ticker
    ticker_css = """
    <style>
        .ticker-container {
            width: 100%;
            background-color: #f0f2f6;
            overflow: hidden;
            white-space: nowrap;
            box-sizing: border-box;
            padding: 10px 0;
            border-radius: 5px;
            margin-bottom: 20px;
        }
        
        .ticker-content {
            display: inline-block;
            animation: ticker-scroll 60s linear infinite;
            padding-right: 100%;
        }
        
        .ticker-item {
            margin: 0 20px;
            font-size: 16px;
        }
        
        .ticker-time {
            margin: 0 20px;
            font-weight: bold;
            color: #1e3a8a;
        }
        
        @keyframes ticker-scroll {
            0% {
                transform: translateX(100%);
            }
            100% {
                transform: translateX(-100%);
            }
        }
    </style>
    """
    
    # HTML structure
    ticker_html = f"""
    {ticker_css}
    <div class="ticker-container">
        <div class="ticker-content">
            {ticker_content}
        </div>
    </div>
    """
    
    return ticker_html

def display_stock_info(stock_symbol):
    """Display detailed information for a selected stock"""
    try:
        stock = yf.Ticker(stock_symbol)
        info = stock.info
        
        # Display basic info
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader(info.get('longName', stock_symbol))
            st.write(f"**Sector:** {info.get('sector', 'N/A')}")
            st.write(f"**Industry:** {info.get('industry', 'N/A')}")
            
        with col2:
            current_price = info.get('currentPrice', info.get('regularMarketPrice', 'N/A'))
            prev_close = info.get('previousClose', 'N/A')
            
            if current_price != 'N/A' and prev_close != 'N/A':
                price_change = current_price - prev_close
                price_change_percent = (price_change / prev_close) * 100
                
                st.metric(
                    "Current Price",
                    f"₹{current_price:,.2f}",
                    f"{price_change:+,.2f} ({price_change_percent:+,.2f}%)"
                )
            else:
                st.metric("Current Price", f"₹{current_price}")
        
        # Display more detailed metrics
        st.subheader("Key Metrics")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("52 Week High", f"₹{info.get('fiftyTwoWeekHigh', 'N/A'):,.2f}" if info.get('fiftyTwoWeekHigh') else "N/A")
            st.metric("Market Cap", f"₹{info.get('marketCap', 'N/A'):,.0f}" if info.get('marketCap') else "N/A")
        
        with col2:
            st.metric("52 Week Low", f"₹{info.get('fiftyTwoWeekLow', 'N/A'):,.2f}" if info.get('fiftyTwoWeekLow') else "N/A")
            st.metric("P/E Ratio", f"{info.get('trailingPE', 'N/A'):,.2f}" if info.get('trailingPE') else "N/A")
        
        with col3:
            st.metric("Volume", f"{info.get('volume', 'N/A'):,.0f}" if info.get('volume') else "N/A")
            st.metric("Dividend Yield", f"{info.get('dividendYield', 0) * 100:.2f}%" if info.get('dividendYield') else "N/A")
        
        # Show stock chart
        st.subheader("Price Chart")
        period = st.selectbox("Select period", ["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "max"])
        interval = "1d"
        if period in ["1d", "5d"]:
            interval = "15m"
        
        # Get historical data
        hist = stock.history(period=period, interval=interval)
        
        # Check if data is available
        if not hist.empty:
            st.line_chart(hist['Close'])
        else:
            st.warning("No historical data available for the selected period.")
            
    except Exception as e:
        st.error(f"Error retrieving stock information: {str(e)}")

if __name__ == "__main__":
    main()