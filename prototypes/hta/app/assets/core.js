/* SPDX-License-Identifier: GPL-3.0-only
 * Copyright (C) 2026 Cristian Carroccio
 * Pure transaction rules. All monetary values use integer cents.
 */
var PosCore=(function(){
 function amount(value){
  var s=String(value).replace(/^\s+|\s+$/g,"").replace(",", ".");
  if(!/^\d+(\.\d{1,2})?$/.test(s))throw Error("Ingresá un importe positivo con hasta dos decimales");
  var a=s.split("."),n=Number(a[0])*100+Number(((a[1]||"")+"00").slice(0,2));
  if(!isFinite(n)||n>900000000000)throw Error("Importe fuera de rango");
  return n;
 }
 function total(cart,products){
  var n=0;
  for(var i=0;i<cart.length;i++){
   var c=cart[i],p=products[c.p];
   if(!p||c.q<=0||c.q%1||!isFinite(c.q))throw Error("Cantidad inválida");
   n+=p.price*c.q;
  }
  if(n>900000000000)throw Error("Total fuera de rango");
  return n;
 }
 function prepare(cart,products,payments,verified){
  if(!cart.length)throw Error("La venta está vacía");
  var due=total(cart,products),sum=0,a=[],lines=[],needed={};
  for(var i=0;i<4;i++){
   var n=payments[i];
   if(typeof n!=="number"||!isFinite(n)||n<0||n%1||n>900000000000)throw Error("Importe inválido");
   a.push(n);sum+=n;
  }
  if(sum<due)throw Error("El pago es insuficiente");
  var change=sum-due;
  if(change>a[0])throw Error("El excedente debe provenir del efectivo");
  if(a[1]>0&&!verified)throw Error("Verificá la acreditación de la wallet");
  for(var j=0;j<cart.length;j++){
   var c=cart[j],p=products[c.p];
   needed[c.p]=(needed[c.p]||0)+c.q;
   if(needed[c.p]>p.stock)throw Error("Stock insuficiente: "+p.name);
   lines.push({name:p.name,q:c.q,price:p.price});
  }
  var received=a[0];a[0]-=change;
  return {total:due,payments:a,received:received,change:change,lines:lines};
 }
 return {amount:amount,total:total,prepare:prepare};
}());
if(typeof module!=="undefined"&&module.exports)module.exports=PosCore;
