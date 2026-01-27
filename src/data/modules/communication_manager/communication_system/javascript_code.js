function initPassiveCaptureBuffer() {
    if (!window.__PASSIVE_CAPTURE__) {
        window.__PASSIVE_CAPTURE__ = {
            buffer: [],
            initialized_at: new Date().toISOString()
        };
        return true; // creado
    }
    return false; // ya existía
}

function isClientProfileVisible() {
    // Selectores de ejemplo (adaptar al CRM)
    const uidElement = document.querySelector("[data-client-uid]");
    return Boolean(uidElement);
}

function extractClientProfileData() {
    if (!isClientProfileVisible()) return null;

    const uid = document.querySelector("[data-client-uid]")?.innerText?.trim();
    if (!uid) return null;

    return {
        uid: uid,
        name: document.querySelector(".client-name")?.innerText || null,
        phone: document.querySelector(".client-phone")?.innerText || null,
        email: document.querySelector(".client-email")?.innerText || null,
        credit_limit: document.querySelector(".credit-limit")?.innerText || null,
        last_approved: document.querySelector(".last-approved")?.innerText || null,
        captured_at: new Date().toISOString()
    };
}

function storeClientInBuffer(clientProfile) {
    if (!clientProfile || !clientProfile.uid) return false;

    const exists = window.__PASSIVE_CAPTURE__.buffer
        .some(c => c.uid === clientProfile.uid);

    if (exists) return false;

    window.__PASSIVE_CAPTURE__.buffer.push(clientProfile);
    return true;
}

function passiveCaptureTick() {
    if (!window.__PASSIVE_CAPTURE__) return;

    const profile = extractClientProfileData();
    if (!profile) return;

    storeClientInBuffer(profile);
}

function passiveCaptureTick() {
    if (!window.__PASSIVE_CAPTURE__) return;

    const profile = extractClientProfileData();
    if (!profile) return;

    storeClientInBuffer(profile);
}

function getPassiveCaptureBuffer() {
    return window.__PASSIVE_CAPTURE__?.buffer || [];
}

function getPassiveCaptureBuffer() {
    return window.__PASSIVE_CAPTURE__?.buffer || [];
}

/*
[ initPassiveCaptureBuffer() ]
            ↓
[ isClientProfileVisible() ]
            ↓
[ extractClientProfileData() ]
            ↓
[ storeClientInBuffer() ]
            ↓
[ getPassiveCaptureBuffer() ]  → Python
 */



/* NEW CODE */
function initializeBufferStorage(){
    // Verify the current existence of the buffer
    if (sessionStorage.getItem("CaptureBuffer")){ return true; }
    else { sessionStorage.setItem("CaptureBuffer", JSON.stringify({})); return true; }
}

function identifyContact(){
    let contactConsoleFrame = document.getElementById("outboundCallConsole");

    if (contactConsoleFrame === null){ return false; }
    else { return true; }
}

function getContactData() {
    const contactConsoleFrame = document.getElementById("outboundCallConsole");
    if (!contactConsoleFrame || !contactConsoleFrame.contentDocument) {
        return null;
    }

    const contactDataFrame =
        contactConsoleFrame.contentDocument.getElementById("contactsConsole");

    if (!contactDataFrame || !contactDataFrame.contentDocument) {
        return null;
    }

    const keys = contactDataFrame.contentDocument.querySelectorAll(
        "div.el-form-item__label"
    );
    const values = contactDataFrame.contentDocument.querySelectorAll(
        "div.el-form-item__content"
    );

    const contactData = {};

    const length = Math.min(keys.length, values.length);

    for (let i = 0; i < length; i++) {
        const key = keys[i].textContent.trim().replace(":", "");
        const value = values[i].textContent.trim();

        contactData[key] = value;
        console.log(key, value);
    }

    return contactData;
}

function saveContactData(contactData) {
    if (!contactData || typeof contactData !== "object") return false;

    const uid = contactData["UID"];
    if (!uid) return false;

    const buffer = getCaptureBuffer();

    if (buffer[uid]) {
        console.log(`Contacto con UID ${uid} ya existe`);
        return false;
    }

    buffer[uid] = contactData;
    setBufferStorage(buffer);

    console.log(`Contacto ${uid} guardado`);
    return true;
}

function setBufferStorage(buffer) {
    sessionStorage.setItem("CaptureBuffer", JSON.stringify(buffer));
}

function backgroundContactWatcher() {
    try {
        // 1️⃣ ¿Hay contacto en pantalla?
        if (!identifyContact()) {
            return;
        }

        // 2️⃣ Intentar obtener datos
        const contactData = getContactData();

        if (!contactData || typeof contactData !== "object") {
            return;
        }

        // 3️⃣ Validar UID mínimo
        if (!contactData["UID"]) {
            console.warn("Contacto detectado sin UID todavía");
            return;
        }

        // 4️⃣ Guardar (la función ya evita duplicados)
        saveContactData(contactData);

    } catch (error) {
        console.error("Error en backgroundContactWatcher:", error);
    }
}

function startContactMonitoring(intervalMs = 1000) {
    if (sessionStorage.getItem("ContactMonitorID")) {
        console.warn("⚠️ Monitor ya activo");
        return sessionStorage.getItem("ContactMonitorID");
    }

    console.log("📡 Iniciando monitoreo de contactos...");
    const monitorId = setInterval(backgroundContactWatcher, intervalMs);
    sessionStorage.setItem("ContactMonitorID", monitorId);

    return monitorId;
}

function stopContactMonitoring() {
    const monitorId = sessionStorage.getItem("ContactMonitorID");

    if (!monitorId) return true;

    clearInterval(Number(monitorId));
    sessionStorage.removeItem("ContactMonitorID");

    console.log("🛑 Monitoreo detenido");
    return true;
}

function getCaptureBuffer(){
    initializeBufferStorage();
    return JSON.parse(sessionStorage.getItem("CaptureBuffer"));
}

function emptyCaptureBuffer(){
    sessionStorage.removeItem("CaptureBuffer");
    initializeBufferStorage();
    return true;
}

/* Uso */
const monitorId = startContactMonitoring(1500);
//stopContactMonitoring();
