# Lead Scoring Rules

## Score to Tier Mapping

Based on model probability output, convert to 0-100 scale and tier:

| Probability | Score | Tier | Action | Expected Conversion |
|-------------|-------|------|--------|---------------------|
| 0.80 - 1.00 | 80-100 | 🔴 **Hot** | Contact immediately | 60%+ |
| 0.50 - 0.79 | 50-79 | 🟡 **Warm** | Follow up within 48h | 40%+ |
| 0.20 - 0.49 | 20-49 | 🔵 **Cold** | Nurture campaign | 10-20% |
| 0.00 - 0.19 | 0-19 | ❄️ **Frozen** | Exclude or long-term nurture | <10% |

## Feature Interpretation

**High-Quality Lead Indicators** (based on feature importance):
1. ✅ Engaged with email (opened + clicked)
2. ✅ Multiple page visits (>5)
3. ✅ Recent activity (within last 7 days)
4. ✅ High time spent on site (>10 minutes)
5. ✅ Downloaded resources (e-books, whitepapers)
6. ✅ Filled out contact form
7. ✅ Company size alignment (target industry)

**Low-Quality Lead Indicators**:
- ❌ No email engagement
- ❌ Single page visit
- ❌ Old last activity (>30 days)
- ❌ No form submission
- ❌ From untrusted source

## Business Rules (Override Model When Necessary)

1. **VIP Accounts**: Always score 90+, regardless of engagement
   - Rule: `if company in vip_list: score = 90`

2. **Spam Detection**: Auto-score 0 for suspicious patterns
   - Rule: `if email is disposable or contains spam keywords: score = 0`

3. **Geographic Filter**: Score >=60 only from target regions
   - Rule: `if country not in target_countries and score < 60: score = max(score, 40)`

