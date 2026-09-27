from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.comments import Comment
from openpyxl.formatting.rule import FormulaRule, CellIsRule
from datetime import date

F="Arial"
NAVY="0F172A"; BLUE="2563EB"; CYAN="22D3EE"; MIST="F1F5F9"
title_f=Font(name=F,size=16,bold=True,color=NAVY)
h_f=Font(name=F,size=11,bold=True,color="FFFFFF")
h_fill=PatternFill("solid",fgColor=BLUE)
sec_f=Font(name=F,size=12,bold=True,color=BLUE)
inp_f=Font(name=F,size=11,color="0000FF")
inp_fill=PatternFill("solid",fgColor="FFFF00")
norm=Font(name=F,size=11,color="000000")
bold=Font(name=F,size=11,bold=True,color="000000")
link_f=Font(name=F,size=11,color="008000")
note_f=Font(name=F,size=9,italic=True,color="55627A")
thin=Side(style="thin",color="CBD5E1"); box=Border(left=thin,right=thin,top=thin,bottom=thin)
kpi_fill=PatternFill("solid",fgColor=MIST)
JOD='#,##0.00 "د.أ";(#,##0.00) "د.أ";"-"'
USD='"$"#,##0.00'
PCT='0.0%;(0.0%);"-"'
INT='#,##0;(#,##0);"-"'
DT='yyyy-mm-dd'

wb=Workbook()
def sheet(name, first=False):
    ws=wb.active if first else wb.create_sheet()
    ws.title=name; ws.sheet_view.rightToLeft=True
    return ws
def header(ws,row,labels,widths=None):
    for i,l in enumerate(labels,1):
        c=ws.cell(row=row,column=i,value=l); c.font=h_f; c.fill=h_fill
        c.alignment=Alignment(horizontal="center",vertical="center",wrap_text=True); c.border=box
    ws.row_dimensions[row].height=32
    if widths:
        for i,w in enumerate(widths,1): ws.column_dimensions[ws.cell(row=1,column=i).column_letter].width=w
def inp(c,v,fmt=None):
    c.value=v; c.font=inp_f; c.fill=inp_fill; c.border=box
    if fmt: c.number_format=fmt
def fx(c,v,fmt=None,b=False):
    c.value=v; c.font=bold if b else norm; c.border=box
    if fmt: c.number_format=fmt

# ---------- Start ----------
s=sheet("ابدأ هنا",True)
s.column_dimensions["A"].width=26; s.column_dimensions["B"].width=80
s["A1"]="naqra | نقرة — ملف إدارة المشروع"; s["A1"].font=title_f
rows=[("كيف تستعمل الملف",None),
("الخلايا الصفراء بخط أزرق","هاي المدخلات، إنت بتعبيها أو بتغيرها. باقي الخلايا معادلات بتنحسب لحالها، لا تكتب فوقها."),
("الخط الأخضر","رقم جاي من صفحة ثانية بالملف."),
("صف المثال","بأول صف بصفحات الطلبات والمخزون والمصاريف والإعلانات في مثال عشان تشوف طريقة التعبئة. امسحه أو اكتب فوقه."),
("الصفحات",None),
("حاسبة التسعير","حط سعر المورد والشحن والجمرك، وبتطلعلك تكلفة الستاند الواحد واصل، والربح لكل باقة، وكم طلب بدك لترجع رأس مالك."),
("الطلبات","سجل كل طلب: الزبون، المدينة، الباقة، السعر، الحالة، والرابط اللي برمجته. الربح بينحسب لحاله."),
("المخزون","سجل كل طلبية بتشتريها من المورد. الملف بيطرح المبيعات وبينبهك لما المخزون يقل."),
("المصاريف","كل دينار بتصرفه: بضاعة، شحن، إعلانات، تغليف، اشتراكات. سجل الإعلانات هون كمان عشان تنحسب بالربح."),
("الإعلانات","تتبع أداء كل حملة أسبوعياً: الصرف، الرسائل، الطلبات، تكلفة الطلب، والعائد. (للمتابعة بس، الصرف الحقيقي بينحسب من صفحة المصاريف)."),
("الملخص","ملخص شهري تلقائي: عدد الطلبات، المبيعات، المصاريف، وصافي الربح."),
("قاعدة ذهبية","سجل كل طلب وكل مصروف بنفس اليوم. خمس دقايق باليوم بتوفر عليك ساعات آخر الشهر.")]
r=3
for a,b in rows:
    s.cell(row=r,column=1,value=a).font=sec_f if b is None else bold
    if b: 
        c=s.cell(row=r,column=2,value=b); c.font=norm; c.alignment=Alignment(wrap_text=True,vertical="top")
    r+=1
s.cell(row=r+1,column=1,value="مثال خلية إدخال").font=bold; inp(s.cell(row=r+1,column=2),"اكتب هون")

# ---------- Pricing ----------
p=sheet("حاسبة التسعير")
for col,w in zip("ABCDEFGH",[38,16,16,16,16,16,16,14]): p.column_dimensions[col].width=w
p["A1"]="حاسبة التسعير والربح"; p["A1"].font=title_f
p["A3"]="المدخلات (غيّرها حسب الأسعار الحقيقية)"; p["A3"].font=sec_f
inputs=[
("سعر الستاند من المورد (دولار)",0.70,USD,"تقدير من منتجات مشابهة على علي بابا (0.50–0.79$ للـ100 قطعة). حط السعر الحقيقي من صفحة المورد."),
("عدد القطع بالطلبية",100,INT,"أقل كمية شائعة عند الموردين: 100 قطعة."),
("سعر صرف الدولار (دينار)",0.709,'0.000',"سعر الصرف الرسمي للدينار الأردني مربوط تقريباً على 0.709."),
("تكلفة الشحن الكلية للأردن (دينار)",35,JOD,"تقدير لشحن سريع 3–5 كغ. تأكد من المورد أو شركة الشحن."),
("الجمرك والضريبة (% من البضاعة + الشحن)",0.16,PCT,"تقدير فقط (ضريبة مبيعات عامة 16%). تأكد من شركة الشحن أو مخلّص جمركي."),
("تغليف وكرت تعليمات للقطعة (دينار)",0.15,JOD,"ظرف أو علبة صغيرة + كرت تعليمات."),
("تكلفة العينات (دينار)",25,JOD,"عينات قبل الطلبية الكبيرة. بتنحسب على تكلفة الطلبية الأولى."),
("تكلفة الإعلان المتوقعة لكل طلب (دينار)",3.5,JOD,"تقدير لبداية الحملة (2–5 د.أ). حدّثه من صفحة الإعلانات."),
("تكلفة التوصيل عليك لكل طلب (دينار)",2.5,JOD,"سعر شركة التوصيل داخل عمّان تقريباً."),
("رسوم التوصيل اللي بتاخذها من الزبون (دينار)",2,JOD,"حطها 0 إذا التوصيل مجاني."),
]
for i,(lab,val,fmt,note) in enumerate(inputs):
    r=4+i
    p.cell(row=r,column=1,value=lab).font=norm
    inp(p.cell(row=r,column=2),val,fmt)
    p.cell(row=r,column=2).comment=Comment(note,"naqra")
    c=p.cell(row=r,column=3,value=note); c.font=note_f
# B4 price B5 qty B6 fx B7 ship B8 customs B9 pack B10 samples B11 ad B12 delcost B13 delfee
p["A15"]="النتائج"; p["A15"].font=sec_f
res=[("تكلفة البضاعة (دينار)","=B4*B5*B6"),
("الجمرك والضريبة (دينار)","=(B16+B7)*B8"),
("التكلفة الكلية للطلبية (دينار)","=B16+B7+B17+B10+B9*B5"),
("تكلفة الستاند الواحد واصل لإيدك (دينار)","=IFERROR(B18/B5,0)")]
for i,(lab,f) in enumerate(res):
    r=16+i; p.cell(row=r,column=1,value=lab).font=bold if r==19 else norm
    fx(p.cell(row=r,column=2),f,JOD,b=(r==19))
p["B19"].fill=kpi_fill
p["A21"]="الربح لكل باقة (غيّر سعر البيع بالعمود C)"; p["A21"].font=sec_f
header(p,22,["الباقة","عدد الستاندات","سعر البيع (دينار)","تكلفة البضاعة","صافي التوصيل","تكلفة الإعلان","الربح الصافي","هامش الربح"])
p.column_dimensions["A"].width=38
packs=[("ستاند واحد",1,10),("باقة ستاندين",2,17),("باقة 3 ستاندات",3,23),("باقة 5 ستاندات (للفروع)",5,35)]
for i,(n,q,pr) in enumerate(packs):
    r=23+i
    fx(p.cell(row=r,column=1),n)
    inp(p.cell(row=r,column=2),q,INT)
    inp(p.cell(row=r,column=3),pr,JOD)
    fx(p.cell(row=r,column=4),f"=B{r}*$B$19",JOD)
    fx(p.cell(row=r,column=5),"=$B$13-$B$12",JOD)
    fx(p.cell(row=r,column=6),"=$B$11",JOD)
    fx(p.cell(row=r,column=7),f"=C{r}-D{r}+E{r}-F{r}",JOD,b=True)
    fx(p.cell(row=r,column=8),f"=IFERROR(G{r}/C{r},0)",PCT)
p.conditional_formatting.add("G23:G26",CellIsRule(operator="lessThan",formula=["0"],font=Font(name=F,color="DC2626",bold=True)))
p["A28"]="استرجاع رأس المال"; p["A28"].font=sec_f
fx(p["A29"],"عدد الطلبات (ستاند واحد) لترجع تكلفة الطلبية"); fx(p["B29"],"=IFERROR(ROUNDUP(B18/G23,0),0)",INT,b=True)
fx(p["A30"],"إذا بعت كل القطع كستاند واحد: المبيعات المتوقعة"); fx(p["B30"],"=B5*C23",JOD)
fx(p["A31"],"الربح الصافي المتوقع من الطلبية كاملة (ستاند واحد)"); fx(p["B31"],"=B5*G23-(B10)",JOD,b=True)
p["C31"]="العينات مطروحة مرة وحدة لأنها داخلة بتكلفة القطعة وبالطلبية."; p["C31"].font=note_f
p["B31"].value="=B5*G23"
p["C31"].value="تكلفة العينات داخلة أصلاً بتكلفة القطعة الواحدة."

# ---------- Orders ----------
o=sheet("الطلبات")
o["A1"]="سجل الطلبات"; o["A1"].font=title_f
o["A2"]="عبّي الخلايا البيضاء. أعمدة التكلفة والربح بتنحسب لحالها. الطلب الملغي ما بينحسب."; o["A2"].font=note_f
cols=["رقم الطلب","التاريخ","اسم المحل / الزبون","رقم الهاتف","المدينة","نوع النشاط","مصدر الطلب","عدد الستاندات","سعر البيع (دينار)","رسوم التوصيل من الزبون","تكلفة التوصيل عليك","طريقة الدفع","الحالة","رابط التقييم المبرمج","تكلفة البضاعة","الربح","ملاحظات"]
header(o,4,cols,[10,12,24,15,12,16,14,10,12,12,12,14,14,32,12,12,24])
N=500
first=5; last=first+N-1
ex=["N-001",date(2026,10,5),"كافيه المثال (مثال – امسحه)","0790000000","عمّان","مطعم / كافيه","انستغرام",2,17,2,2.5,"كاش عند الاستلام","تم التسليم","naqrajo.com/r/example",None,None,"برمجت الستاندين وجربتهم على آيفون وأندرويد"]
for r in range(first,last+1):
    for ci in range(1,18):
        c=o.cell(row=r,column=ci); c.font=norm; c.border=box
    o.cell(row=r,column=2).number_format=DT
    for ci in (9,10,11,15,16): o.cell(row=r,column=ci).number_format=JOD
    o.cell(row=r,column=15).value=f'=IF(OR(H{r}="",M{r}="ملغي"),0,H{r}*\'حاسبة التسعير\'!$B$19)'
    o.cell(row=r,column=16).value=f'=IF(OR(I{r}="",M{r}="ملغي"),0,I{r}+J{r}-K{r}-O{r})'
for ci,v in enumerate(ex,1):
    if v is not None: o.cell(row=first,column=ci).value=v
dvs=[("E",'"عمّان,الزرقاء,إربد,السلط,مادبا,العقبة,جرش,عجلون,المفرق,الكرك,الطفيلة,معان"'),
("F",'"مطعم / كافيه,صالون,عيادة,محل تجاري,جيم,فندق,أخرى"'),
("G",'"انستغرام,فيسبوك,تيك توك,واتساب,توصية زبون,زيارة مباشرة,أخرى"'),
("L",'"كاش عند الاستلام,كليك CliQ,تحويل بنكي,محفظة إلكترونية"'),
("M",'"جديد,تم التأكيد,قيد التوصيل,تم التسليم,ملغي"')]
for col,lst in dvs:
    dv=DataValidation(type="list",formula1=lst,allow_blank=True); o.add_data_validation(dv); dv.add(f"{col}{first}:{col}{last}")
o.conditional_formatting.add(f"A{first}:Q{last}",FormulaRule(formula=[f'$M{first}="ملغي"'],fill=PatternFill("solid",fgColor="FEE2E2")))
o.conditional_formatting.add(f"A{first}:Q{last}",FormulaRule(formula=[f'$M{first}="تم التسليم"'],fill=PatternFill("solid",fgColor="DCFCE7")))
o.freeze_panes="C5"

# ---------- Inventory ----------
v=sheet("المخزون")
v["A1"]="المخزون"; v["A1"].font=title_f
for col,w in zip("ABCDEF",[34,18,14,16,30,4]): v.column_dimensions[col].width=w
v["A3"]="الملخص"; v["A3"].font=sec_f
fx(v["A4"],"إجمالي القطع المشتراة"); fx(v["B4"],"=SUM(C12:C111)",INT)
fx(v["A5"],"القطع المباعة (غير الملغية)"); fx(v["B5"],'=SUMIFS(\'الطلبات\'!H5:H504,\'الطلبات\'!M5:M504,"<>ملغي")',INT); v["B5"].font=link_f
fx(v["A6"],"المتبقي بالمخزون"); fx(v["B6"],"=B4-B5",INT,b=True); v["B6"].fill=kpi_fill
fx(v["A7"],"نبهني لما يوصل المخزون لـ"); inp(v["B7"],20,INT)
fx(v["A8"],"الحالة"); fx(v["B8"],'=IF(B6<=B7,"اطلب بضاعة جديدة","المخزون كافي")',None,b=True)
v.conditional_formatting.add("B8",FormulaRule(formula=['$B$6<=$B$7'],fill=PatternFill("solid",fgColor="FEE2E2"),font=Font(name=F,bold=True,color="DC2626")))
v.conditional_formatting.add("B8",FormulaRule(formula=['$B$6>$B$7'],fill=PatternFill("solid",fgColor="DCFCE7"),font=Font(name=F,bold=True,color="166534")))
v["A10"]="طلبيات الشراء من المورد"; v["A10"].font=sec_f
header(v,11,["التاريخ","المورد","الكمية","التكلفة الكلية واصل (دينار)","ملاحظات"])
v.column_dimensions["A"].width=34
for r in range(12,112):
    for ci in range(1,6): c=v.cell(row=r,column=ci); c.font=norm; c.border=box
    v.cell(row=r,column=1).number_format=DT; v.cell(row=r,column=3).number_format=INT; v.cell(row=r,column=4).number_format=JOD
for ci,val in enumerate([date(2026,10,1),"مورد علي بابا (مثال – امسحه)",100,125,"ستاند PVC مغناطيسي NTAG213"],1):
    v.cell(row=12,column=ci).value=val

# ---------- Expenses ----------
e=sheet("المصاريف")
e["A1"]="المصاريف"; e["A1"].font=title_f
e["A2"]="سجل كل مصروف، ومنها صرف الإعلانات. الملخص الشهري بيعتمد على هالصفحة."; e["A2"].font=note_f
header(e,4,["التاريخ","البند","الوصف","المبلغ (دينار)"],[12,16,40,14])
for r in range(5,505):
    for ci in range(1,5): c=e.cell(row=r,column=ci); c.font=norm; c.border=box
    e.cell(row=r,column=1).number_format=DT; e.cell(row=r,column=4).number_format=JOD
dv=DataValidation(type="list",formula1='"بضاعة,شحن وجمرك,إعلانات,تغليف,توصيل,تصميم وطباعة,اشتراكات وأدوات,تسجيل ورسوم,أخرى"',allow_blank=True); e.add_data_validation(dv); dv.add("B5:B504")
for ci,val in enumerate([date(2026,10,1),"بضاعة","طلبية 100 ستاند من علي بابا شامل الشحن (مثال – امسحه)",125],1):
    e.cell(row=5,column=ci).value=val
e["F4"]="المجموع حسب البند"; e["F4"].font=sec_f; e.column_dimensions["F"].width=20; e.column_dimensions["G"].width=14
cats=["بضاعة","شحن وجمرك","إعلانات","تغليف","توصيل","تصميم وطباعة","اشتراكات وأدوات","تسجيل ورسوم","أخرى"]
for i,cat in enumerate(cats):
    r=5+i; fx(e.cell(row=r,column=6),cat); fx(e.cell(row=r,column=7),f'=SUMIFS($D$5:$D$504,$B$5:$B$504,F{r})',JOD)
fx(e.cell(row=14,column=6),"الإجمالي",b=True); fx(e.cell(row=14,column=7),"=SUM(G5:G13)",JOD,b=True)

# ---------- Ads ----------
a=sheet("الإعلانات")
a["A1"]="متابعة أداء الإعلانات"; a["A1"].font=title_f
a["A2"]="سجل أرقام كل حملة أسبوعياً من Meta Ads Manager. هاي الصفحة للمتابعة، والصرف الحقيقي سجله بصفحة المصاريف."; a["A2"].font=note_f
header(a,4,["بداية الأسبوع","اسم الحملة","المنصة","الصرف (دينار)","الوصول (Reach)","الرسائل","الطلبات","المبيعات (دينار)","تكلفة الرسالة","تكلفة الطلب","العائد على الإعلان (ROAS)"],[12,26,14,12,12,10,10,12,12,12,14])
for r in range(5,209):
    for ci in range(1,12): c=a.cell(row=r,column=ci); c.font=norm; c.border=box
    a.cell(row=r,column=1).number_format=DT
    for ci in (4,8,9,10): a.cell(row=r,column=ci).number_format=JOD
    a.cell(row=r,column=5).number_format=INT
    a.cell(row=r,column=9).value=f'=IF(OR(D{r}="",F{r}=0,F{r}=""),"",D{r}/F{r})'
    a.cell(row=r,column=10).value=f'=IF(OR(D{r}="",G{r}=0,G{r}=""),"",D{r}/G{r})'
    a.cell(row=r,column=11).value=f'=IF(OR(D{r}="",D{r}=0),"",H{r}/D{r})'
    a.cell(row=r,column=11).number_format='0.00"x"'
dv=DataValidation(type="list",formula1='"انستغرام,فيسبوك,انستغرام + فيسبوك,تيك توك"',allow_blank=True); a.add_data_validation(dv); dv.add("C5:C208")
for ci,val in enumerate([date(2026,10,6),"إطلاق – فيديو النقرة (مثال – امسحه)","انستغرام + فيسبوك",35,12000,40,9,160],1):
    a.cell(row=5,column=ci).value=val
a["M4"]="الإجمالي"; a["M4"].font=sec_f; a.column_dimensions["M"].width=22; a.column_dimensions["N"].width=14
tot=[("إجمالي الصرف","=SUM(D5:D208)",JOD),("إجمالي الطلبات","=SUM(G5:G208)",INT),("متوسط تكلفة الطلب",'=IFERROR(N5/N6,0)',JOD),("إجمالي المبيعات من الإعلانات","=SUM(H5:H208)",JOD),("العائد الكلي (ROAS)",'=IFERROR(N8/N5,0)','0.00"x"')]
for i,(l,f,fm) in enumerate(tot):
    fx(a.cell(row=5+i,column=13),l); fx(a.cell(row=5+i,column=14),f,fm,b=True)

# ---------- Summary ----------
m=sheet("الملخص")
m["A1"]="الملخص الشهري"; m["A1"].font=title_f
for col,w in zip("ABCDEFGH",[16,14,16,16,16,16,16,4]): m.column_dimensions[col].width=w
fx(m["A3"],"أول شهر بالجدول"); inp(m["B3"],date(2026,10,1),DT)
m["A5"]="أرقام كلية"; m["A5"].font=sec_f
k=[("عدد الطلبات",'=COUNTIFS(\'الطلبات\'!H5:H504,">0",\'الطلبات\'!M5:M504,"<>ملغي")',INT),
("إجمالي المبيعات",'=SUMIFS(\'الطلبات\'!I5:I504,\'الطلبات\'!M5:M504,"<>ملغي")',JOD),
("متوسط قيمة الطلب","=IFERROR(B7/B6,0)",JOD),
("إجمالي المصاريف","='المصاريف'!G14",JOD),
("صافي الربح (نقدي)","=SUM(G23:G34)",JOD),
("المتبقي بالمخزون","='المخزون'!B6",INT)]
for i,(l,f,fm) in enumerate(k):
    r=6+i; fx(m.cell(row=r,column=1),l,b=True); fx(m.cell(row=r,column=2),f,fm,b=True); m.cell(row=r,column=2).fill=kpi_fill
    if "'" in f: m.cell(row=r,column=2).font=Font(name=F,bold=True,color="008000")
m["A14"]="صافي الربح = المبيعات + رسوم التوصيل المحصلة − تكلفة التوصيل − كل المصاريف (بضاعة، شحن، إعلانات...). يعني الفلوس اللي فعلاً ضلت معك."; m["A14"].font=note_f
m["A21"]="حسب الشهر"; m["A21"].font=sec_f
header(m,22,["الشهر","عدد الطلبات","المبيعات","رسوم التوصيل المحصلة","تكلفة التوصيل","المصاريف","صافي الربح"])
m.column_dimensions["A"].width=16
O="'الطلبات'"; E="'المصاريف'"
for i in range(12):
    r=23+i
    fx(m.cell(row=r,column=1),"=B3" if i==0 else f"=EDATE(A{r-1},1)",'mmm yyyy')
    rng=f'{O}!$B$5:$B$504,">="&A{r},{O}!$B$5:$B$504,"<"&EDATE(A{r},1),{O}!$M$5:$M$504,"<>ملغي"'
    fx(m.cell(row=r,column=2),f'=COUNTIFS({rng},{O}!$H$5:$H$504,">0")',INT)
    fx(m.cell(row=r,column=3),f'=SUMIFS({O}!$I$5:$I$504,{rng})',JOD)
    fx(m.cell(row=r,column=4),f'=SUMIFS({O}!$J$5:$J$504,{rng})',JOD)
    fx(m.cell(row=r,column=5),f'=SUMIFS({O}!$K$5:$K$504,{rng})',JOD)
    fx(m.cell(row=r,column=6),f'=SUMIFS({E}!$D$5:$D$504,{E}!$A$5:$A$504,">="&A{r},{E}!$A$5:$A$504,"<"&EDATE(A{r},1))',JOD)
    fx(m.cell(row=r,column=7),f'=C{r}+D{r}-E{r}-F{r}',JOD,b=True)
fx(m["A35"],"المجموع",b=True)
for ci,col in zip(range(2,8),"BCDEFG"):
    fx(m.cell(row=35,column=ci),f"=SUM({col}23:{col}34)",INT if col=="B" else JOD,b=True)
m.conditional_formatting.add("G23:G35",CellIsRule(operator="lessThan",formula=["0"],font=Font(name=F,bold=True,color="DC2626")))
m.freeze_panes="A23"
wb.calculation.fullCalcOnLoad=True
wb.save("/home/user/-n-ml-ml/tools/naqra-management.xlsx")
print("saved")
