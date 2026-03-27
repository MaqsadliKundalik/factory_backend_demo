// ============================================================
// QODIR INVEST SERVIS — Hisobot Generator (Google Apps Script)
// Google Sheets > Extensions > Apps Script ga joylashtiring
// ============================================================

// ===== SOZLAMALAR — shu joyni o'zgartiring =====
const CFG = {
  API_BASE: 'https://factory-backend-demo.onrender.com',          // API manzili (oxirida "/" bo'lmasin)
  PHONE:    '+998912223344',                          // Login telefon
  PASSWORD: '1',                         // Parol
  COMPANY:  '«QODIR INVEST SERVIS» MCHJ',
  PHONES:   '(+998) 94 444 05 38 Seyitjan   (+998) 77 707 71 72 Begzat',
};

// ============================================================
// MENU
// ============================================================
function onOpen() {
  SpreadsheetApp.getUi()
    .createMenu('📊 Hisobot')
    .addItem("Yuk xati + Ishonch qog'ozi", 'generateYukXatiDoc')
    .addSeparator()
    .addItem('Buyurtmalar hisoboti', 'generateOrdersReport')
    .addItem('Yetkazib beruvchilar hisoboti', 'generateSuppliersReport')
    .addSeparator()
    .addItem('Tokenni yangilash (qayta kirish)', 'refreshLogin')
    .addToUi();
}

// ============================================================
// AUTH
// ============================================================
function login() {
  const resp = UrlFetchApp.fetch(CFG.API_BASE + '/auth/web/login/', {
    method: 'post',
    contentType: 'application/json',
    payload: JSON.stringify({ phone_number: CFG.PHONE, password: CFG.PASSWORD }),
    muteHttpExceptions: true,
  });
  if (resp.getResponseCode() !== 200) {
    throw new Error('Login muvaffaqiyatsiz: ' + resp.getContentText());
  }
  const data = JSON.parse(resp.getContentText());
  PropertiesService.getScriptProperties().setProperty('ACCESS_TOKEN', data.access_token);
  return data.access_token;
}

function refreshLogin() {
  try {
    login();
    SpreadsheetApp.getUi().alert('✅ Muvaffaqiyatli kirdingiz.');
  } catch (e) {
    SpreadsheetApp.getUi().alert('❌ Xato: ' + e.message);
  }
}

function getToken() {
  return PropertiesService.getScriptProperties().getProperty('ACCESS_TOKEN') || login();
}

// ============================================================
// API SO'ROVI — sahifalangan yoki oddiy javobni qaytaradi
// ============================================================
function apiGet(path, params) {
  let url = CFG.API_BASE + path;
  if (params) {
    const qs = Object.entries(params)
      .filter(([, v]) => v !== null && v !== undefined && v !== '')
      .map(([k, v]) => k + '=' + encodeURIComponent(v))
      .join('&');
    if (qs) url += '?' + qs;
  }

  const doFetch = (token) => UrlFetchApp.fetch(url, {
    headers: { Authorization: 'Bearer ' + token },
    muteHttpExceptions: true,
  });

  let token = getToken();
  let resp = doFetch(token);

  if (resp.getResponseCode() === 401) {
    token = login();
    resp = doFetch(token);
  }

  if (resp.getResponseCode() !== 200) {
    throw new Error('API xato ' + resp.getResponseCode() + ': ' + resp.getContentText());
  }

  const json = JSON.parse(resp.getContentText());
  // DRF pagination: { count, results: [...] }
  return Array.isArray(json) ? json : (json.results || json);
}

// Barcha sahifalarni yig'ib oladi (page_size katta bo'lsa odatda bir sahifa)
function apiGetAll(path, params) {
  return apiGet(path, { page_size: 1000, ...params });
}

// ============================================================
// YORDAMCHI FUNKSIYALAR
// ============================================================
const STATUS_UZ = {
  NEW:         'Yangi',
  ON_WAY:      "Yo'lda",
  ARRIVED:     'Yetib keldi',
  UNLOADING:   'Tushirilmoqda',
  COMPLETED:   'Yetkazib berilgan',
  REJECTED:    'Bekor qilingan',
};

function statusUz(s) {
  return STATUS_UZ[s] || s;
}

// status_history massividan vaqtni chiqaradi: "HH:mm"
function getHistoryTime(history, status) {
  if (!Array.isArray(history)) return '';
  const entry = history.find(h => h.status === status);
  if (!entry || !entry.timestamp) return '';
  try {
    return Utilities.formatDate(new Date(entry.timestamp), Session.getScriptTimeZone(), 'HH:mm');
  } catch (e) {
    return String(entry.timestamp);
  }
}

function formatDate(iso) {
  if (!iso) return '';
  try {
    return Utilities.formatDate(new Date(iso), Session.getScriptTimeZone(), 'dd.MM.yyyy');
  } catch (e) {
    return String(iso);
  }
}

// ============================================================
// STIL YORDAMCHILARI
// ============================================================
function applyStyle(range, opts) {
  opts = opts || {};
  range.setFontFamily('Calibri').setFontSize(8);
  range.setHorizontalAlignment(opts.align || 'center');
  range.setVerticalAlignment('middle');
  if (opts.bold) range.setFontWeight('bold');
  if (opts.wrap) range.setWrapStrategy(SpreadsheetApp.WrapStrategy.WRAP);
  if (opts.border) {
    range.setBorder(true, true, true, true, true, true,
      '#000000', SpreadsheetApp.BorderStyle.SOLID);
  }
}

// Faqat tashqi chegaralar (ichki bo'linmasdan)
function setBorderOuter(range, top, left, bottom, right) {
  range.setBorder(top, left, bottom, right, null, null,
    '#000000', SpreadsheetApp.BorderStyle.SOLID);
}

// ============================================================
// SHEET 1 — YUK XATI
// order: GET /orders/{id}/ javobi (sub_orders ichida)
// ============================================================
function fillYukXati(ws, order) {
  ws.clearContents();
  ws.clearFormats();

  // Ustun kengliklarini o'rnatish (pixels)
  ws.setColumnWidth(1, 32);   // A
  ws.setColumnWidth(2, 29);   // B
  ws.setColumnWidth(3, 98);   // C
  ws.setColumnWidth(4, 46);   // D
  ws.setColumnWidth(5, 90);   // E
  ws.setColumnWidth(6, 109);  // F
  ws.setColumnWidth(7, 85);   // G
  ws.setColumnWidth(8, 85);   // H

  const subOrders = order.sub_orders || [];

  // --- Sarlavha ---
  const r2 = ws.getRange('B2:H2');
  r2.merge().setValue('ЮК ХАТИ');
  applyStyle(r2, { bold: true });
  setBorderOuter(r2, true, true, false, true);

  const r3 = ws.getRange('B3:H3');
  r3.merge().setValue('Кимдан:  ' + CFG.COMPANY);
  applyStyle(r3);
  setBorderOuter(r3, false, true, false, true);

  const r4 = ws.getRange('B4:H4');
  r4.merge().setValue('Кимга: ' + order.client.name + '  INN: ' + order.client.inn_number);
  applyStyle(r4);
  setBorderOuter(r4, false, true, true, true);

  // --- Mahsulot jadvali sarlavhasi ---
  ws.getRange('B5').setValue('№');
  ws.getRange('C5:D5').merge().setValue('Махсулот номи');
  ws.getRange('E5').setValue('Улчов бирлиги');
  ws.getRange('F5').setValue('Микдори');
  ws.getRange('G5').setValue('Нархи');
  ws.getRange('H5').setValue('Суммаси');
  applyStyle(ws.getRange('B5:H5'), { border: true });

  // Mahsulot qatori
  ws.getRange('B6').setValue(1);
  ws.getRange('C6:D6').merge().setValue(order.product.name + ' ' + order.type.name);
  ws.getRange('E6').setValue(order.unit.name);
  ws.getRange('F6').setValue(Number(order.quantity));
  ws.getRange('G6').setValue(Number(order.price));
  ws.getRange('H6').setFormula('=F6*G6');
  applyStyle(ws.getRange('B6:H6'), { border: true });
  ws.getRange('G6').setNumberFormat('#,##0');
  ws.getRange('H6').setNumberFormat('#,##0');

  // --- Yetkazib beruvchilar ---
  const r8 = ws.getRange('B8:H8');
  r8.merge().setValue('Yetkazib beruvchilar');
  applyStyle(r8, { bold: true });
  setBorderOuter(r8, false, true, false, true);

  const ybHeaders = [
    '№', 'avtomobil raqami', 'shafyor', 'yuk miqdori (kub)',
    'заводдан \nчикарилган вакти', 'Махсулот етказиб \nберилган вакти', 'Yuk tushirib \nolingan vaqti'
  ];
  ws.getRange(9, 2, 1, 7).setValues([ybHeaders]);
  applyStyle(ws.getRange(9, 2, 1, 7), { border: true, wrap: true });

  subOrders.forEach((so, i) => {
    const row = 10 + i;
    const history = so.status_history || [];
    ws.getRange(row, 2).setValue(i + 1);
    ws.getRange(row, 3).setValue(so.transport ? so.transport.number : '');
    ws.getRange(row, 4).setValue(so.driver ? so.driver.name : '');
    ws.getRange(row, 5).setValue(Number(so.quantity));
    ws.getRange(row, 6).setValue(getHistoryTime(history, 'ON_WAY'));
    ws.getRange(row, 7).setValue(getHistoryTime(history, 'ARRIVED'));
    ws.getRange(row, 8).setValue(getHistoryTime(history, 'COMPLETED'));
    applyStyle(ws.getRange(row, 2, 1, 7), { border: true });
  });

  // --- Qabul qiluvchilar ---
  const qbTitleRow = 10 + subOrders.length + 1;
  const qbHeadRow  = qbTitleRow + 1;
  const qbDataStart = qbHeadRow + 1;

  const rQbTitle = ws.getRange(qbTitleRow, 2, 1, 6);
  rQbTitle.merge().setValue('Qabul qiluvchilar');
  applyStyle(rQbTitle, { bold: true });
  setBorderOuter(rQbTitle, false, true, false, true);

  const qbHeaders = [
    '№', 'avtomobil', 'shafyor',
    'Qabul qiluvchi (ism) ', 'Qabul qiluvchi (lavozimi) ', 'holati'
  ];
  ws.getRange(qbHeadRow, 2, 1, 6).setValues([qbHeaders]);
  applyStyle(ws.getRange(qbHeadRow, 2, 1, 6), { border: true });

  subOrders.forEach((so, i) => {
    const row = qbDataStart + i;
    ws.getRange(row, 2).setValue(i + 1);
    ws.getRange(row, 3).setValue(so.transport ? so.transport.number : '');
    ws.getRange(row, 4).setValue(so.driver ? so.driver.name : '');
    ws.getRange(row, 5).setValue(order.client.name);
    ws.getRange(row, 6).setValue('mijoz');
    ws.getRange(row, 7).setValue(so.status === 'COMPLETED' ? 'Qabul qildim' : statusUz(so.status));
    applyStyle(ws.getRange(row, 2, 1, 6), { border: true });
  });

  // --- Pastki qism ---
  const bottomRow = qbDataStart + subOrders.length + 1;
  ws.getRange(bottomRow,     3).setValue('Manzil: ' + (order.branch ? order.branch.address : ''));
  ws.getRange(bottomRow + 1, 3).setValue(CFG.PHONES);
  ws.getRange(bottomRow + 1, 3).setHorizontalAlignment('left');
  ws.getRange(bottomRow + 3, 8).setValue('{qr code}');
  setBorderOuter(ws.getRange(bottomRow + 3, 8), false, null, true, true);

  SpreadsheetApp.flush();
}

// ============================================================
// SHEET 2 — ISHONCH QOG'OZI
// order: buyurtma, subOrder: bitta sub_order
// ============================================================
function fillIshonchQogozi(ws, order, subOrder) {
  ws.clearContents();
  ws.clearFormats();

  ws.setColumnWidth(1, 28);   // A
  ws.setColumnWidth(2, 156);  // B
  ws.setColumnWidth(3, 76);   // C
  ws.setColumnWidth(4, 51);   // D
  ws.setColumnWidth(5, 61);   // E
  ws.setColumnWidth(6, 98);   // F

  // Sarlavha
  const r1 = ws.getRange('A1:F1');
  r1.merge().setValue('YUK XATI');
  applyStyle(r1, { bold: true });
  setBorderOuter(r1, true, true, false, true);

  const r2 = ws.getRange('A2:F2');
  r2.merge().setValue('Кимдан:  ' + CFG.COMPANY);
  applyStyle(r2, { align: 'left' });
  setBorderOuter(r2, false, true, false, true);

  // Sana
  ws.getRange('F3').setValue(formatDate(order.created_at));
  applyStyle(ws.getRange('F3'));
  setBorderOuter(ws.getRange('F3'), false, null, false, true);

  // Kimga + INN
  const r4a = ws.getRange('A4:C4');
  r4a.merge().setValue('Kimga: ' + order.client.name);
  applyStyle(r4a, { align: 'left' });
  setBorderOuter(r4a, false, true, false, null);

  const r4b = ws.getRange('D4:F4');
  r4b.merge().setValue('INN: ' + order.client.inn_number);
  applyStyle(r4b, { align: 'left' });
  setBorderOuter(r4b, false, null, false, true);

  // Ishonch qog'ozi satri
  const driverName   = subOrder.driver    ? subOrder.driver.name    : '';
  const transportNum = subOrder.transport ? subOrder.transport.number : '';
  const r5 = ws.getRange('A5:F5');
  r5.merge().setValue("Ishonch qog'ozi:  " + driverName + ' / ' + transportNum);
  applyStyle(r5, { align: 'left' });
  setBorderOuter(r5, false, true, false, true);

  // Jadval sarlavha
  const tblHeaders = ['№', 'Mahsulot nomi', "O'lchov birligi", 'Miqdori', 'narxi', 'Summasi'];
  ws.getRange('A6:F6').setValues([tblHeaders]);
  applyStyle(ws.getRange('A6:F6'), { border: true });

  // Mahsulot qatori
  ws.getRange('A7').setValue(1);
  ws.getRange('B7').setValue(order.product.name + ' ' + order.type.name);
  ws.getRange('C7').setValue(order.unit.name);
  ws.getRange('D7').setValue(Number(subOrder.quantity));
  ws.getRange('E7').setValue(Number(order.price));
  ws.getRange('F7').setFormula('=E7*D7');
  applyStyle(ws.getRange('A7:F7'), { border: true });
  ws.getRange('E7').setNumberFormat('#,##0');
  ws.getRange('F7').setNumberFormat('#,##0');

  // Bo'sh qatorlar (imzo uchun)
  [8, 9].forEach(r => {
    ws.getRange(r, 1).setValue(r - 6);
    applyStyle(ws.getRange(r, 1, 1, 6), { border: true });
  });

  // Telefon
  const r10 = ws.getRange('A10:F10');
  r10.merge().setValue(CFG.PHONES);
  applyStyle(r10, { align: 'left' });
  setBorderOuter(r10, false, true, false, true);

  // Topshirdi / Qabul qildi
  const r11a = ws.getRange('A11:B11');
  r11a.merge().setValue('Topshirdi:');
  applyStyle(r11a, { align: 'left' });
  setBorderOuter(r11a, false, true, true, null);
  r11a.setBorder(null, null, null, null, null, null); // faqat bottom

  const r11b = ws.getRange('C11:F11');
  r11b.merge().setValue('Qabul qildi:');
  applyStyle(r11b, { align: 'left' });
  setBorderOuter(r11b, false, null, true, true);

  // Topshirdi va Qabul qildi uchun faqat pastki chegara
  r11a.setBorder(false, true, true, false, null, null, '#000000', SpreadsheetApp.BorderStyle.SOLID);
  r11b.setBorder(false, false, true, true, null, null, '#000000', SpreadsheetApp.BorderStyle.SOLID);

  SpreadsheetApp.flush();
}

// ============================================================
// SHEET 3 — BUYURTMALAR HISOBOTI
// ============================================================
function fillBuyurtmalarHisoboti(ws, orders) {
  ws.clearContents();
  ws.clearFormats();

  ws.setColumnWidth(1, 27);   // A №
  ws.setColumnWidth(2, 153);  // B Mijoz
  ws.setColumnWidth(3, 69);   // C Mahsulot
  ws.setColumnWidth(4, 40);   // D Miqdor
  ws.setColumnWidth(5, 30);   // E Birlik
  ws.setColumnWidth(6, 40);   // F Narx
  ws.setColumnWidth(7, 79);   // G Summa
  ws.setColumnWidth(8, 90);   // H Sana
  ws.setColumnWidth(9, 142);  // I Holat

  // Sarlavha
  const r1 = ws.getRange('A1:I1');
  r1.merge().setValue("Buyurtmalar bo'yicha hisobot " + CFG.COMPANY);
  r1.setFontFamily('Calibri').setFontSize(8).setHorizontalAlignment('center');

  // Jadval sarlavha
  const headers = ['№', 'Mijozlar', 'Maxsulot nomi', 'Miqdori', 'Birligi', 'Narxi', 'Summasi', 'Sana', 'Holati'];
  ws.getRange('A2:I2').setValues([headers]);
  applyStyle(ws.getRange('A2:I2'), { border: true });

  // Ma'lumot qatorlari
  orders.forEach((order, i) => {
    const row = i + 3;
    ws.getRange(row, 1).setValue(i + 1);
    ws.getRange(row, 2).setValue(order.client.name);
    ws.getRange(row, 3).setValue(order.product.name + (order.type ? ' ' + order.type.name : ''));
    ws.getRange(row, 4).setValue(Number(order.quantity));
    ws.getRange(row, 5).setValue(order.unit ? order.unit.name : '');
    ws.getRange(row, 6).setValue(Number(order.price));
    ws.getRange(row, 7).setFormula('=D' + row + '*F' + row);
    ws.getRange(row, 8).setValue(formatDate(order.created_at));
    ws.getRange(row, 9).setValue(statusUz(order.status));
    applyStyle(ws.getRange(row, 1, 1, 9), { border: true });
    ws.getRange(row, 6).setNumberFormat('#,##0');
    ws.getRange(row, 7).setNumberFormat('#,##0');
  });

  // JAMI qatori
  if (orders.length > 0) {
    const totalRow = orders.length + 3;
    const rTotal = ws.getRange(totalRow, 1, 1, 9);
    ws.getRange(totalRow, 1, 1, 6).merge().setValue('JAMI:').setHorizontalAlignment('right').setFontWeight('bold');
    ws.getRange(totalRow, 7).setFormula('=SUM(G3:G' + (totalRow - 1) + ')');
    ws.getRange(totalRow, 7).setNumberFormat('#,##0').setFontWeight('bold');
    applyStyle(rTotal, { border: true });
  }

  SpreadsheetApp.flush();
}

// ============================================================
// SHEET 4 — YETKAZIB BERUVCHILAR HISOBOTI
// items: GET /products/whouse/ javobi
// ============================================================
function fillYetkazibBeruvchilarHisoboti(ws, items) {
  ws.clearContents();
  ws.clearFormats();

  ws.setColumnWidth(1, 27);
  ws.setColumnWidth(2, 161);
  ws.setColumnWidth(3, 99);
  ws.setColumnWidth(4, 119);
  ws.setColumnWidth(5, 74);
  ws.setColumnWidth(6, 81);
  ws.setColumnWidth(7, 77);
  ws.setColumnWidth(8, 94);

  // Sarlavha
  const r1 = ws.getRange('A1:H1');
  r1.merge().setValue("Yetkazib beruvchilar bo'yicha hisobot");
  r1.setFontFamily('Calibri').setFontSize(8).setHorizontalAlignment('center');

  // Jadval sarlavha
  const headers = ['№', 'Yetkazib beruvchi', 'Nomeri', 'Mahsulot nomi', 'Turi', 'Miqdori', 'Birligi', 'Sana'];
  ws.getRange('A2:H2').setValues([headers]);
  applyStyle(ws.getRange('A2:H2'), { border: true });

  // Ma'lumot qatorlari
  items.forEach((item, i) => {
    const row = i + 3;
    const supplier = item.supplier || {};
    const phones   = supplier.phone_numbers || supplier.phones || [];
    const phone    = phones.length > 0 ? phones[0].phone_number : '';

    ws.getRange(row, 1).setValue(i + 1);
    ws.getRange(row, 2).setValue(supplier.name || '');
    ws.getRange(row, 3).setValue(phone);
    ws.getRange(row, 4).setValue(item.product ? item.product.name : '');
    ws.getRange(row, 5).setValue(item.product_type ? item.product_type.name : '-');
    ws.getRange(row, 6).setValue(Number(item.quantity));
    ws.getRange(row, 7).setValue(item.product && item.product.unit ? item.product.unit.name : '');
    ws.getRange(row, 8).setValue(formatDate(item.created_at));
    applyStyle(ws.getRange(row, 1, 1, 8), { border: true });
  });

  SpreadsheetApp.flush();
}

// ============================================================
// MENU AMALLAR
// ============================================================

// Yuk xati + Ishonch qog'ozi: order display_id so'raydi
function generateYukXatiDoc() {
  const ui = SpreadsheetApp.getUi();
  const resp = ui.prompt(
    "Buyurtma raqami",
    'Order display_id kiriting (masalan: 42):',
    ui.ButtonSet.OK_CANCEL
  );
  if (resp.getSelectedButton() !== ui.Button.OK) return;

  const displayId = resp.getResponseText().trim();
  if (!displayId) { ui.alert('Raqam kiritilmadi.'); return; }

  try {
    // search bilan qidirib, keyin mosini topamiz
    const orders = apiGetAll('/orders/', { search: displayId });
    const order  = orders.find(o => String(o.display_id) === displayId);
    if (!order) {
      ui.alert('❌ #' + displayId + ' raqamli buyurtma topilmadi.');
      return;
    }

    const ss = SpreadsheetApp.getActiveSpreadsheet();

    // Sheet 1: Yuk xati
    let yukSheet = ss.getSheetByName('Yuk xati');
    if (!yukSheet) yukSheet = ss.insertSheet('Yuk xati');
    fillYukXati(yukSheet, order);

    // Sheet 2: har bir sub_order uchun Ishonch qog'ozi
    const subOrders = order.sub_orders || [];
    subOrders.forEach((so, i) => {
      const sheetName = subOrders.length === 1
        ? "Ishonch qog'ozi"
        : "Ishonch qog'ozi " + (i + 1);
      let iqSheet = ss.getSheetByName(sheetName);
      if (!iqSheet) iqSheet = ss.insertSheet(sheetName);
      fillIshonchQogozi(iqSheet, order, so);
    });

    ss.setActiveSheet(yukSheet);
    ui.alert(
      '✅ Tayyor!\nBuyurtma #' + displayId +
      '\n— Yuk xati: 1 ta\n— Ishonch qog\'ozi: ' + subOrders.length + ' ta'
    );
  } catch (e) {
    ui.alert('❌ Xato: ' + e.message);
    Logger.log(e);
  }
}

// Sana oralig'ini so'rash (dd.MM.yyyy formatida)
function askDateRange_() {
  const ui = SpreadsheetApp.getUi();

  const from = ui.prompt('Boshlanish sanasi', 'dd.MM.yyyy formatida (masalan: 01.01.2026):', ui.ButtonSet.OK_CANCEL);
  if (from.getSelectedButton() !== ui.Button.OK) return null;

  const to = ui.prompt('Tugash sanasi', 'dd.MM.yyyy formatida (masalan: 31.03.2026):', ui.ButtonSet.OK_CANCEL);
  if (to.getSelectedButton() !== ui.Button.OK) return null;

  function toISO(str) {
    const parts = str.trim().split('.');
    if (parts.length !== 3) throw new Error('Sana formati noto\'g\'ri: ' + str);
    return parts[2] + '-' + parts[1].padStart(2, '0') + '-' + parts[0].padStart(2, '0');
  }

  return {
    start_date: toISO(from.getResponseText()),
    end_date:   toISO(to.getResponseText()),
  };
}

// Buyurtmalar hisoboti
function generateOrdersReport() {
  const ui = SpreadsheetApp.getUi();
  try {
    const dates = askDateRange_();
    if (!dates) return;

    const orders = apiGetAll('/orders/', dates);
    const ss = SpreadsheetApp.getActiveSpreadsheet();
    let ws = ss.getSheetByName('Buyurtmalar boyicha hisobot');
    if (!ws) ws = ss.insertSheet('Buyurtmalar boyicha hisobot');
    fillBuyurtmalarHisoboti(ws, orders);
    ss.setActiveSheet(ws);
    ui.alert('✅ Tayyor! ' + orders.length + " ta buyurtma ko'rsatildi.");
  } catch (e) {
    ui.alert('❌ Xato: ' + e.message);
    Logger.log(e);
  }
}

// Yetkazib beruvchilar hisoboti
function generateSuppliersReport() {
  const ui = SpreadsheetApp.getUi();
  try {
    const dates = askDateRange_();
    if (!dates) return;

    const items = apiGetAll('/products/whouse/', dates);
    const ss = SpreadsheetApp.getActiveSpreadsheet();
    let ws = ss.getSheetByName('Yetkazib beruchilar boyicha xis');
    if (!ws) ws = ss.insertSheet('Yetkazib beruchilar boyicha xis');
    fillYetkazibBeruvchilarHisoboti(ws, items);
    ss.setActiveSheet(ws);
    ui.alert('✅ Tayyor! ' + items.length + " ta yetkazib beruvchi ko'rsatildi.");
  } catch (e) {
    ui.alert('❌ Xato: ' + e.message);
    Logger.log(e);
  }
}
