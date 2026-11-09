import datetime as dt
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.comments import Comment
from openpyxl.utils import get_column_letter as L

F="Arial"
BLUE=Font(name=F,color="0000FF",size=10); BLK=Font(name=F,size=10); GRN=Font(name=F,color="008000",size=10)
BOLD=Font(name=F,bold=True,size=10); H1=Font(name=F,bold=True,size=14,color="FFFFFF"); H2=Font(name=F,bold=True,size=11,color="1F3864")
YEL=PatternFill("solid",fgColor="FFFF00"); NAVY=PatternFill("solid",fgColor="1F3864"); GREY=PatternFill("solid",fgColor="D9E1F2")
NUM='#,##0;(#,##0);"-"'; PCT='0.0%;(0.0%);"-"'; X='0.0"x"'; GHS='"GHS "0.00;("GHS "0.00);"-"'
TOP=Border(top=Side(style="thin"))

wb=Workbook()
def sheet(name,widths):
    ws=wb.create_sheet(name)
    for i,w in enumerate(widths): ws.column_dimensions[L(i+1)].width=w
    ws.sheet_view.showGridLines=False
    return ws
def title(ws,text,span):
    ws.cell(1,1,text).font=H1
    for c in range(1,span+1): ws.cell(1,c).fill=NAVY
    ws.row_dimensions[1].height=24
def sec(ws,r,text,span):
    ws.cell(r,1,text).font=H2
    for c in range(1,span+1): ws.cell(r,c).fill=GREY
def put(ws,r,c,v,font=BLK,fmt=None,bold=False,fill=None,note=None):
    cell=ws.cell(r,c,v); cell.font=Font(name=F,size=10,color=font.color,bold=bold or font.bold)
    if fmt: cell.number_format=fmt
    if fill: cell.fill=fill
    if note: cell.comment=Comment(note,"Model")
    return cell

wb.remove(wb.active)
cover=sheet("Cover",[34,22,70])
inp=sheet("Inputs",[44,12,12,12,12,12,12,62])
his=sheet("Historical",[52,16,16,60])
rat=sheet("Ratios",[48,14,14,62])
fc=sheet("Forecast",[44,15,15,15,15,15,15])
val=sheet("Valuation",[46,15,15,15,15,15,15,40])
src=sheet("Sources",[38,110])

# ---------------- Historical ----------------
title(his,"MTN Ghana (Scancom PLC) - Group historical financials (GHS '000)",4)
for c,t in [(1,"Line item"),(2,"FY2024 (restated)"),(3,"FY2025"),(4,"Notes")]: put(his,3,c,t,bold=True)
H={}  # key -> row
r=4
def hrow(key,label,v24,v25,note=None,formula=False,bold=False,fmt=NUM):
    global r
    put(his,r,1,label,bold=bold)
    for c,v in ((2,v24),(3,v25)):
        if v is None: continue
        if formula:
            f=v.replace("{c}",L(c)); put(his,r,c,f,BLK,fmt,bold=bold)
        else: put(his,r,c,v,BLUE,fmt,bold=bold)
    if note: put(his,r,4,note)
    if key: H[key]=r
    r+=1
def hs(text):
    global r
    r+=1; sec(his,r,text,4); r+=1
def ref(k,c="{c}"): return f"{c}{H[k]}"

hs("Income statement")
rev_lines=[("data","Data",8978582,13358292),("voice","Voice",3530384,3806150),("momo","Mobile Money",4448917,6035167),("digital","Digital",228206,479015),("othsvc","Other service revenue",702454,685188)]
for k,l,a,b in rev_lines: hrow(k,"  "+l,a,b)
hrow("svc","Service revenue","=SUM({c}%d:{c}%d)"%(H["data"],H["othsvc"]),"=SUM({c}%d:{c}%d)"%(H["data"],H["othsvc"]),formula=True,bold=True,note="Ties to reported 17,888,543 / 24,363,812")
hrow("rev","Revenue from contracts with customers (total revenue)",17948326,24430308,bold=True,note="Reported total revenue")
hrow("nonsvc","  of which non-service revenue (devices etc.)","={c}%d-{c}%d"%(H["rev"],H["svc"]),"={c}%d-{c}%d"%(H["rev"],H["svc"]),formula=True,note="Derived: total revenue less service revenue")
hrow("othinc","Other income",2622,13182,note="'Other revenue' line; included above EBITDA")
costs=[("c1","Direct network operating costs",1780442,1870653),("c2","Government and regulatory costs",408240,420204),("c3","Cost of handsets and accessories",72903,78606),("c4","Interconnect and roaming costs",694378,570792),("c5","Employee benefits expense",713017,1061001),("c6","Selling, distribution and marketing",2377229,3411149),("c7","Other operating expenses",1664014,2340752)]
for k,l,a,b in costs: hrow(k,"  "+l,a,b)
hrow("costs","Total operating costs","=SUM({c}%d:{c}%d)"%(H["c1"],H["c7"]),"=SUM({c}%d:{c}%d)"%(H["c1"],H["c7"]),formula=True,bold=True,note="Ties to reported 7,710,223 / 9,753,157")
hrow("ebitda","EBITDA","={c}%d+{c}%d-{c}%d"%(H["rev"],H["othinc"],H["costs"]),"={c}%d+{c}%d-{c}%d"%(H["rev"],H["othinc"],H["costs"]),formula=True,bold=True,note="Reported 10,240,725 / 14,690,333")
hrow("dep","Depreciation",1733794,2322138)
hrow("amort","Amortisation",362177,407471)
hrow("ebit","Operating profit","={c}%d-{c}%d-{c}%d"%(H["ebitda"],H["dep"],H["amort"]),"={c}%d-{c}%d-{c}%d"%(H["ebitda"],H["dep"],H["amort"]),formula=True,bold=True)
hrow("finc","Finance income",372544,450066)
hrow("fcost","Finance costs",926831,1098785,note="Includes interest on lease liabilities")
hrow("pbt","Profit before tax","={c}%d+{c}%d-{c}%d"%(H["ebit"],H["finc"],H["fcost"]),"={c}%d+{c}%d-{c}%d"%(H["ebit"],H["finc"],H["fcost"]),formula=True,bold=True)
hrow("tax","Income tax expense",2183215,2906475)
hrow("gsl","Growth & Sustainability Levy",378187,565600)
hrow("pat","Profit after tax","={c}%d-{c}%d-{c}%d"%(H["pbt"],H["tax"],H["gsl"]),"={c}%d-{c}%d-{c}%d"%(H["pbt"],H["tax"],H["gsl"]),formula=True,bold=True,note="Reported 5,029,065 / 7,839,930")
hrow("shares","Shares in issue (number)",13236175050,13236175050,fmt='#,##0',note="13,236,175,050 per dividend declaration; assumed unchanged in 2024")
hrow("eps","Basic EPS (GHS)","={c}%d*1000/{c}%d"%(H["pat"],H["shares"]),"={c}%d*1000/{c}%d"%(H["pat"],H["shares"]),formula=True,fmt='0.0000',note="Reported 0.380 / 0.5923")
hrow("dps","Dividend per share - total for year (GHS)",None,0.48,fmt='0.00',note="FY2025: interim 0.08 + final 0.40. FY2024 total not captured")

hs("Statement of financial position (31 December)")
nca=[("ppe","Property, plant and equipment",8128597,10704580),("rou","Right-of-use assets",2570430,2978529),("intang","Intangible assets",1734116,2422781),("inv_nc","Investments",20000,34653),("iru_nc","IRU assets",110207,139593),("dta","Deferred tax assets",88170,88228),("ccc","Capitalised contract cost",90719,44122)]
for k,l,a,b in nca: hrow(k,"  "+l,a,b)
hrow("nca","Non-current assets","=SUM({c}%d:{c}%d)"%(H["ppe"],H["ccc"]),"=SUM({c}%d:{c}%d)"%(H["ppe"],H["ccc"]),formula=True,bold=True)
ca=[("invy","Inventory",52270,29503),("recv","Trade and other receivables",1011318,605958),("otha","Other assets",203984,149476),("ofa","Other financial assets at amortised cost",506601,255209),("taxa","Income tax assets",386320,1170834),("gsla","Growth & Sustainability Levy assets",18272,21317),("iru_c","IRU",33710,34702),("secs","Investments in securities",351302,1020578),("float","Mobile Money float",23865561,38392517),("cash","Cash and cash equivalents",3284768,4298477)]
for k,l,a,b in ca: hrow(k,"  "+l,a,b)
hrow("ca","Current assets","=SUM({c}%d:{c}%d)"%(H["invy"],H["cash"]),"=SUM({c}%d:{c}%d)"%(H["invy"],H["cash"]),formula=True,bold=True)
hrow("ta","TOTAL ASSETS","={c}%d+{c}%d"%(H["nca"],H["ca"]),"={c}%d+{c}%d"%(H["nca"],H["ca"]),formula=True,bold=True)
r+=1
eq=[("stcap","Stated capital",2222888,2222888),("re","Retained earnings",7992987,11304087),("icr","Integrity Capital Reserve",0,14653),("othres","Other reserves / MoMo contingency fund",351302,629903),("eqbal","Unreconciled difference in source",0,355)]
for k,l,a,b in eq: hrow(k,"  "+l,a,b,note=("Reported total equity 14,171,886 exceeds sum of listed components by 355 (source inconsistency)" if k=="eqbal" else None))
hrow("eq","Total equity","=SUM({c}%d:{c}%d)"%(H["stcap"],H["eqbal"]),"=SUM({c}%d:{c}%d)"%(H["stcap"],H["eqbal"]),formula=True,bold=True)
ncl=[("dtl","Deferred tax liabilities",823376,1120322),("lease_nc","Lease liabilities (non-current)",2617681,3113102),("irul_nc","IRU liability",22955,19848),("sbp","Share-based payment liability",56232,210713),("prov_nc","Provisions",12153,19341),("oncl","Other non-current liabilities",205713,251739)]
for k,l,a,b in ncl: hrow(k,"  "+l,a,b)
hrow("ncl","Non-current liabilities","=SUM({c}%d:{c}%d)"%(H["dtl"],H["oncl"]),"=SUM({c}%d:{c}%d)"%(H["dtl"],H["oncl"]),formula=True,bold=True)
cl=[("pay","Trade and other payables",2958352,3745984),("emoney","Obligations to e-money holders",23865561,38392517),("cliab","Contract liabilities",251040,448919),("prov_c","Provisions",243664,253043),("lease_c","Lease liabilities (current)",547835,522940),("irul_c","IRU liability",4036,3745),("borr","Borrowings",70443,0),("ocl","Other current liabilities",210127,116958)]
for k,l,a,b in cl: hrow(k,"  "+l,a,b)
hrow("cl","Current liabilities","=SUM({c}%d:{c}%d)"%(H["pay"],H["ocl"]),"=SUM({c}%d:{c}%d)"%(H["pay"],H["ocl"]),formula=True,bold=True)
hrow("tle","TOTAL EQUITY AND LIABILITIES","={c}%d+{c}%d+{c}%d"%(H["eq"],H["ncl"],H["cl"]),"={c}%d+{c}%d+{c}%d"%(H["eq"],H["ncl"],H["cl"]),formula=True,bold=True)
hrow("bschk","Balance check (assets - equity & liabilities)","={c}%d-{c}%d"%(H["ta"],H["tle"]),"={c}%d-{c}%d"%(H["ta"],H["tle"]),formula=True,note="Must be zero")

hs("Statement of cash flows")
op=[("cgo","Cash generated from operations",10991971,16426752),("taxp","Income tax paid",-2135187,-3394101),("intr","Interest received",300834,362320),("intp","Interest paid",-798793,-979636),("divp","Dividends paid",-3176682,-4235576),("gslp","Growth & Sustainability Levy paid",-406019,-568645)]
for k,l,a,b in op: hrow(k,"  "+l,a,b,note=("MTN Ghana classifies dividends paid within operating activities" if k=="divp" else None))
hrow("cfo","Net cash from operating activities","=SUM({c}%d:{c}%d)"%(H["cgo"],H["gslp"]),"=SUM({c}%d:{c}%d)"%(H["cgo"],H["gslp"]),formula=True,bold=True)
iv=[("cppe","Acquisition of PPE",-2969456,-4440310),("cint","Acquisition of intangible assets",-736440,-933441),("mci","Movement in current investments",0,-599643),("isec","Investment in securities",-1742,0),("ciru","Additional IRU capacity",-27592,-78293),("disp","Proceeds on disposal of PPE",2353,1202)]
for k,l,a,b in iv: hrow(k,"  "+l,a,b)
hrow("cfi","Net cash used in investing activities","=SUM({c}%d:{c}%d)"%(H["cppe"],H["disp"]),"=SUM({c}%d:{c}%d)"%(H["cppe"],H["disp"]),formula=True,bold=True)
fi=[("lpay","Lease payments",None,-544529),("dborr","Decrease in borrowings",None,-68995),("iruf","IRU liabilities",None,1941),("doncl","Decrease in other non-current liabilities",None,-47144),("finun","Financing - line detail not legible in source",-684723,0)]
for k,l,a,b in fi: hrow(k,"  "+l,a,b,note=("FY2024 financing lines garbled in the published PDF; only the total is used" if k=="finun" else None))
hrow("cff","Net cash used in financing activities","=SUM({c}%d:{c}%d)"%(H["lpay"],H["finun"]),"=SUM({c}%d:{c}%d)"%(H["lpay"],H["finun"]),formula=True,bold=True)
hrow("netcf","Net increase in cash","={c}%d+{c}%d+{c}%d"%(H["cfo"],H["cfi"],H["cff"]),"={c}%d+{c}%d+{c}%d"%(H["cfo"],H["cfi"],H["cff"]),formula=True,bold=True)
hrow("open","Opening cash",2946133,3284768)
hrow("fx","Exchange gain/(loss) on cash",-19889,111807)
hrow("close","Closing cash (computed)","={c}%d+{c}%d+{c}%d"%(H["netcf"],H["open"],H["fx"]),"={c}%d+{c}%d+{c}%d"%(H["netcf"],H["open"],H["fx"]),formula=True,bold=True)
hrow("cashchk","Check vs balance sheet cash (rounding tolerance 2)",'=IF(ABS({c}%d-{c}%d)<=2,"OK","CHECK")'%(H["close"],H["cash"]),'=IF(ABS({c}%d-{c}%d)<=2,"OK","CHECK")'%(H["close"],H["cash"]),formula=True,fmt=None)
his.freeze_panes="B4"
HS="Historical!"
def h(k,col="C"): return f"{HS}${col}${H[k]}"

# ---------------- Inputs ----------------
title(inp,"Inputs & assumptions  (blue = hardcoded input; yellow = key lever)",8)
I={}
def irow(rr,key,label,v,fmt,note,key_lever=True):
    put(inp,rr,1,label); put(inp,rr,2,v,BLUE if not str(v).startswith("=") else BLK,fmt,fill=YEL if key_lever else None); put(inp,rr,8,note); I[key]=f"Inputs!$B${rr}"
sec(inp,3,"Market data",8)
irow(4,"price","Share price (GHS)",6.67,'0.00',"Close on 30 Oct 2026 per Mansa Markets GSE summary. Update before use.")
irow(5,"pdate","Price date",dt.date(2026,10,30),'dd-mmm-yyyy',"Date of share price above",False)
irow(6,"shares","Shares in issue",f"={h('shares')}",'#,##0',"Linked to Historical",False); inp["B6"].font=GRN
irow(7,"bdate","Valuation base date",dt.date(2025,12,31),'dd-mmm-yyyy',"Forecast cash flows are discounted to this date, then rolled forward",False)
irow(8,"divsince","Dividends paid since base date (GHS/share)",0.40,'0.00',"FY2025 final dividend paid in 2026. Add any FY2026 interim paid before the price date.")
sec(inp,10,"Cost of equity (CAPM, GHS terms)",8)
irow(11,"rf","Risk-free rate",0.0967,PCT,"BoG 364-day T-bill, 26 Oct 2026 (9.6739%). A long-dated GoG bond yield is a defensible alternative.")
irow(12,"beta","Equity beta",1.0,'0.00',"Assumption: market-neutral beta. MTN dominates GSE turnover, so a regression beta vs GSE-CI is biased toward 1.")
irow(13,"erp","Equity risk premium (Ghana)",0.08,PCT,"Assumption, reflecting Ghana's B- sovereign profile. Test in the sensitivity table.")
irow(14,"ke","Cost of equity",f"=B11+B12*B13",PCT,"CAPM: Rf + beta x ERP",False)
irow(15,"g","Terminal growth (nominal)",0.07,PCT,"Assumption: approx. long-run inflation (~5-8%) plus modest real growth.")
irow(16,"wdcf","Weight on DCF in blended value",0.5,PCT,"")
irow(17,"wddm","Weight on DDM",f"=1-B16",PCT,"",False)
sec(inp,19,"Forecast drivers",8)
yrs=["2025A","2026E","2027E","2028E","2029E","2030E"]
for i,y in enumerate(yrs): put(inp,20,2+i,y,bold=True).alignment=Alignment(horizontal="right")
put(inp,20,1,"Driver",bold=True); put(inp,20,8,"Basis",bold=True)
drivers=[
 ("g_data","Data revenue growth",f"={h('data')}/{h('data','B')}-1",[0.45,0.30,0.22,0.16,0.12],"Subscriber and usage growth; 2025A +48.8%. Calibrated so 2026 service revenue growth sits in guided mid-to-upper 30s%."),
 ("g_voice","Voice revenue growth",f"={h('voice')}/{h('voice','B')}-1",[0.06,0.05,0.04,0.03,0.02],"Slowing as traffic migrates to VoIP (management-flagged risk)."),
 ("g_momo","Mobile Money revenue growth",f"={h('momo')}/{h('momo','B')}-1",[0.35,0.26,0.20,0.15,0.12],"2025A +35.7%; advanced services (lending, payments) driving growth."),
 ("g_dig","Digital revenue growth",f"={h('digital')}/{h('digital','B')}-1",[0.60,0.40,0.30,0.20,0.15],"Small base; 2025A +109.9%."),
 ("g_oth","Other service revenue growth",f"={h('othsvc')}/{h('othsvc','B')}-1",[0,0,0,0,0],"Flat (SMS/interconnect declining)."),
 ("nonsvc","Non-service revenue (% of service revenue)",f"={h('nonsvc')}/{h('svc')}",[0.0027]*5,"Held at 2025A level."),
 ("m_ebitda","EBITDA margin",f"={h('ebitda')}/{h('rev')}",[0.58,0.575,0.57,0.57,0.57],"2026 guidance: mid-to-upper 50s%."),
 ("da","D&A (% of revenue)",f"=({h('dep')}+{h('amort')})/{h('rev')}",[0.115]*5,"2025A 11.2%; slight uplift from network investment."),
 ("nfc","Net finance cost (% of revenue)",f"=({h('fcost')}-{h('finc')})/{h('rev')}",[0.027]*5,"Mostly lease interest; held at 2025A level."),
 ("taxr","Income tax (% of PBT)",f"={h('tax')}/{h('pbt')}",[0.255]*5,"25% statutory rate; 2025A effective 25.7%."),
 ("gslr","Growth & Sustainability Levy (% of PBT)",f"={h('gsl')}/{h('pbt')}",[0.05]*5,"5% levy on telecoms PBT, assumed to continue."),
 ("capex","Capex ex-leases (% of revenue)",f"=-({h('cppe')}+{h('cint')})/{h('rev')}",[0.21,0.20,0.19,0.18,0.17],"PPE + intangibles cash capex; 2025A 22.0%, easing as network build matures."),
 ("lease","Lease principal payments (% of revenue)",f"=-{h('lpay')}/{h('rev')}",[0.022]*5,"2025A 2.2%."),
 ("nwc","Change in NWC (% of change in revenue)",None,[0.0]*5,"Assumption: neutral. MoMo float and e-money obligations offset and are excluded."),
 ("payout","Dividend payout ratio",f"={h('dps')}*{h('shares')}/1000/{h('pat')}",[0.80]*5,"Policy 60-80%; 2025A 81%."),
]
rr=21
for k,l,act,vals,note in drivers:
    put(inp,rr,1,l)
    if act: put(inp,rr,2,act,GRN,PCT)
    for j,v in enumerate(vals): put(inp,rr,3+j,v,BLUE,PCT,fill=YEL)
    put(inp,rr,8,note); I[k]=rr; rr+=1
put(inp,rr+1,1,"Legend: edit only blue cells. Yellow cells are the key levers. Green cells link to other sheets; black cells are formulas.",BLK)
inp.freeze_panes="B3"
def drv(k,col): return f"Inputs!{col}${I[k]}"

# ---------------- Forecast ----------------
title(fc,"Forecast (GHS '000)",7)
for i,y in enumerate(yrs): put(fc,3,2+i,y,bold=True).alignment=Alignment(horizontal="right")
put(fc,3,1,"GHS '000",bold=True)
FR={}; fr=4
cols=["B","C","D","E","F","G"]
def frow(key,label,act,proj,fmt=NUM,bold=False):
    global fr
    put(fc,fr,1,label,bold=bold)
    if act is not None: put(fc,fr,2,act,GRN if act.startswith("=Historical") or "Historical!" in act and act.count("!")==act.count("Historical!") and "+" not in act and "-" not in act[1:] else BLK,fmt,bold=bold)
    for j,c in enumerate(cols[1:]):
        p=cols[j]
        put(fc,fr,3+j,proj(c,p),BLK,fmt,bold=bold)
    FR[key]=fr; fr+=1
def F_(k,c): return f"{c}{FR[k]}"
sec(fc,fr,"Income statement",7); fr+=1
for k,(dk) in [("data","g_data"),("voice","g_voice"),("momo","g_momo"),("digital","g_dig"),("othsvc","g_oth")]:
    lbl=dict((a,b) for a,b,_,_ in rev_lines)[k]
    frow(k,"  "+lbl,f"={h(k)}",lambda c,p,k=k,dk=dk: f"={p}{FR.get(k,fr)}*(1+{drv(dk,c)})")
frow("svc","Service revenue",f"=SUM(B{FR['data']}:B{FR['othsvc']})",lambda c,p:f"=SUM({c}{FR['data']}:{c}{FR['othsvc']})",bold=True)
frow("nonsvc","Non-service revenue",f"={h('nonsvc')}",lambda c,p:f"={c}{FR['svc']}*{drv('nonsvc',c)}")
frow("rev","Total revenue",f"=B{FR['svc']}+B{FR['nonsvc']}",lambda c,p:f"={c}{FR['svc']}+{c}{FR['nonsvc']}",bold=True)
frow("revg","  Revenue growth",f"={h('rev')}/{h('rev','B')}-1",lambda c,p:f"={c}{FR['rev']}/{p}{FR['rev']}-1",fmt=PCT)
frow("ebitda","EBITDA",f"={h('ebitda')}",lambda c,p:f"={c}{FR['rev']}*{drv('m_ebitda',c)}",bold=True)
frow("ebm","  EBITDA margin",f"=B{FR['ebitda']}/B{FR['rev']}",lambda c,p:f"={c}{FR['ebitda']}/{c}{FR['rev']}",fmt=PCT)
frow("da","Depreciation & amortisation",f"={h('dep')}+{h('amort')}",lambda c,p:f"={c}{FR['rev']}*{drv('da',c)}")
frow("ebit","Operating profit",f"=B{FR['ebitda']}-B{FR['da']}",lambda c,p:f"={c}{FR['ebitda']}-{c}{FR['da']}",bold=True)
frow("nfc","Net finance cost",f"={h('fcost')}-{h('finc')}",lambda c,p:f"={c}{FR['rev']}*{drv('nfc',c)}")
frow("pbt","Profit before tax",f"=B{FR['ebit']}-B{FR['nfc']}",lambda c,p:f"={c}{FR['ebit']}-{c}{FR['nfc']}",bold=True)
frow("tax","Income tax",f"={h('tax')}",lambda c,p:f"={c}{FR['pbt']}*{drv('taxr',c)}")
frow("gsl","Growth & Sustainability Levy",f"={h('gsl')}",lambda c,p:f"={c}{FR['pbt']}*{drv('gslr',c)}")
frow("pat","Profit after tax",f"=B{FR['pbt']}-B{FR['tax']}-B{FR['gsl']}",lambda c,p:f"={c}{FR['pbt']}-{c}{FR['tax']}-{c}{FR['gsl']}",bold=True)
frow("nm","  Net margin",f"=B{FR['pat']}/B{FR['rev']}",lambda c,p:f"={c}{FR['pat']}/{c}{FR['rev']}",fmt=PCT)
frow("eps","EPS (GHS)",f"=B{FR['pat']}*1000/{I['shares']}",lambda c,p:f"={c}{FR['pat']}*1000/{I['shares']}",fmt='0.000')
frow("dps","DPS (GHS)",f"={h('dps')}",lambda c,p:f"={c}{FR['eps']}*{drv('payout',c)}",fmt='0.000')
fr+=1; sec(fc,fr,"Free cash flow to equity (FCFE)",7); fr+=1
frow("f_pat","Profit after tax",f"=B{FR['pat']}",lambda c,p:f"={c}{FR['pat']}")
frow("f_da","Add: D&A",f"=B{FR['da']}",lambda c,p:f"={c}{FR['da']}")
frow("f_capex","Less: capex (ex-leases)",f"={h('cppe')}+{h('cint')}",lambda c,p:f"=-{c}{FR['rev']}*{drv('capex',c)}")
frow("f_lease","Less: lease principal payments",f"={h('lpay')}",lambda c,p:f"=-{c}{FR['rev']}*{drv('lease',c)}")
frow("f_nwc","Less: increase in net working capital","=0",lambda c,p:f"=-({c}{FR['rev']}-{p}{FR['rev']})*{drv('nwc',c)}")
frow("fcfe","FCFE",f"=SUM(B{FR['f_pat']}:B{FR['f_nwc']})",lambda c,p:f"=SUM({c}{FR['f_pat']}:{c}{FR['f_nwc']})",bold=True)
frow("fcfeps","FCFE per share (GHS)",f"=B{FR['fcfe']}*1000/{I['shares']}",lambda c,p:f"={c}{FR['fcfe']}*1000/{I['shares']}",fmt='0.000')
put(fc,fr+1,1,"2025A FCFE uses accrual PAT + D&A less actual cash capex and lease payments, on the same basis as the forecast.")
fc.freeze_panes="B4"
# fix green font only on pure links
for row in fc.iter_rows(min_col=2,max_col=2):
    for cell in row:
        if isinstance(cell.value,str) and cell.value.startswith("=Historical!") and all(ch not in cell.value[1:] for ch in "+-*/"): cell.font=GRN
        elif isinstance(cell.value,str) and cell.value.startswith("="): cell.font=Font(name=F,size=10,bold=cell.font.bold)

# ---------------- Valuation ----------------
title(val,"Valuation - FCFE DCF and dividend discount model",8)
V={}
put(val,3,1,"Key inputs",bold=True)
for i,(k,l,fmt) in enumerate([("ke","Cost of equity",PCT),("g","Terminal growth",PCT),("price","Current share price (GHS)",'0.00'),("shares","Shares in issue",'#,##0')]):
    put(val,4+i,1,l); put(val,4+i,2,"="+I[k],GRN,fmt); V[k]=f"$B${4+i}"
put(val,8,1,"Years from base date to price date"); put(val,8,2,f"=({I['pdate']}-{I['bdate']})/365",BLK,'0.00'); V["yrs"]="$B$8"
put(val,9,1,"Dividends paid since base date (GHS/share)"); put(val,9,2,"="+I['divsince'],GRN,'0.00'); V["div"]="$B$9"
sec(val,11,"A. FCFE discounted cash flow",8)
for i,y in enumerate(yrs[1:]): put(val,12,3+i,y,bold=True).alignment=Alignment(horizontal="right")
fcols=["C","D","E","F","G"]
put(val,13,1,"Period (years from base date)"); [put(val,13,3+i,i+1,BLK,'0') for i in range(5)]
put(val,14,1,"FCFE (GHS '000)"); [put(val,14,3+i,f"=Forecast!{c}{FR['fcfe']}",GRN,NUM) for i,c in enumerate(fcols)]
put(val,15,1,"Discount factor"); [put(val,15,3+i,f"=1/(1+{V['ke']})^{c}13",BLK,'0.0000') for i,c in enumerate(fcols)]
put(val,16,1,"PV of FCFE"); [put(val,16,3+i,f"={c}14*{c}15",BLK,NUM) for i,c in enumerate(fcols)]
rows=[("Sum of PV (2026-2030)","=SUM(C16:G16)",NUM),
 ("Terminal value at 2030","=G14*(1+%s)/(%s-%s)"%(V['g'],V['ke'],V['g']),NUM),
 ("PV of terminal value","=B18*G15",NUM),
 ("Add: cash & investments in securities (31-Dec-25)",f"={h('cash')}+{h('secs')}",NUM),
 ("Less: borrowings (31-Dec-25)",f"=-{h('borr')}",NUM),
 ("Equity value at base date (GHS '000)","=B17+B19+B20+B21",NUM),
 ("Value per share at base date (GHS)","=B22*1000/%s"%V['shares'],'0.00'),
 ("Value per share at price date (GHS)","=B23*(1+%s)^%s-%s"%(V['ke'],V['yrs'],V['div']),'0.00'),
 ("Terminal value as % of equity value","=B19/B22",PCT)]
for i,(l,f,fmt) in enumerate(rows):
    put(val,17+i,1,l,bold=(i in (5,7))); put(val,17+i,2,f,GRN if f.startswith("=Historical") or f.startswith("=-Historical") else BLK,fmt,bold=(i in (5,7)))
put(val,20,8,"Leases are treated as operating cash outflows inside FCFE, so they are not deducted again here.")
put(val,24,8,"Rolled forward at Ke, less dividends already paid.")
V["dcf"]="$B$24"
sec(val,27,"B. Dividend discount model",8)
for i,y in enumerate(yrs[1:]): put(val,28,3+i,y,bold=True).alignment=Alignment(horizontal="right")
put(val,29,1,"DPS (GHS)"); [put(val,29,3+i,f"=Forecast!{c}{FR['dps']}",GRN,'0.000') for i,c in enumerate(fcols)]
put(val,30,1,"PV of DPS"); [put(val,30,3+i,f"={c}29*{c}15",BLK,'0.000') for i,c in enumerate(fcols)]
drows=[("Sum of PV of DPS","=SUM(C30:G30)",'0.00'),
 ("Terminal value of DPS at 2030","=G29*(1+%s)/(%s-%s)"%(V['g'],V['ke'],V['g']),'0.00'),
 ("PV of terminal value","=B32*G15",'0.00'),
 ("Add: FY2025 final dividend declared (paid 2026)","=%s"%V['div'],'0.00'),
 ("Value per share at base date (GHS)","=B31+B33+B34",'0.00'),
 ("Value per share at price date (GHS)","=B35*(1+%s)^%s-%s"%(V['ke'],V['yrs'],V['div']),'0.00')]
for i,(l,f,fmt) in enumerate(drows):
    put(val,31+i,1,l,bold=(i==5)); put(val,31+i,2,f,BLK,fmt,bold=(i==5))
put(val,34,8,"Declared before base date, so it belongs to holders at 31-Dec-25.")
V["ddm"]="$B$36"
sec(val,38,"C. Summary",8)
srows=[("DCF value per share (GHS)","=B24",'0.00'),("DDM value per share (GHS)","=B36",'0.00'),
 ("Blended fair value per share (GHS)","=B39*%s+B40*%s"%(I['wdcf'],I['wddm']),'0.00'),
 ("Current share price (GHS)","=%s"%V['price'],'0.00'),
 ("Implied upside / (downside)","=B41/B42-1",PCT),
 ("Model signal (illustrative, not advice)",'=IF(B43>0.15,"Undervalued",IF(B43<-0.1,"Overvalued","Fairly valued"))',None),
 ("Implied P/E at fair value (FY2025 EPS)","=B41/Forecast!B%d"%FR['eps'],X),
 ("Market P/E (FY2025 EPS)","=B42/Forecast!B%d"%FR['eps'],X),
 ("Market dividend yield (FY2025 DPS)","=Forecast!B%d/B42"%FR['dps'],PCT)]
for i,(l,f,fmt) in enumerate(srows):
    put(val,39+i,1,l,bold=(i in (2,4))); put(val,39+i,2,f,BLK,fmt,bold=(i in (2,4)))
sec(val,49,"D. Sensitivity - DCF value per share at price date (GHS): cost of equity (rows) vs terminal growth (columns)",8)
put(val,50,2,"Ke \\ g",bold=True)
goff=[-0.02,-0.01,0,0.01,0.02]; koff=[-0.02,-0.01,0,0.01,0.02]
for j,o in enumerate(goff): put(val,50,3+j,f"={V['g']}+({o})",BLK,PCT,bold=True)
for i,o in enumerate(koff):
    rr=51+i; put(val,rr,2,f"={V['ke']}+({o})",BLK,PCT,bold=True)
    for j in range(5):
        cl=L(3+j); k=f"$B{rr}"; g=f"{cl}$50"
        f=f"=((NPV({k},$C$14:$G$14)+$G$14*(1+{g})/({k}-{g})/(1+{k})^5+$B$20+$B$21)*1000/{V['shares']})*(1+{k})^{V['yrs']}-{V['div']}"
        put(val,rr,3+j,f,BLK,'0.00',fill=YEL if (i==2 and j==2) else None)
put(val,57,1,"Centre cell (yellow) equals the base-case DCF value above.")

# ---------------- Ratios ----------------
title(rat,"Ratio analysis",4)
for c,t in [(1,"Ratio"),(2,"FY2024"),(3,"FY2025"),(4,"Definition / comment")]: put(rat,3,c,t,bold=True)
RR=4
def rrow(label,f24,f25,fmt,note):
    global RR
    put(rat,RR,1,label)
    if f24: put(rat,RR,2,f24.replace("{c}","B"),BLK,fmt)
    else: put(rat,RR,2,"n/a").alignment=Alignment(horizontal="right")
    put(rat,RR,3,f25.replace("{c}","C"),BLK,fmt); put(rat,RR,4,note); RR+=1
def rs(t):
    global RR
    RR+=1; sec(rat,RR,t,4); RR+=1
def hh(k): return f"Historical!{{c}}{H[k]}"
def hp(k): return f"Historical!B{H[k]}"
rs("Growth & mix")
rrow("Revenue growth",None,f"={hh('rev')}/{hp('rev')}-1",PCT,"")
rrow("Service revenue growth",None,f"={hh('svc')}/{hp('svc')}-1",PCT,"")
rrow("Data share of service revenue",f"={hh('data')}/{hh('svc')}",f"={hh('data')}/{hh('svc')}",PCT,"Data is now the main revenue engine")
rrow("Mobile Money share of service revenue",f"={hh('momo')}/{hh('svc')}",f"={hh('momo')}/{hh('svc')}",PCT,"")
rrow("Voice share of service revenue",f"={hh('voice')}/{hh('svc')}",f"={hh('voice')}/{hh('svc')}",PCT,"Structural decline as traffic moves to VoIP")
rs("Profitability")
rrow("EBITDA margin",f"={hh('ebitda')}/{hh('rev')}",f"={hh('ebitda')}/{hh('rev')}",PCT,"")
rrow("Operating margin",f"={hh('ebit')}/{hh('rev')}",f"={hh('ebit')}/{hh('rev')}",PCT,"")
rrow("Net margin",f"={hh('pat')}/{hh('rev')}",f"={hh('pat')}/{hh('rev')}",PCT,"")
rrow("Effective tax rate incl. levy",f"=({hh('tax')}+{hh('gsl')})/{hh('pbt')}",f"=({hh('tax')}+{hh('gsl')})/{hh('pbt')}",PCT,"Income tax + Growth & Sustainability Levy over PBT")
rrow("Return on average equity",None,f"={hh('pat')}/AVERAGE({hp('eq')},{hh('eq')})",PCT,"")
rrow("Return on assets (ex-MoMo float)",f"={hh('pat')}/({hh('ta')}-{hh('float')})",f"={hh('pat')}/({hh('ta')}-{hh('float')})",PCT,"Float is customer money held in trust; excluding it shows true asset productivity")
rs("Liquidity & leverage (ex-MoMo float)")
rrow("Current ratio (reported)",f"={hh('ca')}/{hh('cl')}",f"={hh('ca')}/{hh('cl')}",'0.00"x"',"Distorted by float and e-money obligations")
rrow("Current ratio (ex-float)",f"=({hh('ca')}-{hh('float')})/({hh('cl')}-{hh('emoney')})",f"=({hh('ca')}-{hh('float')})/({hh('cl')}-{hh('emoney')})",'0.00"x"',"Strips customer float from both sides; liquidity is comfortable")
rrow("Lease liabilities (GHS '000)",f"={hh('lease_nc')}+{hh('lease_c')}",f"={hh('lease_nc')}+{hh('lease_c')}",NUM,"")
rrow("Net debt incl. leases (GHS '000)",f"={hh('borr')}+{hh('lease_nc')}+{hh('lease_c')}-{hh('cash')}-{hh('secs')}",f"={hh('borr')}+{hh('lease_nc')}+{hh('lease_c')}-{hh('cash')}-{hh('secs')}",NUM,"Borrowings + leases - cash - investments in securities")
rrow("Net debt incl. leases / EBITDA",f"=B{RR-1}/{hh('ebitda')}",f"=C{RR-1}/{hh('ebitda')}",'0.00"x"',"Very low leverage")
rs("Cash flow & investment")
rrow("Capex ex-leases / revenue",f"=-({hh('cppe')}+{hh('cint')})/{hh('rev')}",f"=-({hh('cppe')}+{hh('cint')})/{hh('rev')}",PCT,"")
rrow("Operating cash flow before dividends (GHS '000)",f"={hh('cfo')}-{hh('divp')}",f"={hh('cfo')}-{hh('divp')}",NUM,"Reclassifies dividends out of operating activities")
rrow("Cash conversion (OCF before dividends / EBITDA)",f"=B{RR-1}/{hh('ebitda')}",f"=C{RR-1}/{hh('ebitda')}",PCT,"After tax and interest")
rrow("Cash FCFE (OCF before div - capex - leases)",None,f"=C{RR-2}+{hh('cppe')}+{hh('cint')}+{hh('lpay')}",NUM,"FY2024 lease payments not legible in source")
rrow("Dividend payout ratio",None,f"={hh('dps')}*{hh('shares')}/1000/{hh('pat')}",PCT,"Reported 81%")
rs("Market multiples at current price (FY2025)")
rrow("Market capitalisation (GHS '000)",None,f"={I['price']}*{hh('shares')}/1000",NUM,"Price per Inputs")
mc=RR-1
rrow("Enterprise value incl. leases (GHS '000)",None,f"=C{mc}+{hh('borr')}+{hh('lease_nc')}+{hh('lease_c')}-{hh('cash')}-{hh('secs')}",NUM,"")
rrow("P/E",None,f"={I['price']}/{hh('eps')}",X,"")
rrow("EV/EBITDA",None,f"=C{mc+1}/{hh('ebitda')}",X,"")
rrow("Price / book",None,f"=C{mc}/{hh('eq')}",X,"")
rrow("Dividend yield",None,f"={hh('dps')}/{I['price']}",PCT,"")
rat.freeze_panes="B4"

# ---------------- Cover ----------------
title(cover,"MTN Ghana (Scancom PLC) - Equity Valuation Model",3)
lines=[("Analyst","Daniel Nii Tetteh Tackie"),("Prepared","November 2026"),("Ticker","MTNGH - Ghana Stock Exchange"),
("Question","What is Scancom PLC worth per share, and how does that compare with the GSE price?"),
("Method","Driver-based 5-year forecast (2026-2030); FCFE DCF and dividend discount model; CAPM cost of equity in GHS; sensitivity of value to Ke and growth"),
("Data","FY2025 audited results (with restated FY2024), MTN Ghana investor publications; BoG T-bill rates; GSE prices. See Sources tab.")]
for i,(a,b) in enumerate(lines):
    put(cover,3+i,1,a,bold=True); c=put(cover,3+i,2,b); cover.merge_cells(start_row=3+i,start_column=2,end_row=3+i,end_column=3); c.alignment=Alignment(wrap_text=True,vertical="top")
    cover.row_dimensions[3+i].height=30 if len(b)>70 else 15
sec(cover,10,"Key outputs (live)",3)
outs=[("Cost of equity","="+I['ke'],PCT),("DCF value per share (GHS)","=Valuation!B24",'0.00'),("DDM value per share (GHS)","=Valuation!B36",'0.00'),("Blended fair value (GHS)","=Valuation!B41",'0.00'),("Share price (GHS)","=Valuation!B42",'0.00'),("Implied upside / (downside)","=Valuation!B43",PCT),("Model signal","=Valuation!B44",None),("FY2025 P/E at market","=Valuation!B46",X)]
for i,(a,f,fmt) in enumerate(outs): put(cover,11+i,1,a); put(cover,11+i,2,f,GRN,fmt,bold=True)
sec(cover,20,"How to use",3)
guide=["Inputs: change the share price, cost-of-equity inputs and yearly drivers (blue/yellow cells). Everything else recalculates.",
"Historical: audited FY2024-FY2025 statements with tie-out checks (balance sheet and cash).",
"Ratios: profitability, liquidity and leverage, with MoMo float stripped out where it distorts the picture.",
"Forecast: revenue built line by line (data, voice, MoMo, digital), then margins, tax, EPS, DPS and FCFE.",
"Valuation: DCF, DDM, blended value and a Ke x g sensitivity grid.",
"Colour code: blue = input, black = formula, green = link to another sheet, yellow = key assumption.",
"Disclaimer: educational portfolio model, not investment advice."]
for i,t in enumerate(guide): c=put(cover,21+i,1,t); cover.merge_cells(start_row=21+i,start_column=1,end_row=21+i,end_column=3)

# ---------------- Sources ----------------
title(src,"Sources",2)
S=[("FY2025 financial report (statements, revenue split, capex, shares)","https://mtn.com.gh/wp-content/uploads/2026/03/SCANCOM-PLC-MTN-GHANA-2025-Financial-Report.pdf"),
("FY2025 results release (IC Securities mirror)","https://cms.ic.africa/wp-content/uploads/2026/03/PR_060_SCANCOM_PLC_PERFORMANCE_FOR_THE_YEAR_ENDED_31_DECEMBER_2025_2_.pdf"),
("2026 AGM: total FY2025 dividend GHS 0.48, 81% payout","https://mtn.com.gh/newsabout/mtn-ghana-delivers-strong-revenue-growth-declares-ghs-6-4-billion-dividend-at-2026-agm/"),
("2026 guidance (service revenue growth, EBITDA margin)","https://africanfinancials.com/?p=154144"),
("Dividend policy 60-80% (CFO comments)","https://www.telecomschamber.org/?p=7470"),
("Share price GHS 6.67, 30 Oct 2026","https://www.mansamarkets.com/ghana/summary/2026-10-30"),
("364-day T-bill 9.6739%, 26 Oct 2026 (BoG figures, reported)","https://yen.com.gh/business-economy/money/314616-ghanaian-man-uses-bank-ghana-rates-explain-ghghs50000-treasury-bill-returns/"),
("Known source issues","Total equity FY2025 differs from components by GHS 355k; FY2024 financing cash-flow lines are not legible in the PDF (total used); FY2024 restated for an IFRS 16 lease remeasurement error.")]
for i,(a,b) in enumerate(S): put(src,3+i,1,a,bold=True).alignment=Alignment(wrap_text=True,vertical="top"); put(src,3+i,2,b).alignment=Alignment(wrap_text=True,vertical="top"); src.row_dimensions[3+i].height=30

wb.save("MTN_Ghana_Valuation_Model.xlsx")
print("ok")
