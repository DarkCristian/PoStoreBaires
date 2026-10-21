// SPDX-License-Identifier: GPL-3.0-only
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
const core = require('../app/assets/core.js');
const inventory = [{name:'Agua', price:120000, stock:2}];
const cart = [{p:0,q:1}];
assert.equal(core.amount('0,29'),29);
assert.equal(core.amount('1200.50'),120050);
for(const invalid of ['', '-1', 'NaN', 'Infinity', '0.001', '1e3']) {
  assert.throws(()=>core.amount(invalid));
}
const cash = core.prepare(cart,inventory,[200000,0,0,0],false);
assert.equal(cash.change,80000);
assert.equal(cash.payments.reduce((a,b)=>a+b,0),cash.total);
assert.equal(cash.received,200000);
const mixed = core.prepare(cart,inventory,[50000,70000,0,0],true);
assert.equal(mixed.change,0);
assert.equal(mixed.payments[1],70000);
assert.throws(()=>core.prepare(cart,inventory,[0,120000,0,0],false),/acreditación/);
assert.throws(()=>core.prepare(cart,inventory,[0,120001,0,0],true),/efectivo/);
assert.throws(()=>core.prepare(cart,inventory,[119999,0,0,0],true),/insuficiente/);
assert.throws(()=>core.prepare([{p:0,q:3}],inventory,[360000,0,0,0],true),/Stock/);
assert.throws(()=>core.prepare([{p:0,q:1},{p:0,q:2}],inventory,[360000,0,0,0],true),/Stock/);
assert.equal(inventory[0].stock,2,'preparing/rejecting a transaction never mutates inventory');

// Exercise the actual UI confirmation handler with a minimal DOM stub.
const nodes={};
const sandbox={PosCore:core,window:{},document:{getElementById:id=>nodes[id]},
 setTimeout:()=>0,clearTimeout:()=>{},console};
vm.createContext(sandbox);
vm.runInContext(fs.readFileSync(path.join(__dirname,'../app/assets/app.js'),'utf8'),sandbox);
let warning='';
sandbox.toast=t=>{warning=t};
sandbox.render=()=>{};sandbox.closeModal=()=>{};sandbox.playSound=()=>{};
sandbox.cart=[{p:0,q:1}];
for(let i=0;i<4;i++)nodes['pay'+i]={value:i===1?'850':'0'};
nodes.verified={checked:false};
const stockBefore=sandbox.products[0].stock;
sandbox.confirmSale();
assert.equal(sandbox.sales.length,0);
assert.equal(sandbox.products[0].stock,stockBefore);
assert.match(warning,/acreditación/);
nodes.verified.checked=true;
sandbox.confirmSale();
assert.equal(sandbox.sales.length,1);
assert.equal(sandbox.products[0].stock,stockBefore-1);
assert.equal(sandbox.cart.length,0);
assert.equal(sandbox.sales[0].payments[1],85000);
// A second click must not record a duplicate or change inventory.
sandbox.confirmSale();
assert.equal(sandbox.sales.length,1);
assert.equal(sandbox.products[0].stock,stockBefore-1);
// Customer QR/alias is rendered during an ordinary cart, before payment.
sandbox.cfg.display=true;sandbox.cfg.walletView='both';
sandbox.cfg.qr='file:///C:/qr.png';sandbox.cfg.alias='mi.comercio';
sandbox.cart=[{p:0,q:1}];sandbox.customerState='cart';
const content={innerHTML:''};
sandbox.customer={closed:false,document:{getElementById:()=>content}};
sandbox.updateCustomer();
assert.match(content.innerHTML,/file:\/\/\/C:\/qr.png/);
assert.match(content.innerHTML,/mi\.comercio/);
assert.match(content.innerHTML,/850,00/);
sandbox.customerState='wallet';nodes.pay1.value='300.50';
sandbox.updateCustomer();assert.match(content.innerHTML,/300,50/);
nodes.verified.checked=true;sandbox.paymentChanged();
assert.equal(nodes.verified.checked,false);
sandbox.customerState='result';sandbox.updateCustomer();
assert.match(content.innerHTML,/Cobrado OK/);
console.log('Transaction and customer-display tests passed. Windows UI/hardware remains manual.');
