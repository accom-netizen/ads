import os, sys
from playwright.sync_api import sync_playwright

OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)

CSS = """
*{box-sizing:border-box;margin:0;padding:0}
html,body{width:1080px;height:var(--h);background:#10151d;font-family:Inter,sans-serif;color:#fff}
.page{width:1080px;height:var(--h);display:flex;flex-direction:column;align-items:center;justify-content:center;
  padding:var(--pad) 64px;background:radial-gradient(ellipse at 50% 0%,#1c2430 0%,#10151d 70%)}
.tag{display:flex;align-items:center;gap:14px;font-weight:800;letter-spacing:.16em;font-size:28px;color:#d9b44a;text-transform:uppercase}
.live{display:inline-flex;align-items:center;gap:10px;background:#c8312b;color:#fff;font-size:22px;letter-spacing:.12em;padding:8px 16px;border-radius:8px}
.live i{width:12px;height:12px;border-radius:50%;background:#fff;display:inline-block}
h1{font-family:'Inter Display',Inter;font-weight:800;font-size:var(--h1);line-height:1.04;letter-spacing:-.02em;text-align:center;margin:30px 0 40px}
h1 em{font-style:normal;color:#d9b44a}
.cards{display:flex;gap:22px;width:100%}
.cards.three .num{font-size:58px}
.wrap{width:100%;display:flex;flex-direction:column;align-items:center;zoom:var(--z)}
.card{flex:1;background:#1a212c;border:2px solid #2a3442;border-radius:24px;padding:34px 26px;text-align:center}
.card.hl{border-color:#d9b44a}
.num{white-space:nowrap;font-family:'Inter Display',Inter;font-weight:800;font-size:68px;color:#d9b44a;line-height:1;letter-spacing:-.02em}
.lbl{margin-top:14px;font-size:27px;line-height:1.25;color:#d5dbe3;font-weight:500}
.big{background:#1a212c;border:2px solid #d9b44a;border-radius:28px;padding:40px;width:100%;text-align:center}
.big .num{font-size:130px}
.big .lbl{font-size:32px}
.list{width:100%;background:#1a212c;border:2px solid #2a3442;border-radius:24px;padding:14px 34px}
.row{display:flex;align-items:center;gap:24px;padding:22px 0;border-bottom:1px solid #2a3442;font-size:33px;font-weight:600;line-height:1.2}
.row:last-child{border-bottom:none}
.row b{flex:none;width:52px;height:52px;border-radius:50%;background:#3a3420;color:#d9b44a;display:flex;align-items:center;justify-content:center;font-size:28px;font-weight:800}
.row span em{font-style:normal;color:#d9b44a}
.see{width:100%;display:flex;gap:22px}
.see .card .arrow{font-size:96px;font-weight:800;line-height:1}
.up{color:#4cc38a}.down{color:#e5534b}
.sub{margin-top:44px;font-size:36px;line-height:1.3;font-weight:600;text-align:center;color:#eef1f5;max-width:900px}
.cta{margin-top:36px;background:#d9b44a;color:#111;font-weight:800;font-size:44px;letter-spacing:-.01em;padding:30px 52px;border-radius:18px;text-transform:uppercase}
.fine{margin-top:26px;font-size:21px;color:#8590a0;text-align:center;line-height:1.4}
"""

ADS = {
"n1_fed_hike_odds": dict(tag="Fed decision · Oct 28", h1="Inflation is back to <em>3.7%</em>. The Fed may hike again.",
  body="""<div class="cards three">
   <div class=card><div class=num>3.7%</div><div class=lbl>Inflation<br>(Sept. CPI)</div></div>
   <div class=card><div class=num>3.75–4%</div><div class=lbl>Fed rate, after<br>September's hike</div></div>
   <div class="card hl"><div class=num>85%+</div><div class=lbl>Odds of a<br>December hike</div></div></div>""",
  sub="Rising prices quietly shrink what your savings can buy. See how a Gold IRA can add balance to your 401(k).",
  cta="Get the free guide", src="Sources: Federal Reserve, BLS, CME FedWatch (Oct 2026)."),
"n2_oil_110": dict(tag="Energy · This week", h1="Oil is back above <em>$110</em> a barrel.",
  body="""<div class=cards>
   <div class="card hl"><div class=num>$110+</div><div class=lbl>Brent crude,<br>highest since May</div></div>
   <div class=card><div class=num>+20%</div><div class=lbl>Energy prices<br>over the past year</div></div></div>""",
  sub="When everything costs more, the dollars in your retirement account buy less. Learn how gold can help you diversify.",
  cta="Get the free guide", src="Sources: ICE Brent futures (Oct 22–28, 2026), BLS September CPI."),
"n3_gold_dip": dict(tag="Gold · This week", h1="Gold just slipped to a <em>3&#8209;month low</em>.",
  body="""<div class=big><div class=num>~$4,000</div><div class=lbl>per ounce, its lowest level since July</div></div>""",
  sub="Some savers use pullbacks to start diversifying. Learn how to hold physical gold inside your IRA or 401(k).",
  cta="Get the free guide", src="Source: COMEX gold futures, Oct 26, 2026. Prices change daily. Past performance does not guarantee future results."),
"n4_bond_yields": dict(tag="Bonds · This week", h1="The 10-year Treasury yield is over <em>5%</em>.",
  body="""<div class=see>
   <div class=card><div class="arrow up">↑</div><div class=lbl>When interest rates<br>go up…</div></div>
   <div class="card hl"><div class="arrow down">↓</div><div class=lbl>…bond prices<br>go down</div></div></div>""",
  sub="If your 401(k) leans on bond funds for “safety,” rising rates can pull their value down. See how gold adds a different kind of balance.",
  cta="Get the free guide", src="Source: U.S. Treasury 10-year yield, Oct 28, 2026."),
"n5_headlines": dict(tag="This week in your money", h1="5 headlines every <em>retirement saver</em> should see.",
  body="""<div class=list>
   <div class=row><b>1</b><span>Fed holds rates at <em>3.75–4%</em> in a split vote</span></div>
   <div class=row><b>2</b><span>Inflation climbs to <em>3.7%</em></span></div>
   <div class=row><b>3</b><span>Oil tops <em>$110</em> a barrel</span></div>
   <div class=row><b>4</b><span>10-year Treasury yield above <em>5%</em></span></div>
   <div class=row><b>5</b><span>Gold slips to a 3-month low near <em>$4,000</em></span></div></div>""",
  sub="What does it mean for your 401(k)? Get the free Gold IRA guide.",
  cta="Get the free guide", src="Sources: Federal Reserve, BLS, market data, Oct 22–28, 2026."),
}

SIZES = {"4x5": dict(h=1350, pad=60, h1=88, z=1), "9x16": dict(h=1920, pad=230, h1=88, z=1.16)}

def html(ad, s):
    return f"""<!doctype html><html><head><meta charset=utf-8><style>:root{{--h:{s['h']}px;--pad:{s['pad']}px;--h1:{s['h1']}px;--z:{s['z']}}}{CSS}</style></head>
<body><div class=page><div class=wrap>
<div class=tag><span class=live><i></i>News</span>{ad['tag']}</div>
<h1>{ad['h1']}</h1>{ad['body']}
<div class=sub>{ad['sub']}</div>
<div class=cta>{ad['cta']} &nbsp;→</div>
<div class=fine>Educational information only. Not financial advice.<br>{ad['src']}</div>
</div></div></body></html>"""

with sync_playwright() as p:
    b = p.chromium.launch()
    for name, ad in ADS.items():
        for sz, s in SIZES.items():
            pg = b.new_page(viewport={"width": 1080, "height": s["h"]})
            pg.set_content(html(ad, s)); pg.wait_for_timeout(150)
            over = pg.evaluate("document.querySelector('.page').scrollHeight")
            pg.screenshot(path=f"{OUT}/{name}_{sz}.png")
            print(name, sz, "content height", over, "/", s["h"])
            pg.close()
    b.close()
