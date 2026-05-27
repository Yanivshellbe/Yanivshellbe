# ארכיטקטורה — Yaniv Money Machine

## עקרונות

1. **בטיחות תחילה**: כל הרצה ראשונית במצב Paper. שום פקודה לכסף אמיתי ללא דגל מפורש.
2. **הפרדת אחריות**: Strategies → Signals → Risk Manager → Executor.
3. **Observable כברירת מחדל**: כל החלטה, פוזיציה, סיגנל וכשל נרשמים ונראים בדשבורד.
4. **Reversibility**: גודל פוזיציה ראשוני קטן, Stop-loss קשיח, Circuit Breakers ברמת המערכת.

## שכבות

### L1 — Data Feeds
- Alpaca Market Data (מניות, אופציות, קריפטו לפי תוכנית).
- News & Social: Twitter/X, RSS פיננסי, Polygon news (תלוי תוכנית).
- מאקרו: FRED, חדשות מרכזיות.
- כל מקור נכנס דרך adapter עם schema אחיד.

### L2 — Signal Generation
- כל אסטרטגיה היא מודול עצמאי שמייצא `generate_signals(context) -> List[Signal]`.
- Signal = {symbol, side, confidence, horizon, rationale, source_strategy}.

### L3 — Risk Manager
- אכיפת DTBP, מינוף מקסימלי, חשיפה למגזר, גודל פוזיציה לפי Kelly מצומצם.
- Circuit Breakers: ירידה יומית > X%, drawdown מצטבר > Y%, latency anomalies.
- בדיקת PDT count לפני יום חדש.

### L4 — Executor
- שולח פקודות ל-Alpaca עם order types נכונים (bracket, OCO, trailing stop).
- Reconciliation מול state פנימי בכל tick.

### L5 — Orchestrator
- Scheduler: pre-market, intraday, post-market, overnight dream.
- Strategy ranker שבועי — ניקוד לפי P&L מותאם סיכון, Sharpe, hit-rate.

### L6 — Dashboard
- HTML סטטי + JSON state נטען בכל רענון.
- צפייה ב: חשבון, פוזיציות פתוחות, P&L יומי/שבועי, אסטרטגיות + ניקוד, dream scans, backtests.
- בחירה ידנית של אסטרטגיות פעילות + הרצת backtest.

## אופק רעיונות לבחינה

לפי דברי המשתמש — ימולא אחרי קבלת הרעיונות:

- Trump/political tweet listener → butterfly effect mapping.
- Latency arbitrage cross-venue.
- (להמשך מהמשתמש)

## תקיפה עצמית

לכל רעיון תבוצע סבב Red Team:
- מה הסיכון הגרוע ביותר?
- היכן ה-edge נשחק מהר (alpha decay)?
- מה הסיכוי לשגיאת ביצוע (slippage, fill, latency)?
- האם יש סיכון משפטי/רגולטורי?
- מה הצורך ב-capital ratio (sizing) ובאיזה תרחיש פוקע?

תוצרי הסבב נכנסים לקובץ `docs/red_team/<idea>.md`.
