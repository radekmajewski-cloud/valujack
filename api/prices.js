// Vercel serverless function to proxy Yahoo Finance requests
// This avoids CORS issues when fetching live prices from the browser

export default async function handler(req, res) {
  // Enable CORS
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  // Handle preflight
  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }

  const { ticker, tickers } = req.query;

  // Handle multiple tickers (comma-separated)
  if (tickers) {
    const tickerList = tickers.split(',').map(t => t.trim());
    const results = {};
    
    // Fetch all prices in parallel
    await Promise.all(
      tickerList.map(async (t) => {
        try {
          const yahooUrl = `https://query1.finance.yahoo.com/v8/finance/chart/${t}`;
          const response = await fetch(yahooUrl);
          
          if (!response.ok) {
            return;
          }

          const data = await response.json();
          const result = data?.chart?.result?.[0];
          const price = result?.meta?.regularMarketPrice;
          const currency = result?.meta?.currency;

          if (price) {
            results[t] = {
              price: price,
              currency: currency || 'USD'
            };
          }
        } catch (error) {
          // Skip failed tickers
          console.error(`Failed to fetch ${t}:`, error.message);
        }
      })
    );

    return res.status(200).json(results);
  }

  // Handle single ticker
  if (!ticker) {
    return res.status(400).json({ error: 'Ticker or tickers parameter required' });
  }

  try {
    // Fetch from Yahoo Finance
    const yahooUrl = `https://query1.finance.yahoo.com/v8/finance/chart/${ticker}`;
    const response = await fetch(yahooUrl);
    
    if (!response.ok) {
      throw new Error(`Yahoo Finance API error: ${response.status}`);
    }

    const data = await response.json();
    
    // Extract the current price
    const result = data?.chart?.result?.[0];
    const price = result?.meta?.regularMarketPrice;
    const currency = result?.meta?.currency;
    const symbol = result?.meta?.symbol;

    if (!price) {
      throw new Error('Price data not available');
    }

    return res.status(200).json({
      ticker: symbol || ticker,
      price: price,
      currency: currency || 'USD',
      timestamp: Date.now()
    });

  } catch (error) {
    console.error('Price fetch error:', error);
    return res.status(500).json({ 
      error: 'Failed to fetch price',
      message: error.message 
    });
  }
}