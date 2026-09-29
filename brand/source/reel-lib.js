const $=id=>document.getElementById(id);
const clamp=(x,a=0,b=1)=>Math.min(b,Math.max(a,x));
const prog=(t,a,b)=>clamp((t-a)/(b-a));
const easeOut=x=>1-Math.pow(1-x,3);
const easeInOut=x=>x<.5?4*x*x*x:1-Math.pow(-2*x+2,3)/2;
const back=x=>{const c=1.7;return 1+(c+1)*Math.pow(x-1,3)+c*Math.pow(x-1,2)};
function show(el,t,a,b,fadeIn=.35,fadeOut=.3,dy=40){
  const i=easeOut(prog(t,a,a+fadeIn)), o=1-prog(t,b-fadeOut,b);
  el.style.opacity=Math.min(i,o);
  el.style.transform=`translateY(${(1-i)*dy}px)`;
}
function pop(el,t,a,b,fadeOut=.3){
  const i=prog(t,a,a+.35), o=1-prog(t,b-fadeOut,b);
  el.style.opacity=Math.min(i>0?1:0,o);
  el.style.transform=`scale(${i>0?back(i):0.001})`;
}
function endCard(t,a){
  const e=document.querySelector('.end'); const ei=easeOut(prog(t,a,a+.5));
  e.style.opacity=ei; e.style.transform=`scale(${0.94+0.06*ei})`;
  const l=$('logo'); if(l) l.style.opacity=1-prog(t,a-.2,a);
}
const STAR_PATH="M12 2.8l2.8 5.9 6.4.8-4.7 4.4 1.2 6.3L12 17.1l-5.7 3.1 1.2-6.3L2.8 9.5l6.4-.8z";
