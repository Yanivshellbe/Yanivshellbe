# Yaniv Money Machine

מערכת מסחר אלגוריתמית עבור חשבון Alpaca Paper (100K$). שני מסלולים: שלדת ליבה רגועה (long/short multi-factor + macro rotation) ועוד טורבו אלפא ספייקי (חדשות פוליטיות, latency ב-Polymarket, earnings IV, insiders).

## איך מפעילים

### 1. דשבורד

```bash
cd dashboard
python3 -m http.server 8080
# פתח http://localhost:8080
```

הדשבורד טוען מ-state.json + JSON-ים סטטיים — לא צריך שרת אמיתי כדי לראות אותו.

### 2. בקאנד

```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp config/settings.example.env config/settings.env
# מלא ALPACA_KEY / ALPACA_SECRET / ANTHROPIC_API_KEY

python -m money_machine.cli personas       # רשימת 22 הפרסונות
python -m money_machine.cli strategies     # רשימת אסטרטגיות רשומות
python -m money_machine.cli status         # snapshot חשבון (mock אם אין מפתחות)
python -m money_machine.cli refresh-state  # מעדכן את dashboard/state.json
python -m money_machine.cli dream          # סריקה לילית מלאה
```

## מצב נוכחי

- [x] שלב 0 — תשתית ויזואלית + ריפו
- [x] שלב 1 — קליטת 22 פרסונות אנליסטים + 8 רעיונות + Red-Team
- [x] שלב 2 — שלד Python: orchestrator, registry, risk, alpaca adapter
- [ ] **שלב 3** — מפתחות Alpaca + Anthropic (ממתין למשתמש)
- [ ] שלב 4 — אדפטר מחירים + Backtest runner
- [ ] שלב 5 — Scheduler לילי (APScheduler)
- [ ] שלב 6 — Paper execution + Circuit breakers
- [ ] שלב 7 — שדרוג ל-Live (אישור מפורש בלבד)

## בטיחות

- `LIVE_TRADING_ENABLED=false` ו-`DRY_RUN=true` כברירת מחדל.
- `RiskManager` חוסם כל פקודה שעוברת את: הפסד יומי מקסימלי, drawdown, מכסת PDT, וגודל פוזיציה מקסימלי.
- שום פקודה אמיתית לא נשלחת ל-Alpaca בלי **שני** הדגלים מופעלים במפורש.

## מבנה

```
.
├── dashboard/           # HTML/CSS/JS ללא תלויות — Control Tower
│   ├── index.html
│   ├── styles.css
│   ├── app.js
│   ├── state.json       # שלד מצב — הבקאנד כותב אליו
│   └── data/
│       ├── analysts.json   # 22 פרסונות
│       ├── ideas.json      # רעיונות + red team
│       └── prompts.json    # 22 prompt templates
├── backend/
│   ├── money_machine/
│   │   ├── settings.py
│   │   ├── orchestrator.py
│   │   ├── adapters/alpaca.py
│   │   ├── strategies/{base,registry,multi_factor,news_butterfly,pol_latency,macro_regime}.py
│   │   ├── risk/manager.py
│   │   ├── analysts/runner.py
│   │   ├── dream/nightly.py
│   │   └── cli.py
│   ├── tests/test_smoke.py
│   ├── config/settings.example.env
│   └── requirements.txt
└── docs/
    ├── ARCHITECTURE.md
    └── IDEAS_RED_TEAM.md
```

## הצעד הבא ממך

1. ספק מפתחות Alpaca Paper (env: `ALPACA_KEY`, `ALPACA_SECRET`).
2. ספק `ANTHROPIC_API_KEY` כדי שהאנליסטים יוכלו לרוץ באמת (אחרת הם רצים ב-dry-run ומחזירים את ה-prompt).
3. אישור התקנה של תלויות (`alpaca-py`, `anthropic`, `apscheduler`).
4. החלטה איזה זוג אסטרטגיות להפעיל ראשונות.
