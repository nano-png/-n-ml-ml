from playwright.sync_api import sync_playwright
import pathlib
D=pathlib.Path("/home/user/-n-ml-ml/brand/final")
jobs=[("naqra-logo-primary",2000,1700,None),("naqra-logo-primary-white",2000,1700,None),
      ("naqra-logo-horizontal",1990,740,None),("naqra-logo-horizontal-white",1990,740,None),
      ("naqra-icon",1024,1024,None),("naqra-instagram-profile",1080,1080,None),("naqra-facebook-cover",1640,624,None)]
with sync_playwright() as p:
    b=p.chromium.launch(executable_path="/opt/pw-browsers/chromium-1194/chrome-linux/chrome")
    pg=b.new_page()
    for n,w,h,_ in jobs:
        svg=(D/f"{n}.svg").read_text()
        pg.set_viewport_size({"width":w,"height":h})
        svg2=svg.replace("<svg ",'<svg style="width:100%;height:100%;display:block" ',1)
        pg.set_content('<html><body style="margin:0;background:transparent"><div style="width:%dpx;height:%dpx">%s</div></body></html>'%(w,h,svg2))
        pg.screenshot(path=str(D/f"{n}.png"),omit_background=True,clip={"x":0,"y":0,"width":w,"height":h})
    # preview sheet
    b.close()
print("done")
